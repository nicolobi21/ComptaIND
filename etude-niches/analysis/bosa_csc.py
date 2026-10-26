"""Téléchargement des cahiers des charges (CSC) de lots électricité à offre unique ou sans offre (Hainaut, hors ORES).

Sélection (fixée avant téléchargement) : un lot par dossier, le plus récent d'abord, quotas par type de
travaux pour couvrir les principaux types ; on garde un dossier seulement si les documents de l'avis de
marché sont encore en ligne. Documents gardés : noms de fichier évoquant le cahier des charges
(csc, cdc, cahier, charges, clauses, administratif, technique, métré, bordereau).
Usage : python3 bosa_csc.py lots_classes.csv dossier_details dossier_sortie
"""
import csv, gzip, json, os, re, subprocess, sys, time, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bosa_api as b

QUOTAS = {"Lot électricité d'un chantier de bâtiment": 5, "Détection incendie, alarme, accès, vidéo": 4,
          "Éclairage, relighting, éclairage public/sportif": 3, "Mise en conformité / rénovation d'installation électrique": 3,
          "Photovoltaïque": 2, "Haute / moyenne tension, cabines": 2, "Bornes de recharge": 1}
KEEP = r"csc|cdc|cahier|charges|clauses|administrati|techni|métré|metre|métre|bordereau|inventaire"

def get(path):
    out = subprocess.run(["curl", "-sS", "-m", "90", "-A", "Mozilla/5.0", "-w", "\n%{http_code}", "-H", "Accept: application/json",
                          "-H", "Accept-Language: fr", "-H", f"Authorization: Bearer {b.token()}", "-H", f"BelGov-Trace-Id: {uuid.uuid4()}",
                          b.BASE + "/api/dos" + path], capture_output=True).stdout
    body, code = out.rsplit(b"\n", 1); time.sleep(1.5)
    return code.decode().strip(), body

if __name__ == "__main__":
    lots, det, out = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
    if len(sys.argv) > 4:  # 2e passe : quotas complémentaires (JSON) et aucun filtre sur le nom des fichiers
        QUOTAS = json.loads(sys.argv[4]); KEEP = r"\.(pdf|docx?|odt|xlsx?|rtf)$"
    PREF = sys.argv[5] if len(sys.argv) > 5 else "BE32"  # zone (préfixe NUTS) ; défaut Hainaut
    R = [r for r in csv.DictReader(open(lots, encoding="utf-8")) if any(c.startswith(PREF) for c in r["nuts"].split())
         and (("ORES" not in (r["acheteur"] or "").upper()))
         and ((r["resultat"] == "selec-w" and r["offres_recues"] == "1.0") or (r["resultat"] == "clos-nw" and r["offres_recues"] in ("0.0", "")))]
    R.sort(key=lambda r: r["date"], reverse=True)
    done, seen, manifest = {k: 0 for k in QUOTAS}, set(), []
    for r in R:
        t = r["type_travaux"]
        if t not in QUOTAS or done[t] >= QUOTAS[t] or r["workspace_id"] in seen: continue
        if os.path.isdir(os.path.join(out, str(json.loads(gzip.open(os.path.join(det, r["workspace_id"] + ".json.gz")).read())["dossierId"]))): continue
        seen.add(r["workspace_id"])
        d = json.loads(gzip.open(os.path.join(det, r["workspace_id"] + ".json.gz")).read())
        code, body = get(f"/dossiers/{d['dossierId']}/publication-workspaces")
        if code != "200": continue
        comp = [w for w in json.loads(body) if w.get("formType") == "COMPETITION"]
        files = []
        for w in comp:
            c, bd = get(f"/publication-workspaces/{w['id']}/documents")
            if c != "200": continue
            for doc in json.loads(bd):
                v = doc["versions"][-1]; name = v["document"]["originalFileName"]
                if not re.search(KEEP, name.lower()): continue
                c2, bd2 = get(f"/publication-workspace-document-versions/{v['id']}/download-url")
                if c2 != "200": continue
                url = json.loads(bd2)["value"]
                folder = os.path.join(out, str(d["dossierId"])); os.makedirs(folder, exist_ok=True)
                safe = re.sub(r"[^A-Za-z0-9._-]+", "_", name)[-120:]
                subprocess.run(["curl", "-sS", "-m", "120", "-o", os.path.join(folder, safe), url]); time.sleep(1.5)
                files.append(safe)
        if not files: continue
        done[t] += 1
        manifest.append({"dossier_id": d["dossierId"], "workspace_attribution": r["workspace_id"], "type_travaux": t,
                         "date_attribution": r["date"], "acheteur": r["acheteur"], "titre": r["titre"], "resultat": r["resultat"],
                         "offres_recues": r["offres_recues"], "montant_retenu": r["montant_retenu"], "estimation_lot": r["estimation_lot"],
                         "gagnant": r["gagnant"], "procedure": r["procedure"], "agreations": r["agreations"], "fichiers": files})
        print(sum(done.values()), t, d["dossierId"], len(files), flush=True)
        if all(done[k] >= QUOTAS[k] for k in QUOTAS): break
    mpath = os.path.join(out, "_manifest.json")
    old = json.load(open(mpath)) if os.path.exists(mpath) else []
    known = {m["dossier_id"] for m in old}
    json.dump(old + [m for m in manifest if m["dossier_id"] not in known], open(mpath, "w"), ensure_ascii=False, indent=1)
    print("dossiers avec documents :", len(manifest), done)
