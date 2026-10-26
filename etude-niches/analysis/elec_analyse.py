"""Analyse des attributions « électricité » (Wallonie + Bruxelles, 26/10/2023-25/10/2026).

Entrée : CSV produit par eforms_parse.py (une ligne par lot). Définitions :
- lot attribué = résultat « selec-w » ; infructueux = « clos-nw » (aucun gagnant) ; « open-nw » = encore ouvert.
- montant = « montant_retenu » (montant de l'offre gagnante, gardé seulement s'il est compris entre l'offre
  basse et l'offre haute du lot) ; tranches de montant purement descriptives (sans valeur juridique).
- zone = codes NUTS de la publication : HAINAUT = BE32*, CHARLEROI = BE32B, WAL = BE3*, BXL = BE1*.
- gagnant « local Hainaut » = code postal du gagnant 6000-6599 ou 7000-7999.
Usage : python3 -I elec_analyse.py lots.csv dossier_sortie
"""
import csv, collections, statistics, sys, os

def f(x):
    try: return float(x)
    except (TypeError, ValueError): return None

def zone_ok(r, z):
    n = r["nuts"].split()
    return {"TOUT": True, "WAL": any(c.startswith("BE3") for c in n), "BXL": any(c.startswith("BE1") for c in n),
            "HAINAUT": any(c.startswith("BE32") for c in n), "CHARLEROI": any(c.startswith("BE32B") for c in n)}[z]

BANDS = [(0, 30000, "< 30 k€"), (30000, 143000, "30-143 k€"), (143000, 750000, "143-750 k€"), (750000, 1e12, "> 750 k€")]
def band(m):
    for a, b, l in BANDS:
        if a <= m < b: return l

def hainaut_cp(cp):
    try: p = int((cp or "").split("|")[0].strip()[:4])
    except ValueError: return None
    return 6000 <= p <= 6599 or 7000 <= p <= 7999

if __name__ == "__main__":
    rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
    out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    rep = []
    for z in ("TOUT", "WAL", "BXL", "HAINAUT", "CHARLEROI"):
        R = [r for r in rows if zone_ok(r, z)]
        if not R: continue
        res = collections.Counter(r["resultat"] for r in R)
        won = [r for r in R if r["resultat"] == "selec-w"]
        offers = [f(r["offres_recues"]) for r in won if f(r["offres_recues"]) is not None]
        amts = [f(r["montant_retenu"]) for r in won if f(r["montant_retenu"])]
        spread = [(f(r["offre_haute"]) - f(r["offre_basse"])) / f(r["offre_basse"]) for r in won
                  if f(r["offre_basse"]) and f(r["offre_haute"]) and f(r["offres_recues"]) and f(r["offres_recues"]) >= 2]
        ratio = [f(r["montant_retenu"]) / f(r["estimation_lot"]) for r in won if f(r["montant_retenu"]) and f(r["estimation_lot"])]
        rep.append(f"\n## Zone {z}")
        rep.append(f"Lots : {len(R)} ; résultats : {dict(res)} ; part infructueux (clos-nw) = {res['clos-nw']}/{len(R)} = {res['clos-nw']/len(R):.0%}")
        if offers:
            c = collections.Counter("1" if o == 1 else "2" if o == 2 else "3-4" if o <= 4 else "5+" if o >= 5 else "0" for o in offers)
            rep.append(f"Offres reçues (lots attribués, n={len(offers)}) : médiane {statistics.median(offers)} ; répartition {dict(sorted(c.items()))} ; offre unique = {c['1']/len(offers):.0%}")
        if amts:
            q = statistics.quantiles(amts, n=4)
            rep.append(f"Montant retenu (n={len(amts)}) : médiane {statistics.median(amts):,.0f} € ; Q1 {q[0]:,.0f} € ; Q3 {q[2]:,.0f} € ; total {sum(amts):,.0f} €")
            bc = collections.Counter(band(a) for a in amts)
            rep.append("Tranches : " + " ; ".join(f"{l} {bc[l]} ({bc[l]/len(amts):.0%})" for _, _, l in BANDS))
            for _, _, l in BANDS:
                o = [f(r["offres_recues"]) for r in won if f(r["montant_retenu"]) and band(f(r["montant_retenu"])) == l and f(r["offres_recues"]) is not None]
                if o: rep.append(f"  {l} : offres reçues médiane {statistics.median(o)} (n={len(o)}), offre unique {sum(1 for x in o if x == 1)/len(o):.0%}")
        if spread: rep.append(f"Écart offre haute / offre basse (lots ≥ 2 offres, n={len(spread)}) : médiane {statistics.median(spread):.0%}")
        if ratio: rep.append(f"Montant attribué / estimation (n={len(ratio)}) : médiane {statistics.median(ratio):.2f}")
        winners = collections.Counter(); wsum = collections.Counter(); wcp = {}
        for r in won:
            if r["gagnant"]:
                for g in r["gagnant"].split(" | "):
                    k = g.strip().upper(); winners[k] += 1; wsum[k] += f(r["montant_retenu"]) or 0; wcp.setdefault(k, r["gagnant_cp"])
        ident = sum(1 for r in won if r["gagnant"])
        rep.append(f"Gagnant identifié : {ident}/{len(won)} lots ; gagnants distincts : {len(winners)}")
        if winners:
            top10 = sum(c for _, c in winners.most_common(10))
            rep.append(f"Part des 10 premiers gagnants dans les lots identifiés : {top10/sum(winners.values()):.0%}")
            loc = [hainaut_cp(r["gagnant_cp"]) for r in won if r["gagnant_cp"]]
            loc = [x for x in loc if x is not None]
            if loc: rep.append(f"Gagnants avec code postal en Hainaut : {sum(loc)}/{len(loc)} = {sum(loc)/len(loc):.0%}")
            with open(os.path.join(out, f"gagnants_{z}.csv"), "w", newline="", encoding="utf-8") as fo:
                w = csv.writer(fo); w.writerow(["gagnant (nom tel que saisi)", "lots_gagnes", "montant_retenu_cumule_EUR", "code_postal"])
                for k, c in winners.most_common(): w.writerow([k, c, round(wsum[k]), wcp.get(k)])
        sizes = collections.Counter(r["gagnant_taille"] for r in won if r["gagnant_taille"])
        if sizes: rep.append(f"Taille déclarée des gagnants : {dict(sizes)} (n={sum(sizes.values())})")
        buyers = collections.Counter(r["acheteur"] for r in R).most_common(8)
        rep.append("Acheteurs principaux : " + " ; ".join(f"{b} {c}" for b, c in buyers))
    open(os.path.join(out, "synthese.txt"), "w").write("\n".join(rep))
    print("\n".join(rep))
