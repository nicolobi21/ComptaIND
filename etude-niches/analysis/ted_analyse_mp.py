"""Analyse des avis TED belges : fréquence des besoins par code CPV, région, année, valeur et concurrence.

Définitions (affichées dans les sorties) :
- Zone : code postal de l'acheteur. BXL 1000-1299 ; Brabant wallon 1300-1499 ; Hainaut 6000-6599 et 7000-7999 ;
  Namur 5000-5999 ; Liège 4000-4999 ; Luxembourg 6600-6999 ; autres = Flandre. WAL = toutes les provinces wallonnes.
- Années glissantes : A1 = 26/10/2023-25/10/2024 ; A2 = 26/10/2024-25/10/2025 ; A3 = 26/10/2025-26/10/2026.
- cn = avis de marché (besoin publié) ; can = avis d'attribution (marché conclu).
- Valeur estimée = « estimated-value-proc » (avis de marché ; renseignée dans une minorité d'avis) ; valeur attribuée = « total-value » (attributions),
  qui peut être un maximum d'accord-cadre.
- Concurrence = médiane du nombre d'offres reçues (« received-submissions-type-val ») sur les attributions.
- CPV principal = premier code CPV de l'avis ; regroupé à N chiffres.
Usage : python3 -I ted_analyse_mp.py fichier.json niveau_cpv zone(WAL|BXLWAL|HAINAUT) [prefixe_cpv]
"""
import json, re, sys, statistics, collections

def prov(n):
    v = [p for p in (n.get("organisation-post-code-buyer") or []) if re.fullmatch(r"\d{4}", str(p))]
    if not v: return "NA"
    p = int(v[0])
    if 1000 <= p <= 1299: return "BXL"
    if 1300 <= p <= 1499: return "BW"
    if 4000 <= p <= 4999: return "LIE"
    if 5000 <= p <= 5999: return "NAM"
    if 6000 <= p <= 6599 or 7000 <= p <= 7999: return "HAI"
    if 6600 <= p <= 6999: return "LUX"
    return "VL"

ZONES = {"WAL": {"BW", "LIE", "NAM", "HAI", "LUX"}, "BXLWAL": {"BXL", "BW", "LIE", "NAM", "HAI", "LUX"}, "HAINAUT": {"HAI"}}

def year(n):
    d = n["publication-date"][:10].replace("-", "")
    return "A1" if d < "20241026" else ("A2" if d < "20251026" else "A3")

def label(n):
    t = (n.get("notice-title") or {}).get("fra") or ""
    t = t[0] if isinstance(t, list) else t
    p = t.split(" – ")
    return p[1] if len(p) > 2 else ""

def num(v):
    if isinstance(v, list): v = v[0] if v else None
    try:
        v = float(v)  # l'API renvoie parfois la valeur sous forme de texte
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None

if __name__ == "__main__":
    f, lvl, zone = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    pref = sys.argv[4] if len(sys.argv) > 4 else ""
    d = json.load(open(f))
    g = collections.defaultdict(list)
    for n in d:
        if prov(n) not in ZONES[zone]: continue
        cpv = (n.get("classification-cpv") or ["0"])[0]
        if not cpv.startswith(pref): continue
        g[cpv[:lvl]].append(n)
    rows = []
    for k, ns in g.items():
        cn = [n for n in ns if str(n.get("notice-type", "")).startswith("cn")]
        can = [n for n in ns if str(n.get("notice-type", "")).startswith("can")]
        yc = collections.Counter(year(n) for n in cn)
        est = [num(n.get("estimated-value-proc")) for n in cn]; est = [x for x in est if x]
        att = [num(n.get("total-value")) for n in can]; att = [x for x in att if x]
        subs = [int(x) for n in can for x in (n.get("received-submissions-type-val") or []) if str(x).isdigit()]
        sized = [n for n in can if n.get("winner-size")]
        sme = [n for n in sized if set(n["winner-size"]) & {"micro", "small", "sme", "medium"}]
        lab = collections.Counter(label(n) for n in ns).most_common(1)[0][0]
        rows.append((len(cn), k, lab, yc["A1"], yc["A2"], yc["A3"], len(can),
                     statistics.median(est) if est else "", statistics.median(att) if att else "",
                     statistics.median(subs) if subs else "", f"{len(sme)}/{len(sized)}"))
    rows.sort(key=lambda r: -r[0])
    print("cpv;libelle;n_avis_marche_36m;A1;A2;A3;n_attributions;mediane_valeur_estimee_EUR;mediane_valeur_attribuee_EUR;mediane_offres_recues;attrib_PME")
    for r in rows:
        print(";".join(str(x) for x in (r[1], r[2], r[0]) + r[3:]))
