"""Seeded, CLEARLY FICTIONAL value pools for deterministic generation.

All values are invented. Phone numbers use the 555-01xx fiction range, emails use
reserved example.* domains, and street addresses are made up. Real Maine county and
court-location names are used only for jurisdiction routing, never to imply a real person.
"""
from __future__ import annotations

import json
import random
from datetime import date, timedelta

from .paths import FAKER_POOLS


class Pools:
    """Random fictional value factory bound to a single seeded RNG."""

    def __init__(self, rng: random.Random):
        self.rng = rng
        with open(FAKER_POOLS, encoding="utf-8") as fh:
            self.data = json.load(fh)

    # -- low-level picks ---------------------------------------------------
    def pick(self, key: str):
        return self.rng.choice(self.data[key])

    # -- people ------------------------------------------------------------
    def person_name(self) -> dict:
        first = self.rng.choice(self.data["first_names"])
        last = self.rng.choice(self.data["last_names"])
        middle = self.rng.choice(self.data["middle_initials"])
        return {
            "first_name": first,
            "middle_name": middle,
            "last_name": last,
            "full_name": f"{first} {middle}. {last}",
        }

    def dob(self, min_age: int = 25, max_age: int = 70) -> str:
        today = date(2026, 1, 1)
        age = self.rng.randint(min_age, max_age)
        days = self.rng.randint(0, 364)
        born = date(today.year - age, 1, 1) + timedelta(days=days)
        return born.isoformat()

    def child_dob(self) -> str:
        today = date(2026, 1, 1)
        age = self.rng.randint(1, 17)
        days = self.rng.randint(0, 364)
        born = date(today.year - age, 1, 1) + timedelta(days=days)
        return born.isoformat()

    # -- contact -----------------------------------------------------------
    def phone(self) -> str:
        area = self.data["phone_area_code"]
        suffix = f"{self.data['phone_fiction_prefix']}{self.rng.randint(0, 99):02d}"
        return f"({area}) {suffix}"

    def email(self, first: str, last: str) -> str:
        domain = self.rng.choice(self.data["email_domains"])
        user = f"{first}.{last}".lower()
        user = "".join(ch for ch in user if ch.isalnum() or ch == ".")
        return f"{user}@{domain}"

    def address(self) -> dict:
        number = self.rng.randint(2, 480)
        street = self.rng.choice(self.data["street_names"])
        city = self.rng.choice(self.data["cities"])
        zip_code = f"{self.data['zip_prefix']}{self.rng.randint(1, 99):02d}"
        return {
            "address": f"{number} {street}",
            "city": city,
            "state": "ME",
            "zip": zip_code,
        }

    # -- organizations -----------------------------------------------------
    _FORCED_SUFFIX = {"llc": "LLC", "corp": "Inc.", "corporation": "Inc.",
                      "inc": "Inc.", "lp": "LP", "llp": "LLP", "pllc": "PLLC",
                      "pa": "P.A.", "trust": "Trust"}

    def org_name(self, kind: str = "") -> str:
        a = self.rng.choice(self.data["business_words_a"])
        b = self.rng.choice(self.data["business_words_b"])
        forced = self._FORCED_SUFFIX.get(kind.lower()) if kind else None
        suffix = forced or self.rng.choice(self.data["business_suffixes"])
        return f"{a} {b} {suffix}"

    def bank(self) -> str:
        return self.rng.choice(self.data["bank_names"])

    def employer(self) -> str:
        return self.rng.choice(self.data["employers"])

    def law_firm(self) -> str:
        return self.rng.choice(self.data["law_firms"])

    def credential(self) -> str:
        return self.rng.choice(self.data["expert_credentials"])

    def ssn_last4(self) -> str:
        return f"{self.rng.randint(0, 9999):04d}"

    def bar_number(self) -> str:
        return f"{self.rng.randint(1000, 9999)}"

    # -- jurisdiction ------------------------------------------------------
    def county(self) -> str:
        return self.rng.choice(self.data["maine_counties"])

    def court_location(self, county: str) -> str:
        return self.data["court_locations_by_county"].get(county, "Portland")


def build_person(pools: Pools, role: str = "", with_contact: bool = True,
                 with_dob: bool = True, child: bool = False) -> dict:
    """Assemble a full party object for a fictional person."""
    party = {"entity_type": "person"}
    party.update(pools.person_name())
    if role:
        party["role"] = role
    if with_contact:
        party.update(pools.address())
        party["phone"] = pools.phone()
        party["email"] = pools.email(party["first_name"], party["last_name"])
    if with_dob:
        party["date_of_birth"] = pools.child_dob() if child else pools.dob()
    if not child:
        party["ssn_last4"] = pools.ssn_last4()
    return party


def build_organization(pools: Pools, name: str = "", role: str = "",
                       kind: str = "") -> dict:
    """Assemble a full party object for a fictional organization. ``kind`` (llc,
    corp, lp, ...) forces a matching legal suffix so the entity name agrees with
    the instrument being drafted (an LLC matter never names a '... Corp.')."""
    org = {
        "entity_type": "organization",
        "organization_name": name or pools.org_name(kind),
    }
    if kind:
        org["entity_kind"] = kind.lower()
    org["full_name"] = org["organization_name"]
    if role:
        org["role"] = role
    org.update(pools.address())
    org["phone"] = pools.phone()
    return org
