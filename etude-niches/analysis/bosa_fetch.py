"""Téléchargement compact des publications publicprocurement.be (voir bosa_api.py).
Usage : python3 bosa_fetch.py '<filtres JSON>' sortie.jsonl
Champs conservés : date, nature, sous-type d'avis, CPV principal, NUTS, organisme, type de procédure,
agréations exigées (catégorie/classe), titre FR/NL, nombre de lots, publié aussi sur TED.
"""
import json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import bosa_api as b

def txt(lst, lang="FR"):
    lst = lst or []
    for x in lst:
        if x.get("language") == lang: return x.get("text")
    return lst[0].get("text") if lst else ""

def compact(p):
    d = p.get("dossier") or {}
    return {"date": p.get("publicationDate"), "natures": p.get("natures"), "subtype": p.get("noticeSubType"),
            "cpv": (p.get("cpvMainCode") or {}).get("code"), "cpv_fr": txt((p.get("cpvMainCode") or {}).get("descriptions")),
            "nuts": p.get("nutsCodes"), "org": txt((p.get("organisation") or {}).get("organisationNames")),
            "org_id": (p.get("organisation") or {}).get("organisationId"),
            "procedure": d.get("procurementProcedureType"), "technique": d.get("specialPurchasingTechnique"),
            "accreditations": d.get("accreditations"), "titre": txt(d.get("titles")), "n_lots": len(p.get("lots") or []),
            "ted": p.get("tedPublished"), "ref": p.get("referenceNumber"), "deadline": p.get("vaultSubmissionDeadline")}

if __name__ == "__main__":
    filters, out = json.loads(sys.argv[1]), sys.argv[2]
    page, n, size = 1, 0, 250
    with open(out, "w") as f:
        while True:
            d = b.search(filters, page=page, page_size=size)
            pubs = d.get("publications") or []
            for p in pubs:
                f.write(json.dumps(compact(p), ensure_ascii=False) + "\n"); n += 1
            if page == 1 or page % 10 == 0: print(page, n, d.get("totalCount"), flush=True)
            if len(pubs) < size: break
            page += 1
    print("total écrit", n)
