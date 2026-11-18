# A bemutató levél

A levél mindig a repó legfrissebb sablonjából és a portál adataiból készül, ezért a partnernek nem kell semmit
másolnia vagy frissítenie: ha az ExarLabs módosítja a sablont vagy a bemutatót, a következő levél már azzal megy.

## 1. Melyik lead

A partner cégnevet vagy nevet mond. A `leadek` listából (böngészőben `my_leads`) keresd ki. Ha több illik rá, kérdezz.
Ha egy sem: lehet, hogy még nincs felvéve; ajánld fel a felvételt ([lead-felvetel.md](lead-felvetel.md)).

## 2. Melyik sablon (magától választasz, és megmondod, mit választottál)

| Sablon | Mikor |
|---|---|
| `bemutato-hu-magazo` | **alapértelmezés**: magyar kapcsolattartó, első levél |
| `bemutato-hu-tegezo` | ha a partner azt mondja, hogy a hívásban tegeződtek, vagy a „Mi a gondjuk” mezőben ez áll |
| `bemutato-ro` | ha a hívás románul zajlott, vagy a partner román levelet kér |

A nyelvet a hívás nyelve dönti el, nem a megye és nem a név. Ha nem tudod, és a név vagy a cég alapján bizonytalan,
**kérdezz egyet**: „Magyarul vagy románul beszéltetek? Tegeződtetek?” A választásod egy sorban mondd meg a partnernek
(például „Magyar, magázó sablont használtam.”), hogy szólhasson, ha másképp akarja.

A román sablon `allapot` mezője jelezheti, hogy még anyanyelvi átnézésre vár; ilyenkor szólj a partnernek, hogy
küldés előtt olvassa át figyelmesen.

## 3. Időpontok

A levél két időpontot ajánlhat a 30 perces videóhívásra. Kérdezd meg a partnert: „Javasoljunk két időpontot? Ha igen,
melyiket?” Ha nem ad meg kettőt, a sablon azt a változatot használja, amelyik a címzettet kéri meg, hogy írjon egy
időpontot. Ne találj ki időpontot.

## 4. Kitöltés

**Program:** `level --lead <név> --sablon <id> [--idopont1 "…" --idopont2 "…"] [--megszolitas "…"]`. A kimenet a
kitöltött levél, az `outlook_link`, és a `hianyzik` lista.

**Böngésző:** a [bongeszo.md](bongeszo.md) kitöltő függvénye ugyanezt adja.

A helyek:

| Hely | Honnan |
|---|---|
| `megszolitas` | magázó: a kapcsolattartó teljes neve („Kovács Anna”), név nélkül „Hölgyem/Uram”; tegező: a keresztnév; román: „Bună ziua”, vagy ha a partner tudja: „Stimate domnule Popescu” / „Stimată doamnă Popescu” |
| `bemutato_link` | a portál adja (`deck_url`) |
| `idopont1`, `idopont2` | a partner mondja |
| `nev`, `email` | a portál adja (a partner neve és céges címe) |
| `titulus`, `telefon` | a partner profilja (program: `profil`; böngésző: kérdezd meg egyszer, és javasold, hogy a Claude-projekt utasításaiba írja be) |

Ha a `hianyzik` lista nem üres, minden tételét kérd el a partnertől, egyenként. Ha a leadnek nincs e-mail címe, azt is.

Ha a lead „Mi a gondjuk” mezője ki van töltve, a köszönő mondat után **legfeljebb egy** saját mondattal utalhatsz rá,
a sablon nyelvén és megszólításával. Mást nem teszel hozzá.

## 5. Megnyitás és átadás

Nyisd meg az `outlook_link`-et (böngészőben új lapon; program esetén add át a partnernek kattintható linkként). A
partner az exar.ro fiókjával van belépve, a levél az ő nevében, az ő Outlookjában nyílik meg. Ha a kiegészítő mondatot
hozzáadtad, a linket azzal együtt építsd újra.

Mutasd meg a levelet a chatben is, és zárd így: „Nézd át, és ha jó, nyomd meg a Küldést.”

Ha az Outlook nem nyitja meg (túl hosszú link, nincs belépve), add át a tárgyat és a törzset másolható blokkban, és
a partner illessze be egy új levélbe.
