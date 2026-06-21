"""Compound (intertwined) matters: a universe of linked matters sharing one cast.

A compound archetype (compound/<id>/compound.yaml) names a cast of people and
organizations and a list of constituent matters, each built from an existing scenario
with cast members injected into specific roles. Because the SAME party objects are reused
across matters, the universe is genuinely intertwined: the company formed in one matter is
the defendant in another; the decedent in the probate matter is the decedent in the estate
tax matter; the children in the divorce are the wards in the guardianship.

Generation is deterministic in the compound seed.
"""
from __future__ import annotations

import random
from functools import lru_cache

import yaml

from .dsl import safe_format
from .engine import GENERATOR_VERSION, generate_matter
from .paths import COMPOUND_DIR
from .pools import Pools, build_organization, build_person
from .project import project_to_canonical


def list_compounds() -> list[str]:
    if not COMPOUND_DIR.exists():
        return []
    return sorted(
        p.name for p in COMPOUND_DIR.iterdir()
        if p.is_dir() and (p / "compound.yaml").exists()
    )


@lru_cache(maxsize=None)
def load_compound(compound_id: str) -> dict:
    path = COMPOUND_DIR / compound_id / "compound.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"Unknown compound '{compound_id}'. Available: {', '.join(list_compounds()) or '(none)'}"
        )
    with open(path, encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    spec.setdefault("id", compound_id)
    return spec


def _build_cast(specs: list[dict], pools: Pools) -> dict:
    """Build the shared party objects keyed by cast id (no fixed role; per-matter set)."""
    cast: dict = {}
    for spec in specs:
        if spec.get("kind") == "organization":
            party = build_organization(pools, name=spec.get("name", ""))
            party.pop("role", None)
        else:
            party = build_person(
                pools,
                role="",
                with_contact=spec.get("contact", True),
                with_dob=spec.get("dob", True),
                child=spec.get("child", False),
            )
        cast[spec["cast_id"]] = party
    return cast


def _cast_ctx(cast: dict) -> dict:
    ctx: dict = {}
    for cid, party in cast.items():
        name = party.get("full_name") or party.get("organization_name", "")
        ctx[f"{cid}_full_name"] = name
        ctx[f"{cid}_name"] = name
        ctx[f"{cid}_first"] = party.get("first_name", "")
        ctx[f"{cid}_last"] = party.get("last_name", "")
    return ctx


def generate_compound(compound_id: str, seed: int = 0) -> dict:
    """Build a compound matter universe from an archetype and seed."""
    spec = load_compound(compound_id)
    rng = random.Random(seed)
    pools = Pools(rng)

    cast = _build_cast(spec.get("cast", []), pools)
    ctx = _cast_ctx(cast)
    universe_id = f"UNIV-{compound_id}-{seed:04d}"

    matter_specs = spec.get("matters", [])
    matters_by_local: dict = {}
    for i, mspec in enumerate(matter_specs):
        overrides = {role: cast[cid] for role, cid in mspec.get("roles", {}).items() if cid in cast}
        matter_seed = seed * 1000 + i + 1
        matter = generate_matter(mspec["scenario"], matter_seed, overrides=overrides)
        matter["matter"]["universe_id"] = universe_id
        matters_by_local[mspec["id"]] = matter

    # Wire related_matters back-links using the siblings' generated matter_ids.
    relationships = []
    for mspec in matter_specs:
        matter = matters_by_local[mspec["id"]]
        related = []
        for rel in mspec.get("relates", []):
            target = matters_by_local.get(rel["to"])
            if target is None:
                continue
            description = safe_format(rel.get("description", ""), ctx)
            related.append({
                "universe_id": universe_id,
                "matter_id": target["matter"]["matter_id"],
                "scenario_id": target["provenance"]["scenario_id"],
                "relationship": rel["type"],
                "description": description,
            })
            relationships.append({
                "from": mspec["id"], "to": rel["to"],
                "type": rel["type"], "description": description,
            })
        if related:
            matter["related_matters"] = related

    # Cast roster with where each member appears.
    cast_out = []
    for cspec in spec.get("cast", []):
        cid = cspec["cast_id"]
        party = cast[cid]
        appears = [
            {"matter_id": mspec["id"], "role": role}
            for mspec in matter_specs
            for role, mapped in mspec.get("roles", {}).items()
            if mapped == cid
        ]
        cast_out.append({
            "cast_id": cid,
            "kind": cspec.get("kind", "person"),
            "name": party.get("full_name") or party.get("organization_name", ""),
            "description": cspec.get("label", ""),
            "appears_as": appears,
        })

    return {
        "schema_version": "1.0",
        "provenance": {
            "mock": True,
            "fictional": True,
            "generator": "compound-engine",
            "generator_version": GENERATOR_VERSION,
            "compound_id": compound_id,
            "seed": seed,
        },
        "universe_id": universe_id,
        "title": safe_format(spec.get("title", "Compound Matter"), ctx),
        "theme": safe_format(spec.get("theme", ""), ctx),
        "narrative": safe_format(spec.get("narrative", ""), ctx),
        "cast": cast_out,
        "matters": [matters_by_local[m["id"]] for m in matter_specs],
        "relationships": relationships,
    }


def project_compound(compound: dict) -> list[dict]:
    """Project every constituent matter to its canonical case (one per matter)."""
    out = []
    for matter in compound.get("matters", []):
        out.append({
            "universe_id": compound.get("universe_id"),
            "matter_id": matter.get("matter", {}).get("matter_id"),
            "scenario_id": matter.get("provenance", {}).get("scenario_id"),
            "canonical": project_to_canonical(matter),
        })
    return out
