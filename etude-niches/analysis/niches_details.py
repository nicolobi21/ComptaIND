"""Téléchargement du détail eForms des avis d'attribution des 4 niches candidates (sortie de niches_population.py).

Méthode (fixée avant téléchargement) : N1 et N4 → tous les avis ; N2 et N3 → tirage aléatoire de N_MAX avis
(graine 2026, reproductible). Les avis déjà téléchargés (échantillon CPV, électricité) sont réutilisés.
Politesse : 1,2 s entre requêtes, API publicprocurement.be (usage autorisé par l'utilisateur).
Usage : python3 -I niches_details.py prefixe_pop dossier_details [N_MAX]
"""
import glob, gzip, json, os, random, subprocess, sys, time, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bosa_api as b
from niches_population import AWARD

if __name__ == "__main__":
    pref, dst = sys.argv[1], sys.argv[2]
    n_max = int(sys.argv[3]) if len(sys.argv) > 3 else 250
    os.makedirs(dst, exist_ok=True)
    caches = ["/tmp/claude-0/p1/niche/details", "/tmp/claude-0/p1/mp/elec_details"]
    sel = {}
    for f in sorted(glob.glob(pref + "_N*.json")):
        k = os.path.basename(f)[len(os.path.basename(pref)) + 1:-5]
        aw = sorted((n for n in json.load(open(f)) if n["subtype"] in AWARD and n.get("workspace_id")), key=lambda n: n["ref"])
        if len(aw) > n_max: aw = random.Random(2026).sample(aw, n_max)
        sel[k] = aw
        print(k, len(aw), flush=True)
    json.dump(sel, open(os.path.join(dst, "_selection.json"), "w"), ensure_ascii=False)
    todo = [n for v in sel.values() for n in v]
    for i, n in enumerate(todo):
        path = os.path.join(dst, n["workspace_id"] + ".json.gz")
        if os.path.exists(path): continue
        old = [os.path.join(c, n["workspace_id"] + ".json.gz") for c in caches]
        old = [o for o in old if os.path.exists(o)]
        if old: os.link(old[0], path); continue
        r = subprocess.run(["curl", "-sS", "-m", "90", "-A", "Mozilla/5.0", "-w", "\n%{http_code}", "-H", "Accept: application/json",
                            "-H", f"Authorization: Bearer {b.token()}", "-H", f"BelGov-Trace-Id: {uuid.uuid4()}",
                            f"{b.BASE}/api/dos/publication-workspaces/{n['workspace_id']}"], capture_output=True)
        body, code = r.stdout.rsplit(b"\n", 1)
        if code.strip() == b"200":
            with gzip.open(path, "wb") as f: f.write(body)
        else: print("échec", code, n["workspace_id"], flush=True)
        if i % 50 == 0: print(i, "/", len(todo), flush=True)
        time.sleep(1.2)
    print("terminé", flush=True)
