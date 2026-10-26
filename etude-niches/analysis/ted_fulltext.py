"""Comptage des avis TED belges par piste B2B (recherche plein texte FR + NL).

Période : 26/10/2023 → 26/10/2026, découpée en 3 années glissantes :
  A1 = 26/10/2023-25/10/2024, A2 = 26/10/2024-25/10/2025, A3 = 26/10/2025-26/10/2026.
Région : déduite du code postal de l'acheteur (Bruxelles 1000-1299 ; Wallonie
1300-1499 et 4000-7999 ; sinon Flandre).
Types : avis de marché (cn-*) = intention d'acheter ; avis d'attribution (can-*) = achat attribué.
Syntaxe : un FT~("terme") par terme, reliés par OR (un OR à l'intérieur de FT~ renvoie des résultats incohérents, testé le 26/10/2026).
Limites : TED ne publie que les marchés publics (souvent au-dessus des seuils
européens) ; un même marché peut produire plusieurs avis (marché + attribution) ;
un terme peut apparaître dans un avis sans en être l'objet principal.
Usage : python3 -I ted_fulltext.py sortie_dossier
"""
import json, subprocess, sys, time, re, collections, os

NICHES = {
 "QAI": ["purificateurs d'air", "purificateur", "luchtreinigers", "luchtreiniger", "CO2-meters", "CO2-meter", "capteurs de CO2", "qualité de l'air intérieur", "binnenluchtkwaliteit"],
 "CAISSES_HORECA": ["caisse enregistreuse", "caisses enregistreuses", "kassasysteem", "kassasystemen"],
 "ECRANS_INTERACTIFS": ["écran interactif", "écrans interactifs", "interactieve schermen", "interactief scherm", "affichage dynamique", "digital signage"],
 "WIFI_RESEAU": ["wifi", "wi-fi", "réseau sans fil", "draadloos netwerk"],
 "VETEMENTS_PRO": ["vêtements de travail", "vêtements professionnels", "werkkledij", "werkkleding"],
 "FONTAINES_EAU": ["fontaines à eau", "fontaine à eau", "waterfonteinen", "waterkoelers"],
 "CUISINE_PRO": ["équipement de cuisine", "matériel de cuisine", "keukenapparatuur", "grootkeuken"],
 "MOBILIER_ERGO": ["assis-debout", "sièges ergonomiques", "chaises ergonomiques", "zit-sta", "ergonomische stoelen"],
 "ECLAIRAGE_LED": ["éclairage LED", "luminaires LED", "LED-verlichting", "relighting"],
 "BOITES_SECOURS": ["boîtes de secours", "trousses de secours", "EHBO-koffers", "verbandkoffers"],
}
FIELDS = ["publication-number", "publication-date", "notice-type", "organisation-post-code-buyer",
          "total-value", "winner-size", "received-submissions-type-val", "received-submissions-type-code"]

def fetch(q):
    body = {"query": q, "fields": FIELDS, "limit": 250, "paginationMode": "ITERATION"}
    out = []
    while True:
        r = subprocess.run(["curl", "-sS", "-m", "120", "-X", "POST", "-H", "Content-Type: application/json",
                            "https://api.ted.europa.eu/v3/notices/search", "-d", json.dumps(body)], capture_output=True)
        d = json.loads(r.stdout)
        if "notices" not in d:
            raise SystemExit(str(d)[:300])
        for n in d["notices"]:
            n.pop("links", None)
        out += d["notices"]
        tok = d.get("iterationNextToken")
        if not tok or not d["notices"]:
            return out
        body["iterationNextToken"] = tok
        time.sleep(1)

def region(n):
    v = [p for p in (n.get("organisation-post-code-buyer") or []) if re.fullmatch(r"\d{4}", str(p))]
    if not v: return "NA"
    p = int(v[0])
    if 1000 <= p <= 1299: return "BXL"
    if 1300 <= p <= 1499 or 4000 <= p <= 7999: return "WAL"
    return "VL"

def year(n):
    d = n["publication-date"][:10].replace("-", "")
    return "A1" if d < "20241026" else ("A2" if d < "20251026" else "A3")

if __name__ == "__main__":
    outdir = sys.argv[1]; os.makedirs(outdir, exist_ok=True)
    print("piste;type;A1_BE;A2_BE;A3_BE;A1_WALBXL;A2_WALBXL;A3_WALBXL;mediane_offres_recues_attrib;attrib_gagnees_PME/attrib_avec_taille")
    for k, terms in NICHES.items():
        ft = " OR ".join('FT~("%s")' % x.replace('"', '') for x in terms)
        ns = fetch(f"buyer-country=BEL AND publication-date>=20231026 AND ({ft})")
        json.dump(ns, open(os.path.join(outdir, k + ".json"), "w"), ensure_ascii=False)
        for typ in ("cn", "can"):
            sel = [n for n in ns if str(n.get("notice-type", "")).startswith(typ + "-")]
            c = collections.Counter((year(n), region(n) in ("WAL", "BXL")) for n in sel)
            be = [sum(v for (y, _), v in c.items() if y == a) for a in ("A1", "A2", "A3")]
            wb = [c[(a, True)] for a in ("A1", "A2", "A3")]
            extra = ""
            if typ == "can":
                subs = []
                for n in sel:
                    v = n.get("received-submissions-type-val") or []
                    subs += [int(x) for x in v if str(x).isdigit()]
                sized = [n for n in sel if n.get("winner-size")]
                sme = [n for n in sized if set(n["winner-size"]) & {"micro", "small", "sme", "medium"}]
                subs.sort()
                med = subs[len(subs)//2] if subs else ""
                extra = f"{med};{len(sme)}/{len(sized)}"
            print(f"{k};{typ};{be[0]};{be[1]};{be[2]};{wb[0]};{wb[1]};{wb[2]};{extra}", flush=True)
