#!/usr/bin/env python3
"""A skill zip-be csomagolása a claude.ai-feltöltéshez: dist/exar-sales.zip (a zip gyökerében az exar-sales mappa).

Használat: python3 -I scripts/csomagol.py [--cel MAPPA]. A kimenet JSON. Standard könyvtár, Python 3.9+.
"""
import argparse
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "exar-sales"


def csomagol(cel):
    cel.mkdir(parents=True, exist_ok=True)
    zip_ut = cel / "exar-sales.zip"
    fajlok = sorted(p for p in SKILL.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
    with zipfile.ZipFile(zip_ut, "w", zipfile.ZIP_DEFLATED) as z:
        for p in fajlok:
            z.write(p, pathlib.Path("exar-sales") / p.relative_to(SKILL))
    return {"zip": str(zip_ut), "fajlok": len(fajlok), "meret": zip_ut.stat().st_size}


def main(argv=None):
    ap = argparse.ArgumentParser(description="A skill zip-be csomagolása.")
    ap.add_argument("--cel", default=str(ROOT / "dist"))
    args = ap.parse_args(argv)
    print(json.dumps(csomagol(pathlib.Path(args.cel)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
