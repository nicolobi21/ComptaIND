"""Analyse des publications publicprocurement.be (Wallonie + Bruxelles, 26/10/2023 → 25/10/2026).

Définitions :
- Une publication = une référence unique (« ref ») ; les doublons sont retirés.
- Type d'avis (sous-type eForms, d'après le code du site) : MISE EN CONCURRENCE = 10-24, E3, BE-E3 ;
  ATTRIBUTION = 25-40, E4, BE-E4, E5, E6 ; autres = préinformation, etc.
- Années glissantes : A1 = 26/10/2023-25/10/2024 ; A2 = 26/10/2024-25/10/2025 ; A3 = 26/10/2025-25/10/2026.
- Zones (codes NUTS de l'avis, libellés lus dans l'API /api/loc/nuts) : BXL = BE1* ; WAL = BE3* ;
  HAINAUT = BE32* ; CHARLEROI = BE32B (« Arr. Charleroi ») ; un avis avec « BE » seul n'a pas de zone précise.
- Agréation : sous-catégories exigées dans l'avis (ex. P1, D16) et classe (1 = plus petits marchés … 8).
Usage : python3 -I bosa_analyse.py dossier_jsonl dossier_sortie
"""
import json, glob, collections, statistics, sys, os

COMP = {str(i) for i in range(10, 25)} | {"E3", "BE-E3"}
AWARD = {str(i) for i in range(25, 41)} | {"E4", "BE-E4", "E5", "E6"}

# Libellés : tableau des catégories et sous-catégories d'agréation (annexe 14, Charleroi Métropole, 2022)
LIB = {"D": "Entreprise générale de bâtiments", "D1": "Gros œuvre et mise sous toit", "D4": "Isolation, cloisons légères, faux plafonds",
       "D5": "Menuiserie générale, charpentes, escaliers bois", "D6": "Marbrerie, taille de pierres", "D7": "Ferronnerie",
       "D8": "Couvertures asphaltiques", "D10": "Carrelages", "D11": "Plafonnage, crépissage", "D12": "Couvertures non métalliques",
       "D13": "Peinture", "D14": "Vitrerie", "D15": "Parquetage", "D16": "Sanitaire et chauffage gaz individuel",
       "D17": "Chauffage central, installations thermiques", "D18": "Ventilation, climatisation", "D20": "Menuiserie métallique",
       "D21": "Ravalement de façades", "D22": "Couvertures métalliques, zinguerie", "D23": "Restauration par des artisans",
       "D24": "Restauration de monuments", "D25": "Revêtements de murs et de sols", "D29": "Chapes, sols industriels",
       "C": "Entreprise générale de travaux routiers", "C1": "Égouts courants", "C2": "Distribution d'eau, canalisations",
       "C3": "Signalisation non électrique", "C5": "Revêtements hydrocarbonés", "C6": "Pose de câbles en tranchées",
       "E": "Génie civil", "F": "Constructions métalliques", "G": "Terrassements", "G1": "Forage, sondage", "G2": "Drainage",
       "G3": "Plantations", "G4": "Sols sportifs", "G5": "Démolition", "N1": "Ascenseurs", "P1": "Électricité des bâtiments",
       "P2": "Électricité ouvrages d'art/industriels", "P3": "Lignes aériennes", "P4": "Électricité portuaire",
       "S1": "Téléphonie", "S2": "Télécommande, télécontrôle", "S3": "Radio, télévision", "S4": "Informatique et régulation",
       "B": "Entreprise générale de travaux hydrauliques", "A": "Dragage", "H": "Voies ferrées", "M1": "Électronique de puissance"}

def year(d):
    d = d.replace("-", "")
    return "A1" if d < "20241026" else ("A2" if d < "20251026" else "A3")

def zones(n):
    z = set()
    for c in n.get("nuts") or []:
        if c.startswith("BE1"): z.add("BXL")
        if c.startswith("BE3"): z.add("WAL")
        if c.startswith("BE32"): z.add("HAINAUT")
        if c.startswith("BE32B"): z.add("CHARLEROI")
    return z

def load(folder, nature):
    seen, rows = set(), []
    for f in sorted(glob.glob(os.path.join(folder, f"{nature}_*.jsonl"))):
        for l in open(f):
            n = json.loads(l)
            if n["ref"] in seen: continue
            seen.add(n["ref"]); rows.append(n)
    return rows

def table(rows, keyf, labelf, zone):
    g = collections.defaultdict(list)
    for n in rows:
        if zone and zone not in zones(n): continue
        for k in keyf(n): g[k].append(n)
    out = []
    for k, ns in g.items():
        y = collections.Counter(year(n["date"]) for n in ns)
        out.append((len(ns), k, labelf(k, ns), y["A1"], y["A2"], y["A3"], ns))
    return sorted(out, key=lambda r: -r[0])

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]; os.makedirs(dst, exist_ok=True)
    W = [n for n in load(src, "WORKS")]
    S = [n for n in load(src, "SUPPLIES")]
    print("Publications uniques : travaux", len(W), "; fournitures", len(S))
    for name, rows in (("travaux", W), ("fournitures", S)):
        c = collections.Counter("CONCURRENCE" if n["subtype"] in COMP else ("ATTRIBUTION" if n["subtype"] in AWARD else "AUTRE") for n in rows)
        print(name, dict(c))
    Wc = [n for n in W if n["subtype"] in COMP]
    Sc = [n for n in S if n["subtype"] in COMP]
    # 1. Travaux : sous-catégories d'agréation exigées
    for zone in ("", "WAL", "BXL", "HAINAUT", "CHARLEROI"):
        t = table(Wc, lambda n: [k for k in (n.get("accreditations") or {})], lambda k, ns: LIB.get(k, "?"), zone)
        with open(os.path.join(dst, f"travaux_agreations_{zone or 'WALBXL'}.csv"), "w") as f:
            f.write("sous_categorie;libelle;n_avis_mise_en_concurrence_36m;A1;A2;A3;classe_mediane;part_classes_1_2\n")
            for n_, k, lab, a1, a2, a3, ns in t:
                cl = [n["accreditations"][k] for n in ns if isinstance(n["accreditations"].get(k), int)]
                med = statistics.median(cl) if cl else ""
                p12 = f"{sum(1 for x in cl if x <= 2) / len(cl):.0%}" if cl else ""
                f.write(f"{k};{lab};{n_};{a1};{a2};{a3};{med};{p12}\n")
    # 2. Travaux : part des avis sans agréation exigée, par procédure
    for zone in ("", "CHARLEROI"):
        sel = [n for n in Wc if not zone or zone in zones(n)]
        sans = sum(1 for n in sel if not n.get("accreditations"))
        print(f"Travaux mise en concurrence {zone or 'WAL+BXL'} : {len(sel)} avis ; sans agréation exigée : {sans} ({sans/len(sel):.0%})")
        print("  procédures :", collections.Counter(n["procedure"] for n in sel).most_common(6))
    # 3. CPV (5 chiffres) travaux et fournitures
    for nm, rows in (("travaux", Wc), ("fournitures", Sc)):
        for zone in ("", "CHARLEROI"):
            t = table(rows, lambda n: [(n.get("cpv") or "0")[:5]], lambda k, ns: collections.Counter(n["cpv_fr"] for n in ns).most_common(1)[0][0], zone)
            with open(os.path.join(dst, f"{nm}_cpv5_{zone or 'WALBXL'}.csv"), "w") as f:
                f.write("cpv5;libelle_principal;n_avis_mise_en_concurrence_36m;A1;A2;A3\n")
                for n_, k, lab, a1, a2, a3, ns in t:
                    f.write(f"{k};{lab};{n_};{a1};{a2};{a3}\n")
    # 4. Acheteurs les plus actifs (travaux) autour de Charleroi
    t = collections.Counter(n["org"] for n in Wc if "CHARLEROI" in zones(n)).most_common(25)
    with open(os.path.join(dst, "travaux_acheteurs_CHARLEROI.csv"), "w") as f:
        f.write("acheteur;n_avis_mise_en_concurrence_36m\n")
        for o, c in t: f.write(f"{o};{c}\n")
