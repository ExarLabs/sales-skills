"""A program: sablon-kitöltés, megszólítás, Outlook-link, és a portál-hívások egy hamis szerverrel."""
import contextlib
import io
import json
import os
import pathlib
import sys
import tempfile
import threading
import unittest
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "exar-sales"))
import exar_sales as es  # noqa: E402

LEAD = {
    "name": "CRM-LEAD-1", "organization": "Példa Kft.", "contact": "Kovács Anna Mária", "email": "anna@pelda.test",
    "problem": "sok kézi számlázás",
}
PREP = {"lead": LEAD, "template": None, "deck_url": "https://exarlabs.com/bemutato",
        "partner": {"name": "Teszt Partner", "email": "partner@exar.test"}}


class Hamis(BaseHTTPRequestHandler):
    keresek = []

    def log_message(self, *a):
        pass

    def _valasz(self, kod, adat):
        body = json.dumps(adat).encode()
        self.send_response(kod)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        Hamis.keresek.append(("GET", self.path, self.headers.get("Authorization")))
        if self.headers.get("Authorization") != "token k:t":
            return self._valasz(403, {})
        if self.path.startswith("/api/method/exar_sales.api.my_leads"):
            return self._valasz(200, {"message": [LEAD]})
        if self.path.startswith("/api/method/exar_sales.api.email_prep"):
            lead = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("lead", [""])[0]
            if lead != "CRM-LEAD-1":
                return self._valasz(403, {})
            return self._valasz(200, {"message": PREP})
        self._valasz(404, {})

    def do_POST(self):
        hossz = int(self.headers.get("Content-Length") or 0)
        adat = urllib.parse.parse_qs(self.rfile.read(hossz).decode())
        Hamis.keresek.append(("POST", self.path, adat))
        if "tax_id" not in adat:
            msg = json.dumps([json.dumps({"message": "Hiányzó mező: Adószám (CUI)"})])
            return self._valasz(417, {"_server_messages": msg})
        self._valasz(200, {"message": {"name": "CRM-LEAD-2"}})


class Alap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.szerver = HTTPServer(("127.0.0.1", 0), Hamis)
        threading.Thread(target=cls.szerver.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.szerver.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.szerver.shutdown()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.regi = (es.BASE, es.SABLON_URL, es.PROFIL, dict(os.environ))
        es.BASE = self.url
        es.SABLON_URL = self.url + "/nincs-ilyen"  # a friss sablon nem érhető el: csomagolt példány
        es.PROFIL = pathlib.Path(self.tmp.name) / "profil.json"
        os.environ["EXAR_SALES_API_KEY"], os.environ["EXAR_SALES_API_SECRET"] = "k", "t"

    def tearDown(self):
        es.BASE, es.SABLON_URL, es.PROFIL, env = self.regi
        os.environ.clear()
        os.environ.update(env)
        self.tmp.cleanup()

    def futtat(self, *argv):
        ki = io.StringIO()
        with contextlib.redirect_stdout(ki):
            kod = es.main(list(argv))
        return kod, json.loads(ki.getvalue())


class TestKitoltes(unittest.TestCase):
    def test_idopont_valtozatok(self):
        torzs = "A\n?idopont: két időpont: {{idopont1}} vagy {{idopont2}}.\n?!idopont: írjon időpontot.\nB\n"
        van, _ = es.kitolt(torzs, {"idopont1": "H 10", "idopont2": "K 14"}, True)
        nincs, _ = es.kitolt(torzs, {"idopont1": "", "idopont2": ""}, False)
        self.assertEqual(van, "A\nkét időpont: H 10 vagy K 14.\nB\n")
        self.assertEqual(nincs, "A\nírjon időpontot.\nB\n")

    def test_hianyzo_hely_jelolve(self):
        szoveg, hianyzik = es.kitolt("Tel.: {{telefon}}\n", {"telefon": ""}, False)
        self.assertEqual(szoveg, "Tel.: [telefon]\n")
        self.assertEqual(hianyzik, ["telefon"])

    def test_megszolitas(self):
        self.assertEqual(es.alap_megszolitas({"megszolitas": "magazo", "nyelv": "hu"}, "Kovács Anna"), "Kovács Anna")
        self.assertEqual(es.alap_megszolitas({"megszolitas": "magazo", "nyelv": "hu"}, ""), "Hölgyem/Uram")
        self.assertEqual(es.alap_megszolitas({"megszolitas": "tegezo", "nyelv": "hu"}, "Kovács Anna Mária"), "Anna Mária")
        self.assertEqual(es.alap_megszolitas({"megszolitas": "formal", "nyelv": "ro"}, "Ion Popescu"), "Bună ziua")

    def test_outlook_link_kodolt(self):
        link = es.outlook_link("a@b.test", "Tárgy: x", "Sor 1\nSor 2 & más")
        self.assertTrue(link.startswith(es.OUTLOOK + "?to=a%40b.test&subject="))
        self.assertIn("Sor%201%0ASor%202%20%26%20m%C3%A1s", link)
        self.assertNotIn("+", link)


class TestPortal(Alap):
    def test_nincs_kulcs(self):
        del os.environ["EXAR_SALES_API_KEY"]
        kod, ki = self.futtat("leadek")
        self.assertEqual(kod, 1)
        self.assertEqual(ki["hiba"]["kod"], "nincs_kulcs")

    def test_ellenoriz_es_leadek(self):
        self.assertEqual(self.futtat("ellenoriz")[1], {"rendben": True, "portal": self.url, "leadek_szama": 1})
        self.assertEqual(self.futtat("leadek")[1]["leadek"][0]["name"], "CRM-LEAD-1")

    def test_kulcs_nem_jelenik_meg(self):
        os.environ["EXAR_SALES_API_SECRET"] = "rossz-titok"
        kod, ki = self.futtat("leadek")
        self.assertEqual(ki["hiba"]["kod"], "nincs_hozzaferes")
        self.assertNotIn("rossz-titok", json.dumps(ki))

    def test_mas_leadje_elutasitva(self):
        kod, ki = self.futtat("lead", "CRM-LEAD-9")
        self.assertEqual((kod, ki["hiba"]["kod"]), (1, "nincs_hozzaferes"))

    def test_level_magazo_idopontokkal(self):
        self.futtat("profil", "--telefon", "+40 700 000 000")
        kod, ki = self.futtat("level", "--lead", "CRM-LEAD-1", "--sablon", "bemutato-hu-magazo",
                              "--idopont1", "csütörtök 10:00", "--idopont2", "péntek 14:00")
        self.assertEqual(kod, 0)
        self.assertEqual(ki["cimzett"], "anna@pelda.test")
        self.assertTrue(ki["torzs"].startswith("Kedves Kovács Anna Mária!"))
        self.assertIn("csütörtök 10:00 vagy péntek 14:00", ki["torzs"])
        self.assertNotIn("Írja meg, kérem", ki["torzs"])
        self.assertIn("https://exarlabs.com/bemutato", ki["torzs"])
        self.assertIn("Teszt Partner\nÜzletfejlesztés | ExarLabs\nTel.: +40 700 000 000\nE-mail: partner@exar.test", ki["torzs"])
        self.assertNotIn("{{", ki["torzs"])
        self.assertEqual(ki["hianyzik"], [])
        self.assertEqual(ki["sablon"]["forras"], "csomagolt")
        self.assertEqual(ki["lead"]["mi_a_gondjuk"], "sok kézi számlázás")

    def test_level_tegezo_idopont_nelkul_profil_nelkul(self):
        kod, ki = self.futtat("level", "--lead", "CRM-LEAD-1", "--sablon", "bemutato-hu-tegezo")
        self.assertTrue(ki["torzs"].startswith("Szia Anna Mária!"))
        self.assertIn("Írd meg, melyik nap", ki["torzs"])
        self.assertEqual(ki["hianyzik"], ["telefon"])
        self.assertIn("Tel.: [telefon]", ki["torzs"])

    def test_level_roman(self):
        self.futtat("profil", "--telefon", "+40 700 000 000")
        kod, ki = self.futtat("level", "--lead", "CRM-LEAD-1", "--sablon", "bemutato-ro")
        self.assertTrue(ki["torzs"].startswith("Bună ziua,"))
        self.assertIn("Dezvoltare afaceri | ExarLabs", ki["torzs"])
        self.assertIn("Vă rog să-mi spuneți", ki["torzs"])
        self.assertTrue(ki["targy"].startswith("ExarLabs: despre"))

    def test_ismeretlen_sablon(self):
        kod, ki = self.futtat("level", "--lead", "CRM-LEAD-1", "--sablon", "nincs")
        self.assertEqual(ki["hiba"]["kod"], "nincs_sablon")

    def test_uj_lead(self):
        adat = pathlib.Path(self.tmp.name) / "lead.json"
        adat.write_text(json.dumps({"organization": "Minta SRL", "tax_id": "RO123", "first_name": "Ion",
                                    "mobile_no": "0700000000", "partner": "MÁS", "email": ""}), encoding="utf-8")
        kod, ki = self.futtat("uj-lead", "--adat", str(adat))
        self.assertEqual(ki, {"felveve": "CRM-LEAD-2"})
        elkuldve = Hamis.keresek[-1][2]
        self.assertNotIn("partner", elkuldve)
        self.assertNotIn("email", elkuldve)

    def test_uj_lead_portal_uzenete(self):
        adat = pathlib.Path(self.tmp.name) / "lead.json"
        adat.write_text(json.dumps({"organization": "Minta SRL"}), encoding="utf-8")
        kod, ki = self.futtat("uj-lead", "--adat", str(adat))
        self.assertEqual(ki["hiba"], {"kod": "elutasitva", "uzenet": "Hiányzó mező: Adószám (CUI)"})


if __name__ == "__main__":
    unittest.main()
