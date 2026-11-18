# Telepítés

## Az egyszerű út: mondd a Claude-nak

Claude Code-ban, vagy a Claude Desktop Code lapján (bármelyik mappában), másold be:

> Olvasd el a https://exarlabs.com/sales-skills oldalt, és telepítsd az Exar Sales skillt.

A Claude elolvassa a telepítési lépéseket ([install/INSTALL.md](../install/INSTALL.md)), letölti a repót a
`~/.sales-skills` mappába (git-tel, vagy git nélkül zipként; GitHub-fiók nem kell), és a Claude skill-mappájába
(`~/.claude/skills/exar-sales/`) egy belépőt ír. Engedélyt kér a letöltéshez: ha egyetértesz, kattints az
Engedélyezés gombra. Utána végigvezet a portál bekötésén.

**Frissítés:** magától, minden használat elején. Ha új változat jött, a Claude egy sorban szól.

**Eltávolítás:** mondd a Claude-nak: „Távolítsd el az Exar Sales skillt.” (`python ~/.sales-skills/install/install.py
--uninstall`, majd a `~/.sales-skills` mappa törlése.)

Python kell hozzá (3.9 vagy újabb). Ha nincs, a Claude megmondja, hogyan telepítsd.

## Más utak

Csak az egyiket használd, hogy egy skillt láss.

**Plugin (Claude Code, Cowork):** Claude Code-ban `/plugin marketplace add ExarLabs/sales-skills`, majd
`/plugin install exar-sales@sales-skills`; Cowork-ben Customize, Plugins, Add, Add marketplace, Add from a repository,
`ExarLabs/sales-skills`, majd az exar-sales plugin. Frissítés: az alkalmazás intézi.

**Zip (sima claude.ai vagy Claude Desktop beszélgetés, ahol nincs parancssor):** töltsd le a
[`exar-sales.zip`](https://github.com/ExarLabs/sales-skills/releases/latest/download/exar-sales.zip) fájlt (ne
csomagold ki), majd Beállítások, Képességek (Capabilities), Skills, feltöltés. Ehhez a böngészős út kell (Claude in
Chrome bővítmény). Frissítéskor a zipet újra fel kell tölteni; a levélsablonok viszont mindig frissek, mert a skill a
repóból olvassa őket.

## Utána

A bekötés: [bekotes.md](bekotes.md).
