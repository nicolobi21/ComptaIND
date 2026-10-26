"""Indicateurs de concurrence par page « Meilleures ventes » Amazon.

Formules (montrées pour chaque page) :
- n_eval_total = somme des « évaluations » des produits classés (30 max)
- part_top3 = (évaluations des 3 produits les plus évalués) / n_eval_total
- n_sous_100 = nombre de produits classés ayant moins de 100 évaluations
  (indice, pas preuve, que des fiches récentes ou peu notées vendent assez
  pour entrer dans le classement)
- prix_median = médiane des prix affichés (adresse de livraison US : ordre de
  grandeur seulement, cf. amazon_bs.py)
Limites : les évaluations cumulent plusieurs années et parfois plusieurs
variantes ; ce sont des indicateurs relatifs, pas des volumes de ventes.
Usage : python3 -I concentration.py fichier1.csv [fichier2.csv ...]
"""
import csv
import statistics
import sys
from collections import OrderedDict

pages = OrderedDict()
for f in sys.argv[1:]:
    for r in csv.DictReader(open(f, encoding="utf-8")):
        pages.setdefault(r["fichier"], []).append(r)

print("page;n_produits;n_eval_total;part_top3;n_sous_100;prix_median")
for p, rs in pages.items():
    ev = sorted([int(r["nb_evaluations"]) for r in rs if r["nb_evaluations"]], reverse=True)
    tot = sum(ev)
    top3 = sum(ev[:3])
    sous100 = sum(1 for r in rs if not r["nb_evaluations"] or int(r["nb_evaluations"]) < 100)
    prix = [float(r["prix_affiche_eur"]) for r in rs if r["prix_affiche_eur"]]
    med = statistics.median(prix) if prix else ""
    name = p.replace("www_amazon_fr_gp_bestsellers_", "").replace(".html.gz", "")
    print(f"{name};{len(rs)};{tot};{top3/tot:.2f} ({top3}/{tot});{sous100};{med}")
