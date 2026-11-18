# Új lead felvétele egy hívás után

A partner elmondja, kivel beszélt. Te összeszeded a mezőket, egyszer visszaolvasod, és a partner igenje után
felveszed. A lead a partner nevén jön létre; az ExarLabs-kapcsolattartó feladatot kap róla.

## Mezők

| Kulcs | Mező | Kötelező |
|---|---|---|
| `organization` | cégnév | igen |
| `tax_id` | adószám (CUI), „RO” előtaggal vagy anélkül | igen |
| `first_name` | a döntéshozó keresztneve | igen |
| `last_name` | vezetéknév | |
| `job_title` | beosztás | |
| `mobile_no` | telefon; a 0-val kezdődő romániai szám elé a portál +40-et tesz, más számot országkóddal kérj | igen |
| `email` | a döntéshozó e-mail címe (nem a partneré) | |
| `website` | honlap | |
| `county`, `city` | megye, település | |
| `meeting_at` | megbeszélt időpont, `ÉÉÉÉ-HH-NN ÓÓ:PP` alakban | |
| `problem` | „Mi a gondjuk”: a partner szavaival, röviden, legfeljebb 2000 karakter | |

## Lépések

1. Ami hiányzik a kötelezőkből, kérd el, egyszerre egyet. Az adószámot ne találd ki; ha a partner nem tudja, kérd meg,
   hogy nézze meg (például a listán vagy a cég honlapján), vagy vegye fel később a portálon.
2. Olvasd vissza egy rövid listában, és kérdezd: „Felvegyem így?”
3. Igen után:
   - **Program:** írd az adatokat egy ideiglenes JSON-fájlba, és `uj-lead --adat <fájl>`; a kimenet `felveve` mezője
     a lead neve.
   - **Böngésző:** a [bongeszo.md](bongeszo.md) `ujLead` függvénye.
4. Ha a portál elutasítja („Ezt a céget már felvetted”, „Ez a cég már szerepel a rendszerünkben”, hiányzó mező),
   mondd el a partnernek szó szerint. Egy már ismert céget nem lehet újra felvenni; ezt nem kerülöd meg.
5. Ha a partner bemutató levelet is kért, folytasd a [bemutato.md](bemutato.md) szerint.
