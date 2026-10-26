"""Sous-segment N1 : support / gestion informatique des POUVOIRS LOCAUX (communes, CPAS, logement social, régies,
intercommunales locales), à partir de niches/niches_lots.csv.

Règles (fixées après lecture des 200 lots N1, appliquées mécaniquement) :
- titre « générique » : maintenance / gestion / assistance / support / infogérance / prise en charge, SANS nom de produit
  ou d'éditeur (Microsoft, Oracle, AWS, Cisco, Fortinet, SharePoint, Teams…) dans le titre ou le nom du gagnant ;
- acheteur local : nom d'un seul mot (= nom de commune sur publicprocurement.be, ex. « Antoing », « Tinlot ») hors
  Smals, Belnet, SNCB, FormaForm, IFAPME, VisitFlanders (contrôlés à la main), ou nom contenant commune / ville / CPAS / logement / logis / foyer / habitation(s) / immobilière / régie
  communale / crématorium / intercommunale / Charleroi Entreprendre / IPBW / Maison liégeoise / Ruche / Jardins de Wallonie ;
- exclusion des titres sans rapport (caméras, conseil communal, lignes téléphoniques, réseaux sociaux, SIG, information publique).
Usage : python3 -I niches_n1_local.py niches/niches_lots.csv sortie.csv
"""
import csv, re, statistics, sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from niches_concurrence import wilson

GEN = r"maintenance|gestion|assistance|support|infogérance|prise en charge"
BRAND = (r"microsoft|oracle|aws|cyberark|sparc|solaris|tenable|cisco|\bsap\b|vmware|fujitsu|hpe|ibm|dell|fortinet|f5|checkpoint"
         r"|citrix|microfocus|sharepoint|teams|moodle|waldur|gmi|zabbix|applinx|caris|ivanti|quantum|bmc|dinclock|honeywell|proximus|orange")
LOCAL = (r"^(commune|ville|c\.?p\.?a\.?s)|cpas|logement|logis|foyer|habitation|immobili|régie communale|crématorium|intercommunale"
         r"|charleroi entreprendre|ipbw|maison liégeoise|ruche|jardins de wallonie|^ville de charleroi")
HORS = r"caméra|conseil communal|lignes internet|réseaux sociaux|vidéosurveillance|sig\b|information publique"
NON_LOCAL = r"smals|belnet|sncb|formaform|ifapme|visitflanders"  # noms d'un seul mot qui ne sont pas des communes

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    R = [r for r in csv.DictReader(open(src, encoding="utf-8")) if r["niche"].startswith("N1")]
    sel = []
    for r in R:
        t, a = r["titre_avis"].lower(), r["acheteur"].strip()
        if not re.search(GEN, t) or re.search(BRAND, t + " " + (r["gagnant"] or "").lower()) or re.search(HORS, t): continue
        if re.search(NON_LOCAL, a.lower()) or not (" " not in a.split("(")[0].strip() or re.search(LOCAL, a.lower())): continue
        sel.append(r)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(R[0].keys())); w.writeheader(); w.writerows(sel)
    off = [float(r["offres_recues"]) for r in sel if r["offres_recues"] != ""]
    u = sum(1 for o in off if o <= 1); mt = sorted(float(r["montant_retenu"]) for r in sel if r["montant_retenu"])
    print(f"lots {len(sel)} ; avis {len({r['workspace_id'] for r in sel})} ; offres connues {len(off)} ; 0-1 offre {u} "
          f"({100*u/len(off):.0f} %, IC90 {wilson(u, len(off))}) ; offres médiane {statistics.median(off)}")
    print(f"montants {len(mt)} : P25/médiane/P75 {[round(x) for x in statistics.quantiles(mt, n=4)]} ; Hainaut {sum(r['hainaut']=='True' for r in sel)}")
    print("procédure :", {m: sum(r['mode'] == m for r in sel) for m in ('publiée', 'sans publication', 'autre/inconnue')})
    for r in sorted(sel, key=lambda r: r["acheteur"]):
        print(f"  {r['offres_recues'][:1]} | {r['mode'][:4]} | {(r['montant_retenu'] or '-')[:9]:>9} | {r['acheteur'][:32]} | {r['titre_avis'][:60]} | {(r['gagnant'] or '')[:28]}")
