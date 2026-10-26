"""Marchés publics d'architecture publiés sur publicprocurement.be (Belgique entière, nature SERVICES).

Règle (missions d'architecture de BÂTIMENT) : CPV principal 712* (services d'architecture) sauf 712221* (cartographie
urbaine), OU CPV principal 71* hors 713* (ingénierie) avec un titre citant architecte / auteur(s) de projet / équipe
pluridisciplinaire / bureau d'études / mission d'étude / ontwerper / ontwerpteam / ontwerpbureau, OU tout CPV avec un
titre citant architecte / architecture / architectuur ; exclusion des titres informatiques (informatique, logiciel, data,
IT, ICT, cloud), d'assurances, de photographie et de génie civil (pont, voirie, égouttage, route, mur de soutènement,
épuration, postes HT…) sauf si le titre cite l'architecture.
Corrigée après deux contrôles des titres : la 1re version prenait « ontwerp » seul (ex. conception de bactéries) et ratait des
missions d'architecture classées sous un autre CPV (ex. 50000000) ; la 2e ratait « auteur.e.s de projet » et
« bureau d'études » pour des bâtiments, et prenait des ponts.
Langue : champ « publicationLanguages » de la plateforme (FR = publié en français, seul ou avec NL/DE/EN). Le code NUTS
déclaré n'est pas fiable pour la région (des communes flamandes déclarent BE100 = Bruxelles) : affiché pour info.
Avis de mise en concurrence : sous-types 10-24, E3, BE-E3 ; attribution : 25-40, E4, BE-E4, E5, E6.
Fenêtre : avis dont la 1re publication (champ premiere_publication de bosa_fetch.py) est >= date_debut ; les avis plus
anciens présents seulement à cause d'un rectificatif sont écartés.
Usage : python3 -I archi_2mois.py publications.jsonl sortie.csv date_debut date_reference
"""
import collections, csv, json, re, sys
COMP = {str(i) for i in range(10, 25)} | {"E3", "BE-E3"}
AWARD = {str(i) for i in range(25, 41)} | {"E4", "BE-E4", "E5", "E6"}
TIT = r"architect|auteur|pluridisciplinaire|bureau d.études|mission d.étude|ontwerper|ontwerpteam|ontwerpbureau"
GENIE_CIVIL = r"\bpont\b|voirie|égouttage|\broute|mur de soutènement|épuration|bassin d.orage|réseau d.eau|\bwegen|riolering|\bbrug\b|modélisation des eaux|postes? ht|tgbt|stabilité au feu"
ARCHI = r"architect|architectu"
IT = r"informati|logiciel|software|\bdata\b|\bit\b|\bict\b|cloud|assuranc|verzekering|photograph|fotograf"
REG = {"BE1": "Bruxelles", "BE2": "Flandre", "BE3": "Wallonie"}

def archi(n):
    cpv, t = n.get("cpv") or "", (n.get("titre") or "").lower()
    if re.search(IT, t): return False
    if cpv.startswith("712221"): return False
    if re.search(GENIE_CIVIL, t) and not re.search(ARCHI, t): return False
    if cpv.startswith("713") and not re.search(ARCHI, t): return False  # 713* = ingénierie
    return cpv.startswith("712") or (cpv.startswith("71") and bool(re.search(TIT, t))) or bool(re.search(ARCHI, t))

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    start, ref_date = sys.argv[3], sys.argv[4]
    seen, rows = set(), []
    for l in open(src, encoding="utf-8"):
        n = json.loads(l)
        if n["ref"] in seen or not archi(n) or (n.get("premiere_publication") or n["date"]) < start: continue
        seen.add(n["ref"]); rows.append(n)
    def kind(n): return "mise en concurrence" if n["subtype"] in COMP else "attribution" if n["subtype"] in AWARD else "autre"
    def langue(n):
        L = n.get("langues") or []
        return "FR" if "FR" in L else "NL" if "NL" in L else "DE" if "DE" in L else "?"
    def region(n):
        r = {REG.get(c[:3], "?") for c in n.get("nuts") or []}; return " / ".join(sorted(r)) or "?"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["premiere_publication", "date_derniere_version", "type", "langue", "region_nuts_declaree", "hainaut", "acheteur", "titre", "cpv", "procedure", "echeance", "ouvert_au", "ref", "workspace_id"])
        for n in sorted(rows, key=lambda n: n.get("premiere_publication") or n["date"]):
            dl = (n.get("deadline") or "")[:10]
            w.writerow([n.get("premiere_publication"), n["date"], kind(n), langue(n), region(n), any(c.startswith("BE32") for c in n.get("nuts") or []), n["org"], n.get("titre"),
                        n.get("cpv"), n.get("procedure"), dl, "oui" if kind(n) == "mise en concurrence" and dl >= ref_date else "",
                        n["ref"], n.get("workspace_id")])
    c = collections.Counter((kind(n), langue(n)) for n in rows)
    for k in sorted(c): print(k, c[k])
    comp = [n for n in rows if kind(n) == "mise en concurrence"]
    fr = [n for n in comp if langue(n) == "FR"]
    print("FR : mises en concurrence", len(fr), "; Hainaut", sum(any(x.startswith("BE32") for x in n.get("nuts") or []) for n in fr),
          "; encore ouvertes", sum((n.get("deadline") or "")[:10] >= ref_date for n in fr))
    print("mises en concurrence :", len(comp), "; Hainaut :", sum(any(x.startswith("BE32") for x in n.get("nuts") or []) for n in comp),
          "; encore ouvertes au", ref_date, ":", sum((n.get("deadline") or "")[:10] >= ref_date for n in comp))
    print("procédures :", collections.Counter(n.get("procedure") for n in comp).most_common(8))
