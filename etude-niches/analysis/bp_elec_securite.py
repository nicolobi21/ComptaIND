"""Compte d'exploitation type — petite entreprise d'électricité orientée détection incendie / alarme / accès (Hainaut).

DONNÉES MESURÉES (sources dans sources.csv) :
- Ratios de 5 PME électricité gagnantes en Hainaut, dernier exercice (S044, comptes BNB) :
  marge brute (rubrique 9900) par ETP et résultat de l'exercice (9904) en % de la marge brute.
- Montant moyen annuel de marchés publics électricité gagnés par ces PME (S042, 36 mois Wallonie+Bruxelles).
- Marché public « détection incendie, alarme, accès, vidéo » en Hainaut : montant retenu cumulé 6 088 993 € sur
  36 mois (50 lots attribués, 26 gagnants, médiane 30 210 €) (S042).
- Taux horaires observés dans des accords-cadres : 110 et 125 €/h (Farciennes, S042) — repère de prix, non utilisé dans le calcul.
- Frais de dossier de l'autorisation « entreprise de systèmes d'alarme » : 1 000 € (SPF Intérieur, S045).
HYPOTHÈSES (à valider) : taille de l'entreprise (ETP), et le fait qu'une nouvelle entreprise atteigne les ratios
médians des PME existantes (ce qui est optimiste pour une première année).
LIMITE MAJEURE : les PME en schéma abrégé ne publient pas leur chiffre d'affaires ; on raisonne en marge brute.
Usage : python3 -I bp_elec_securite.py
"""
import statistics as st

PAIRS = {  # société : (marge brute 2025 €, ETP 2025, résultat 2025 €, marchés publics électricité gagnés €/an)
    "TSAV": (209428, 3.0, 5030, 54982),
    "IMCE": (2435338, 23.9, 356922, 871606),
    "AEGENTIS": (736933, 10.0, 37604, 218234),
    "AES": (1220325, 22.5, 48578, 255341),
    "D.E.I.": (1606016, 20.3, 227806, 441745),
}
MARCHE_HAINAUT_AN = 6088993 / 3
TAUX_HORAIRES = (110, 125)

mb_etp = sorted(v[0] / v[1] for v in PAIRS.values())
res_mb = sorted(v[2] / v[0] for v in PAIRS.values())
pub_mb = sorted(v[3] / v[0] for v in PAIRS.values())

def q(vals):  # minimum, médiane, maximum
    return vals[0], st.median(vals), vals[-1]

if __name__ == "__main__":
    print("Marge brute par ETP (€) min/médiane/max :", [round(x) for x in q(mb_etp)])
    print("Résultat / marge brute min/médiane/max :", [f"{x:.1%}" for x in q(res_mb)])
    print("Marchés publics gagnés / marge brute (intensité publique) min/médiane/max :", [f"{x:.0%}" for x in q(pub_mb)])
    print(f"Marché public Hainaut détection incendie/alarme/accès : {MARCHE_HAINAUT_AN:,.0f} €/an\n")
    print("Scénario ; ETP ; marge brute = ETP × MB/ETP ; résultat = MB × (résultat/MB) ; marchés publics visés = MB × intensité ; part du marché public Hainaut")
    for nom, i in (("prudent", 0), ("médian", 1), ("favorable", 2)):
        for etp in (2, 3, 5):
            mb = etp * q(mb_etp)[i]
            res = mb * q(res_mb)[i]
            pub = mb * st.median(pub_mb)
            print(f"{nom} ; {etp} ; {etp} × {q(mb_etp)[i]:,.0f} = {mb:,.0f} € ; {mb:,.0f} × {q(res_mb)[i]:.1%} = {res:,.0f} € ; "
                  f"{mb:,.0f} × {st.median(pub_mb):.0%} = {pub:,.0f} € ; {pub / MARCHE_HAINAUT_AN:.1%}")
