"""Téléchargement du détail (avis eForms XML) des attributions « électricité » — publicprocurement.be.

Sélection (définie avant téléchargement) :
- avis d'ATTRIBUTION (sous-types 25-40, E4, BE-E4, E5, E6), travaux, Wallonie + Bruxelles, 26/10/2023-25/10/2026 ;
- « électricité » = CPV principal commençant par 4531 SAUF 45313 (ascenseurs), OU agréation exigée P1 ou P2.
Route : GET /api/dos/publication-workspaces/{id} (même accès que le site public). 1,5 s entre requêtes.
Usage : python3 bosa_details.py dossier_jsonl dossier_sortie
"""
import gzip, json, glob, os, subprocess, sys, time, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bosa_api as b

AWARD = {str(i) for i in range(25, 41)} | {"E4", "BE-E4", "E5", "E6"}

def is_elec(n):
    cpv = n.get("cpv") or ""
    acc = n.get("accreditations") or {}
    return (cpv.startswith("4531") and not cpv.startswith("45313")) or "P1" in acc or "P2" in acc

def select(folder):
    seen, out = set(), []
    for f in sorted(glob.glob(os.path.join(folder, "WORKS_*.jsonl"))):
        for l in open(f):
            n = json.loads(l)
            if n["ref"] in seen: continue
            seen.add(n["ref"])
            if n["subtype"] in AWARD and is_elec(n): out.append(n)
    return out

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]; os.makedirs(dst, exist_ok=True)
    sel = select(src)
    json.dump(sel, open(os.path.join(dst, "_selection.json"), "w"), ensure_ascii=False)
    print("sélection", len(sel), flush=True)
    for i, n in enumerate(sel):
        path = os.path.join(dst, n["workspace_id"] + ".json.gz")
        if os.path.exists(path): continue
        r = subprocess.run(["curl", "-sS", "-m", "90", "-A", "Mozilla/5.0", "-w", "\n%{http_code}",
                            "-H", "Accept: application/json", "-H", "Accept-Language: fr",
                            "-H", f"Authorization: Bearer {b.token()}", "-H", f"BelGov-Trace-Id: {uuid.uuid4()}",
                            f"{b.BASE}/api/dos/publication-workspaces/{n['workspace_id']}"], capture_output=True)
        body, code = r.stdout.rsplit(b"\n", 1)
        if code.strip() == b"200":
            with gzip.open(path, "wb") as f: f.write(body)
        else:
            print("erreur", code, n["workspace_id"], flush=True)
        if i % 50 == 0: print(i, "/", len(sel), flush=True)
        time.sleep(1.5)
    print("terminé", flush=True)
