"""Comptes annuels publics (Centrale des bilans de la BNB, consult.cbso.nbb.be) des gagnants récurrents.

Pour chaque n° d'entreprise : les 3 derniers dépôts (tri par exercice décroissant), PDF officiel, puis
extraction des rubriques normalisées (exercice N et N-1 tels qu'affichés) :
20/58 total actif ; 10/15 capitaux propres ; 42/48 dettes à un an au plus ; 70 chiffre d'affaires
(souvent absent des schémas abrégés/micro) ; 9900 marge brute ; 9901 résultat d'exploitation ;
9904 résultat de l'exercice ; effectif moyen (rubrique 9087 ou ligne 100 « nombre moyen de travailleurs »).
Politesse : 2 s entre requêtes. Usage : python3 -I nbb_bilans.py entreprises.json dossier_pdf sortie.csv
"""
import csv, json, os, re, subprocess, sys, time

API = "https://consult.cbso.nbb.be/api"
CODES = {"total_actif": r"20/58", "capitaux_propres": r"10/15", "dettes_1an": r"42/48", "chiffre_affaires": r"70",
         "marge_brute": r"9900", "resultat_exploitation": r"9901", "resultat_exercice": r"9904"}

def curl(url, out=None):
    # PDF : pas d'en-tête Accept (le serveur répond 406 si on demande application/pdf ou json)
    args = ["curl", "-sS", "-m", "90", "-A", "Mozilla/5.0"] + ([] if out else ["-H", "Accept: application/json"]) + [url]
    if out: args[1:1] = ["-o", out]
    r = subprocess.run(args, capture_output=True); time.sleep(2)
    return r.stdout

def num(s):
    s = s.strip()
    neg = s.startswith("-") or s.startswith("(")
    s = re.sub(r"[^\d]", "", s)
    return (-int(s) if neg else int(s)) if s else None

def extract(txt):
    res = {}
    for k, code in CODES.items():
        m = re.search(rf"(?m)^.*?\s{code}\s+(-?[\d.]+)(?:\s+(-?[\d.]+))?\s*$", txt)
        res[k] = num(m.group(1)) if m else None
    # priorité : rubrique 9087 (ETP) ; sinon ligne 100, 3e colonne = total en ETP (temps plein, temps partiel, total)
    m = re.search(r"(?m)^.*\s9087\s+([\d,.]+)", txt)
    if m: etp = m.group(1)
    else:
        m = re.search(r"(?m)^\s*Nombre moyen de travailleurs\s+100\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)", txt)
        etp = m.group(3) if m else None
    res["effectif_moyen_ETP"] = etp.replace(",", ".") if etp else None
    return res

if __name__ == "__main__":
    ents, pdfdir, out = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3]
    os.makedirs(pdfdir, exist_ok=True); rows = []
    for e in ents:
        lst = json.loads(curl(f"{API}/rs-consult/published-deposits?page=0&size=10&enterpriseNumber={e['bce']}&sort=periodEndDateYear,desc") or b"{}")
        # un dépôt par exercice (le plus récemment modifié, ex. dépôt rectificatif), 3 derniers exercices
        best = {}
        for d in lst.get("content", []):
            k = d.get("periodEndDate", "")
            if k not in best or d.get("modificationDate", "") > best[k].get("modificationDate", ""): best[k] = d
        deps = [best[k] for k in sorted(best, reverse=True)[:3]]
        for d in deps:
            pdf = os.path.join(pdfdir, f"{e['bce']}_{d['periodEndDate'][:10]}.pdf")
            if not os.path.exists(pdf) or open(pdf, "rb").read(4) != b"%PDF":
                curl(f"{API}/external/broker/public/deposits/pdf/{d['id']}", pdf)
            txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
            r = {"nom_marche": e["nom"], "bce": e["bce"], "denomination_bnb": d.get("enterpriseName"), "exercice_fin": d["periodEndDate"][:10],
                 "modele": d.get("modelName"), "reference_depot": d.get("reference")}
            r.update(extract(txt)); rows.append(r)
            print(e["nom"][:30], r["exercice_fin"], r["modele"], {k: r[k] for k in ("total_actif", "capitaux_propres", "marge_brute", "chiffre_affaires", "resultat_exercice", "effectif_moyen_ETP")}, flush=True)
        if not deps: print(e["nom"], "aucun dépôt trouvé", flush=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
