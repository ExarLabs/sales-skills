# Változásnapló

## 0.2.0 (2026-11-18)

- Telepítés egy mondattal: „Olvasd el a https://exarlabs.com/sales-skills oldalt, és telepítsd az Exar Sales skillt.”
  Az agent az `install/INSTALL.md` szerint dolgozik.
- `install/install.py`: a repó a `~/.sales-skills` mappába kerül (git, vagy git nélkül zip), a Claude skill-mappájába
  csak egy belépő; a skill minden használat elején frissíti magát (`--frissit`), eltávolítás `--uninstall`.
- A régi, másoló `scripts/telepit.py` kikerült; a zip csak a parancssor nélküli claude.ai-útra kell.

## 0.1.0 (2026-11-18)

- Első kiadás: `exar-sales` skill (leadek, bemutató levél, új lead, bekötés), böngészős és programos úttal.
- Sablonok: `bemutato-hu-magazo`, `bemutato-hu-tegezo`, `bemutato-ro` (a román tervezet, anyanyelvi átnézésre vár).
- A program: `exar_sales.py` (ellenoriz, leadek, lead, sablonok, sablon, level, profil, uj-lead).
- A portál olvasó végpontjai (`my_leads`, `email_prep`) az exar_sales app 0.4.0-s kiadásától érhetők el.
