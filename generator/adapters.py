"""Namespace adapters: bridge a projected canonical case into a downstream repo's
fact-key namespace.

The court-forms repos consume the canonical namespace directly
(``matter`` / ``parties`` / ``party`` / ``facts``), so they need no adapter
(profile ``canonical``). The transactional-tax-forms repo uses a different namespace
(``entity`` / ``responsible_party`` / ``executor`` / ``decedent`` / ``trust`` / ``facts``),
so business and estate matters are translated by :func:`to_tax_case` (profile ``tax``).

Everything stays fictional; no value is invented beyond what the matter already implies.
"""
from __future__ import annotations


def _pick(d: dict, *keys: str):
    for k in keys:
        v = d.get(k)
        if v not in (None, ""):
            return v
    return ""


def _fiction_tin(party: dict) -> str:
    """A clearly-fictional taxpayer id. 900-series area numbers are never valid SSNs."""
    last4 = party.get("ssn_last4")
    if last4:
        return f"900-00-{last4}"
    return ""


def to_tax_case(canonical: dict, matter: dict) -> dict:
    """Translate a canonical case into the transactional-tax-forms namespace.

    Handles both business matters (``company`` + applicant) and estate matters
    (``decedent`` + ``personal_representative``). Unmapped, situational EIN-application
    fields are left blank on purpose — the coverage report shows them as gaps.
    """
    parties = canonical.get("parties", {})
    facts = dict(canonical.get("facts", {}))
    signer = canonical.get("party", {})
    jurisdiction = matter.get("matter", {}).get("jurisdiction", {})

    # The canonical projection drops ssn_last4; read identifiers from the full matter.
    m_parties = matter.get("parties", {})
    signer_full = m_parties.get("client", {})
    decedent_full = m_parties.get("decedent", {})

    company = parties.get("company", {})
    decedent = parties.get("decedent", {})
    personal_rep = parties.get("personal_representative", {})

    tax: dict = {
        "entity": {},
        "responsible_party": {},
        "executor": {},
        "decedent": {},
        "trust": {},
        "facts": {},
    }

    # --- Business entity (Form SS-4 for a new corporation) ---------------
    if company:
        tax["entity"] = {
            "legal_name": _pick(facts, "entity_name") or company.get("full_name", ""),
            "trade_name": facts.get("trade_name", ""),
            "street_address": company.get("address", ""),
            "mailing_address": company.get("address", ""),
            "mailing_city": company.get("city", ""),
            "county": jurisdiction.get("county", ""),
            "phone": company.get("phone", ""),
            "state_of_formation": _pick(facts, "state_of_incorporation") or company.get("state", ""),
            "formation_date": facts.get("incorporation_date", ""),
            "ein": "",  # blank: the form IS the EIN application
        }
        tax["responsible_party"] = {
            "name": _pick(facts, "responsible_party_name") or signer.get("full_name", ""),
            "ssn_itin_ein": _fiction_tin(signer_full),
        }
        closing = facts.get("fiscal_year_end", "")
        tax["facts"].update({
            "new_org_type": "Corporation (S-corporation election pending)"
            if facts.get("s_corp_election") else "Corporation",
            "new_business_type": facts.get("principal_activity", ""),
            "principal_line_of_merchandise": facts.get("principal_activity", ""),
            "first_date_wages_paid": facts.get("first_payroll_date", ""),
            "accounting_year_closing_month": str(closing).split()[0] if closing else "",
            "reason_for_applying": "Started new business",
        })

    # --- Estate (an estate may need its own EIN) ------------------------
    if decedent:
        tax["decedent"] = {"ssn": _fiction_tin(decedent_full)}
        tax["executor"] = {
            "name": personal_rep.get("full_name") or signer.get("full_name", "")
        }
        tax["facts"].setdefault("reason_for_applying", "Estate administration")

    # Pass through any flat canonical facts so tax forms that read facts.* still resolve.
    for key, value in facts.items():
        tax["facts"].setdefault(key, value)

    return tax


# Grantor/grantee role fallbacks: deed-style scenarios use transferor/transferee,
# the closing-suite scenarios use seller/buyer — both drive the same RETTD.
_RE_ROLE_FALLBACKS = {
    "transferor": ("transferor", "seller"),
    "transferee": ("transferee", "buyer"),
}


def to_real_estate_case(canonical: dict, matter: dict) -> dict:
    """Translate a canonical case into the real-estate transfer namespace (ME-RETTD):
    property / transferor / transferee / facts. Reads grantor/grantee from the
    `transferor`/`transferee` party roles (falling back to `seller`/`buyer`) and the
    property from facts.
    """
    parties = canonical.get("parties", {})
    facts = dict(canonical.get("facts", {}))
    m_parties = matter.get("parties", {})
    jurisdiction = matter.get("matter", {}).get("jurisdiction", {})

    def party_block(role: str) -> dict:
        key = next((k for k in _RE_ROLE_FALLBACKS[role] if parties.get(k)), role)
        party = parties.get(key, {})
        return {
            "name": party.get("full_name", ""),
            "address": party.get("address", ""),
            "mailing_address": party.get("address", ""),
            "mailing_city": party.get("city", ""),
            "mailing_state": party.get("state", ""),
            "mailing_zip": party.get("zip", ""),
            "ssn_or_ein": _fiction_tin(m_parties.get(key, {})),
        }

    re_case = {
        "transferor": party_block("transferor"),
        "transferee": party_block("transferee"),
        "property": {
            "address": facts.get("property_address", ""),
            "town": facts.get("property_town", ""),
            "county": facts.get("property_county") or jurisdiction.get("county", ""),
            "map_block_lot": facts.get("property_map_block_lot", ""),
            "purchase_price": facts.get("purchase_price", ""),
            "transfer_date": facts.get("transfer_date", ""),
            "type": facts.get("property_type", ""),
        },
        "facts": {},
    }
    for key, value in facts.items():
        re_case["facts"].setdefault(key, value)
    return re_case


# Profile name -> adapter callable. "canonical" needs no translation.
PROFILES = {
    "tax": to_tax_case,
    "real_estate": to_real_estate_case,
}
