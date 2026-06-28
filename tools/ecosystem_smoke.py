#!/usr/bin/env python3
"""Compatibility wrapper for ``mmcg ecosystem-smoke``."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generator.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["ecosystem-smoke", *sys.argv[1:]]))
