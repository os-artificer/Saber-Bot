#!/usr/bin/env python3
"""
Merge Saber-Bot custom skills into ~/.openclaw/openclaw.json → skills.entries.*.enabled = true
Creates a .bak next to the config file before writing.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: patch-openclaw-skills-json.py <openclaw.json> <skill_name>...", file=sys.stderr)
        return 2
    cfg = Path(sys.argv[1])
    names = sys.argv[2:]
    if not cfg.is_file():
        print(f"SKIP: config not found: {cfg}", file=sys.stderr)
        return 1
    data = json.loads(cfg.read_text(encoding="utf-8"))
    skills = data.setdefault("skills", {})
    entries = skills.setdefault("entries", {})
    for n in names:
        e = entries.setdefault(n, {})
        e["enabled"] = True
    bak = cfg.with_suffix(cfg.suffix + ".bak")
    shutil.copy2(cfg, bak)
    cfg.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: {cfg} (backup: {bak})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
