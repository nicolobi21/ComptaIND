"""Manque d'offres dans les 4 niches candidates (détails téléchargés par niches_details.py).

Par niche et par mode de procédure (code national : « publiée » = OPEN, RESTRICTED, *_W_CALL_* → tout le monde peut
remettre offre ; « sans publication » = *_WO_CALL_* → seules les firmes invitées remettent offre ; autres codes
(LOW_VALUE_T, SUIGEN_*) = « autre ») :
lots, part de lots à 0 offre, à 1 offre, indice de manque d'offres (0 ou 1 offre) avec IC Wilson 90 %,
part de lots infructueux (clos-nw), montant médian retenu, gagnants distincts, gagnants les plus fréquents.
Valeur annuelle ESTIMÉE = (somme des montants retenus de l'échantillon / avis de l'échantillon ayant un montant)
× avis d'attribution de la population par an. Les montants d'accords-cadres sont des maxima ou des estimations.
Usage : python3 -I niches_analyse.py dossier_details prefixe_pop dossier_sortie
"""
import collections, csv, gzip, json, os, re, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eforms_parse import parse
from niches_concurrence import wilson
from niches_population import AWARD

def sous_niche(k, titre):  # N4 : l'impression demande une presse ou de la sous-traitance, la conception non
    if not k.startswith("N4"): return ""
    return "N4a_impression" if re.search(r"impression|imprim|routage|\bdruk", (titre or "").lower()) else "N4b_conception_graphique"

def mode(proc):  # code national de procédure publicprocurement.be (champ « procedure » de la recherche)
    proc = proc or ""
    if "WO_CALL" in proc: return "sans publication"
    if "W_CALL" in proc or proc in ("OPEN", "RESTRICTED"): return "publiée"
    return "autre/inconnue"

if __name__ == "__main__":
    src, pref, dst = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(dst, exist_ok=True)
    sel = json.load(open(os.path.join(src, "_selection.json")))
    lots, avis_mt = [], collections.defaultdict(lambda: [0, 0.0])
    for k, notices in sel.items():
        for meta in notices:
            p = os.path.join(src, meta["workspace_id"] + ".json.gz")
            if not os.path.exists(p): continue
            d = json.loads(gzip.open(p).read())
            pubs = [v for v in d.get("versions", []) if v.get("status") == "PUBLISHED" and (v.get("notice") or {}).get("xmlContent")]
            if not pubs: continue
            try: rows = parse(max(pubs, key=lambda v: v.get("version", 0))["notice"]["xmlContent"])
            except Exception: continue
            mts = [r["montant_retenu"] for r in rows if r["montant_retenu"]]
            if mts: avis_mt[k][0] += 1; avis_mt[k][1] += sum(mts)
            for r in rows:
                r.update({"niche": k, "workspace_id": meta["workspace_id"], "date": meta.get("date"), "acheteur": meta.get("org"),
                          "hainaut": any(c.startswith("BE32") for c in meta.get("nuts") or []), "mode": mode(meta.get("procedure")),
                          "titre_avis": meta.get("titre"), "sous_niche": sous_niche(k, meta.get("titre")), "procedure_nationale": meta.get("procedure")})
                lots.append(r)
    fields = ["niche", "sous_niche", "mode", "workspace_id", "date", "acheteur", "hainaut", "titre_avis", "lot", "resultat", "offres_recues",
              "montant_retenu", "offre_basse", "offre_haute", "gagnant", "gagnant_cp", "gagnant_taille", "procedure", "procedure_nationale", "cpv"]
    with open(os.path.join(dst, "niches_lots.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(lots)
    pop_aw = {k: sum(1 for n in json.load(open(f"{pref}_{k}.json")) if n["subtype"] in AWARD) for k in sel}
    out = []
    groupes = [(k, m) for k in sel for m in ["toutes", "publiée", "sans publication"]]
    groupes += [(sn, "toutes") for sn in sorted({r["sous_niche"] for r in lots if r["sous_niche"]})]
    for k, m in groupes:
            R = [r for r in lots if (r["niche"] == k or r["sous_niche"] == k) and (m == "toutes" or r["mode"] == m)]
            off = [r["offres_recues"] for r in R if r["offres_recues"] is not None]
            z, u = sum(1 for o in off if o == 0), sum(1 for o in off if o == 1)
            lo, hi = wilson(z + u, len(off))
            mt = [r["montant_retenu"] for r in R if r["montant_retenu"]]
            gw = collections.Counter(r["gagnant"] for r in R if r["gagnant"])
            row = {"niche": k, "mode": m, "lots": len(R), "lots_offres_connues": len(off),
                   "pct_0_offre": round(100 * z / len(off)) if off else "", "pct_1_offre": round(100 * u / len(off)) if off else "",
                   "indice_manque_offres_pct": round(100 * (z + u) / len(off)) if off else "", "ic90_bas": lo, "ic90_haut": hi,
                   "offres_mediane": statistics.median(off) if off else "",
                   "pct_infructueux": round(100 * sum(1 for r in R if r["resultat"] == "clos-nw") / len(R)) if R else "",
                   "montant_median_eur": round(statistics.median(mt)) if mt else "", "lots_avec_montant": len(mt),
                   "pct_lots_hainaut": round(100 * sum(1 for r in R if r["hainaut"]) / len(R)) if R else "",
                   "gagnants_distincts": len(gw), "top_gagnants": " ; ".join(f"{g} ({c})" for g, c in gw.most_common(5))}
            if m == "toutes" and k in sel:
                a, s = avis_mt[k]
                row["attributions_population_par_an"] = round(pop_aw[k] / 3)
                row["valeur_annuelle_estimee_eur"] = round(s / a * pop_aw[k] / 3) if a else ""
            out.append(row)
    keys = list(out[0].keys())
    with open(os.path.join(dst, "niches_indicateurs.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(out)
    for r in out: print({k: v for k, v in r.items() if k != "top_gagnants"}); print("   ", r["top_gagnants"][:300])
