"""Indicateurs par dossier à partir du texte des cahiers des charges + délai de remise des offres.

Délai de remise = date limite de dépôt (« deadline » de l'avis de marché, plateforme BOSA) − date de publication
de l'avis de marché, en jours calendrier. Les autres indicateurs sont des détections de mots-clés (oui/non)
à vérifier à la lecture ; « délai d'exécution » = premier nombre de jours trouvé après « délai d'exécution ».
Usage : python3 csc_indicateurs.py dossier_csc dossier_jsonl_travaux sortie.csv
"""
import csv, datetime as dt, glob, json, os, re, subprocess, sys, time, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bosa_api as b

RX = {
 "visite_obligatoire": r"visite (des lieux )?(est )?obligatoire|obligatoirement visiter|visite préalable obligatoire|attestation de visite",
 "prix_seul": r"(sur la base|sur base) du (seul )?prix\b|critères? d.attribution suivants? ?: ?prix|seul critère.{0,40}prix|unique critère.{0,40}prix",
 "critere_qualite": r"note méthodologique|critère.{0,30}qualit|pondération|planning.{0,40}critère",
 "pas_de_revision_prix": r"ne donne pas lieu à (une )?révision des prix|aucune révision des prix|pas de révision des prix",
 "site_occupe": r"site occupé|bâtiment occupé|logements? occupés?|en activité|hors des heures|en dehors des heures",
 "chiffre_affaires_min": r"chiffre d.affaires (annuel )?(global |spécifique )?(minimum|d.au moins|supérieur|au moins)",
 "references_exigees": r"liste des (principaux )?travaux (exécutés|similaires)|références? (de chantiers|de travaux|similaires)",
 "fonds_europeens_delai": r"\bpnrr\b|\bprr\b|repowereu|feder|facilité pour la reprise|résilience",
 "travaux_hors_horaires_ou_conges": r"congés|week-end|de nuit|vacances",
 "cautionnement_5pct": r"cautionnement.{0,80}5 ?%|5 ?% du montant",
}

def get(path):
    out = subprocess.run(["curl", "-sS", "-m", "90", "-A", "Mozilla/5.0", "-w", "\n%{http_code}", "-H", "Accept: application/json",
                          "-H", f"Authorization: Bearer {b.token()}", "-H", f"BelGov-Trace-Id: {uuid.uuid4()}", b.BASE + "/api/dos" + path],
                         capture_output=True).stdout
    body, code = out.rsplit(b"\n", 1); time.sleep(1.5); return code.decode().strip(), body

if __name__ == "__main__":
    root, jl, out = sys.argv[1:4]
    pubs = {}
    for f in glob.glob(os.path.join(jl, "WORKS_*.jsonl")):
        for l in open(f):
            n = json.loads(l); pubs.setdefault(n.get("workspace_id"), n)
    man = json.load(open(os.path.join(root, "_manifest.json")))
    rows = []
    for m in man:
        text = ""
        for dp, dn, fn in os.walk(os.path.join(root, str(m["dossier_id"]))):
            for f in fn:
                if f.endswith(".txt"): text += open(os.path.join(dp, f), errors="ignore").read() + "\n"
        tl = text.lower()
        r = {k: m[k] for k in ("dossier_id", "type_travaux", "acheteur", "titre", "resultat", "offres_recues", "montant_retenu", "gagnant", "procedure", "agreations")}
        for k, rx in RX.items(): r[k] = "oui" if re.search(rx, tl) else "non"
        me = re.search(r"délai d.exécution[^0-9]{0,120}?(\d{1,4})\s*(jours? ouvrables|jours? calendrier|jours?|mois)", tl)
        r["delai_execution"] = f"{me.group(1)} {me.group(2)}" if me else ""
        code, body = get(f"/dossiers/{m['dossier_id']}/publication-workspaces")
        win = ""
        if code == "200":
            for w in json.loads(body):
                if w.get("formType") != "COMPETITION": continue
                p = pubs.get(w["id"])
                if p and p.get("deadline") and p.get("date"):
                    d1 = dt.date.fromisoformat(p["date"][:10]); d2 = dt.date.fromisoformat(p["deadline"][:10])
                    win = (d2 - d1).days
        r["jours_pour_remettre_offre"] = win
        rows.append(r)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(len(rows))
