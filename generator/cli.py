"""``mmcg`` — console entry point so sibling repos can drive the generator after
``pip install -e path/to/maine_mock_case_generator``.

Core subcommands are implemented here against the package API; the heavier dev tools
(``corpus``, ``stress``, ``fill``, ``smoke``) are dispatched to their scripts under
``tools/`` in the repo checkout, so one binary covers the whole surface:

  mmcg list
  mmcg generate residential-purchase-sale --seed 3 --canonical
  mmcg corpus --seeds 3 --stress --out out/corpus
  mmcg stress family-divorce-cumberland --mutators unicode_stress
  mmcg fill ME-RETTD --scenario residential-purchase-sale --seed 1
  mmcg smoke --count 5
"""
from __future__ import annotations

import argparse
import json
import runpy
import sys

from .paths import REPO_ROOT


def _dump(obj: dict) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def _run_tool(name: str, argv: list[str]) -> int:
    """Re-dispatch to a tools/ script in the repo checkout (editable-install layout)."""
    tool = REPO_ROOT / "tools" / f"{name}.py"
    if not tool.exists():
        print(f"mmcg: tools/{name}.py not found under {REPO_ROOT} — "
              "run from an editable install / checkout (see docs/integration.md)",
              file=sys.stderr)
        return 2
    sys.argv = [str(tool), *argv]
    runpy.run_path(str(tool), run_name="__main__")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        return _main(argv)
    except BrokenPipeError:  # e.g. `mmcg list | head`
        return 0


def _main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    # Tool-dispatched subcommands keep their own --help and full flag surface.
    if argv and argv[0] in ("corpus", "stress", "fill", "smoke", "compound", "probate"):
        tool = {"probate": "probate_case"}.get(argv[0], argv[0])
        return _run_tool(tool, argv[1:])

    ap = argparse.ArgumentParser(prog="mmcg", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command")

    sub.add_parser("list", help="List scenario ids.")

    gen = sub.add_parser("generate", help="Generate a Mock Matter (JSON to stdout).")
    gen.add_argument("scenario")
    gen.add_argument("--seed", type=int, default=0)
    gen.add_argument("--canonical", action="store_true",
                     help="Emit the projected canonical case instead of the full matter.")

    for name in ("corpus", "stress", "fill", "smoke", "compound", "probate"):
        sub.add_parser(name, help=f"Dispatch to tools/{name}.py (own --help).")

    args = ap.parse_args(argv)

    from . import generate_matter, list_scenarios, project_to_canonical, validate_matter

    if args.command == "list":
        for sid in list_scenarios():
            print(sid)
        return 0
    if args.command == "generate":
        matter = generate_matter(args.scenario, args.seed)
        errors = validate_matter(matter)
        if errors:
            print(f"VALIDATION FAILED: {errors[0]}", file=sys.stderr)
            return 1
        print(_dump(project_to_canonical(matter) if args.canonical else matter))
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
