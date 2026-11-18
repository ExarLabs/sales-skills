# Bekötés lépésről lépésre

Egyszerre egy lépést kérsz, és megvárod, hogy a partner jelezze: kész.

## 1. Belépés a portálra (minden úthoz kell)

A portál címe: `https://sales.exarlabs.com/sales/leads`. A partner a céges (exar.ro) címével lép be:

- „Belépés Microsoft 365-fiókkal” gomb, vagy
- e-mailes belépő link: beírja a céges címét, és a levélben kapott linkre kattint.

Ha „Nincs elegendő jogosultsága” üzenetet kap, vagy a link nem érkezik meg: ezt az ExarLabs-kapcsolattartó intézi,
írja meg neki a pontos üzenetet és az időpontot.

## 2/A. Böngészős út (kulcs nélkül)

1. Chrome, a Claude in Chrome bővítménnyel (a Chrome Web Store-ból, bejelentkezve ugyanazzal a Claude-fiókkal).
2. A skill feltöltése a Claude-ba: a repó kiadásaiból letöltött `exar-sales.zip` a claude.ai beállításaiban, a
   Skills (Képességek) résznél (lásd a repó `docs/telepites.md` leírását).
3. Próba: „Milyen leadjeim vannak?” Ha a portál lapja nyitva van és be van lépve, a lista megjelenik.

## 2/B. Programos út (Claude Code vagy Claude Desktop, API-kulccsal)

1. Python 3.9 vagy újabb legyen a gépen (`python3 --version`; Windowson `python --version`).
2. A kulcsot az ExarLabs adja közvetlenül a partnernek, **nem a chatben**. Két része van: kulcs és titok.
3. A partner maga állítja be környezeti változóként (te nem látod és nem írod):
   - Windows (PowerShell), egyszer: `setx EXAR_SALES_API_KEY "<kulcs>"` és `setx EXAR_SALES_API_SECRET "<titok>"`,
     utána a Claude-ot újra kell indítani.
   - Mac: a `~/.zshrc` végére `export EXAR_SALES_API_KEY="<kulcs>"` és `export EXAR_SALES_API_SECRET="<titok>"`,
     utána új terminál, és a Claude újraindítása.
4. Próba: `ellenoriz`. Ha `rendben: true`, kész. Ha `nincs_kulcs`: a változó nem látszik (újraindítás kell). Ha
   `nincs_hozzaferes`: a kulcs rossz vagy le van tiltva; az ExarLabs-kapcsolattartó ad újat.
5. Aláírás: `profil --telefon "+40 …" --titulus-hu "Üzletfejlesztés" --titulus-ro "Dezvoltare afaceri"`. Ez a
   gépen marad (`~/.exar-sales/profil.json`), nem kerül a repóba és a portálra.

## 3. Outlook

A levél az Outlook webes felületén nyílik meg (`outlook.office.com`), a partner exar.ro fiókjával. Ha a böngészőben
nincs belépve, előbb ott kell belépnie. Ha a céges fiókba belépéskor eszközkezelési (MDM) hibát kap, az admin
intézi; addig a böngészős Outlook (outlook.office.com) általában működik.
