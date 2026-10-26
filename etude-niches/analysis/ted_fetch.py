import json, subprocess, sys, time
q = sys.argv[1]; out = sys.argv[2]
fields = ["publication-number","publication-date","notice-title","classification-cpv","organisation-post-code-buyer","organisation-city-buyer","organisation-name-buyer","total-value","total-value-cur","result-value-notice","winner-size","winner-country","received-submissions-type-val","received-submissions-type-code"]
body = {"query": q, "fields": fields, "limit": 250, "paginationMode": "ITERATION"}
allnot = []
while True:
    r = subprocess.run(["curl","-sS","-m","120","-X","POST","-H","Content-Type: application/json",
        "https://api.ted.europa.eu/v3/notices/search","-d",json.dumps(body)], capture_output=True)
    d = json.loads(r.stdout)
    if "notices" not in d:
        print("ERR", str(d)[:500]); break
    for n in d["notices"]:
        n.pop("links", None)
    allnot += d["notices"]
    print(len(allnot), d.get("totalNoticeCount"), flush=True)
    tok = d.get("iterationNextToken")
    if not tok or not d["notices"]:
        break
    body["iterationNextToken"] = tok
    time.sleep(1)
json.dump(allnot, open(out, "w"), ensure_ascii=False)
