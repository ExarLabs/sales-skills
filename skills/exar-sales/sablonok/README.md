# Levélsablonok

Egy sablon egy fájl. A partner Claude-ja minden levélnél innen, a repó `main` ágáról olvassa a legfrissebb
változatot; ha a hálózat nem engedi, a telepítéskor csomagolt példányt használja (a program kimenetében
`forras: friss` vagy `csomagolt`).

| Sablon | Nyelv | Megszólítás | Mire |
|---|---|---|---|
| [bemutato-hu-magazo](bemutato-hu-magazo.md) | magyar | magázó (alapértelmezés) | bemutató levél a hideghívás után |
| [bemutato-hu-tegezo](bemutato-hu-tegezo.md) | magyar | tegező | ugyanaz, ha a hívásban tegeződtek |
| [bemutato-ro](bemutato-ro.md) | román | formális | ugyanaz, ha a hívás románul zajlott |

A választás szabálya: [references/bemutato.md](../references/bemutato.md), 2. lépés.

## Formátum

```
---
id: <a fájl neve kiterjesztés nélkül>
mire: <egy sor>
nyelv: hu | ro
megszolitas: magazo | tegezo | formal
version: <semver>
allapot: <opcionális, például: tervezet, anyanyelvi átnézésre vár>
targy: "<a levél tárgya>"
---
<törzs>
```

A törzsben:

- `{{hely}}`: kitöltendő; a helyek: `megszolitas`, `bemutato_link`, `idopont1`, `idopont2`, `nev`, `titulus`,
  `telefon`, `email`.
- `?idopont:` kezdetű sor csak akkor marad benne, ha a partner két időpontot adott; `?!idopont:` kezdetű csak akkor,
  ha nem.

## Módosítás

Szövegváltozás: a fájl szerkesztése, `version` emelése, bejegyzés a `CHANGELOG.md`-be, `sh scripts/ellenorzes.sh`,
commit a `main` ágra. A következő levél már az új szöveggel megy. Új sablon: új fájl ugyanebben a formátumban, és egy
sor a fenti táblában meg a `references/bemutato.md` választási táblájában.

A repó nyilvános: a sablonba nem kerülhet belső adat, személyes telefonszám vagy e-mail cím (ezek a partner
profiljából és a portálról jönnek), és ügyfélnév csak nyilvános referenciaként.
