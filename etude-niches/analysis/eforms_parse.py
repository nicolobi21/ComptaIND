"""Lecture des avis d'attribution eForms (XML) téléchargés par bosa_details.py → une ligne par lot attribué.

Champs : montant attribué du lot (PayableAmount de l'offre gagnante = offre liée au contrat conclu, ou offre unique), estimation du lot, nombre d'offres
reçues, offre la plus basse/haute, gagnant (nom, code postal, n° d'entreprise, taille si déclarée),
procédure, CPV, acheteur, zone. Quand l'avis simplifié ne lie pas le gagnant à une organisation,
le nom est pris dans « TenderReference »/« ContractReference » (texte saisi par l'acheteur) et signalé.
Usage : python3 -I eforms_parse.py dossier_details sortie.csv
"""
import csv, gzip, json, os, sys, xml.etree.ElementTree as ET

def L(e):  # nom local d'une balise
    return e.tag.rsplit("}", 1)[-1]

def kids(e, name):
    return [c for c in e if L(c) == name]

def kid(e, name):
    k = kids(e, name); return k[0] if k else None

def find_all(e, name):
    return [x for x in e.iter() if L(x) == name]

def text(e, *path):
    for p in path:
        if e is None: return None
        e = kid(e, p)
    return e.text.strip() if e is not None and e.text else None

def num(s):
    try: return float(s)
    except (TypeError, ValueError): return None

def parse(xml):
    root = ET.fromstring(xml)
    orgs = {}
    for o in find_all(root, "Organization"):
        c = kid(o, "Company")
        if c is None: continue
        oid = text(c, "PartyIdentification", "ID")
        names = {n.get("languageID"): n.text for n in find_all(c, "Name") if L(n) == "Name"}
        orgs[oid] = {"nom": names.get("FRA") or next(iter(names.values()), None),
                     "cp": text(c, "PostalAddress", "PostalZone"), "ville": text(c, "PostalAddress", "CityName"),
                     "bce": text(c, "PartyLegalEntity", "CompanyID"), "taille": text(c, "CompanySizeCode")}
    nr = next(iter(find_all(root, "NoticeResult")), None)
    tparties = {}
    tenders = {}
    if nr is not None:
        for tp in kids(nr, "TenderingParty"):
            tid = text(tp, "ID")
            tparties[tid] = [text(t, "ID") for t in kids(tp, "Tenderer")]
        for lt in kids(nr, "LotTender"):
            tenders[text(lt, "ID")] = {"montant": num(text(lt, "LegalMonetaryTotal", "PayableAmount")),
                                      "tpa": text(lt, "TenderingParty", "ID"),
                                      "ref": text(lt, "TenderReference", "ID"), "lot": text(lt, "TenderLot", "ID")}
    contracts = {}
    if nr is not None:
        for sc in kids(nr, "SettledContract"):
            contracts[text(sc, "ID")] = [text(x, "ID") for x in kids(sc, "LotTender")]
    est = {}
    for lot in kids(root, "ProcurementProjectLot"):
        est[text(lot, "ID")] = num(text(lot, "ProcurementProject", "RequestedTenderTotal", "EstimatedOverallContractAmount"))
    proc = text(root, "TenderingProcess", "ProcedureCode")
    cpv = text(root, "ProcurementProject", "MainCommodityClassification", "ItemClassificationCode")
    titre = None
    pp = kid(root, "ProcurementProject")
    if pp is not None:
        for n in kids(pp, "Name"):
            if n.get("languageID") == "FRA" or titre is None: titre = n.text
    rows = []
    for lr in (kids(nr, "LotResult") if nr is not None else []):
        res = text(lr, "TenderResultCode")
        offers = None
        for st in kids(lr, "ReceivedSubmissionsStatistics"):
            code = text(st, "StatisticsCode")
            if code in (None, "tenders"): offers = num(text(st, "StatisticsNumeric"))
        all_t = [text(t, "ID") for t in kids(lr, "LotTender")]
        # gagnant(s) = offres liées au contrat conclu du lot ; à défaut, l'offre unique du lot
        lot = text(lr, "TenderLot", "ID")
        won = [tid for c in kids(lr, "SettledContract") for tid in contracts.get(text(c, "ID"), [])
               if tenders.get(tid, {}).get("lot") in (None, lot)]
        methode = "contrat"
        if not won and len(all_t) == 1: won, methode = all_t, "offre_unique"
        if not won: methode = "inconnu"
        win = [tenders.get(tid, {}) for tid in won]
        names, cps, bces, tailles, fallback = [], [], [], [], False
        for w in win:
            ids = tparties.get(w.get("tpa"), [])
            if ids:
                for i in ids:
                    o = orgs.get(i, {}); names.append(o.get("nom")); cps.append(o.get("cp")); bces.append(o.get("bce")); tailles.append(o.get("taille"))
            elif w.get("ref"):
                names.append(w["ref"]); fallback = True
        m = sum(w["montant"] for w in win if w.get("montant")) or None
        lo, hi = num(text(lr, "LowerTenderAmount")), num(text(lr, "HigherTenderAmount"))
        # contrôle de cohérence : montant retenu seulement s'il est compris entre l'offre basse et l'offre haute du lot
        if m is None: coh = "absent"
        elif lo is not None and hi is not None and not (lo - 1 <= m <= hi + 1): coh = "incoherent"
        else: coh = "ok"
        rows.append({"lot": lot, "resultat": res, "offres_recues": offers,
                     "montant_attribue": m, "controle_montant": coh, "montant_retenu": m if coh == "ok" else None,
                     "offre_basse": num(text(lr, "LowerTenderAmount")), "offre_haute": num(text(lr, "HigherTenderAmount")),
                     "estimation_lot": est.get(lot), "gagnant": " | ".join(x for x in names if x) or None,
                     "gagnant_cp": " | ".join(x for x in cps if x) or None, "gagnant_bce": " | ".join(x for x in bces if x) or None,
                     "gagnant_taille": " | ".join(x for x in tailles if x) or None, "gagnant_nom_libre": fallback,
                     "identification_gagnant": methode, "n_offres_listees": len(all_t),
                     "procedure": proc, "cpv": cpv, "titre": titre})
    return rows

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    sel = {n["workspace_id"]: n for n in json.load(open(os.path.join(src, "_selection.json")))}
    fields = None; nfile = nerr = 0
    with open(out, "w", newline="", encoding="utf-8") as f:
        for fn in sorted(os.listdir(src)):
            if not fn.endswith(".json.gz"): continue
            wid = fn[:-8]; meta = sel.get(wid, {})
            d = json.loads(gzip.open(os.path.join(src, fn)).read())
            pubs = [v for v in d.get("versions", []) if v.get("status") == "PUBLISHED" and (v.get("notice") or {}).get("xmlContent")]
            if not pubs: nerr += 1; continue
            v = max(pubs, key=lambda v: v.get("version", 0))
            try: rows = parse(v["notice"]["xmlContent"])
            except ET.ParseError: nerr += 1; continue
            nfile += 1
            for r in rows:
                r.update({"workspace_id": wid, "ref": meta.get("ref"), "date": meta.get("date"), "acheteur": meta.get("org"),
                          "nuts": " ".join(meta.get("nuts") or []), "sous_type": d.get("noticeSubType"),
                          "agreations": json.dumps(meta.get("accreditations") or {})})
                if fields is None:
                    fields = list(r.keys()); w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
                w.writerow(r)
    print("avis lus", nfile, "; illisibles ou sans version publiée", nerr)
