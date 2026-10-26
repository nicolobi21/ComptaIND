"""Extraction d'extraits de clauses des cahiers des charges (texte) pour lecture humaine.
Pour chaque dossier et chaque thème, on garde les 2 premiers extraits (±220 caractères) trouvés.
Usage : python3 -I csc_extract.py dossier_csc sortie.md
"""
import json, os, re, sys

THEMES = {
 "Délai d'exécution": r"délai d.exécution|delai d.execution|jours ouvrables|jours calendrier",
 "Remise des offres": r"date limite|remise des offres|dépôt des offres|ouverture des offres|au plus tard le",
 "Visite": r"visite (obligatoire|des lieux|préalable)|attestation de visite",
 "Agréation": r"agréation|catégorie [a-z] ?\d|classe \d",
 "Critères d'attribution": r"critères? d.attribution|offre (économiquement )?la plus avantageuse|prix (le plus bas|seul)|pondération",
 "Sélection qualitative": r"chiffre d.affaires|références? (similaires|de chantiers|de travaux)|capacité (technique|financière|économique)",
 "Cautionnement": r"cautionnement",
 "Pénalités / amendes": r"amende(s)? pour retard|pénalit",
 "Révision des prix": r"révision des prix|revision des prix|formule de révision",
 "Délai de paiement": r"délai de paiement|payé dans un délai|paiement.{0,40}jours",
 "Site occupé / horaires": r"site occupé|en activité|bâtiment occupé|logements? occupés?|hors des heures|en dehors des heures|week-end",
 "Montant estimé": r"montant estimé|estimation du marché|valeur estimée",
 "Sous-traitance": r"sous-traitan",
}

def snip(t, m):
    a, b = max(0, m.start() - 220), min(len(t), m.end() + 220)
    return re.sub(r"\s+", " ", t[a:b]).strip()

if __name__ == "__main__":
    root, out = sys.argv[1], sys.argv[2]
    man = {str(m["dossier_id"]): m for m in json.load(open(os.path.join(root, "_manifest.json")))}
    lines = ["# Extraits de cahiers des charges — lots électricité à offre unique ou sans offre\n"]
    for did, m in man.items():
        texts = []
        for dp, dn, fn in os.walk(os.path.join(root, did)):
            for f in sorted(fn):
                if f.endswith(".txt"):
                    texts.append((f, open(os.path.join(dp, f), errors="ignore").read()))
        lines.append(f"\n## Dossier {did} — {m['titre']}\nAcheteur : {m['acheteur']} ; type : {m['type_travaux']} ; attribution {m['date_attribution']} ; "
                     f"résultat {m['resultat']} ; offres reçues {m['offres_recues']} ; montant {m['montant_retenu']} ; estimation {m['estimation_lot']} ; "
                     f"gagnant {m['gagnant']} ; procédure {m['procedure']} ; agréations {m['agreations']} ; fichiers {len(m['fichiers'])}")
        for th, rx in THEMES.items():
            found = []
            for f, t in texts:
                for mt in re.finditer(rx, t, re.I):
                    found.append(f"[{f[:40]}] " + snip(t, mt))
                    if len(found) >= 2: break
                if len(found) >= 2: break
            lines.append(f"- **{th}** : " + (" ‖ ".join(found) if found else "non trouvé"))
    open(out, "w").write("\n".join(lines))
    print(len(man), "dossiers")
