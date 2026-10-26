"""Manque d'offres par catégorie CPV — échantillon d'attributions publicprocurement.be (Wallonie + Bruxelles).

Entrée : dossier de bosa_echantillon.py (détails eForms) ; lecture par eforms_parse.parse().
Par groupe CPV (4 chiffres) : lots, part de lots à offre unique (offres reçues = 1), part de lots sans offre
(offres reçues = 0), part infructueux (résultat clos-nw), montant médian retenu, taille de la population
(nombre total d'avis d'attribution du groupe sur 36 mois) → volume annuel ≈ population / 3.
« Indice de manque d'offres » = part (offre unique + aucune offre) parmi les lots dont le nombre d'offres est connu.
Limite : 12 avis tirés par groupe → intervalle de confiance large (indiqué : borne basse/haute Wilson 90 %).
Usage : python3 -I niches_concurrence.py dossier_details sortie.csv
"""
import csv, gzip, json, math, os, statistics, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eforms_parse import parse

def wilson(k, n, z=1.645):
    if n == 0: return ("", "")
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(100 * max(0, c - h)), round(100 * min(1, c + h)))

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    sel = {n["workspace_id"]: n for n in json.load(open(os.path.join(src, "_selection.json")))}
    pop = json.load(open(os.path.join(src, "_taille_groupes.json")))
    g = collections.defaultdict(list); lib = collections.defaultdict(collections.Counter); nat = {}
    for wid, meta in sel.items():
        p = os.path.join(src, wid + ".json.gz")
        if not os.path.exists(p): continue
        d = json.loads(gzip.open(p).read())
        pubs = [v for v in d.get("versions", []) if v.get("status") == "PUBLISHED" and (v.get("notice") or {}).get("xmlContent")]
        if not pubs: continue
        try: rows = parse(max(pubs, key=lambda v: v.get("version", 0))["notice"]["xmlContent"])
        except Exception: continue
        k = (meta.get("cpv") or "0000")[:4]
        lib[k][meta.get("cpv_fr")] += 1; nat[k] = (meta.get("natures") or ["?"])[0]
        for r in rows:
            r["avis"] = wid; g[k].append(r)
    res = []
    for k, R in g.items():
        off = [r["offres_recues"] for r in R if r["offres_recues"] is not None]
        one = sum(1 for o in off if o == 1); zero = sum(1 for o in off if o == 0)
        clos = sum(1 for r in R if r["resultat"] == "clos-nw")
        am = [r["montant_retenu"] for r in R if r["montant_retenu"]]
        lo, hi = wilson(one + zero, len(off))
        res.append({"nature": nat[k], "cpv4": k, "libelle": lib[k].most_common(1)[0][0], "avis_36m_population": pop.get(k, ""),
                    "avis_par_an": round(pop.get(k, 0) / 3), "avis_echantillon": len({r["avis"] for r in R}), "lots": len(R),
                    "lots_avec_nb_offres": len(off), "offre_unique_%": round(100 * one / len(off)) if off else "",
                    "aucune_offre_%": round(100 * zero / len(off)) if off else "",
                    "indice_manque_offres_%": round(100 * (one + zero) / len(off)) if off else "", "IC90_bas": lo, "IC90_haut": hi,
                    "infructueux_%": round(100 * clos / len(R)) if R else "",
                    "montant_median_EUR": round(statistics.median(am)) if am else "", "n_montants": len(am)})
    res.sort(key=lambda r: -(r["indice_manque_offres_%"] if r["indice_manque_offres_%"] != "" else -1))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0].keys())); w.writeheader(); w.writerows(res)
    print(len(res), "groupes")
