#!/usr/bin/env python3
"""Exar Sales telepítő: letölti vagy frissíti a sales-skills repót, és beköti az exar-sales skillt a Claude-ba.

Használat (python, python3 vagy Windowson py -3):
  python install.py               letöltés vagy frissítés, és a skill belépőjének megírása
  python install.py --frissit     csak frissítés (a skill ezt futtatja minden használat elején; hibánál a meglévő marad)
  python install.py --uninstall   a skill belépőjének törlése (a ~/.sales-skills mappát kézzel törölheted)

A repó helye: ~/.sales-skills (git clone, vagy git nélkül zip a GitHubról, fiók nélkül). A Claude skill-mappájába
(~/.claude/skills/exar-sales/) csak egy vékony belépő kerül, amely a repóban lévő skillt olvassa. A partner profilja
(~/.exar-sales/) és a kulcsa nem változik. A kimenet JSON. Standard könyvtár, Python 3.9+.
"""
import argparse
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

REPO = "https://github.com/ExarLabs/sales-skills.git"
ZIP = "https://codeload.github.com/ExarLabs/sales-skills/zip/refs/heads/main"
SKILL = "exar-sales"
JEL = "<!-- exar-sales-belepo -->"


def verzio(hely):
    try:
        return (hely / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def van_git():
    return shutil.which("git") is not None


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, timeout=120)


def zip_letolt(zip_url, hova):
    """A repó zipként (a GitHub a gyökérben egy sales-skills-main/ mappát ad); a régi tartalom helyére."""
    with urllib.request.urlopen(zip_url, timeout=60) as resp:
        adat = resp.read()
    with tempfile.TemporaryDirectory() as tmp:
        zipfile.ZipFile(io.BytesIO(adat)).extractall(tmp)
        gyokerek = [p for p in pathlib.Path(tmp).iterdir() if p.is_dir()]
        if len(gyokerek) != 1 or not (gyokerek[0] / "skills" / SKILL / "SKILL.md").exists():
            raise RuntimeError("A letöltött zip nem a sales-skills repó.")
        if hova.exists():
            shutil.rmtree(hova)
        shutil.copytree(gyokerek[0], hova)


def beszerez(hova, forras, zip_url):
    """Letölti vagy frissíti a repót. Visszaadja, hogyan (clone, pull, zip) és a régi verziót."""
    regi = verzio(hova)
    if (hova / ".git").exists():
        r = git("-C", str(hova), "pull", "--ff-only", "-q")
        if r.returncode != 0:
            raise RuntimeError("A frissítés nem sikerült (git pull): " + (r.stderr or r.stdout).strip()[:300])
        return "pull", regi
    if hova.exists() and not (hova / "skills" / SKILL / "SKILL.md").exists():
        raise RuntimeError(f"A {hova} mappa létezik, de nem a sales-skills repó; nem írom felül.")
    if not hova.exists() and van_git():
        r = git("clone", "-q", forras, str(hova))
        if r.returncode == 0:
            return "clone", regi
    zip_letolt(zip_url, hova)
    return "zip", regi


def frontmatter(szoveg):
    if not szoveg.startswith("---"):
        return {}, szoveg
    _, fej, torzs = szoveg.split("---", 2)
    meta = {}
    for sor in fej.strip().splitlines():
        if ":" in sor and not sor.startswith(" "):
            k, v = sor.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, torzs


def python_parancs():
    if os.name == "nt":
        return "py -3" if shutil.which("py") else "python"
    return "python3"


def belepo(hova, skills_hova):
    """A vékony belépő a Claude skill-mappájába. Egy régi, másolt exar-sales mappát lecserél; idegent nem."""
    forras_skill = hova / "skills" / SKILL / "SKILL.md"
    meta, _ = frontmatter(forras_skill.read_text(encoding="utf-8"))
    cel = skills_hova / SKILL
    if cel.exists():
        regi = (cel / "SKILL.md").read_text(encoding="utf-8") if (cel / "SKILL.md").exists() else ""
        if "name: exar-sales" not in regi:
            raise RuntimeError(f"A {cel} mappa létezik, de nem az exar-sales skillé; nem írom felül.")
        shutil.rmtree(cel)
    cel.mkdir(parents=True)
    telepito = (hova / "install" / "install.py").as_posix()
    szoveg = f"""---
name: exar-sales
description: {meta.get("description", "")}
---
{JEL}
# Exar Sales (belépő)

Ez csak a belépő; a skill a `{hova.as_posix()}` mappában él, és onnan frissül.

1. **Minden használat elején frissíts**, csendben: `{python_parancs()} "{telepito}" --frissit`. Ha a kimenetben
   `uj_verzio` áll, egy sorban mondd meg a partnernek, hogy frissült (és mi az újdonság a `CHANGELOG.md` elején). Ha
   a frissítés nem sikerül, a meglévő változattal folytasd.
2. Olvasd be és kövesd: `{forras_skill.as_posix()}`. A program (`exar_sales.py`), a sablonok és a leírások
   ugyanabban a mappában vannak.
"""
    (cel / "SKILL.md").write_text(szoveg, encoding="utf-8")
    return cel


def main(argv=None):
    ap = argparse.ArgumentParser(description="Az Exar Sales skill telepítése és frissítése.")
    ap.add_argument("--frissit", action="store_true", help="csak frissítés")
    ap.add_argument("--uninstall", action="store_true", help="a belépő törlése")
    ap.add_argument("--hova", default=str(pathlib.Path.home() / ".sales-skills"), help=argparse.SUPPRESS)
    ap.add_argument("--skills-hova", default=str(pathlib.Path.home() / ".claude" / "skills"), help=argparse.SUPPRESS)
    ap.add_argument("--forras", default=REPO, help=argparse.SUPPRESS)
    ap.add_argument("--zip-url", default=ZIP, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    hova, skills_hova = pathlib.Path(args.hova).expanduser(), pathlib.Path(args.skills_hova).expanduser()

    if args.uninstall:
        cel = skills_hova / SKILL
        torolve = False
        if (cel / "SKILL.md").exists() and JEL in (cel / "SKILL.md").read_text(encoding="utf-8"):
            shutil.rmtree(cel)
            torolve = True
        print(json.dumps({"belepo_torolve": torolve, "repo_marad": str(hova)}, ensure_ascii=False, indent=2))
        return 0

    try:
        mod, regi = beszerez(hova, args.forras, args.zip_url)
        uj = verzio(hova)
        kimenet = {"rendben": True, "mod": mod, "hely": str(hova), "verzio": uj}
        if regi and uj != regi:
            kimenet["uj_verzio"] = {"regi": regi, "uj": uj}
        if not args.frissit or not (skills_hova / SKILL / "SKILL.md").exists():
            kimenet["belepo"] = str(belepo(hova, skills_hova))
        kod = 0
    except Exception as e:  # a frissítés hibája ne állítsa meg a munkát: a meglévő változat marad
        kimenet = {"rendben": False, "hiba": str(e)[:400], "hely": str(hova), "verzio": verzio(hova)}
        kod = 0 if args.frissit and (hova / "skills" / SKILL / "SKILL.md").exists() else 1
    print(json.dumps(kimenet, ensure_ascii=False, indent=2))
    return kod


if __name__ == "__main__":
    sys.exit(main())
