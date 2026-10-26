"""Phase 2 — Notation des 10 pistes B2B (Belgique francophone, base Charleroi).

POIDS (fixés par le cahier des charges, arbitraires) :
  demande 25 %, tendance 15 %, concurrence 15 %, marge 20 %, réglementaire/logistique 10 %, adéquation 15 %
Score pondéré = somme(note_critère × poids_critère), notes de 1 à 5.

ÉCHELLES (définies AVANT la notation) :
- demande : 5 = achats mesurés nombreux et directement liés ; 4 = achats mesurés nombreux (parc installé
  ou ≥ 30 attributions pertinentes estimées en Wallonie+Bruxelles sur 3 ans) ; 3 = obligation légale
  vérifiée sans preuve d'achat, ou 10-29 attributions estimées ; 2 = < 10 attributions estimées ; 1 = rien.
  « attributions estimées » = attributions TED Wallonie+Bruxelles (3 ans) × précision mesurée sur un
  échantillon de 6 avis (analysis/ted_fulltext_pistes.csv, contrôle du 26/10/2026).
- tendance : avis TED (marché + attribution) Wallonie+Bruxelles A1 → A3 ; 4-5 = hausse ou obligation à venir
  vérifiée ; 3 = stable ou inconnu ; 1-2 = baisse.
- concurrence (5 = faible) : médiane du nombre d'offres reçues par marché attribué (TED) ; ≤2 → 4, 3 → 3,
  ≥5 → 2 ; abaissée d'un point si des vendeurs en ligne à bas prix existent (Phase 1, S012). Concurrents
  privés locaux NON mesurés.
- marge : HYPOTHÈSE (aucun prix de gros public accessible : Alibaba vide, devis nécessaires) ; 4 = forte part
  de service facturable et faible transparence des prix ; 2 = produit standard au prix comparé en ligne.
- réglementaire/logistique (5 = simple) : d'après les textes S015-S023, S029.
- adéquation (HYPOTHÈSE motivée) : composante informatique, démonstration possible, service, compatibilité
  avec voiture + 10 000 € de budget.
"""
import csv, itertools, sys

W = {"demande": .25, "tendance": .15, "concurrence": .15, "marge": .20, "reglem": .10, "adequation": .15}

P = [
 # id, piste, notes{...}, justifications{...}, statut
 ("QAI", "Qualité de l'air intérieur : CO2-mètres + purificateurs + mise en place",
  dict(demande=3, tendance=4, concurrence=3, marge=4, reglem=3, adequation=5),
  dict(demande="OBLIGATION vérifiée, progressive dès le 01/01/2027 (S028) ; aucune attribution TED pertinente (0/4 avis contrôlés) → aucune preuve d'achat",
       tendance="Obligation qui démarre en 2027 et s'étend jusqu'à fin 2037 (S028) ; avis de marché WAL/BXL 3→0→6 (non pertinents)",
       concurrence="Je ne sais pas (aucune attribution TED pertinente) → note neutre",
       marge="HYPOTHÈSE : forte part de service (installation, tableau de bord, suivi) ; prix de gros inconnus",
       reglem="EEE : distributeur si achat en Belgique (S015) ; exigences belges pour CO2-mètres (S029) ; appareils légers",
       adequation="HYPOTHÈSE : capteurs connectés et tableaux de bord (IT), démonstration facile, matériel compact, budget suffisant"),
  "À TESTER (pas de preuve d'achat)"),
 ("CAISSES", "Systèmes de caisse pour l'horeca (revente + installation)",
  dict(demande=4, tendance=3, concurrence=3, marge=3, reglem=2, adequation=4),
  dict(demande="Parc installé : 32 417 établissements en 2023 (S031) = achats effectifs ; donnée de plus de 24 mois (potentiellement obsolète)",
       tendance="+6,7 % de 2022 à 2023 ((32 417 − 30 376) ÷ 30 376, S031) ; TED WAL/BXL 4→0→5 (peu significatif) ; « version 2.0 » au 01/07/2026 selon source secondaire",
       concurrence="Médiane de 3 offres par marché attribué (TED, 10 attributions BE) ; éditeurs établis non mesurés",
       marge="HYPOTHÈSE : commission de revendeur et installation ; conditions des éditeurs inconnues",
       reglem="Système certifié requis (source secondaire) ; matériel fiscal sensible ; EEE",
       adequation="HYPOTHÈSE : IT et démonstration ; dépend d'un partenariat avec un éditeur certifié"),
  "GARDÉE"),
 ("ECRANS", "Écrans interactifs et affichage dynamique (écoles, commerces, salles de réunion)",
  dict(demande=2, tendance=2, concurrence=2, marge=3, reglem=2, adequation=4),
  dict(demande="12 attributions WAL/BXL en 3 ans × précision 4/6 ≈ 8 (TED)",
       tendance="Avis WAL/BXL (marché + attribution) 23 → 16 → 5 : baisse",
       concurrence="Médiane de 5 offres par marché attribué (TED)",
       marge="HYPOTHÈSE : matériel au prix comparable en ligne ; installation facturable",
       reglem="EEE ; écrans grands formats lourds et fragiles",
       adequation="HYPOTHÈSE : IT, démonstration ; transport d'un écran de démonstration en voiture à vérifier"),
  "GARDÉE"),
 ("WIFI", "Réseaux Wi-Fi pour PME (matériel + installation)",
  dict(demande=2, tendance=3, concurrence=3, marge=4, reglem=3, adequation=4),
  dict(demande="Recherche plein texte inutilisable (0/6 avis pertinents) ; CPV 32571 : 9 avis WAL/BXL en 24 mois, dont 8 gagnés par des PME (S032)",
       tendance="Je ne sais pas → note neutre",
       concurrence="Je ne sais pas (aucune médiane fiable) → note neutre",
       marge="HYPOTHÈSE : surtout du service",
       reglem="EEE de petite taille ; règles d'installation : je ne sais pas",
       adequation="HYPOTHÈSE : très forte composante IT, mais peu de « produit physique »"),
  "GARDÉE"),
 ("VETEMENTS", "Vêtements professionnels personnalisés",
  dict(demande=4, tendance=3, concurrence=3, marge=3, reglem=3, adequation=2),
  dict(demande="83 attributions WAL/BXL en 3 ans × précision 3/6 ≈ 41 (TED)",
       tendance="Avis WAL/BXL 96 → 140 → 104 : stable",
       concurrence="Médiane de 2 offres (→4) moins 1 : vêtements de travail vendus en ligne (non mesuré précisément)",
       marge="HYPOTHÈSE : la personnalisation ajoute de la valeur ; textile au prix comparé en ligne",
       reglem="Étiquetage des fibres (S023) ; EPI si protection revendiquée (S017)",
       adequation="HYPOTHÈSE : aucun avantage IT ; voiture utile pour les essayages"),
  "GARDÉE"),
 ("FONTAINES", "Fontaines à eau pour entreprises (vente/location + entretien)",
  dict(demande=2, tendance=3, concurrence=3, marge=3, reglem=2, adequation=2),
  dict(demande="12 attributions WAL/BXL × précision 3/6 ≈ 6 (TED)",
       tendance="Avis WAL/BXL 18 → 20 → 18 : stable",
       concurrence="Médiane de 2 offres (→4) moins 1 : acteurs nationaux non mesurés",
       marge="HYPOTHÈSE : revenu récurrent (filtres, entretien) ; inconnue",
       reglem="Contact alimentaire (S021), hygiène, raccordement",
       adequation="HYPOTHÈSE : pas d'avantage IT"),
  "GARDÉE"),
 ("CUISINE", "Petit équipement de cuisine professionnelle",
  dict(demande=3, tendance=4, concurrence=3, marge=2, reglem=1, adequation=1),
  dict(demande="33 attributions WAL/BXL × précision 4/6 ≈ 22 (TED)",
       tendance="Avis WAL/BXL 36 → 48 → 57 : hausse",
       concurrence="Médiane de 3 offres (TED)",
       marge="HYPOTHÈSE : prix comparés en ligne, matériel lourd",
       reglem="Contact alimentaire (S021), poids, raccordements",
       adequation="HYPOTHÈSE : aucun avantage IT, logistique lourde"),
  "GARDÉE"),
 ("MOBILIER", "Mobilier de bureau ergonomique",
  dict(demande=2, tendance=3, concurrence=2, marge=2, reglem=2, adequation=2),
  dict(demande="6 attributions WAL/BXL × précision 5/6 ≈ 5 ; CPV 39130 : 9 avis en 24 mois (S032)",
       tendance="Avis WAL/BXL 2 → 5 → 4 : effectifs trop faibles",
       concurrence="Médiane de 6 offres (TED)",
       marge="HYPOTHÈSE : prix comparés en ligne, livraison coûteuse",
       reglem="Lourd et volumineux",
       adequation="HYPOTHÈSE : pas d'avantage IT"),
  "GARDÉE"),
 ("LED", "Éclairage LED professionnel",
  dict(demande=2, tendance=2, concurrence=3, marge=3, reglem=2, adequation=2),
  dict(demande="15 attributions WAL/BXL × précision 2/6 ≈ 5 (TED)",
       tendance="Avis WAL/BXL 26 → 13 → 6 : baisse",
       concurrence="Médiane de 3 offres (TED)",
       marge="HYPOTHÈSE : composants bon marché en ligne ; pose facturable",
       reglem="Installation électrique : règles de qualification non vérifiées",
       adequation="HYPOTHÈSE : pas d'avantage IT"),
  "GARDÉE"),
 ("SECOURS", "Boîtes de secours et recharges pour employeurs",
  dict(demande=3, tendance=3, concurrence=2, marge=2, reglem=4, adequation=2),
  dict(demande="OBLIGATION en vigueur pour tout employeur (S030) ; 4 attributions WAL/BXL × précision 3/6 ≈ 2",
       tendance="Avis WAL/BXL 1 → 5 → 3 : stable",
       concurrence="Médiane de 3 offres (→3) moins 1 : trousses vendues en ligne (Phase 1, S012)",
       marge="HYPOTHÈSE : petit ticket, prix comparés en ligne",
       reglem="Kits finis achetés chez un distributeur ; médicaments déconseillés (S030)",
       adequation="HYPOTHÈSE : pas d'avantage IT ; petit ticket"),
  "GARDÉE"),
]

def score(n, w):
    return sum(n[k] * w[k] for k in w)

def ranking(w):
    return [p[0] for p in sorted(P, key=lambda p: -score(p[2], w))]

if __name__ == "__main__":
    out = sys.argv[1]
    with open(out, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        hdr = ["rang", "id", "piste", "score_pondere", "calcul"]
        for k in W: hdr += [k + "_1a5", k + "_justification"]
        wr.writerow(hdr + ["statut"])
        for i, p in enumerate(sorted(P, key=lambda p: -score(p[2], W)), 1):
            calc = " + ".join(f"{p[2][k]}×{W[k]:.2f}" for k in W)
            row = [i, p[0], p[1], f"{score(p[2], W):.2f}", calc]
            for k in W: row += [p[2][k], p[3][k]]
            wr.writerow(row + [p[4]])
    base = ranking(W)[:3]
    print("Classement de base :", [(pid, round(score(next(p for p in P if p[0]==pid)[2], W), 2)) for pid in ranking(W)])
    print("Top 3 de base :", base)
    # Sensibilité : chaque poids ×0,8 puis ×1,2, les autres renormalisés pour garder une somme de 1
    changes = []
    for k in W:
        for f in (0.8, 1.2):
            w2 = dict(W); w2[k] = W[k] * f
            s = sum(w2.values()); w2 = {a: b / s for a, b in w2.items()}
            top = ranking(w2)[:3]
            flag = "" if top == base else "  <-- CHANGE"
            print(f"{k} ×{f}: top3 = {top}{flag}")
            if top != base: changes.append((k, f, top))
    print("Nombre de scénarios où le top 3 change :", len(changes), "sur", 2 * len(W))

def scenarios_hypotheses():
    """Robustesse aux notes HYPOTHÈSE : (a) marge neutralisée à 3 pour tous ;
    (b) seuls les critères mesurés (demande, tendance, concurrence, réglementaire), poids renormalisés."""
    import copy
    saved = copy.deepcopy(P)
    for p in P: p[2]["marge"] = 3
    a = [(p[0], round(score(p[2], W), 2)) for p in sorted(P, key=lambda p: -score(p[2], W))][:4]
    P[:] = saved
    wm = {k: W[k] for k in ("demande", "tendance", "concurrence", "reglem")}
    s = sum(wm.values()); wm = {k: v / s for k, v in wm.items()}
    b = [(p[0], round(score(p[2], wm), 2)) for p in sorted(P, key=lambda p: -score(p[2], wm))][:4]
    print("(a) marge neutralisée à 3 :", a)
    print("(b) critères mesurés seulement :", b)

if __name__ == "__main__":
    scenarios_hypotheses()
