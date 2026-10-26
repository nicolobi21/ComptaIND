"""Téléchargement d'avis TED (API officielle v3, sans authentification) pour l'analyse des marchés publics belges.
Usage : python3 -I ted_fetch_mp.py "<requête experte TED>" sortie.json
"""
import json, subprocess, sys, time
q, out = sys.argv[1], sys.argv[2]
FIELDS = ["publication-number", "publication-date", "notice-type", "contract-nature", "notice-title",
          "classification-cpv", "organisation-post-code-buyer", "organisation-city-buyer",
          "estimated-value-proc", "estimated-value-cur-proc", "total-value", "winner-size",
          "received-submissions-type-val", "received-submissions-type-code"]
body = {"query": q, "fields": FIELDS, "limit": 250, "paginationMode": "ITERATION"}
res = []
while True:
    r = subprocess.run(["curl", "-sS", "-m", "120", "-X", "POST", "-H", "Content-Type: application/json",
                        "https://api.ted.europa.eu/v3/notices/search", "-d", json.dumps(body)], capture_output=True)
    d = json.loads(r.stdout)
    if "notices" not in d:
        print("ERREUR", str(d)[:300]); break
    for n in d["notices"]:
        n.pop("links", None)
        t = n.get("notice-title") or {}
        n["notice-title"] = {k: v for k, v in t.items() if k in ("fra", "nld", "eng")}
    res += d["notices"]
    print(len(res), d.get("totalNoticeCount"), flush=True)
    tok = d.get("iterationNextToken")
    if not tok or not d["notices"]:
        break
    body["iterationNextToken"] = tok
    time.sleep(1)
json.dump(res, open(out, "w"), ensure_ascii=False)
