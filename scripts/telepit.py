#!/usr/bin/env python3
"""Kézi telepítő: a skills/exar-sales mappát a Claude Code skill-mappájába másolja (alap: ~/.claude/skills).

Használat: python3 -I scripts/telepit.py [--cel MAPPA]. Azonos nevű régi mappát felülír. A profil
(~/.exar-sales/profil.json) és a kulcs nem változik. A kimenet JSON. Standard könyvtár, Python 3.9+.
"""
import argparse
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "exar-sales"


def telepit(cel):
    cel.mkdir(parents=True, exist_ok=True)
    hova = cel / SKILL.name
    felulirva = hova.exists()
    if felulirva:
        shutil.rmtree(hova)
    shutil.copytree(SKILL, hova, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return {"hova": str(hova), "felulirva": felulirva}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Az exar-sales skill telepítése a Claude Code skill-mappájába.")
    ap.add_argument("--cel", help="a célmappa (alap: ~/.claude/skills)")
    args = ap.parse_args(argv)
    cel = pathlib.Path(args.cel).expanduser() if args.cel else pathlib.Path.home() / ".claude" / "skills"
    print(json.dumps(telepit(cel.resolve()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
