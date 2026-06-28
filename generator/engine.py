"""Deterministic generation of a Mock Matter from a scenario archetype.

generate_matter(scenario_id, seed) is fully reproducible: the same (scenario_id, seed)
always yields the same matter (no timestamps or external state are embedded).
"""
from __future__ import annotations

import copy
import hashlib
import random
from datetime import date, timedelta

from . import dsl
from .pools import Pools, build_organization, build_person
from .scenarios import load_scenario

GENERATOR_VERSION = "0.2.0"
DEFAULT_REFERENCE_DATE = date(2026, 1, 1)

_NUM_WORDS = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
_PERSON_TYPES = {
    "witness", "expert", "opposing_counsel", "guardian_ad_litem", "beneficiary",
    "fiduciary", "creditor", "neighbor", "family_member", "healthcare_provider",
}


def _normalize_reference_date(reference_date: str | date | None) -> date:
    if reference_date is None:
        return DEFAULT_REFERENCE_DATE
    return date.fromisoformat(reference_date) if isinstance(reference_date, str) else reference_date


def _random_recent_date(rng: random.Random, reference_date: date) -> str:
    start = reference_date - timedelta(days=365)
    return (start + timedelta(days=rng.randint(0, 365))).isoformat()


def _ctx_for_party(ctx: dict, key: str, party: dict) -> None:
    ctx[f"{key}_full_name"] = party.get("full_name", "")
    ctx[f"{key}_first"] = party.get("first_name", "")
    ctx[f"{key}_last"] = party.get("last_name", "")


def _name_list(names: list[str]) -> str:
    names = [n for n in names if n]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def _third_party_name(item: dict, pools: Pools) -> tuple[str, str]:
    """Return (name, entity_kind) for a third party, honoring an explicit name/kind."""
    if item.get("name"):
        return item["name"], item.get("entity_type", "organization")
    kind = item.get("name_kind")
    if kind == "bank":
        return pools.bank(), "organization"
    if kind == "employer":
        return pools.employer(), "organization"
    if kind == "law_firm":
        return pools.law_firm(), "organization"
    if kind == "organization":
        return pools.org_name(), "organization"
    if kind == "person" or item.get("type") in _PERSON_TYPES:
        return pools.person_name()["full_name"], "person"
    return pools.org_name(), "organization"


def _build_third_parties(scenario: dict, ctx: dict, rng: random.Random, pools: Pools) -> list:
    spec = scenario.get("third_parties")
    if not spec:
        return []
    chosen = dsl.pick_pool(spec.get("pool", []), spec.get("count"), ctx, rng)
    out = []
    for idx, item in enumerate(chosen, start=1):
        name, entity_kind = _third_party_name(item, pools)
        tp = {
            "id": f"tp{idx}",
            "name": name,
            "type": item.get("type", "other"),
        }
        for field in ("role", "relationship", "description", "relevance"):
            if item.get(field):
                tp[field] = item[field]
        contact = {"phone": pools.phone()}
        addr = pools.address()
        contact["city"] = addr["city"]
        contact["state"] = addr["state"]
        if entity_kind == "person":
            contact["email"] = pools.email(name.split()[0], name.split()[-1])
        tp["contact"] = contact
        out.append(tp)
    return out


def _build_parties(scenario: dict, ctx: dict, rng: random.Random, pools: Pools,
                   overrides: dict | None = None) -> dict:
    pcfg = scenario.get("parties", {})
    overrides = overrides or {}
    parties: dict = {}

    for role in pcfg.get("roles", []):
        key = role["key"]
        if key in overrides:
            party = copy.deepcopy(overrides[key])
            party.setdefault("role", role.get("label", ""))
        elif role.get("entity") == "organization":
            party = build_organization(pools, name=role.get("name", ""), role=role.get("label", ""))
        else:
            party = build_person(
                pools,
                role=role.get("label", ""),
                with_dob=role.get("with_dob", True),
                with_contact=role.get("with_contact", True),
            )
        parties[key] = party
        _ctx_for_party(ctx, key, party)

    # Children: shared-cast overrides win; otherwise generate child_1..N.
    child_keys = sorted((k for k in overrides if k.startswith("child_")),
                        key=lambda k: int(k.split("_")[1]))
    child_names = []
    if child_keys:
        for n, k in enumerate(child_keys, start=1):
            child = copy.deepcopy(overrides[k])
            child.setdefault("role", "Minor child")
            parties[f"child_{n}"] = child
            _ctx_for_party(ctx, f"child_{n}", child)
            child_names.append(child.get("full_name", ""))
        num_children = len(child_keys)
    else:
        num_children = dsl.resolve_count(pcfg.get("children"), rng) if pcfg.get("children") else 0
        for n in range(1, num_children + 1):
            child = build_person(pools, role="Minor child", with_contact=False, child=True)
            parties[f"child_{n}"] = child
            _ctx_for_party(ctx, f"child_{n}", child)
            child_names.append(child["full_name"])
    ctx["num_children"] = num_children
    ctx["num_children_words"] = _NUM_WORDS.get(num_children, str(num_children))
    ctx["children_names"] = _name_list(child_names)

    # Attorney for the represented client.
    if pcfg.get("attorney", True):
        if "attorney" in overrides:
            attorney = copy.deepcopy(overrides["attorney"])
            attorney.setdefault("role", "Attorney for the client")
        else:
            attorney = build_person(pools, role="Attorney for the client")
            attorney["bar_number"] = pools.bar_number()
            attorney["organization_name"] = pools.law_firm()
        parties["attorney"] = attorney
        _ctx_for_party(ctx, "attorney", attorney)
        ctx["attorney_firm"] = attorney.get("organization_name", "")

    # Client alias (independent copy) for the signing-filer projection.
    client_role = pcfg.get("client_role")
    if not client_role and pcfg.get("roles"):
        client_role = pcfg["roles"][0]["key"]
    if client_role and client_role in parties:
        parties["client"] = copy.deepcopy(parties[client_role])
        _ctx_for_party(ctx, "client", parties["client"])

    return parties


def _assemble_fact_pattern(scenario: dict, ctx: dict, rng: random.Random) -> dict:
    fp_spec = scenario.get("fact_pattern", {})
    summary = dsl.resolve(fp_spec.get("summary", ""), ctx, rng)
    narrative_blocks = dsl.resolve(fp_spec.get("narrative", []), ctx, rng)
    fact_pattern = {
        "summary": summary,
        "narrative": "\n\n".join(b for b in narrative_blocks if b),
    }
    if fp_spec.get("undisputed"):
        fact_pattern["undisputed_facts"] = dsl.resolve(fp_spec["undisputed"], ctx, rng)
    if fp_spec.get("disputed"):
        fact_pattern["disputed_facts"] = dsl.resolve(fp_spec["disputed"], ctx, rng)
    if fp_spec.get("timeline"):
        timeline = dsl.resolve(fp_spec["timeline"], ctx, rng)
        timeline = [e for e in timeline if e.get("date")]
        timeline.sort(key=lambda e: e["date"])
        fact_pattern["timeline"] = timeline
    return fact_pattern


def _assemble_issues(scenario: dict, ctx: dict, rng: random.Random) -> list:
    spec = scenario.get("issues")
    if not spec:
        return []
    chosen = dsl.pick_pool(spec.get("pool", []), spec.get("count"), ctx, rng)
    for idx, issue in enumerate(chosen, start=1):
        issue.setdefault("id", f"iss{idx}")
    return chosen


def _assemble_experts(scenario: dict, ctx: dict, rng: random.Random, pools: Pools) -> list:
    spec = scenario.get("experts")
    if not spec:
        return []
    chosen = dsl.pick_pool(spec.get("pool", []), spec.get("count"), ctx, rng)
    out = []
    for idx, item in enumerate(chosen, start=1):
        expert = {
            "name": pools.person_name()["full_name"],
            "field": item.get("field", "Expert"),
            "credentials": item.get("credentials") or pools.credential(),
        }
        if item.get("retained_by"):
            expert["retained_by"] = item["retained_by"]
        out.append({
            "id": f"exp{idx}",
            "expert": expert,
            "topic": item.get("topic", ""),
            "opinion": item.get("opinion", ""),
            "basis": item.get("basis", ""),
        })
    return out


def _assemble_evidence(scenario: dict, ctx: dict, rng: random.Random) -> list:
    spec = scenario.get("evidence")
    if not spec:
        return []
    chosen = dsl.pick_pool(spec.get("pool", []), spec.get("count"), ctx, rng)
    for idx, item in enumerate(chosen, start=1):
        item.setdefault("id", f"ev{idx}")
        item.setdefault("type", "document")
    return chosen


def _assemble_financials(scenario: dict, ctx: dict, rng: random.Random):
    spec = scenario.get("financials")
    if not spec:
        return None
    amounts = dsl.pick_pool(spec.get("amounts", []), spec.get("count"), ctx, rng)
    if not amounts:
        return None
    financials = {"currency": spec.get("currency", "USD"), "amounts": amounts}
    if spec.get("total_is_sum"):
        financials["total_claimed"] = round(sum(a.get("amount", 0) for a in amounts), 2)
    return financials


def generate_matter(
    scenario_id: str,
    seed: int = 0,
    reference_date: str | date | None = None,
    overrides: dict | None = None,
) -> dict:
    """Build a fully-validated Mock Matter from a scenario archetype and seed.

    ``overrides`` maps a party role key (plaintiff, decedent, child_1, attorney, ...) to a
    pre-built party object, so a compound matter can share the same cast across several
    constituent matters. Overridden identities are in place before any templating, so
    narrative and facts stay internally consistent.
    """
    scenario = load_scenario(scenario_id)
    reference = _normalize_reference_date(reference_date)
    rng = random.Random(seed)
    pools = Pools(rng)
    ctx: dict = {}

    # --- jurisdiction ----------------------------------------------------
    jur_spec = scenario.get("jurisdiction", {})
    state = jur_spec.get("state", "ME")
    county = jur_spec.get("county")
    if not county or county == "random":
        county = pools.county()
    court_location = jur_spec.get("court_location") or pools.court_location(county)
    court_type = jur_spec.get("court_type", "District Court")
    ctx.update(state=state, county=county, court_location=court_location, court_type=court_type)

    # --- dates (filing first so facts may reference it) ------------------
    dates_spec = scenario.get("dates", {})
    filing_date = (
        dsl.resolve(dates_spec["filing_date"], ctx, rng)
        if dates_spec.get("filing_date")
        else _random_recent_date(rng, reference)
    )
    ctx["filing_date"] = filing_date

    # --- parties ---------------------------------------------------------
    parties = _build_parties(scenario, ctx, rng, pools, overrides)

    # --- canonical bridge facts -----------------------------------------
    facts = dsl.resolve(scenario.get("facts", {}), ctx, rng)
    for key, value in facts.items():
        if isinstance(value, (str, int, float)):
            ctx[key] = value
        if isinstance(value, str):
            ctx[f"{key}_lower"] = value.lower()

    # event_date may reference a resolved fact (e.g. date_of_death)
    event_date = dsl.resolve(dates_spec["event_date"], ctx, rng) if dates_spec.get("event_date") else None
    if event_date:
        ctx["event_date"] = event_date

    # --- matter ----------------------------------------------------------
    year = filing_date[:4]
    fact_pattern = _assemble_fact_pattern(scenario, ctx, rng)
    matter = {
        "matter_id": f"MMC-{year}-{rng.randint(100000, 999999)}",
        "practice_area": scenario["practice_area"],
        "title": dsl.resolve(scenario.get("title", "Mock Matter"), ctx, rng),
        "jurisdiction": {
            "state": state,
            "county": county,
            "court_location": court_location,
            "court_type": court_type,
        },
        "case_type": scenario.get("case_type", ""),
        "filing_date": filing_date,
        "status": scenario.get("status", "intake"),
        "summary": fact_pattern["summary"],
    }
    if event_date:
        matter["event_date"] = event_date
    if scenario.get("assign_docket", True):
        matter["docket_number"] = f"{county[:3].upper()}-{scenario.get('docket_prefix', 'XX')}-{year}-{rng.randint(100, 999)}"

    # --- assemble excludes/includes ------------------------------------
    fixture_id = hashlib.sha256(
        f"{scenario_id}:{seed}:{reference.isoformat()}:{GENERATOR_VERSION}".encode()
    ).hexdigest()[:20]
    out = {
        "schema_version": "1.0",
        "provenance": {
            "mock": True,
            "fictional": True,
            "generator": "deterministic-engine",
            "generator_version": GENERATOR_VERSION,
            "scenario_id": scenario_id,
            "seed": seed,
            "reference_date": reference.isoformat(),
            "fixture_id": fixture_id,
            "jurisdiction": {"state": state, "county": county},
        },
        "matter": matter,
        "parties": parties,
        "fact_pattern": fact_pattern,
    }

    third_parties = _build_third_parties(scenario, ctx, rng, pools)
    if third_parties:
        out["third_parties"] = third_parties

    if scenario.get("interview"):
        iv = scenario["interview"]
        out["intake_interview"] = {
            "interviewer": iv.get("interviewer", "Intake Attorney"),
            "interviewee_role": iv.get("interviewee_role", "client"),
            "date": filing_date,
            "exchanges": dsl.resolve(iv.get("exchanges", []), ctx, rng),
        }

    if scenario.get("objectives"):
        out["client_objectives"] = dsl.resolve(scenario["objectives"], ctx, rng)

    issues = _assemble_issues(scenario, ctx, rng)
    if issues:
        out["issues"] = issues

    experts = _assemble_experts(scenario, ctx, rng, pools)
    if experts:
        out["expert_opinions"] = experts

    evidence = _assemble_evidence(scenario, ctx, rng)
    if evidence:
        out["evidence"] = evidence

    financials = _assemble_financials(scenario, ctx, rng)
    if financials:
        out["financials"] = financials

    if scenario.get("litigation"):
        out["litigation"] = dsl.resolve(scenario["litigation"], ctx, rng)

    if facts:
        out["facts"] = facts

    return out
