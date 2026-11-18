# Telepítés

## claude.ai vagy Claude Desktop (a legegyszerűbb)

1. Töltsd le a [`exar-sales.zip`](https://github.com/ExarLabs/sales-skills/releases/latest/download/exar-sales.zip)
   fájlt. Ne csomagold ki.
2. claude.ai (vagy Claude Desktop): Beállítások, Képességek (Capabilities). Ha a Skills (Képességek) kapcsoló ki van
   kapcsolva, kapcsold be.
3. „Skill feltöltése” (Upload skill), és válaszd ki a zipet. Megjelenik az `exar-sales` skill; legyen bekapcsolva.
4. A böngészős úthoz (kulcs nélkül) kell a Claude in Chrome bővítmény is: Chrome Web Store, „Claude”, ugyanazzal a
   fiókkal belépve.

Frissítés: új kiadásnál töltsd le újra a zipet, töröld a régi skillt, és töltsd fel az újat. A levélsablonok ehhez
nem kellenek: azokat a skill mindig a repóból olvassa.

## Claude Code

```
/plugin marketplace add ExarLabs/sales-skills
/plugin install exar-sales@sales-skills
```

Frissítés: `/plugin marketplace update sales-skills`.

Plugin nélkül, kézzel: `git clone https://github.com/ExarLabs/sales-skills.git`, majd
`python3 -I sales-skills/scripts/telepit.py` (a skill a `~/.claude/skills/exar-sales` alá kerül).

## Utána

A bekötés: [bekotes.md](bekotes.md).
