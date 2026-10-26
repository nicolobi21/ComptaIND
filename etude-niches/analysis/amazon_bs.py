"""Relevé des pages publiques « Meilleures ventes » Amazon (amazon.fr, amazon.com.be).

Méthode et limites (à lire avant d'utiliser les sorties) :
- Pages consultées : /gp/bestsellers/... uniquement. Le robots.txt d'Amazon
  (sources S003, S004) n'interdit pas ces chemins pour User-agent *.
- Politesse : une requête toutes les DELAY secondes, pas de connexion, pas de
  contournement. Une page bloquée (captcha, 503) est notée et ignorée.
- Amazon définit ce classement ainsi : « Nos produits les plus populaires en
  vertu du nombre de ventes. Mis à jour fréquemment. » → rang = preuve d'ACHAT
  relative (pas un volume de ventes).
- Le nombre d'« évaluations » mélange notes et avis, et peut être partagé entre
  variantes d'un même produit : c'est un indicateur d'achats cumulés, pas un
  volume.
- La page est servie avec « Votre adresse de livraison : États-Unis » : les prix
  affichés peuvent différer des prix vus par un client belge ou français
  (TVA, frais). Les prix servent uniquement d'ordre de grandeur.
- Seuls les 30 premiers rangs sont rendus côté serveur.

Usage :
  python3 -I amazon_bs.py fetch  <fichier_urls> <dossier_brut>
  python3 -I amazon_bs.py parse  <dossier_brut> <sortie.csv>
  python3 -I amazon_bs.py subcats <fichier.html.gz>
"""
import csv
import gzip
import html
import os
import re
import subprocess
import sys
import time

DELAY = 6
UA = "Mozilla/5.0 (X11; Linux x86_64)"


def slug(url):
    return re.sub(r"[^a-z0-9]+", "_", url.lower().split("//", 1)[1]).strip("_")


def fetch(url_file, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    urls = [u.strip() for u in open(url_file) if u.strip() and not u.startswith("#")]
    for n, url in enumerate(urls):
        path = os.path.join(out_dir, slug(url) + ".html.gz")
        if os.path.exists(path):
            continue
        r = subprocess.run(
            ["curl", "-sS", "--compressed", "-m", "40", "-A", UA, "-H", "Accept-Language: fr-FR,fr;q=0.9",
             "-w", "%{http_code}", "-o", "-", url],
            capture_output=True)
        body, code = r.stdout[:-3], r.stdout[-3:].decode(errors="ignore")
        blocked = b"captcha" in body.lower() or code != "200"
        print(f"{n+1}/{len(urls)} {code} {'BLOQUÉ' if blocked else 'ok'} {url}", flush=True)
        if not blocked:
            with gzip.open(path, "wb") as f:
                f.write(body)
        time.sleep(DELAY)


def num(s):
    return int(re.sub(r"[^\d]", "", s)) if s and re.search(r"\d", s) else None


def parse_page(t):
    title = re.search(r"<title>([^<]*)", t)
    cat = html.unescape(title.group(1)) if title else ""
    rows = []
    for blk in t.split('id="gridItemRoot"')[1:]:
        rank = re.search(r'zg-bdg-text">#(\d+)', blk)
        asin = re.search(r'data-asin="([A-Z0-9]{10})"', blk)
        name = re.search(r'line-clamp-\d_[^"]*">([^<]+)<', blk)
        rating = re.search(r'aria-label="([\d,]+) sur 5[\s\xa0]étoiles, ([\d\s \xa0]+)[\s\xa0]évaluations?"', blk)
        offers = re.search(r'(\d+) offres? à partir de', blk)
        price = re.search(r'a-price-whole">([\d\s \xa0.]+)<.*?a-price-fraction">(\d+)<', blk, re.S)
        rows.append({
            "rang": rank.group(1) if rank else "",
            "asin": asin.group(1) if asin else "",
            "titre": html.unescape(name.group(1)).strip() if name else "",
            "note": rating.group(1).replace(",", ".") if rating else "",
            "nb_evaluations": num(rating.group(2)) if rating else "",
            "nb_offres": offers.group(1) if offers else "",
            "prix_affiche_eur": f"{num(price.group(1))}.{price.group(2)}" if price else "",
        })
    return cat, rows


def parse(raw_dir, out_csv):
    fields = ["fichier", "page", "rang", "asin", "titre", "note", "nb_evaluations",
              "nb_offres", "prix_affiche_eur"]
    with open(out_csv, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=fields)
        w.writeheader()
        for fn in sorted(os.listdir(raw_dir)):
            if not fn.endswith(".html.gz"):
                continue
            cat, rows = parse_page(read_raw(os.path.join(raw_dir, fn)))
            for r in rows:
                w.writerow({"fichier": fn, "page": cat, **r})


def read_raw(path):
    # Certaines réponses ont été reçues compressées (gzip) avant l'ajout de --compressed.
    b = gzip.open(path, "rb").read()
    if b[:2] == b"\x1f\x8b":
        b = gzip.decompress(b)
    return b.decode("utf-8", errors="ignore")


def subcats(path):
    t = read_raw(path)
    for href, label in re.findall(
            r'href="(/gp/bestsellers/[a-z\-]+/\d+)[^"]*"[^>]*>([^<]{2,80})<', t):
        print(f"{href}\t{html.unescape(label).strip()}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"fetch": fetch, "parse": parse, "subcats": subcats}[cmd](*sys.argv[2:])
