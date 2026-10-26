"""Concurrence par catégorie CPV dans les attributions TED (Belgique, 26/10/2023-26/10/2026).

Indicateurs par groupe CPV (4 chiffres) et par nature : nombre d'attributions, part à OFFRE UNIQUE
(received-submissions = 1 sur l'ensemble des valeurs déclarées de l'avis), médiane des offres reçues,
valeur médiane attribuée, part gagnée par des PME. Zone : BE entier et Wallonie+Bruxelles (code postal acheteur).
Limite : TED couvre surtout les marchés au-dessus des seuils européens.
Usage : python3 -I ted_concurrence.py ted_can.json sortie.csv
"""
import csv, json, re, statistics, sys, collections

def zone(n):
    v = [p for p in (n.get("organisation-post-code-buyer") or []) if re.fullmatch(r"\d{4}", str(p))]
    if not v: return "NA"
    p = int(v[0])
    return "WALBXL" if (1000 <= p <= 1499 or 4000 <= p <= 7999) else "VL"

def lab(n):
    t = (n.get("notice-title") or {}).get("fra") or ""
    t = t[0] if isinstance(t, list) else t
    p = t.split(" – "); return p[1] if len(p) > 2 else ""

def num(v):
    v = v[0] if isinstance(v, list) and v else v
    try: return float(v)
    except (TypeError, ValueError): return None

if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    g = collections.defaultdict(list)
    for n in d:
        cpv = (n.get("classification-cpv") or ["0000"])[0][:4]
        nat = (n.get("contract-nature") or ["?"]); nat = nat[0] if isinstance(nat, list) else nat
        g[(nat, cpv)].append(n)
    rows = []
    for (nat, cpv), ns in g.items():
        for z in ("BE", "WALBXL"):
            sel = ns if z == "BE" else [n for n in ns if zone(n) == "WALBXL"]
            subs = [[int(x) for x in (n.get("received-submissions-type-val") or []) if str(x).isdigit()] for n in sel]
            subs = [s for s in subs if s]
            if len(subs) < 5: continue
            single = sum(1 for s in subs if min(s) <= 1)
            vals = [num(n.get("total-value")) for n in sel]; vals = [v for v in vals if v]
            sized = [n for n in sel if n.get("winner-size")]
            sme = sum(1 for n in sized if set(n["winner-size"]) & {"micro", "small", "sme", "medium"})
            rows.append({"nature": nat, "cpv4": cpv, "libelle": collections.Counter(lab(n) for n in sel).most_common(1)[0][0], "zone": z,
                         "attributions": len(sel), "avec_nb_offres": len(subs), "part_au_moins_un_lot_offre_unique_%": round(100 * single / len(subs)),
                         "mediane_offres": statistics.median(statistics.median(s) for s in subs),
                         "valeur_mediane_EUR": round(statistics.median(vals)) if vals else "", "PME_gagnantes": f"{sme}/{len(sized)}"})
    rows.sort(key=lambda r: (r["zone"], -r["part_au_moins_un_lot_offre_unique_%"]))
    with open(sys.argv[2], "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(len(rows), "lignes")
