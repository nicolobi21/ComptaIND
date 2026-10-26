"""Volume des niches candidates sur toute la population publicprocurement.be (Wallonie + Bruxelles, 36 mois).

Définitions (règles de sélection fixées avant comptage) :
- N1 Maintenance/gestion informatique des pouvoirs locaux : nature SERVICES et titre contenant parc informatique,
  infrastructure informatique, réseau informatique, maintenance informatique, support informatique, helpdesk,
  infogérance, gestion du réseau ; EXCLUSION des titres citant copieur/photocopieur/multifonction/imprimante/licence.
- N2 Formations : CPV principal 80* (services d'enseignement et de formation), hors permis de conduire / auto-école.
- N3 Fournitures de matériaux pour régies et sociétés de logement : nature SUPPLIES, CPV 441*-444* ou titre contenant
  matériaux, quincaillerie, menuiserie, bois, plomberie, sanitaire, visserie, outillage ; titre contenant aussi
  stock / accord-cadre / fournitures / matériaux.
- N4 Graphisme et communication imprimée : CPV 7982*, 7981* (impression) ou titre contenant graphisme, mise en page,
  bulletin communal (« graphique » et « bois » en mot entier : exclut topographique, cartographique, boissons).
Indicateurs : avis de mise en concurrence et d'attribution, par an, part Hainaut, principaux acheteurs.
Usage : python3 -I niches_population.py dossier_jsonl sortie_prefixe
"""
import glob, json, os, re, sys, collections
COMP = {str(i) for i in range(10, 25)} | {"E3", "BE-E3"}
AWARD = {str(i) for i in range(25, 41)} | {"E4", "BE-E4", "E5", "E6"}
RULES = {
 "N1_informatique_pouvoirs_locaux": lambda n, t: "SERVICES" in (n.get("natures") or []) and re.search(r"parc informatique|infrastructure informatique|réseau informatique|maintenance informatique|support informatique|helpdesk|infogérance|gestion du réseau|maintenance du parc", t) and not re.search(r"copieur|multifonction|imprimante|licence", t),
 "N2_formations": lambda n, t: (n.get("cpv") or "").startswith("80") and not re.search(r"permis|auto-école|conduite", t),
 "N3_materiaux_regies_logement": lambda n, t: "SUPPLIES" in (n.get("natures") or []) and (re.match(r"44[1-4]", n.get("cpv") or "") or re.search(r"matériaux|quincaillerie|menuiserie|\bbois\b|plomberie|sanitaire|visserie|outillage", t)) and re.search(r"stock|accord.cadre|fourniture|matériaux", t),
 "N4_graphisme_communication": lambda n, t: re.match(r"798[12]", n.get("cpv") or "") or re.search(r"\bgraphisme|\bgraphique|mise en page|bulletin communal|bulletin d.information", t),
}
if __name__ == "__main__":
    src, pref = sys.argv[1], sys.argv[2]
    seen, rows = set(), []
    for f in glob.glob(os.path.join(src, "*.jsonl")):
        for l in open(f):
            n = json.loads(l)
            if n["ref"] in seen: continue
            seen.add(n["ref"]); rows.append(n)
    out = {}
    for k, rule in RULES.items():
        sel = [n for n in rows if rule(n, (n.get("titre") or "").lower())]
        comp = [n for n in sel if n["subtype"] in COMP]; aw = [n for n in sel if n["subtype"] in AWARD]
        hai = sum(1 for n in sel if any(c.startswith("BE32") for c in n.get("nuts") or []))
        print(f"{k}: mises en concurrence {len(comp)} ({len(comp)/3:.0f}/an) ; attributions {len(aw)} ({len(aw)/3:.0f}/an) ; Hainaut {hai}/{len(sel)}")
        print("   acheteurs :", collections.Counter(n["org"] for n in sel).most_common(6))
        out[k] = [n for n in aw]
        json.dump(sel, open(f"{pref}_{k}.json", "w"), ensure_ascii=False)
    json.dump({k: [n["workspace_id"] for n in v] for k, v in out.items()}, open(f"{pref}_attributions_ids.json", "w"))
