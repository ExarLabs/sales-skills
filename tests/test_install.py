"""A telepítő: git clone, git pull, zip (git nélkül), a belépő tartalma, a frissítés jelzése, az eltávolítás,
és hogy idegen mappát nem ír felül. A valódi home-ot nem érinti (HOME és USERPROFILE ideiglenes mappára)."""
import contextlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "install"))
import install  # noqa: E402

KIHAGY = shutil.ignore_patterns(".git", "__pycache__", "dist", "*.pyc")


class Telepito(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.env = mock.patch.dict(os.environ, {"HOME": str(self.tmp / "home"), "USERPROFILE": str(self.tmp / "home")})
        self.env.start()
        # forrás-repó a munkapéldány mostani állapotából (a még nem commitolt fájlokkal együtt)
        self.forras = self.tmp / "forras"
        shutil.copytree(ROOT, self.forras, ignore=KIHAGY)
        for args in (["init", "-q", "-b", "main"], ["add", "-A"],
                     ["-c", "user.name=t", "-c", "user.email=t@t.test", "commit", "-q", "-m", "x"]):
            subprocess.run(["git", "-C", str(self.forras), *args], check=True, capture_output=True)
        self.hova = self.tmp / "home" / ".sales-skills"
        self.skills = self.tmp / "home" / ".claude" / "skills"

    def tearDown(self):
        self.env.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def futtat(self, *extra):
        ki = io.StringIO()
        with contextlib.redirect_stdout(ki):
            kod = install.main(["--hova", str(self.hova), "--skills-hova", str(self.skills),
                                "--forras", str(self.forras), "--zip-url", self.zip_url(), *extra])
        return kod, json.loads(ki.getvalue())

    def zip_url(self):
        z = self.tmp / "repo.zip"
        if not z.exists():
            with zipfile.ZipFile(z, "w") as zf:
                for p in self.forras.rglob("*"):
                    if p.is_file() and ".git" not in p.parts:
                        zf.write(p, pathlib.Path("sales-skills-main") / p.relative_to(self.forras))
        return z.as_uri()

    def test_clone_es_belepo(self):
        kod, ki = self.futtat()
        self.assertEqual((kod, ki["mod"], ki["rendben"]), (0, "clone", True))
        belepo = (self.skills / "exar-sales" / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(belepo.startswith("---\nname: exar-sales\ndescription: \"Exar Sales:"))
        self.assertIn("--frissit", belepo)
        self.assertIn((self.hova / "skills" / "exar-sales" / "SKILL.md").as_posix(), belepo)
        self.assertTrue((self.hova / "skills" / "exar-sales" / "exar_sales.py").exists())

    def test_pull_es_uj_verzio(self):
        self.futtat()
        (self.forras / "VERSION").write_text("9.9.9\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.forras), "-c", "user.name=t", "-c", "user.email=t@t.test",
                        "commit", "-qam", "v"], check=True)
        kod, ki = self.futtat("--frissit")
        self.assertEqual(ki["mod"], "pull")
        self.assertEqual(ki["uj_verzio"]["uj"], "9.9.9")
        self.assertNotIn("belepo", ki)  # frissítéskor a meglévő belépő marad

    def test_zip_git_nelkul(self):
        with mock.patch.object(install, "van_git", return_value=False):
            kod, ki = self.futtat()
        self.assertEqual((kod, ki["mod"]), (0, "zip"))
        self.assertFalse((self.hova / ".git").exists())
        self.assertTrue((self.skills / "exar-sales" / "SKILL.md").exists())

    def test_idegen_mappat_nem_ir_felul(self):
        (self.skills / "exar-sales").mkdir(parents=True)
        (self.skills / "exar-sales" / "SKILL.md").write_text("---\nname: mas\n---\n", encoding="utf-8")
        kod, ki = self.futtat()
        self.assertEqual(kod, 1)
        self.assertIn("nem az exar-sales", ki["hiba"])
        self.assertIn("name: mas", (self.skills / "exar-sales" / "SKILL.md").read_text(encoding="utf-8"))

    def test_regi_masolt_skillt_lecserel(self):
        regi = self.skills / "exar-sales"
        shutil.copytree(ROOT / "skills" / "exar-sales", regi, ignore=KIHAGY)
        kod, ki = self.futtat()
        self.assertEqual(kod, 0)
        self.assertFalse((regi / "exar_sales.py").exists())

    def test_frissites_hibaja_nem_allit_meg(self):
        self.futtat()
        with mock.patch.object(install, "git", return_value=subprocess.CompletedProcess([], 1, "", "nincs net")):
            kod, ki = self.futtat("--frissit")
        self.assertEqual((kod, ki["rendben"]), (0, False))

    def test_uninstall(self):
        self.futtat()
        kod, ki = self.futtat("--uninstall")
        self.assertTrue(ki["belepo_torolve"])
        self.assertFalse((self.skills / "exar-sales").exists())
        self.assertTrue(self.hova.exists())


if __name__ == "__main__":
    unittest.main()
