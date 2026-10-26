"""Contrôle d'exhaustivité du comptage archi_2mois.py (fenêtre 26/08/2026 → 26/10/2026).

Entrées (bosa_fetch.py, même fenêtre) : services sans filtre NUTS, travaux, fournitures, tout (sans filtre), recherche
par CPV 71200000-0 ; TED (ted_fetch_mp.py) : avis cn-standard belges portant un CPV 712*.
Contrôles :
1. tout = services + travaux + fournitures (aucun avis sans nature) ;
2. avis de services hors filtre NUTS BE1/BE2/BE3 retenus par la règle ;
3. avis renvoyés par la recherche CPV 71200000 (CPV principal ou complémentaire) absents de la sélection ;
4. projets TED (titres dédoublonnés, préfixe « Belgique – <CPV> – » retiré) retrouvés sur publicprocurement.be.
Usage : python3 -I archi_verif.py dossier_verif selection.csv date_debut
"""
import csv, json, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from archi_2mois import archi

def load(p):
    d = {}
    for l in open(p, encoding="utf-8"):
        n = json.loads(l); d.setdefault(n["ref"], n)
    return d

def norm(s):
    s = unicodedata.normalize("NFKD", (s or "").lower()); return re.sub(r"[^a-z0-9]", "", s)[:40]

if __name__ == "__main__":
    V, sel, start = sys.argv[1], sys.argv[2], sys.argv[3]
    ours = {r["ref"] for r in csv.DictReader(open(sel, encoding="utf-8"))}
    S, W, F, A = (load(os.path.join(V, f + ".jsonl")) for f in ("services_sans_nuts", "works", "supplies", "tout"))
    print("1. tout :", len(A), "; services + travaux + fournitures :", len(set(S) | set(W) | set(F)))
    print("2. services retenus par la règle mais absents de la sélection :",
          [(n["langues"], n["org"][:30], n["titre"][:60]) for n in S.values()
           if archi(n) and n["ref"] not in ours and (n.get("premiere_publication") or n["date"]) >= start])
    C = [n for n in load(os.path.join(V, "cpv712.jsonl")).values() if (n.get("premiere_publication") or n["date"]) >= start]
    print("3. recherche CPV 71200000 :", len(C), "avis ; dans la sélection :", sum(n["ref"] in ours for n in C))
    for n in C:
        if n["ref"] not in ours and "FR" in (n.get("langues") or []) and n["subtype"] in {str(i) for i in range(10, 25)} | {"E3", "BE-E3"}:
            print("   mise en concurrence FR non retenue :", n["cpv"], n["org"][:30], "|", n["titre"][:80])
    B = {}
    for d in (S, W, F):
        for n in d.values(): B.setdefault(norm(n.get("titre")), n)
    T, seen, found, inside, missing = json.load(open(os.path.join(V, "ted_cn_712.json"))), set(), 0, 0, []
    for t in T:
        keys = [norm(v.split(" – ", 2)[-1]) for v in (t.get("notice-title") or {}).values()]
        if not keys or keys[0] in seen: continue
        seen.add(keys[0]); m = next((B[k] for k in keys if k in B), None)
        if m: found += 1; inside += m["ref"] in ours
        else: missing.append((t["publication-number"], t.get("organisation-city-buyer"), (t["notice-title"].get("fra") or "")[:110]))
    print("4. TED :", len(T), "avis ;", len(seen), "projets ; retrouvés sur publicprocurement.be :", found, "; dans la sélection :", inside)
    for m in missing: print("   absent de publicprocurement.be :", m)
