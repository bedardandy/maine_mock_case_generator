"""Project a rich Mock Matter down to the downstream canonical case object.

This is the seam into the form-filling repos (maine-court-forms, maine-probate-forms,
transactional-tax-forms): they consume the canonical fact object, and this function
produces it from a Mock Matter. Validate the result with schema.validate_canonical().
"""
from __future__ import annotations

_CANONICAL_PARTY_FIELDS = (
    "full_name", "first_name", "middle_name", "last_name",
    "address", "city", "state", "zip", "phone", "email",
    "date_of_birth", "signature", "bar_number",
)

# "client" is intentionally not projected as a party because it aliases another
# role and becomes the signing `party` instead. Every other party role carries
# through (including multi-party rosters like plaintiff_2 / third_party_defendant),
# since the canonical schema allows additional party keys.
_SKIP_ROLES = ("client",)

# When a strict downstream filler expects plaintiff/defendant, supply them from an
# equivalent role without dropping the original. Each target lists candidate sources
# tried in order. Estate forms (e.g. MRS-706ME) model the decedent as the primary
# "plaintiff" party, so a decedent fills plaintiff when no literal plaintiff exists.
_ALIASES = {
    "plaintiff": ("petitioner", "decedent"),
    "defendant": ("respondent",),
}


def _reduce_party(party: dict) -> dict:
    out = {k: party[k] for k in _CANONICAL_PARTY_FIELDS if party.get(k) not in (None, "")}
    # Organizations carry their name in organization_name; mirror to full_name.
    if "full_name" not in out and party.get("organization_name"):
        out["full_name"] = party["organization_name"]
    return out


def project_to_canonical(matter: dict) -> dict:
    matter_meta = matter.get("matter", {})
    jurisdiction = matter_meta.get("jurisdiction", {})

    canonical_matter = {}
    if matter_meta.get("docket_number"):
        canonical_matter["docket_number"] = matter_meta["docket_number"]
    if matter_meta.get("matter_id"):
        canonical_matter["case_id"] = matter_meta["matter_id"]
    if jurisdiction.get("county"):
        canonical_matter["court_county"] = jurisdiction["county"]
    if jurisdiction.get("court_location"):
        canonical_matter["court_location"] = jurisdiction["court_location"]
    if jurisdiction.get("court_type"):
        canonical_matter["court_type"] = jurisdiction["court_type"]
    if matter_meta.get("case_type"):
        canonical_matter["case_type"] = matter_meta["case_type"]
    if matter_meta.get("filing_date"):
        canonical_matter["filing_date"] = matter_meta["filing_date"]
    if matter_meta.get("event_date"):
        canonical_matter["event_date"] = matter_meta["event_date"]

    src_parties = matter.get("parties", {})
    canonical_parties: dict = {}
    for key, party in src_parties.items():
        if key in _SKIP_ROLES:
            continue
        canonical_parties[key] = _reduce_party(party)
    # Aliases so plaintiff/defendant exist for strict downstream fillers.
    for target, sources in _ALIASES.items():
        if target in canonical_parties:
            continue
        for source in sources:
            if source in canonical_parties:
                canonical_parties[target] = dict(canonical_parties[source])
                break

    case = {"matter": canonical_matter, "parties": canonical_parties}
    provenance = matter.get("provenance", {})
    if provenance:
        case["_provenance"] = {
            key: provenance.get(key)
            for key in ("fixture_id", "scenario_id", "seed", "reference_date", "generator_version")
            if provenance.get(key) is not None
        }

    # Signing filer (`party`): the represented client, else plaintiff/petitioner.
    signer_source = None
    for key in ("client", "plaintiff", "petitioner", "personal_representative"):
        if key in src_parties:
            signer_source = src_parties[key]
            break
    if signer_source is not None:
        case["party"] = _reduce_party(signer_source)
        # A filer signs their own name; provide it for forms with a signature field.
        if case["party"].get("full_name") and not case["party"].get("signature"):
            case["party"]["signature"] = case["party"]["full_name"]

    if matter.get("facts"):
        case["facts"] = dict(matter["facts"])

    return case
