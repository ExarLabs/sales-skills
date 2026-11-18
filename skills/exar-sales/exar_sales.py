#!/usr/bin/env python3
"""Exar Sales: a sales partner's own Claude talks to the Exar Sales portal with this program.

Parancsok (a kimenet mindig JSON; hibánál a "hiba" kulcs alatt kód és üzenet):
  ellenoriz                       a kapcsolat és a kulcs próbája
  leadek                          a saját leadjeid
  lead NÉV                        egy saját lead adatai és a bemutató linkje
  sablonok                        a levélsablonok listája
  sablon AZONOSÍTÓ                egy sablon nyers szövege (a legfrissebb, ha elérhető)
  level --lead NÉV --sablon ID    a kitöltött levél és az Outlook-link (nem küld el semmit)
  profil [--telefon ...]          az aláírás saját adatai (megmutatja vagy beállítja)
  uj-lead --adat FÁJL|-           új lead felvétele a portálra (JSON-ból)

A kulcs a környezetből jön: EXAR_SALES_API_KEY és EXAR_SALES_API_SECRET; a program soha nem írja ki.
Opcionális: EXAR_SALES_URL (alap: https://sales.exarlabs.com), EXAR_SALES_SABLON_URL (a sablonok forrása).
Standard könyvtár, Python 3.9+.
"""

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

HERE = pathlib.Path(__file__).resolve().parent
SABLONOK = HERE / "sablonok"
BASE = os.environ.get("EXAR_SALES_URL", "https://sales.exarlabs.com").rstrip("/")
SABLON_URL = os.environ.get(
    "EXAR_SALES_SABLON_URL",
    "https://raw.githubusercontent.com/ExarLabs/sales-skills/main/skills/exar-sales/sablonok",
).rstrip("/")
PROFIL = pathlib.Path(os.environ.get("EXAR_SALES_PROFIL", pathlib.Path.home() / ".exar-sales" / "profil.json"))
OUTLOOK = "https://outlook.office.com/mail/deeplink/compose"
TITULUS = {"hu": "Üzletfejlesztés", "ro": "Dezvoltare afaceri"}
RO_MEGSZOLITAS = "Bună ziua"


class Hiba(Exception):
    def __init__(self, kod, uzenet):
        super().__init__(uzenet)
        self.kod, self.uzenet = kod, uzenet


# --- portál -----------------------------------------------------------------------------------------------------


def _kulcs():
    key, secret = os.environ.get("EXAR_SALES_API_KEY"), os.environ.get("EXAR_SALES_API_SECRET")
    if not key or not secret:
        raise Hiba("nincs_kulcs", "Hiányzik az EXAR_SALES_API_KEY vagy az EXAR_SALES_API_SECRET környezeti változó.")
    return f"token {key}:{secret}"


def hivas(method, params=None, post=None):
    """Egy portál-végpont hívása; a "message" mezőt adja vissza."""
    url = f"{BASE}/api/method/{method}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {"Authorization": _kulcs(), "Accept": "application/json"}
    data = None
    if post is not None:
        data = urllib.parse.urlencode(post).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if post is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")).get("message")
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            raise Hiba("nincs_hozzaferes", "Nincs hozzáférés: a kulcs érvénytelen, vagy ez nem a saját leaded.")
        if e.code == 417:
            raise Hiba("elutasitva", _szerver_uzenet(e) or "A portál nem fogadta el az adatokat.")
        if e.code == 429:
            raise Hiba("tul_sok_keres", "Túl sok kérés; próbáld újra egy óra múlva.")
        raise Hiba("szerver_hiba", f"A portál hibát adott: HTTP {e.code}.")
    except urllib.error.URLError as e:
        raise Hiba("nincs_kapcsolat", f"A portál nem érhető el: {e.reason}.")


def _szerver_uzenet(e):
    """A Frappe hibaüzenete (_server_messages), ha van; különben üres."""
    try:
        body = json.loads(e.read().decode("utf-8"))
        msgs = json.loads(body.get("_server_messages") or "[]")
        return "; ".join(json.loads(m).get("message", "") for m in msgs).strip()
    except Exception:
        return ""


# --- sablonok ---------------------------------------------------------------------------------------------------


def sablon_ids():
    return sorted(p.stem for p in SABLONOK.glob("*.md") if p.stem != "README")


def elemez(szoveg):
    """Frontmatter (egyszerű kulcs: érték sorok) és törzs."""
    if not szoveg.startswith("---"):
        raise Hiba("rossz_sablon", "A sablon nem frontmatterrel kezdődik.")
    _, fej, torzs = szoveg.split("---", 2)
    meta = {}
    for sor in fej.strip().splitlines():
        if ":" in sor:
            k, v = sor.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, torzs.lstrip("\n")


def sablon(azon, helyi=False):
    """A sablon a repó friss változatából; ha az nem érhető el, a csomagolt példányból. Visszaadja a forrást is."""
    if azon not in sablon_ids():
        raise Hiba("nincs_sablon", f"Nincs ilyen sablon: {azon}. Ezek vannak: {', '.join(sablon_ids())}.")
    if not helyi:
        try:
            with urllib.request.urlopen(f"{SABLON_URL}/{azon}.md", timeout=8) as resp:
                meta, torzs = elemez(resp.read().decode("utf-8"))
                return meta, torzs, "friss"
        except Exception:
            pass
    meta, torzs = elemez((SABLONOK / f"{azon}.md").read_text(encoding="utf-8"))
    return meta, torzs, "csomagolt"


def kitolt(torzs, ertekek, van_idopont):
    """Feltételes sorok (?idopont: / ?!idopont:) és {{helyek}} kitöltése. Visszaadja a szöveget és a hiányzó helyeket."""
    sorok = []
    for sor in torzs.splitlines():
        if sor.startswith("?idopont:"):
            if not van_idopont:
                continue
            sor = sor[len("?idopont:"):].lstrip()
        elif sor.startswith("?!idopont:"):
            if van_idopont:
                continue
            sor = sor[len("?!idopont:"):].lstrip()
        sorok.append(sor)
    szoveg = "\n".join(sorok).strip() + "\n"
    hianyzik = []
    for kulcs, ertek in ertekek.items():
        hely = "{{" + kulcs + "}}"
        if hely not in szoveg:
            continue
        if ertek:
            szoveg = szoveg.replace(hely, ertek)
        else:
            hianyzik.append(kulcs)
            szoveg = szoveg.replace(hely, f"[{kulcs}]")
    return szoveg, hianyzik


def alap_megszolitas(meta, kapcsolattarto):
    """Magázó: teljes név (vezetéknév elöl); tegező: a keresztnév (a név első szava utáni rész); román: Bună ziua."""
    mod = meta.get("megszolitas")
    nev = (kapcsolattarto or "").strip()
    if meta.get("nyelv") == "ro":
        return RO_MEGSZOLITAS
    if mod == "tegezo":
        reszek = nev.split(" ", 1)
        return reszek[1] if len(reszek) == 2 else nev
    return nev or "Hölgyem/Uram"


def outlook_link(cimzett, targy, torzs):
    q = urllib.parse.urlencode({"to": cimzett, "subject": targy, "body": torzs}, quote_via=urllib.parse.quote)
    return f"{OUTLOOK}?{q}"


# --- profil -----------------------------------------------------------------------------------------------------


def profil_olvas():
    try:
        return json.loads(PROFIL.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def profil_ir(adat):
    PROFIL.parent.mkdir(parents=True, exist_ok=True)
    PROFIL.write_text(json.dumps(adat, ensure_ascii=False, indent=2), encoding="utf-8")


# --- parancsok --------------------------------------------------------------------------------------------------


def p_ellenoriz(_):
    leadek = hivas("exar_sales.api.my_leads")
    return {"rendben": True, "portal": BASE, "leadek_szama": len(leadek or [])}


def p_leadek(_):
    return {"leadek": hivas("exar_sales.api.my_leads") or []}


def p_lead(args):
    return hivas("exar_sales.api.email_prep", {"lead": args.nev})


def p_sablonok(_):
    lista = []
    for azon in sablon_ids():
        meta, _, _ = sablon(azon, helyi=True)
        lista.append({k: meta.get(k, "") for k in ("id", "mire", "nyelv", "megszolitas", "version", "allapot")})
    return {"sablonok": lista}


def p_sablon(args):
    meta, torzs, forras = sablon(args.azon, args.helyi)
    return {"meta": meta, "torzs": torzs, "forras": forras}


def p_level(args):
    adat = hivas("exar_sales.api.email_prep", {"lead": args.lead})
    lead, partner = adat.get("lead") or {}, adat.get("partner") or {}
    meta, torzs, forras = sablon(args.sablon, args.helyi)
    nyelv = meta.get("nyelv", "hu")
    prof = profil_olvas()
    van_idopont = bool(args.idopont1 and args.idopont2)
    ertekek = {
        "megszolitas": args.megszolitas or alap_megszolitas(meta, lead.get("contact")),
        "bemutato_link": adat.get("deck_url") or "",
        "idopont1": args.idopont1 or "",
        "idopont2": args.idopont2 or "",
        "nev": prof.get("nev") or partner.get("name") or "",
        "titulus": prof.get(f"titulus_{nyelv}") or TITULUS.get(nyelv, ""),
        "telefon": prof.get("telefon") or "",
        "email": partner.get("email") or "",
    }
    szoveg, hianyzik = kitolt(torzs, ertekek, van_idopont)
    cimzett = lead.get("email") or ""
    if not cimzett:
        hianyzik.insert(0, "cimzett_email")
    if meta.get("megszolitas") == "tegezo" and not ertekek["megszolitas"]:
        hianyzik.append("megszolitas")
    return {
        "cimzett": cimzett,
        "targy": meta.get("targy", ""),
        "torzs": szoveg,
        "outlook_link": outlook_link(cimzett, meta.get("targy", ""), szoveg),
        "sablon": {"id": meta.get("id"), "version": meta.get("version"), "forras": forras, "allapot": meta.get("allapot", "")},
        "lead": {"name": lead.get("name"), "ceg": lead.get("organization"), "kapcsolattarto": lead.get("contact"),
                 "mi_a_gondjuk": lead.get("problem") or lead.get("business_problem") or ""},
        "hianyzik": sorted(set(hianyzik), key=hianyzik.index),
    }


def p_profil(args):
    prof = profil_olvas()
    valtozott = False
    for kulcs in ("nev", "telefon", "titulus_hu", "titulus_ro"):
        ertek = getattr(args, kulcs)
        if ertek is not None:
            prof[kulcs] = ertek.strip()
            valtozott = True
    if valtozott:
        profil_ir(prof)
    return {"profil": prof, "hely": str(PROFIL), "mentve": valtozott}


def p_uj_lead(args):
    nyers = sys.stdin.read() if args.adat == "-" else pathlib.Path(args.adat).read_text(encoding="utf-8")
    try:
        adat = json.loads(nyers)
    except ValueError:
        raise Hiba("rossz_adat", "Az adat nem érvényes JSON.")
    if not isinstance(adat, dict):
        raise Hiba("rossz_adat", "Az adat egy JSON-objektum legyen.")
    adat = {k: str(v) for k, v in adat.items() if v not in (None, "") and k not in ("partner", "cmd")}
    eredmeny = hivas("exar_sales.api.create_lead", post=adat)
    return {"felveve": (eredmeny or {}).get("name")}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Exar Sales: a saját leadjeid és a bemutató levél.")
    sub = ap.add_subparsers(dest="parancs", required=True)
    sub.add_parser("ellenoriz").set_defaults(f=p_ellenoriz)
    sub.add_parser("leadek").set_defaults(f=p_leadek)
    p = sub.add_parser("lead")
    p.add_argument("nev")
    p.set_defaults(f=p_lead)
    sub.add_parser("sablonok").set_defaults(f=p_sablonok)
    p = sub.add_parser("sablon")
    p.add_argument("azon")
    p.add_argument("--helyi", action="store_true", help="csak a csomagolt példány")
    p.set_defaults(f=p_sablon)
    p = sub.add_parser("level")
    p.add_argument("--lead", required=True)
    p.add_argument("--sablon", required=True)
    p.add_argument("--megszolitas")
    p.add_argument("--idopont1")
    p.add_argument("--idopont2")
    p.add_argument("--helyi", action="store_true", help="csak a csomagolt sablon")
    p.set_defaults(f=p_level)
    p = sub.add_parser("profil")
    for kulcs in ("nev", "telefon", "titulus_hu", "titulus_ro"):
        p.add_argument("--" + kulcs.replace("_", "-"), dest=kulcs)
    p.set_defaults(f=p_profil)
    p = sub.add_parser("uj-lead")
    p.add_argument("--adat", required=True, help="JSON-fájl, vagy - a bemenethez")
    p.set_defaults(f=p_uj_lead)
    args = ap.parse_args(argv)
    try:
        kimenet = args.f(args)
        kod = 0
    except Hiba as h:
        kimenet, kod = {"hiba": {"kod": h.kod, "uzenet": h.uzenet}}, 1
    print(json.dumps(kimenet, ensure_ascii=False, indent=2))
    return kod


if __name__ == "__main__":
    sys.exit(main())
