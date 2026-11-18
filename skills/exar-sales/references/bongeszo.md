# Böngészős út (Claude in Chrome, kulcs nélkül)

A partner be van lépve a `https://sales.exarlabs.com/sales/leads` oldalon. Ezen a lapon, a lap saját munkamenetével
hívod a portált: nem kell kulcs, és a portál ugyanúgy csak a partner saját leadjeit adja. A sablon a repó nyilvános
címéről jön (`raw.githubusercontent.com`), mindig a legfrissebb.

## Előkészítés

1. Keresd meg a portál lapját; ha nincs nyitva, nyisd meg. Ha a lap a belépő oldalra visz, kérd meg a partnert, hogy
   lépjen be (Microsoft-fiókkal vagy e-mailes linkkel). A belépést nem te végzed.
2. A lapon futtasd le egyszer az alábbi kódot (javascript eszközzel). Ez csak függvényeket tesz a lapra, semmit nem ír.

```js
window.exarSales = (() => {
  const SABLON = "https://raw.githubusercontent.com/ExarLabs/sales-skills/main/skills/exar-sales/sablonok/";
  const TITULUS = { hu: "Üzletfejlesztés", ro: "Dezvoltare afaceri" };
  async function api(method, params) {
    const r = await fetch("/api/method/" + method + (params ? "?" + new URLSearchParams(params) : ""),
      { headers: { Accept: "application/json" }, credentials: "same-origin" });
    if (!r.ok) throw new Error("A portál hibát adott: HTTP " + r.status);
    return (await r.json()).message;
  }
  function elemez(szoveg) {
    const [, fej, ...rest] = szoveg.split("---");
    const meta = {};
    fej.trim().split("\n").forEach(s => { const i = s.indexOf(":"); if (i > 0) meta[s.slice(0, i).trim()] = s.slice(i + 1).trim().replace(/^"|"$/g, ""); });
    return { meta, torzs: rest.join("---").replace(/^\n+/, "") };
  }
  async function sablon(id) {
    const r = await fetch(SABLON + id + ".md", { cache: "no-store" });
    if (!r.ok) throw new Error("Nincs ilyen sablon: " + id);
    return elemez(await r.text());
  }
  function megszolitas(meta, nev) {
    nev = (nev || "").trim();
    if (meta.nyelv === "ro") return "Bună ziua";
    if (meta.megszolitas === "tegezo") { const i = nev.indexOf(" "); return i > 0 ? nev.slice(i + 1) : nev; }
    return nev || "Hölgyem/Uram";
  }
  async function level(lead, id, o = {}) {
    const adat = await api("exar_sales.api.email_prep", { lead });
    const { meta, torzs } = await sablon(id);
    const vanIdopont = !!(o.idopont1 && o.idopont2);
    const ertek = {
      megszolitas: o.megszolitas || megszolitas(meta, adat.lead.contact),
      bemutato_link: adat.deck_url || "", idopont1: o.idopont1 || "", idopont2: o.idopont2 || "",
      nev: o.nev || adat.partner.name || "", titulus: o.titulus || TITULUS[meta.nyelv] || "",
      telefon: o.telefon || "", email: adat.partner.email || "",
    };
    let szoveg = torzs.split("\n").filter(s =>
      s.startsWith("?idopont:") ? vanIdopont : s.startsWith("?!idopont:") ? !vanIdopont : true
    ).map(s => s.replace(/^\?!?idopont:\s*/, "")).join("\n").trim() + "\n";
    const hianyzik = [];
    for (const [k, v] of Object.entries(ertek)) {
      if (!szoveg.includes("{{" + k + "}}")) continue;
      if (!v) hianyzik.push(k);
      szoveg = szoveg.split("{{" + k + "}}").join(v || "[" + k + "]");
    }
    if (!adat.lead.email) hianyzik.unshift("cimzett_email");
    return { cimzett: adat.lead.email, targy: meta.targy, torzs: szoveg, sablon: meta, hianyzik,
             mi_a_gondjuk: adat.lead.problem, outlook_link: link(adat.lead.email, meta.targy, szoveg) };
  }
  function link(to, subject, body) {
    const q = [["to", to || ""], ["subject", subject], ["body", body]]
      .map(([k, v]) => k + "=" + encodeURIComponent(v)).join("&");
    return "https://outlook.office.com/mail/deeplink/compose?" + q;
  }
  async function ujLead(mezok) {
    const token = window.frappe && window.frappe.csrf_token;
    const r = await fetch("/api/method/exar_sales.api.create_lead", {
      method: "POST", credentials: "same-origin",
      headers: { Accept: "application/json", "Content-Type": "application/x-www-form-urlencoded",
                 ...(token && token !== "None" ? { "X-Frappe-CSRF-Token": token } : {}) },
      body: new URLSearchParams(mezok),
    });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) {
      let uzenet = "HTTP " + r.status;
      try { uzenet = JSON.parse(j._server_messages).map(m => JSON.parse(m).message).join("; "); } catch (e) {}
      throw new Error(uzenet);
    }
    return j.message;
  }
  return { leadek: () => api("exar_sales.api.my_leads"), lead: n => api("exar_sales.api.email_prep", { lead: n }),
           sablon, level, link, ujLead };
})();
"kész"
```

## Használat

| Mit | Hívás |
|---|---|
| a saját leadek | `await exarSales.leadek()` |
| egy lead | `await exarSales.lead("CRM-LEAD-…")` |
| a kitöltött levél | `await exarSales.level("CRM-LEAD-…", "bemutato-hu-magazo", {idopont1, idopont2, telefon, titulus, megszolitas})` |
| link újraépítése (kiegészítő mondat után) | `exarSales.link(cimzett, targy, torzs)` |
| új lead (csak a partner igenje után) | `await exarSales.ujLead({organization, tax_id, first_name, mobile_no, …})` |

A `telefon` és a `titulus` a partneré: első alkalommal kérdezd meg, és javasold, hogy írja be a Claude-projekt
utasításaiba (például „Az aláírásomban: telefon +40 …, titulus Üzletfejlesztés”), hogy legközelebb ne kelljen kérdezni.

A hosszú válaszokat (a levél törzsét) kiolvasás után egyben mutasd meg; ha a javascript eszköz levágja, kérd le
részletekben (`.torzs.slice(0, 1500)`, majd tovább).

Az `outlook_link`-et új lapon nyisd meg. A Küldés gombra nem kattintasz.
