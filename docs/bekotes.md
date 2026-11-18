# A CRM (Exar Sales portál) bekötése

A leadjeid az ExarLabs CRM-jében élnek; te a sales portálon át éred el őket: `https://sales.exarlabs.com`. A portál
csak a saját leadjeidet mutatja és adja ki, a CRM többi részét nem.

A Claude kétféleképpen éri el a portált:

| | Böngészős út | Programos út |
|---|---|---|
| Hol | claude.ai vagy Claude Desktop, Claude in Chrome bővítménnyel | Claude Code vagy Claude Desktop, Pythonnal |
| Kulcs | nem kell: a böngésződ belépett lapját használja | API-kulcs, az ExarLabs adja |
| Mikor jó | ha amúgy is a böngészőben dolgozol | ha a gépeden futó Claude-dal dolgozol, böngésző nélkül |

A lépésenkénti leírás a skillben van, és a Claude végigvezet rajta („Kösd be az Exar Sales-t”):
[skills/exar-sales/references/bekotes.md](../skills/exar-sales/references/bekotes.md).

## A legfontosabb szabályok

- A portálra a céges (exar.ro) címeddel lépsz be: Microsoft-fiókkal vagy e-mailes linkkel.
- Az API-kulcsot az ExarLabs-kapcsolattartód adja, közvetlenül neked. **Soha ne írd be a chatbe**, és ne tedd fájlba,
  amit megosztasz. Környezeti változóként állítod be (`EXAR_SALES_API_KEY`, `EXAR_SALES_API_SECRET`).
- Ha a kulcs kiszivárgott (például beírtad a chatbe), szólj, és kapsz újat.
