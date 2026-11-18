"""A repó szerkezete: a sablonok formája, a skill frontmattere, a verziók egyezése, a csomagolás."""
import json
import pathlib
import re
import sys
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "exar-sales"
sys.path.insert(0, str(SKILL))
sys.path.insert(0, str(ROOT / "scripts"))
import csomagol  # noqa: E402
import exar_sales as es  # noqa: E402

HELYEK = {"megszolitas", "bemutato_link", "idopont1", "idopont2", "nev", "titulus", "telefon", "email"}


class TestSablonok(unittest.TestCase):
    def test_minden_sablon_ervenyes(self):
        ids = es.sablon_ids()
        self.assertEqual(set(ids), {"bemutato-hu-magazo", "bemutato-hu-tegezo", "bemutato-ro"})
        for azon in ids:
            with self.subTest(azon):
                meta, torzs, _ = es.sablon(azon, helyi=True)
                self.assertEqual(meta["id"], azon)
                for kulcs in ("mire", "nyelv", "megszolitas", "version", "targy"):
                    self.assertTrue(meta.get(kulcs), kulcs)
                self.assertIn(meta["nyelv"], {"hu", "ro"})
                self.assertRegex(meta["version"], r"^\d+\.\d+\.\d+$")
                self.assertTrue(set(re.findall(r"\{\{(\w+)\}\}", torzs)) <= HELYEK)
                self.assertEqual(sum(s.startswith("?idopont:") for s in torzs.splitlines()), 1)
                self.assertEqual(sum(s.startswith("?!idopont:") for s in torzs.splitlines()), 1)
                self.assertNotIn("—", torzs)

    def test_valasztasi_tabla_minden_sablont_nevez(self):
        szoveg = (SKILL / "references" / "bemutato.md").read_text(encoding="utf-8")
        for azon in es.sablon_ids():
            self.assertIn(f"`{azon}`", szoveg)


class TestSkill(unittest.TestCase):
    def test_frontmatter_es_verzio(self):
        szoveg = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(szoveg.startswith("---\nname: exar-sales\n"))
        verzio = (ROOT / "VERSION").read_text().strip()
        self.assertIn(f"version: {verzio}", szoveg)
        self.assertEqual(json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"], verzio)
        self.assertIn(f"## {verzio}", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_hivatkozott_fajlok_leteznek(self):
        for md in [SKILL / "SKILL.md", *SKILL.glob("references/*.md")]:
            for cel in re.findall(r"\]\(([^)#:]+\.md)\)", md.read_text(encoding="utf-8")):
                self.assertTrue((md.parent / cel).exists(), f"{md.name}: {cel}")

    def test_csomag(self):
        with tempfile.TemporaryDirectory() as d:
            ki = csomagol.csomagol(pathlib.Path(d))
            nevek = zipfile.ZipFile(ki["zip"]).namelist()
        self.assertIn("exar-sales/SKILL.md", nevek)
        self.assertIn("exar-sales/exar_sales.py", nevek)
        self.assertIn("exar-sales/sablonok/bemutato-ro.md", nevek)
        self.assertFalse([n for n in nevek if "__pycache__" in n])


if __name__ == "__main__":
    unittest.main()
