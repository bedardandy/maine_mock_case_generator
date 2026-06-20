#!/usr/bin/env python3
"""Seeded, schema-driven mock case generator for Maine probate forms.

Ported from the `maine-probate-forms` project (see HANDOFF in the PR that added this).
This is a SECOND, complementary generation path: where `generator/engine.py` builds a rich
scenario-driven Mock Matter that projects to the canonical fact object (court/tax repos),
this builds the probate pipeline's native fixture shape directly from a form's schema fields.

The core entry point `generate_case(fields, seed, stress)` takes a list of schema field
dicts and returns a canonical case object. It only reads three keys per field:

    {"field_id": "...", "data_type": "date", "fill_strategy": {"source": "llm_over_narrative"}}

`fill_strategy.source` is the routing contract; each synthesized value is placed where the
probate fill pipeline looks for it:

    case_dict.<key>        -> case["case_dict"][key]
    <role>_record.<attr>   -> case["<role>_record"][attr]   (one coherent identity per role)
    llm_over_narrative      -> case["narrative_facts"][field_id]
    recompute_* / wet_ink / human_decision / left_blank / triage -> not filled (by design)

Output is the probate fill pipeline's case object:
    {"case_dict": {...}, "<role>_record": {...}, "narrative_facts": {...}, "_meta": {...}}

Values are Maine-flavoured, FICTIONAL, and deterministic per (seed, stress); no real PII.
"""
from __future__ import annotations

import argparse
import json
import random
import re

from .paths import REPO_ROOT

PROBATE_DIR = REPO_ROOT / "integration" / "maine-probate-forms"

COUNTIES = ["Cumberland", "York", "Penobscot", "Kennebec", "Androscoggin",
            "Aroostook", "Hancock", "Knox", "Lincoln", "Sagadahoc"]
TOWNS = [("Portland", "04101"), ("Falmouth", "04105"), ("Bangor", "04401"),
         ("Augusta", "04330"), ("Brunswick", "04011"), ("Saco", "04072"),
         ("Camden", "04843"), ("Bath", "04530"), ("Orono", "04473"),
         ("Lewiston", "04240"), ("Scarborough", "04074"), ("Kennebunk", "04043")]
STREETS = ["Pine Hill Road", "Commercial Street", "Maple Avenue", "Ocean View Drive",
           "Birch Lane", "Falmouth Foreside Way", "Main Street", "Elm Court",
           "Highland Terrace", "Shore Road", "Mill Pond Lane", "Cedar Street"]
FIRST = ["Margaret", "Robert", "Sarah", "James", "Patricia", "John", "Linda",
         "Michael", "Barbara", "David", "Susan", "Thomas", "Helen", "Daniel",
         "Nancy", "Paul", "Karen", "Mark", "Ruth", "Joseph"]
LAST = ["Walsh", "Bennett", "Goff", "Pelletier", "Thibodeau", "Hutchins",
        "Gagnon", "Day", "Crowley", "Mercier", "Lapointe", "Snow", "Frost",
        "Googins", "Jewett", "Pomroy"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


class Bank:
    """Deterministic synthetic-data bank with one coherent identity per role."""

    def __init__(self, seed, stress=False):
        self.r = random.Random(seed)
        self.stress = stress
        self.county = self.r.choice(COUNTIES)
        yr = self.r.randint(2024, 2026)
        self.docket = f"{yr}-{self.county[:4].upper()}-{self.r.randint(1, 9999):04d}"
        self._roles = {}

    def person(self):
        if self.stress:  # long hyphenated names to shake out horizontal overflow
            return (f"{self.r.choice(FIRST)}-{self.r.choice(FIRST)} "
                    f"{self.r.choice(LAST)}-{self.r.choice(LAST)} {self.r.choice(LAST)}")
        return f"{self.r.choice(FIRST)} {self.r.choice(LAST)[:1]}. {self.r.choice(LAST)}"

    def role(self, role):
        if role not in self._roles:
            town, zp = self.r.choice(TOWNS)
            street = f"{self.r.randint(2, 990)} {self.r.choice(STREETS)}"
            if self.stress:
                street = f"{self.r.randint(100, 9999)} {self.r.choice(STREETS)}, Apt {self.r.randint(1, 40)}B"
            self._roles[role] = {
                "name": self.person(), "street": street,
                "city": town, "state": "ME", "zip": zp,
                "phone": f"(207) 555-0{self.r.randint(100, 199)}",
                "email": f"user{self.r.randint(10, 99)}@example.com",
                "bar": str(self.r.randint(3000, 9999)),
            }
        return self._roles[role]

    def date(self, lo=1940, hi=2026):
        return f"{self.r.randint(lo, hi):04d}-{self.r.randint(1, 12):02d}-{self.r.randint(1, 28):02d}"

    def money(self):
        d = self.r.randint(2, 800) * 1000 + self.r.randint(0, 999)
        if self.stress:
            d = self.r.randint(10, 99) * 1_000_000 + self.r.randint(0, 999_999)
        return f"{d:,}.{self.r.randint(0, 99):02d}"


_ADDR = {"address": "street", "city": "city", "state": "state", "zip": "zip",
         "phone": "phone", "telephone": "phone", "email": "email",
         "bar_number": "bar", "bar": "bar"}


def _value_for(field_id, data_type, key, bank: Bank):
    """Synthesize a value from the field's data_type and key/name."""
    k = (key or field_id).lower()
    # jurat/date components in narrow blanks: short, fitting values (never a
    # long narrative sentinel that would overflow a 25pt "day" box).
    if re.search(r"(^|_)day($|_)", k):
        return str(bank.r.randint(1, 28))
    if re.search(r"(^|_)month($|_)", k):
        return bank.r.choice(MONTHS)
    if re.search(r"(^|_)year($|_)", k):
        return str(bank.r.randint(2024, 2026))
    if data_type == "date" or k.endswith("date") or "date_of" in k:
        if "death" in k:
            return bank.date(2024, 2026)
        if "birth" in k or "dob" in k:
            return bank.date(1940, 1970)
        return bank.date(2025, 2026)
    if data_type == "currency" or "value" in k or "amount" in k or "fee" in k:
        if "fee" in k:
            return bank.r.choice(["175.00", "21.00", "0.00", "50.00"])
        return bank.money()
    if data_type == "person_name" or k.endswith("name"):
        return bank.role("primary")["name"]
    if data_type in ("docket_number",) or k == "docket_number":
        return bank.docket
    if "county" in k:
        return bank.county
    if "email" in k:
        return bank.role("attorney")["email"]
    if "phone" in k or "telephone" in k:
        return bank.role("primary")["phone"]
    if "bar" in k:
        return bank.role("attorney")["bar"]
    return None


def _role_of(source):
    m = re.match(r"([a-z_]+)_record\.(.+)", source)
    return (m.group(1), m.group(2)) if m else (None, None)


def generate_case(fields, seed=0, stress=False, form_id=None):
    """fields: list of {field_id, data_type, fill_strategy:{source}}."""
    bank = Bank(seed, stress=stress)
    case = {"case_dict": {}, "narrative_facts": {}}
    for f in fields:
        fid = f["field_id"]
        dt = f.get("data_type")
        src = (f.get("fill_strategy") or {}).get("source") or ""
        if src.startswith("case_dict."):
            key = src[len("case_dict."):]
            kl = key.lower()
            if "county" in kl:
                v = bank.county
            elif kl == "docket_number":
                v = bank.docket
            elif "estate_of" in kl or kl.startswith("estate_") or "decedent" in kl:
                v = bank.role("decedent")["name"]
            elif "name" in kl and "county" not in kl:
                v = bank.role("primary")["name"]
            else:
                v = _value_for(fid, dt, key, bank) or bank.role("primary")["name"]
            case["case_dict"][key] = v
        elif "_record." in src:
            role, attr = _role_of(src)
            if not role:
                continue
            rec = case.setdefault(f"{role}_record", {})
            al = attr.lower()
            r = bank.role(role)
            if attr == role or al.endswith("name") or al in ("decedent", "applicant", "petitioner"):
                rec[attr] = r["name"]
            elif al.endswith("address"):
                rec[attr] = f"{r['street']}, {r['city']}, ME {r['zip']}"
            elif any(al.endswith(s) for s in _ADDR):
                suf = next(s for s in _ADDR if al.endswith(s))
                rec[attr] = r[_ADDR[suf]]
            elif "date" in al:
                rec[attr] = _value_for(fid, "date", attr, bank)
            else:
                rec[attr] = _value_for(fid, dt, attr, bank) or r["name"]
        elif src == "llm_over_narrative":
            v = _value_for(fid, dt, fid, bank)
            # only fall back to a sentinel for genuinely free-text fields; a
            # date/currency/numeric blank left blank is better than overflowed.
            if v is None and dt in ("text", None):
                v = "Not applicable"
            if v is not None:
                case["narrative_facts"][fid] = v
        # recompute_* / wet_ink / human_decision / left_blank / triage: intentionally unfilled
    case["_meta"] = {"form": form_id, "seed": seed, "stress": stress, "synthetic": True}
    return case


def load_fields(schema_path):
    """Convenience loader for a schema.json of shape {"fields": [...]}."""
    with open(schema_path, encoding="utf-8") as fh:
        return json.load(fh)["fields"]


# --- repo integration -------------------------------------------------------

def list_probate_forms() -> list[str]:
    """Vendored probate form ids (folders under integration/maine-probate-forms with a schema.json)."""
    if not PROBATE_DIR.exists():
        return []
    return sorted(
        p.name for p in PROBATE_DIR.iterdir()
        if p.is_dir() and (p / "schema.json").exists()
    )


def load_form_fields(form_id: str):
    path = PROBATE_DIR / form_id / "schema.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Unknown probate form '{form_id}'. Available: {', '.join(list_probate_forms()) or '(none)'}"
        )
    return load_fields(path)


def generate_for_form(form_id: str, seed: int = 0, stress: bool = False) -> dict:
    """Generate a probate case object for a vendored form id."""
    return generate_case(load_form_fields(form_id), seed=seed, stress=stress, form_id=form_id)


def main():
    ap = argparse.ArgumentParser(description="Generate a probate case from a schema.json")
    ap.add_argument("--schema", help="path to a form schema.json")
    ap.add_argument("--form", help="vendored probate form id (alternative to --schema)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--stress", action="store_true")
    a = ap.parse_args()
    if a.form:
        case = generate_for_form(a.form, a.seed, a.stress)
    elif a.schema:
        case = generate_case(load_fields(a.schema), a.seed, a.stress)
    else:
        ap.error("provide --form or --schema")
    print(json.dumps(case, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
