#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tobe_engine.py - silnik składania wielotorowych modeli to-be (BPMN) z opisu deklaratywnego.

Model procesu = krotka (lanes, nodes, flows, data):
  lanes : lista nazw rol (tory, kolejnosc gora->dol)
  nodes : [(id, type, name, rola|"", opts)]   # opts: eventType/loop/attachedTo/interrupting
  flows : [(src, tgt, etykieta|None, default 0/1)]
  data  : [(id, dtype, name, host_id)]          # artefakty/aktywa -> obiekty danych
mk() zamienia to na spec generatora bpmn_generator (basen 'SCM Sp. z o.o.' + tory).
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build_pkg import parse_assets, asset_node_type, short, AI

POOL = "SCM Sp. z o.o."

def C(*ids):
    """Łańcuch sekwencyjny: C('s','a1','a2') -> [(s,a1),(a1,a2)] (bez etykiet)."""
    return [(ids[i], ids[i+1], None, 0) for i in range(len(ids)-1)]

# Ujednolicenie nazw rol ze slownikiem SZBI (Mapa dokumentacji SZBI v9.2) - zakres:
# role z domeny bezpieczenstwa informacji / IT / audytu / zmian. Oryginalne nazwy
# jednostek (Dzial Personalno-Placowy, Dzial Zamowien Publicznych, Radca prawny,
# Dzial Organizacyjno-Prawny, Zarzad...) oraz role kliniczne/medyczne - BEZ ZMIAN.
# Mapowania kontekstowe (W4.07->Zespol reagowania IR, W4.08->Administratorzy sieci,
# Z2.06/07, Z3.02/03) realizowane sa wprost w builderach tobe_models.
ROLE_MAP = {
    "Inspektor Ochrony Danych": "IOD",
    "Administrator Bezpieczeństwa": "Pełnomocnik ds. SZBI",
    "Dział Informatyki": "Administratorzy IT",
    "Audytor wewnętrzny": "Audytorzy wewnętrzni",
    "Komitet zmian (CAB)": "CAB",
    "Wnioskujący": "Wnioskodawcy",
    "Wnioskujący / Przełożony": "Wnioskodawcy / Przełożony",
}

def _role(r):
    return ROLE_MAP.get(r, r)

def mk(kod, name, proc, lanes, nodes, flows, data=()):
    # ujednolicenie nazw rol wg slownika SZBI (z zachowaniem kolejnosci i deduplikacja)
    mapped = []
    for nm in lanes:
        rn = _role(nm)
        if rn not in mapped:
            mapped.append(rn)
    lanes = mapped
    lane_id = {nm: "L%d" % i for i, nm in enumerate(lanes)}
    pool = {"id": "P1", "name": POOL, "lanes": [{"id": lane_id[nm], "name": nm} for nm in lanes]}
    out_nodes = []
    for tup in nodes:
        nid, typ, nm, role, opts = (tup + ({},))[:5] if len(tup) == 4 else tup
        nd = {"id": nid, "type": typ, "name": nm}
        if typ == "boundaryEvent":
            nd["attachedTo"] = opts.get("attachedTo")
            if "interrupting" in opts: nd["interrupting"] = opts["interrupting"]
        elif role:
            nd["lane"] = lane_id[_role(role)]
        if opts.get("eventType"): nd["eventType"] = opts["eventType"]
        if opts.get("loop"): nd["loop"] = True
        out_nodes.append(nd)
    assoc = []
    hosts = [t[0] for t in nodes if t[1].endswith("Task")]
    for did, dtyp, dnm, host in data:
        out_nodes.append({"id": did, "type": dtyp, "name": dnm}); assoc.append({"source": did, "target": host})
    # aktywa AI z rejestru (jesli zmapowane) jako dodatkowe obiekty danych
    for i, c in enumerate(parse_assets(proc.get("Aktywa informacyjne (kody)"))):
        did = "ai_%s" % c.replace("-", "_")
        if any(n["id"] == did for n in out_nodes):  # nie duplikuj
            continue
        out_nodes.append({"id": did, "type": asset_node_type(c),
                          "name": "%s: %s" % (c, " ".join((AI.get(c, {}).get("nazwa") or "aktyw informacyjny").split()))})
        assoc.append({"source": did, "target": hosts[i % len(hosts)] if hosts else nodes[0][0]})
    # stopka: systemy + RODO (tylko kluczowe)
    sysraw = proc.get("Systemy / moduły (kody)")
    med = (proc.get("Dane medyczne (art. 9 RODO)") or "").strip().lower()
    os_ = (proc.get("Dane osobowe (RODO)") or "").strip().lower()
    parts = []
    if sysraw: parts.append("Systemy: %s" % " ".join(str(sysraw).split()))
    if med == "tak": parts.append("RODO: dane medyczne (art. 9)")
    elif os_ == "tak": parts.append("RODO: dane osobowe")
    if parts: out_nodes.append({"id": "n_info", "type": "textAnnotation", "name": " · ".join(parts)})
    flow_list = []
    for s, t, lab, dflt in flows:
        f = {"source": s, "target": t}
        if lab: f["name"] = lab
        if dflt: f["default"] = True
        flow_list.append(f)
    return {"id": "Proc_%s" % re.sub(r'[^A-Za-z0-9]', '_', kod), "name": "%s  %s" % (kod, name),
            "pools": [pool], "nodes": out_nodes, "flows": flow_list, "associations": assoc}

