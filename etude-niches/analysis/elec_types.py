"""Classement des lots « électricité » par type de travaux (règles à mots-clés sur le titre + code CPV).

Règles appliquées DANS L'ORDRE (première règle qui correspond) ; « titre » = intitulé du marché (FR/NL).
Une seconde dimension indépendante signale la FORME du marché : accord-cadre / marché « stock » / entretien.
Limites : classement automatique sur l'intitulé (pas sur le cahier des charges) ; contrôle manuel par
échantillon dans REPORT.md.
Usage : python3 -I elec_types.py lots.csv sortie_dossier
"""
import csv, collections, statistics, sys, os, re

RULES = [
 ("Photovoltaïque", r"photovolt|panneaux? solaire|zonnepan|\bpv\b", r"^45261215"),
 ("Bornes de recharge", r"borne|recharge|laadpal|laadinfra", None),
 ("Haute / moyenne tension, cabines", r"cabine|haute tension|moyenne tension|\bht\b|\bmt\b|middenspanning|hoogspanning|transformateur|poste ht", r"^453154"),
 ("Détection incendie, alarme, accès, vidéo", r"incendie|détection|detection|alarme|intrusion|contrôle d.accès|controle d.acces|vidéo|video|caméra|camera|\bsri\b|branddetectie|toegangscontrole|parlophon", r"^45312"),
 ("Éclairage, relighting, éclairage public/sportif", r"éclairage|eclairage|luminaire|relighting|\bled\b|verlichting|illumination|lumière", r"^45316|^453161"),
 ("Câblage data, télécom, télédistribution", r"câblage|cablage|data|fibre|informatique|télédistribution|telecom|bekabeling", r"^45314"),
 ("Chauffage, PAC, HVAC, cogénération", r"chauffage|pompe.? à chaleur|pompes à chaleur|hvac|ventilation|cogénération|cogeneration|poêle|chaudière|warmtepomp", None),
 ("Signalisation routière/ferroviaire", r"signalisation|feux|seininrichting|signalis", r"^4523"),
 ("Mise en conformité / rénovation d'installation électrique", r"conformit|rénovation (des |de l.|d.)?install|renovation (des |de l.|d.)?install|réhabilitation des installations électriques|rehabilitation des installations electriques|remise en état.*électri|rénovations? électrique|renovations? electrique|normes pics|installation électrique|installations électriques|elektrische install", r"^453112"),
 ("Lot électricité d'un chantier de bâtiment", r"électricité|electricite|electricité|elektriciteit|lot.*électri|construction|rénovation|renovation|aménagement|amenagement|transformation|extension|école|ecole|logements?|crèche|creche|bâtiment|batiment", r"^45000|^4521|^453|^454"),
]
FORME = r"stock|accord.cadre|raamovereenkomst|dépannage|depannage|maintenance|entretien|marché à bordereau|bons de commande"

def classe(r):
    t = (r.get("titre") or "").lower(); cpv = r.get("cpv") or ""
    for name, kw, cp in RULES:
        if re.search(kw, t) or (cp and re.search(cp, cpv)):
            return name
    return "Autre / non classé"

def f(x):
    try: return float(x)
    except (TypeError, ValueError): return None

def stats(R):
    won = [r for r in R if r["resultat"] == "selec-w"]
    off = [f(r["offres_recues"]) for r in won if f(r["offres_recues"]) is not None]
    am = [f(r["montant_retenu"]) for r in won if f(r["montant_retenu"])]
    clos = sum(1 for r in R if r["resultat"] == "clos-nw")
    gag = {g.strip().upper() for r in won for g in (r["gagnant"] or "").split(" | ") if g.strip()}
    return {"lots": len(R), "attribues": len(won), "infructueux_%": round(100 * clos / len(R)) if R else "",
            "montant_median_EUR": round(statistics.median(am)) if am else "", "n_montants": len(am),
            "offres_mediane": statistics.median(off) if off else "",
            "offre_unique_%": round(100 * sum(1 for o in off if o == 1) / len(off)) if off else "",
            "gagnants_distincts": len(gag),
            "part_accord_cadre_stock_%": round(100 * sum(1 for r in R if re.search(FORME, (r.get("titre") or "").lower())) / len(R)) if R else ""}

if __name__ == "__main__":
    rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
    out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    for r in rows: r["type_travaux"] = classe(r)
    with open(os.path.join(out, "lots_classes.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    for zone, pref in (("WALBXL", ("BE1", "BE3")), ("HAINAUT", ("BE32",)), ("CHARLEROI", ("BE32B",))):
        Z = [r for r in rows if any(c.startswith(pref) for c in r["nuts"].split())]
        g = collections.defaultdict(list)
        for r in Z: g[r["type_travaux"]].append(r)
        with open(os.path.join(out, f"types_{zone}.csv"), "w", newline="", encoding="utf-8") as fo:
            keys = ["type_travaux", "part_lots_%"] + list(stats(Z).keys())
            w = csv.DictWriter(fo, fieldnames=keys); w.writeheader()
            for k, R in sorted(g.items(), key=lambda kv: -len(kv[1])):
                s = stats(R); s.update({"type_travaux": k, "part_lots_%": round(100 * len(R) / len(Z))}); w.writerow(s)
        print(f"\n== {zone} ({len(Z)} lots)")
        print(open(os.path.join(out, f"types_{zone}.csv")).read())
