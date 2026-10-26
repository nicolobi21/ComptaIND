"""Client minimal pour la recherche publique de publicprocurement.be (SPF BOSA).

Utilisation autorisée par l'utilisateur le 26/10/2026. API interne NON documentée : elle peut changer.
Accès identique à celui du site public : jeton « client_credentials » du client « frontend-public »,
dont les identifiants sont lus à l'exécution dans https://www.publicprocurement.be/env.config.js
(rien n'est stocké dans ce dépôt). Politesse : ≥ 1,5 s entre deux requêtes.
"""
import base64, json, re, subprocess, time, uuid

BASE = "https://www.publicprocurement.be"
_token = {"v": None, "t": 0}

def _curl(args):
    r = subprocess.run(["curl", "-sS", "-m", "90", "-A", "Mozilla/5.0"] + args, capture_output=True)
    return r.stdout

def _cfg():
    js = _curl([BASE + "/env.config.js"]).decode()
    get = lambda k: re.search(k + r":\s*'([^']*)'", js).group(1)
    return get("VITE_AUTH_URL"), get("VITE_AUTH_REALM"), get("VITE_AUTH_CLIENTID"), get("VITE_AUTH_CLIENTSECRET"), get("VITE_SEARCH_API_ENDPOINT")

def token():
    if _token["v"] and time.time() - _token["t"] < 240:
        return _token["v"]
    url, realm, cid, sec, _ = _cfg()
    basic = base64.b64encode(f"{cid}:{sec}".encode()).decode()
    out = _curl(["-X", "POST", f"{url}/realms/{realm}/protocol/openid-connect/token",
                 "-H", "Content-Type: application/x-www-form-urlencoded", "-H", f"Authorization: Basic {basic}",
                 "--data", "grant_type=client_credentials&scope=openid"])
    _token["v"] = json.loads(out)["access_token"]; _token["t"] = time.time()
    return _token["v"]

def search(filters, page=1, page_size=100, order=None):
    body = dict(filters); body.update({"page": page, "pageSize": page_size})
    if order: body["order"] = order
    out = _curl(["-X", "POST", BASE + "/api/sea/search/publications", "-H", "Content-Type: application/json",
                 "-H", "Accept: application/json", "-H", "Accept-Language: fr", "-H", f"Authorization: Bearer {token()}",
                 "-H", f"BelGov-Trace-Id: {uuid.uuid4()}",  # en-tête ajouté par le site à chaque requête
                 "--data", json.dumps(body)])
    time.sleep(1.5)
    return json.loads(out)

if __name__ == "__main__":
    import sys
    d = search(json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}, page_size=2)
    print(json.dumps(d, ensure_ascii=False)[:4000])
