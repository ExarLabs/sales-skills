#!/usr/bin/env python3
"""Kiadási tiltólista-ellenőrzés: a git által követett fájlokat nézi, soronként.

Kilépési kód: 0 ha nincs találat, 1 ha van. Találatnál: fájl:sor: minta: sor.
Két mintafájlt olvas:
  - scripts/tiltolista.txt: az általános lista (a CI ezt futtatja, a repóban van);
  - scripts/tiltolista.local.txt: a karbantartók helyi kiegészítő listája (nincs a repóban).
    Ha hiányzik, figyelmeztetés az stderr-re, de a futás nem bukik.
A "!" sorok engedett kivételek (szó szerinti egyezés); a találatból kivesszük.
"""
import argparse
import pathlib
import re
import subprocess
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
MINTA_FAJL = pathlib.Path(__file__).resolve().parent / "tiltolista.txt"
HELYI_FAJL = pathlib.Path(__file__).resolve().parent / "tiltolista.local.txt"
KIHAGYANDO = {"scripts/tiltolista.txt", "scripts/tiltolista.local.txt"}


def ekezet_nelkul(szoveg):
    return "".join(c for c in unicodedata.normalize("NFKD", szoveg) if not unicodedata.combining(c))


def betolt(fajlok):
    mintak, engedett = [], []
    for fajl in fajlok:
        for sor in fajl.read_text(encoding="utf-8").splitlines():
            sor = sor.strip()
            if not sor or sor.startswith("#"):
                continue
            if sor.startswith("!"):
                engedett.append(re.escape(sor[1:].strip()))
            else:
                mintak.append(re.compile(sor, re.IGNORECASE))
    kivetel = re.compile("|".join(engedett), re.IGNORECASE) if engedett else None
    return mintak, kivetel


def talalatok(szoveg, mintak, kivetel):
    for sor_szam, sor in enumerate(szoveg.splitlines(), 1):
        vizsgalt = kivetel.sub("", sor) if kivetel else sor
        alakok = {vizsgalt, ekezet_nelkul(vizsgalt)}
        for m in mintak:
            if any(m.search(a) for a in alakok):
                yield sor_szam, m.pattern, sor.strip()[:160]
                break


def kovetett_fajlok(repo):
    kimenet = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"], capture_output=True, check=True).stdout
    return [f for f in kimenet.decode("utf-8").split("\0") if f]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Kiadási tiltólista-ellenőrzés.")
    ap.add_argument("--repo", default=str(ROOT), help="az ellenőrzendő git-repó gyökere")
    ap.add_argument("--lista", default=str(MINTA_FAJL), help="az általános mintafájl")
    ap.add_argument("--helyi", default=str(HELYI_FAJL),
                    help="a helyi kiegészítő mintafájl; üres érték: nincs helyi lista")
    args = ap.parse_args(argv)
    repo = pathlib.Path(args.repo).resolve()

    fajlok = [pathlib.Path(args.lista)]
    if args.helyi:
        helyi = pathlib.Path(args.helyi)
        if helyi.is_file():
            fajlok.append(helyi)
        else:
            print("tiltolista: figyelem: a helyi lista hiányzik (%s), csak az általános listát futtatom." % helyi,
                  file=sys.stderr)
    mintak, kivetel = betolt(fajlok)

    hibak = 0
    for rel in kovetett_fajlok(repo):
        if rel in KIHAGYANDO:
            continue
        utvonal = repo / rel
        if not utvonal.is_file():
            continue
        bajt = utvonal.read_bytes()
        if b"\0" in bajt:
            continue
        szoveg = bajt.decode("utf-8", errors="replace")
        for sor_szam, minta, sor in talalatok(szoveg, mintak, kivetel):
            print("%s:%d: %s: %s" % (rel, sor_szam, minta, sor))
            hibak += 1
    if hibak:
        print("tiltolista: %d találat. Javítsd, mielőtt kiadás vagy commit készül." % hibak)
        return 1
    print("tiltolista: rendben")
    return 0


if __name__ == "__main__":
    sys.exit(main())
