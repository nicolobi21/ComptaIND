"""Échantillon d'avis d'attribution par catégorie CPV (Wallonie + Bruxelles, 26/10/2023-25/10/2026) → détail eForms.

Méthode (fixée avant téléchargement) :
- population = avis d'ATTRIBUTION (sous-types 25-40, E4, BE-E4, E5, E6), toutes natures (travaux, fournitures, services) ;
- groupe = CPV principal à 4 chiffres ; seuls les groupes avec au moins MIN_GROUPE avis sont retenus ;
- tirage aléatoire simple de N_PAR_GROUPE avis par groupe (graine fixe 2026 → reproductible) ;
- les avis électricité déjà téléchargés (dossier existant) sont réutilisés.
Usage : python3 bosa_echantillon.py dossier_jsonl dossier_details [N_PAR_GROUPE] [MIN_GROUPE]
"""
import collections, glob, gzip, json, os, random, subprocess, sys, time, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bosa_api as b

AWARD = {str(i) for i in range(25, 41)} | {"E4", "BE-E4", "E5", "E6"}

def population(folder):
    seen, rows = set(), []
    for f in sorted(glob.glob(os.path.join(folder, "*.jsonl"))):
        for l in open(f):
            n = json.loads(l)
            if n["ref"] in seen or n["subtype"] not in AWARD or not n.get("workspace_id"): continue
            seen.add(n["ref"]); rows.append(n)
    return rows

def sample(rows, n_par, min_g):
    g = collections.defaultdict(list)
    for n in rows: g[(n.get("cpv") or "0000")[:4]].append(n)
    rnd = random.Random(2026); out = []
    for k in sorted(g):
        if len(g[k]) < min_g: continue
        out += rnd.sample(g[k], min(n_par, len(g[k])))
    return g, out

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    n_par = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    min_g = int(sys.argv[4]) if len(sys.argv) > 4 else 40
    os.makedirs(dst, exist_ok=True)
    rows = population(src); g, sel = sample(rows, n_par, min_g)
    json.dump(sel, open(os.path.join(dst, "_selection.json"), "w"), ensure_ascii=False)
    json.dump({k: len(v) for k, v in g.items()}, open(os.path.join(dst, "_taille_groupes.json"), "w"))
    print("avis d'attribution", len(rows), "; groupes retenus", sum(1 for v in g.values() if len(v) >= min_g), "; échantillon", len(sel), flush=True)
    for i, n in enumerate(sel):
        path = os.path.join(dst, n["workspace_id"] + ".json.gz")
        old = os.path.join("/tmp/claude-0/p1/mp/elec_details", n["workspace_id"] + ".json.gz")
        if os.path.exists(path): continue
        if os.path.exists(old): os.link(old, path); continue
        r = subprocess.run(["curl", "-sS", "-m", "90", "-A", "Mozilla/5.0", "-w", "\n%{http_code}", "-H", "Accept: application/json",
                            "-H", f"Authorization: Bearer {b.token()}", "-H", f"BelGov-Trace-Id: {uuid.uuid4()}",
                            f"{b.BASE}/api/dos/publication-workspaces/{n['workspace_id']}"], capture_output=True)
        body, code = r.stdout.rsplit(b"\n", 1)
        if code.strip() == b"200":
            with gzip.open(path, "wb") as f: f.write(body)
        if i % 100 == 0: print(i, "/", len(sel), flush=True)
        time.sleep(1.2)
    print("terminé", flush=True)
