"""Deterministic perturbation harness for smoke-testing downstream document automation.

A *mutator* takes a fully-generated Mock Matter and returns a stressed variant that is
still **schema-valid** — the point is to break downstream assumptions (a filler that
dereferences a phone that isn't there, a caption sized for short names, a template that
chokes on unicode), never the contract itself. Variants are reproducible: the same
(scenario, seed, mutator) always yields the same bytes.

Mutators:

* ``drop_optionals``   — strip the matter to schema-required bones: required top-level
  sections only, parties reduced to ``entity_type`` + ``full_name``, matter reduced to
  its required fields. The "empty intake" a real office produces on day one.
* ``blank_strings``    — keep every optional field present but set optional *strings*
  (contact fields, summaries) to ``""``. Present-but-empty is a different failure mode
  than absent.
* ``maximal_lengths``  — pad names, addresses, titles, and narrative text with long
  fictional filler. Field-overflow stress for fixed-width PDFs and captions.
* ``unicode_stress``   — decorate free text with diacritics, guillemets, em dashes, and
  non-Latin characters. Encoding round-trip stress. ISO dates and numbers are left
  untouched so the variant stays semantically consumable.

Each variant records its lineage in ``provenance.stress_mutator``.
"""
from __future__ import annotations

import copy
import random
import re

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_NUMERIC = re.compile(r"^[\d\s.,%$()-]+$")

_REQUIRED_TOP = ("schema_version", "provenance", "matter", "parties", "fact_pattern")
_REQUIRED_MATTER = ("matter_id", "practice_area", "jurisdiction")
_PARTY_OPTIONAL_STRINGS = ("phone", "email", "address", "city", "zip", "signature", "description")

_PAD = (
    " — additional clearly-fictional narrative filler inserted by the stress harness to "
    "exercise field widths, line wrapping, and pagination in downstream documents;"
)
_ALIAS_PAD = (
    ' a/k/a "The Party Formerly Known By A Substantially Longer Business And Trade Name '
    'Used Solely For Field-Width Stress Testing"'
)
_UNI_PREFIX = "«Üñïçødé» "
_UNI_SUFFIX = " — tête-à-tête, œuvre, søster, 龍, ½ £ ✓"


def _pad_to(text: str, target: int) -> str:
    while len(text) < target:
        text += _PAD
    return text


def drop_optionals(matter: dict, rng: random.Random) -> dict:
    """Reduce the matter to its schema-required skeleton."""
    out = {key: copy.deepcopy(matter[key]) for key in _REQUIRED_TOP if key in matter}
    out["matter"] = {
        key: copy.deepcopy(matter["matter"][key])
        for key in _REQUIRED_MATTER
        if key in matter["matter"]
    }
    slim_parties = {}
    for key, party in matter["parties"].items():
        slim = {"entity_type": party.get("entity_type", "person")}
        if party.get("full_name"):
            slim["full_name"] = party["full_name"]
        slim_parties[key] = slim
    out["parties"] = slim_parties
    fp = matter["fact_pattern"]
    out["fact_pattern"] = {"summary": fp["summary"], "narrative": fp["narrative"]}
    return out


def blank_strings(matter: dict, rng: random.Random) -> dict:
    """Keep optional fields present but set optional strings to the empty string."""
    out = copy.deepcopy(matter)
    for party in out["parties"].values():
        for field in _PARTY_OPTIONAL_STRINGS:
            if field in party:
                party[field] = ""
    if "summary" in out["matter"]:
        out["matter"]["summary"] = ""
    for tp in out.get("third_parties", []):
        if isinstance(tp.get("contact"), dict):
            tp["contact"] = {key: "" for key in tp["contact"]}
        if "relevance" in tp:
            tp["relevance"] = ""
    for ev in out.get("evidence", []):
        if "description" in ev:
            ev["description"] = ""
    return out


def maximal_lengths(matter: dict, rng: random.Random) -> dict:
    """Pad names, addresses, and free text far past typical field widths."""
    out = copy.deepcopy(matter)
    m = out["matter"]
    if m.get("title"):
        m["title"] = _pad_to(m["title"], 220)
    if m.get("summary"):
        m["summary"] = _pad_to(m["summary"], 600)
    fp = out["fact_pattern"]
    fp["summary"] = _pad_to(fp["summary"], 600)
    if isinstance(fp.get("narrative"), str):
        fp["narrative"] = _pad_to(fp["narrative"], 2500)
    for party in out["parties"].values():
        if party.get("full_name"):
            party["full_name"] = party["full_name"] + _ALIAS_PAD
        if party.get("address"):
            party["address"] = party["address"] + ", Building 7, Floor 3, Suite 412-B, Mailstop QX-9"
    return out


def unicode_stress(matter: dict, rng: random.Random) -> dict:
    """Decorate free text with hostile-but-valid unicode; leave dates and numbers alone."""
    out = copy.deepcopy(matter)

    def decorate(text: str) -> str:
        if not text or _ISO_DATE.match(text) or _NUMERIC.match(text):
            return text
        return _UNI_PREFIX + text + _UNI_SUFFIX

    m = out["matter"]
    for field in ("title", "summary"):
        if m.get(field):
            m[field] = decorate(m[field])
    fp = out["fact_pattern"]
    fp["summary"] = decorate(fp["summary"])
    if isinstance(fp.get("narrative"), str):
        fp["narrative"] = decorate(fp["narrative"])
    for lst in ("undisputed_facts", "disputed_facts"):
        if fp.get(lst):
            fp[lst] = [decorate(item) for item in fp[lst]]
    for key, value in list(out.get("facts", {}).items()):
        if isinstance(value, str):
            out["facts"][key] = decorate(value)
    return out


MUTATORS: dict = {
    "drop_optionals": drop_optionals,
    "blank_strings": blank_strings,
    "maximal_lengths": maximal_lengths,
    "unicode_stress": unicode_stress,
}


def stress_matter(matter: dict, mutator: str, seed: int = 0) -> dict:
    """Apply one named mutator to a matter, deterministically, and tag its lineage."""
    if mutator not in MUTATORS:
        raise KeyError(f"Unknown mutator '{mutator}'. Available: {', '.join(MUTATORS)}")
    rng = random.Random(f"stress:{mutator}:{seed}")
    variant = MUTATORS[mutator](matter, rng)
    variant.setdefault("provenance", {})
    variant["provenance"]["stress_mutator"] = mutator
    return variant


def stress_variants(matter: dict, seed: int = 0, mutators: list[str] | None = None):
    """Yield (mutator_name, variant) for each requested (default: all) mutator."""
    for name in mutators or MUTATORS:
        yield name, stress_matter(matter, name, seed)
