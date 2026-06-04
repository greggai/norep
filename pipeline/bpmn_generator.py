#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bpmn_generator.py - generator diagramow BPMN 2.0.

Wejscie: opis procesu (dict w Pythonie lub plik JSON) zgodny ze schematem
opisanym w references/format_spec.md.

Wyjscie (z jednego, wspolnego ukladu wspolrzednych):
  - <nazwa>.bpmn  - poprawny plik BPMN 2.0 (semantyka + diagram interchange/DI),
                    otwiera sie i edytuje w Camunda Modeler, bpmn.io, Signavio, Bizagi
  - <nazwa>.png   - rastrowy podglad (matplotlib)
  - <nazwa>.svg   - wektorowy podglad (matplotlib)

Filozofia: plik .bpmn jest "zrodlem prawdy" (przenosny standard OMG). Podglad PNG/SVG
sluzy do szybkiego ogladu w czacie. Uklad (layout) liczony jest raz i uzywany w obu.

Uzycie z CLI:
  python bpmn_generator.py --in proces.json --out /sciezka/nazwa
  python bpmn_generator.py --demo --out /sciezka/demo
  cat proces.json | python bpmn_generator.py --out /sciezka/nazwa

Uzycie z kodu:
  from bpmn_generator import generate
  generate(spec_dict, "/sciezka/nazwa")   # -> {'bpmn':..., 'png':..., 'svg':...}
"""

import argparse
import json
import re
import sys
from xml.sax.saxutils import escape

# ----------------------------------------------------------------------------
# Stale geometryczne (w jednostkach BPMN DI; y rosnie w dol, jak w narzedziach)
# ----------------------------------------------------------------------------
EVENT_D = 36          # srednica zdarzenia
GATE = 50             # bok rombu bramki (przekatna)
TASK_W, TASK_H = 110, 80
SUB_W, SUB_H = 140, 90
DATA_W, DATA_H = 40, 50
ANNO_W, ANNO_H = 250, 54

COL_W = 170           # odstep miedzy kolumnami (rank)
ROW_SLOT = 132        # wysokosc slotu wiersza (wieksze tory - tekst rol miesci sie wygodniej)
MARGIN_X = 70
MARGIN_Y = 70
LANE_LABEL_W = 42     # minimalny pasek z nazwa toru/basenu (rosnie dynamicznie)
LANE_PAD = 25         # margines wewnatrz toru


def _per_chars(avail_h, char_px=6.6, pad=18):
    """Ile znakow miesci sie w jednej (obroconej o 90 st.) linii etykiety o wysokosci avail_h."""
    return max(6, int((avail_h - pad) / char_px))


def _nlines(name, per):
    """Liczba linii po zawinieciu nazwy do 'per' znakow (sufit dzielenia)."""
    n = len((name or "").strip())
    return max(1, -(-n // per))

# ----------------------------------------------------------------------------
# PALETA "profesjonalna / nowoczesna".
# Odcienie wyprowadzone wg ZLOTEJ PROPORCJI - drabinka luminancji ~1:1.618
# (ink 22% -> ink_soft 40% -> mid ~50% -> light ~81% -> wash ~97%).
# Liczba rodzin barw = 5 (Fibonacci): neutralny slate, indygo, bursztyn,
# zielen, roz. Stosowane oszczednie: struktura na neutralnym slate, zadania
# w indygo, bramki w bursztynie, zdarzenia z semantycznym akcentem
# (start=zielen, koniec=roz, posrednie=slate).
# ----------------------------------------------------------------------------
PALETTE = {
    "ink":        "#363D4E",  # slate ciemny - linie sekwencji, obrysy, tekst glowny
    "ink_soft":   "#5B6475",  # slate sredni - etykiety drugorzedne
    "task_fill":  "#EDF2FB",  # delikatny wash indygo - wypelnienie zadan
    "task_edge":  "#3A5B8C",  # indygo - obrys zadan, tytul
    "gw_fill":    "#FBF0DA",  # delikatny wash bursztynowy - wypelnienie bramek
    "gw_edge":    "#C2872B",  # bursztyn - obrys bramek
    "gw_sym":     "#9A6A1C",  # bursztyn ciemny - symbol w bramce
    "start_edge": "#2E9E6B",  # zielen - zdarzenie poczatkowe
    "start_fill": "#E9F6EF",  # delikatny wash zielony
    "end_edge":   "#CE4257",  # roz/czerwien - zdarzenie koncowe
    "end_fill":   "#FBECEF",  # delikatny wash rozowy
    "evt_edge":   "#3A4254",  # slate - zdarzenia posrednie
    "evt_fill":   "#EEF1F7",  # delikatny wash slate - zdarzenia posrednie
    "pool_edge":  "#AEB6C2",  # jasny slate - obrys basenow i torow
    "lane_strip": "#F2F5F9",  # wash neutralny - pasek naglowka toru/basenu
    "data_fill":  "#EFF2F7",  # delikatny wash slate - obiekty/magazyny danych
    "data_edge":  "#6B7384",  # slate - obrys danych
    "label_bg":   "#FFFFFF",  # tlo pod etykieta przeplywu
}

# Typy elementow -> (tag BPMN, kategoria ksztaltu)
# kategoria: 'event' | 'gateway' | 'activity' | 'data' | 'annotation'
TASK_TYPES = {
    "task": "task", "userTask": "userTask", "serviceTask": "serviceTask",
    "sendTask": "sendTask", "receiveTask": "receiveTask", "manualTask": "manualTask",
    "scriptTask": "scriptTask", "businessRuleTask": "businessRuleTask",
}
GATEWAY_TYPES = {
    "exclusiveGateway", "parallelGateway", "inclusiveGateway",
    "eventBasedGateway", "complexGateway",
}
EVENT_TYPES = {
    "startEvent", "endEvent", "intermediateCatchEvent",
    "intermediateThrowEvent", "boundaryEvent",
}
EVENT_DEFS = {  # eventType -> nazwa elementu definicji zdarzenia
    "message": "messageEventDefinition", "timer": "timerEventDefinition",
    "signal": "signalEventDefinition", "error": "errorEventDefinition",
    "escalation": "escalationEventDefinition", "compensation": "compensateEventDefinition",
    "conditional": "conditionalEventDefinition", "link": "linkEventDefinition",
    "terminate": "terminateEventDefinition", "cancel": "cancelEventDefinition",
}
# Krotkie glify do podgladu (renderowane jako tekst w domyslnej czcionce)
EVENT_GLYPH = {
    "message": "M", "timer": "T", "signal": "S", "error": "Er",
    "escalation": "Es", "compensation": "C", "conditional": "?",
    "link": "L", "terminate": "\u25cf", "cancel": "X",
}
TASK_GLYPH = {
    "userTask": "U", "serviceTask": "S", "sendTask": "Sd", "receiveTask": "Rc",
    "manualTask": "Mn", "scriptTask": "Sc", "businessRuleTask": "Br",
}


# ----------------------------------------------------------------------------
# Walidacja i normalizacja spec
# ----------------------------------------------------------------------------
def _kind(node_type):
    if node_type in EVENT_TYPES:
        return "event"
    if node_type in GATEWAY_TYPES:
        return "gateway"
    if node_type in TASK_TYPES or node_type in ("subProcess", "callActivity", "transaction"):
        return "activity"
    if node_type in ("dataObject", "dataObjectReference", "dataStore", "dataStoreReference"):
        return "data"
    if node_type == "textAnnotation":
        return "annotation"
    raise ValueError("Nieznany typ elementu: %r" % node_type)


def normalize(spec):
    """Sprawdza spojnosc i uzupelnia braki. Zwraca znormalizowana kopie."""
    spec = json.loads(json.dumps(spec))  # gleboka kopia
    spec.setdefault("id", "Process_1")
    spec.setdefault("name", "Proces")
    spec.setdefault("nodes", [])
    spec.setdefault("flows", [])
    spec.setdefault("messageFlows", [])
    spec.setdefault("dataAssociations", [])
    spec.setdefault("associations", [])
    spec.setdefault("pools", [])

    ids = set()
    for n in spec["nodes"]:
        if "id" not in n or "type" not in n:
            raise ValueError("Wezel bez 'id' lub 'type': %r" % n)
        if n["id"] in ids:
            raise ValueError("Zduplikowane id wezla: %r" % n["id"])
        ids.add(n["id"])
        n.setdefault("name", "")
        n["_kind"] = _kind(n["type"])

    for f in spec["flows"]:
        if f.get("source") not in ids or f.get("target") not in ids:
            raise ValueError("Przeplyw odnosi sie do nieistniejacego wezla: %r" % f)
    return spec


# ----------------------------------------------------------------------------
# Warstwowanie (longest-path) + porzadek w warstwach (barycentrum)
# ----------------------------------------------------------------------------
def _build_graph(spec):
    succ = {n["id"]: [] for n in spec["nodes"]}
    pred = {n["id"]: [] for n in spec["nodes"]}
    # zdarzenia brzegowe nie maja wlasnej kolumny (sa przyczepione do czynnosci);
    # do warstwowania ich przeplyw wychodzacy traktujemy tak, jakby wychodzil z hosta
    boundary_host = {n["id"]: n.get("attachedTo")
                     for n in spec["nodes"] if n["type"] == "boundaryEvent"}
    flowable = {n["id"] for n in spec["nodes"]
                if n["_kind"] in ("event", "gateway", "activity") and n["type"] != "boundaryEvent"}
    for f in spec["flows"]:
        s, t = f["source"], f["target"]
        es = boundary_host.get(s, s)  # gdy zrodlem jest zdarzenie brzegowe - uzyj hosta
        if es in flowable and t in flowable:
            succ[es].append(t)
            pred[t].append(es)
    return succ, pred, flowable


def _detect_back_edges(succ, flowable):
    """DFS - wyznacza krawedzie wsteczne (petle), by warstwowanie bylo DAG.
    DFS startuje od wezlow zrodlowych (najmniejszy stopien wejsciowy) - dzieki temu
    jako 'wsteczna' klasyfikowana jest faktyczna krawedz domykajaca petle (np. przerobki),
    a nie krawedz strukturalna prowadzaca w przod."""
    indeg = {n: 0 for n in flowable}
    for u in flowable:
        for v in succ[u]:
            if v in indeg:
                indeg[v] += 1
    color = {n: 0 for n in flowable}  # 0 bialy,1 szary,2 czarny
    back = set()
    order = sorted(flowable, key=lambda n: (indeg[n], str(n)))

    def dfs(u):
        stack = [(u, iter(succ[u]))]
        color[u] = 1
        while stack:
            node, it = stack[-1]
            advanced = False
            for v in it:
                if color[v] == 0:
                    color[v] = 1
                    stack.append((v, iter(succ[v])))
                    advanced = True
                    break
                elif color[v] == 1:
                    back.add((node, v))
            if not advanced:
                color[node] = 2
                stack.pop()

    for s in order:
        if color[s] == 0:
            dfs(s)
    return back


def _ranks(spec, succ, pred, flowable):
    back = _detect_back_edges(succ, flowable)
    fsucc = {u: [v for v in succ[u] if (u, v) not in back] for u in flowable}
    fpred = {u: [] for u in flowable}
    for u in flowable:
        for v in fsucc[u]:
            fpred[v].append(u)
    # sortowanie topologiczne (Kahn)
    indeg = {u: len(fpred[u]) for u in flowable}
    queue = [u for u in flowable if indeg[u] == 0]
    rank = {u: 0 for u in flowable}
    topo = []
    queue.sort()
    while queue:
        u = queue.pop(0)
        topo.append(u)
        for v in sorted(fsucc[u]):
            rank[v] = max(rank[v], rank[u] + 1)
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
        queue.sort()
    # wezly w petli, ktore nie weszly do topo - przypisz po sasiadach
    for u in flowable:
        if u not in topo:
            rank[u] = max([rank[p] + 1 for p in pred[u] if p in rank] or [0])
    return rank, back


def _order_layers(spec, rank, succ, pred, flowable):
    by_rank = {}
    for u in flowable:
        by_rank.setdefault(rank[u], []).append(u)
    max_rank = max(by_rank) if by_rank else 0
    # init: kolejnosc wg pojawienia sie w spec
    order_index = {n["id"]: i for i, n in enumerate(spec["nodes"])}
    layers = {}
    for r in range(max_rank + 1):
        layers[r] = sorted(by_rank.get(r, []), key=lambda u: order_index[u])

    def barycenter(u, ref_layer_pos):
        neigh = [ref_layer_pos[p] for p in (pred[u] + succ[u]) if p in ref_layer_pos]
        return sum(neigh) / len(neigh) if neigh else ref_layer_pos.get(u, 0)

    # kilka przebiegow w dol i w gore dla redukcji skrzyzowan
    for _ in range(4):
        for r in range(1, max_rank + 1):
            prev_pos = {u: i for i, u in enumerate(layers[r - 1])}
            layers[r].sort(key=lambda u: barycenter(u, prev_pos))
        for r in range(max_rank - 1, -1, -1):
            nxt_pos = {u: i for i, u in enumerate(layers[r + 1])}
            layers[r].sort(key=lambda u: barycenter(u, nxt_pos))
    return layers, max_rank


# ----------------------------------------------------------------------------
# Przydzial wspolrzednych
# ----------------------------------------------------------------------------
def _node_size(n):
    k = n["_kind"]
    if k == "event":
        return EVENT_D, EVENT_D
    if k == "gateway":
        return GATE, GATE
    if k == "activity":
        if n["type"] in ("subProcess", "transaction"):
            return SUB_W, SUB_H
        return TASK_W, TASK_H
    if k == "data":
        return DATA_W, DATA_H
    if k == "annotation":
        return ANNO_W, ANNO_H
    return TASK_W, TASK_H


def _lane_assignment(spec):
    """Zwraca: lane_of(id)->lane_id, lista lanes [(pool_id,lane_id,name)], pool_of."""
    lane_of = {}
    lanes = []
    pool_of_lane = {}
    pool_names = {}
    for p in spec.get("pools", []):
        pool_names[p["id"]] = p.get("name", "")
        for ln in p.get("lanes", []):
            lanes.append((p["id"], ln["id"], ln.get("name", "")))
            pool_of_lane[ln["id"]] = p["id"]
    for n in spec["nodes"]:
        if "lane" in n:
            lane_of[n["id"]] = n["lane"]
    return lane_of, lanes, pool_of_lane, pool_names


def layout(spec):
    succ, pred, flowable = _build_graph(spec)
    rank, back = _ranks(spec, succ, pred, flowable)
    layers, max_rank = _order_layers(spec, rank, succ, pred, flowable)
    lane_of, lanes, pool_of_lane, pool_names = _lane_assignment(spec)

    pos = {}  # id -> (x_left, y_top, w, h, cx, cy)
    col_x = [MARGIN_X + r * COL_W for r in range(max_rank + 1)]

    nodes_by_id = {n["id"]: n for n in spec["nodes"]}
    use_lanes = len(lanes) > 0
    geom = {"lanes": [], "pools": [], "width": 0, "height": 0, "label_w": 0}

    if use_lanes:
        # ile wierszy potrzebuje kazdy tor (max liczba wezlow tego toru w jednej kolumnie)
        lane_rows = {lid: 1 for (_, lid, _) in lanes}
        col_lane_count = {}
        for r in range(max_rank + 1):
            for u in layers[r]:
                lid = lane_of.get(u)
                if lid is None:
                    continue
                col_lane_count[(r, lid)] = col_lane_count.get((r, lid), 0) + 1
        for (r, lid), c in col_lane_count.items():
            lane_rows[lid] = max(lane_rows[lid], c)

        lane_top = {}
        y_cursor = MARGIN_Y
        for (_, lid, _name) in lanes:
            lane_top[lid] = y_cursor
            y_cursor += lane_rows[lid] * ROW_SLOT
        total_h = y_cursor - MARGIN_Y

        pool_left = MARGIN_X - 40
        # Dynamiczna szerokosc paskow etykiet: nazwa toru/basenu jest zawijana wzdluz
        # wysokosci (tekst obrocony o 90 st.); liczba zawinietych linii wyznacza szerokosc
        # paska. Dzieki temu dlugie nazwy rol nie wychodza poza tor ani na siebie.
        LINE_PX = 16
        lane_label_lines = 1
        for (_, lid, name) in lanes:
            per = _per_chars(lane_rows[lid] * ROW_SLOT)
            lane_label_lines = max(lane_label_lines, _wrap(name, per, cap=per).count("\n") + 1)
        lane_label_w = max(LANE_LABEL_W, 12 + lane_label_lines * LINE_PX)
        this_pool = next(iter(dict.fromkeys([p for (p, _l, _n) in lanes])), None)
        pool_name = pool_names.get(this_pool, "")
        pper = _per_chars(total_h)
        pool_label_w = max(LANE_LABEL_W, 12 + (_wrap(pool_name, pper, cap=pper).count("\n") + 1) * LINE_PX)

        # kolumny zaczynaja sie ZA paskami etykiet (basen + tor) -> brak nachodzenia na wezly
        x_origin = pool_left + pool_label_w + lane_label_w + LANE_PAD
        col_x = [x_origin + r * COL_W for r in range(max_rank + 1)]

        # numer wiersza wezla w obrebie (kolumna, tor)
        for r in range(max_rank + 1):
            seen = {}
            for u in layers[r]:
                lid = lane_of.get(u)
                if lid is None:
                    continue
                idx = seen.get(lid, 0)
                seen[lid] = idx + 1
                n = nodes_by_id[u]
                w, h = _node_size(n)
                cx = col_x[r] + max(TASK_W, w) / 2.0
                cy = lane_top[lid] + idx * ROW_SLOT + ROW_SLOT / 2.0
                pos[u] = (cx - w / 2.0, cy - h / 2.0, w, h, cx, cy)

        content_right = (col_x[max_rank] if max_rank >= 0 else x_origin) + COL_W
        pool_width = content_right - pool_left + 40
        # geometrie torow i basenu (zakladamy jeden basen gdy tory naleza do 1 pool)
        lane_x = pool_left + pool_label_w
        for (_, lid, name) in lanes:
            geom["lanes"].append({
                "id": lid, "name": name,
                "x": lane_x, "y": lane_top[lid],
                "w": pool_width - pool_label_w, "h": lane_rows[lid] * ROW_SLOT,
            })
        pools_in = list(dict.fromkeys([p for (p, _l, _n) in lanes]))
        for pid in pools_in:
            geom["pools"].append({
                "id": pid, "name": pool_names.get(pid, ""),
                "x": pool_left, "y": MARGIN_Y,
                "w": pool_width, "h": total_h, "label_w": pool_label_w,
            })
        geom["label_w"] = lane_label_w
        geom["width"] = pool_left + pool_width + MARGIN_X
        geom["height"] = MARGIN_Y + total_h + MARGIN_Y
    else:
        # bez torow: kolumny wycentrowane pionowo
        max_col = max((len(layers[r]) for r in range(max_rank + 1)), default=1)
        band_h = max(max_col, 1) * ROW_SLOT
        for r in range(max_rank + 1):
            col = layers[r]
            offset = (max_col - len(col)) / 2.0
            for i, u in enumerate(col):
                n = nodes_by_id[u]
                w, h = _node_size(n)
                cx = col_x[r] + max(TASK_W, w) / 2.0
                cy = MARGIN_Y + (offset + i) * ROW_SLOT + ROW_SLOT / 2.0
                pos[u] = (cx - w / 2.0, cy - h / 2.0, w, h, cx, cy)
        geom["width"] = (col_x[max_rank] if max_rank >= 0 else MARGIN_X) + COL_W + MARGIN_X
        geom["height"] = MARGIN_Y + band_h + MARGIN_Y

    # wezly danych / adnotacje bez przeplywu sekwencji.
    # jesli powiazane asocjacja z umieszczonym wezlem - ustaw POD nim (krotka, pionowa asocjacja);
    # w przeciwnym razie w wierszu pod diagramem.
    assoc_host = {}
    by_id_all = {x["id"]: x for x in spec["nodes"]}
    for a in (spec.get("associations", []) + spec.get("dataAssociations", [])):
        s, t = a.get("source"), a.get("target")
        ns_, nt_ = by_id_all.get(s), by_id_all.get(t)
        if ns_ and nt_:
            if ns_["_kind"] in ("data", "annotation") and nt_["_kind"] in ("event", "gateway", "activity"):
                assoc_host[s] = t
            elif nt_["_kind"] in ("data", "annotation") and ns_["_kind"] in ("event", "gateway", "activity"):
                assoc_host[t] = s
    # Pass 1: zdarzenia brzegowe + wezly danych/adnotacji powiazane asocjacja (pod hostem).
    # Pass 2: wezly bez hosta (adnotacje-stopka) w rzedzie pod CALYM diagramem.
    DATA_PITCH = 152            # rozstaw poziomy danych - dopasowany do szerokosci etykiet
    LBL_DROP = 62              # zapas na etykiete obiektu danych (rysowana POD nim)

    # prostokaty zajete przez wezly glownego ukladu (+ zapas na etykiety zdarzen pod nimi)
    occupied = []
    for nid, p in pos.items():
        x, y, w, h, cx, cy = p
        k = by_id_all.get(nid, {}).get("_kind")
        pad_b = 46 if k == "event" else (18 if k == "gateway" else 6)
        occupied.append((x - 18, y - 6, x + w + 18, y + h + pad_b))

    def _hits(nx, ny, w, h):
        bx0, by0, bx1, by1 = nx - 8, ny - 6, nx + max(w, 92) + 8, ny + h + LBL_DROP
        for (ox0, oy0, ox1, oy1) in occupied:
            if bx0 < ox1 and ox0 < bx1 and by0 < oy1 and oy0 < by1:
                return True
        return False

    assoc_bottom = geom["height"] - MARGIN_Y
    floating = []
    # gdy sa baseny/tory - obiekty danych laduja w pasmie POD basenem (nie nachodza na tory)
    use_lanes_local = len(geom.get("pools", [])) > 0
    pool_bottom = max((gp["y"] + gp["h"] for gp in geom["pools"]), default=assoc_bottom) if use_lanes_local else None
    band_x = MARGIN_X
    for n in spec["nodes"]:
        if n["id"] in pos:
            continue
        w, h = _node_size(n)
        # zdarzenie brzegowe - na dolnej krawedzi czynnosci-hosta
        if n["type"] == "boundaryEvent" and n.get("attachedTo") in pos:
            hb = pos[n["attachedTo"]]
            bx = hb[0] + hb[2] * 0.72 - w / 2.0
            by = hb[1] + hb[3] - h / 2.0
            pos[n["id"]] = (bx, by, w, h, bx + w / 2.0, by + h / 2.0)
            rank[n["id"]] = rank.get(n["attachedTo"], 0)
            continue
        host = assoc_host.get(n["id"])
        if host and host in pos:
            hx, hy, hw, hh, hcx, hcy = pos[host]
            tries = 0
            if use_lanes_local:
                # pasmo pod basenem: ulozenie lewo->prawo (asocjacja prowadzi w gore do hosta)
                nx, ny = band_x, pool_bottom + 35
                while _hits(nx, ny, w, h) and tries < 30:
                    nx += DATA_PITCH
                    tries += 1
                band_x = nx + DATA_PITCH
            else:
                # zdarzenia maja etykiete POD soba - daj wiekszy odstep, by nie nachodzic
                drop = 50 if by_id_all.get(host, {}).get("_kind") == "event" else 30
                nx, ny = hcx - w / 2.0, hy + hh + drop
                while _hits(nx, ny, w, h) and tries < 16:
                    nx += DATA_PITCH
                    tries += 1
            pos[n["id"]] = (nx, ny, w, h, nx + w / 2.0, ny + h / 2.0)
            occupied.append((nx - 8, ny - 6, nx + max(w, 92) + 8, ny + h + LBL_DROP))
            assoc_bottom = max(assoc_bottom, ny + h + LBL_DROP)
            geom["width"] = max(geom["width"], nx + max(w, 92) + MARGIN_X)
        else:
            floating.append(n)
    content_bottom = assoc_bottom
    extra_x = MARGIN_X
    extra_y = assoc_bottom + 52
    for n in floating:
        w, h = _node_size(n)
        pos[n["id"]] = (extra_x, extra_y, w, h, extra_x + w / 2.0, extra_y + h / 2.0)
        extra_x += w + 60
        content_bottom = max(content_bottom, extra_y + h)
        geom["width"] = max(geom["width"], extra_x + MARGIN_X)
    geom["height"] = max(geom["height"], content_bottom + MARGIN_Y)

    # metryka procesu (prawy dolny rog) - rezerwacja miejsca i pozycja
    if spec.get("meta"):
        MB_W, MB_H = 256, 110
        base_y = geom["height"] - MARGIN_Y + 8
        geom["width"] = max(geom["width"], MB_W + 2 * MARGIN_X)
        mx = geom["width"] - MB_W - MARGIN_X + 24
        geom["meta_box"] = (mx, base_y, MB_W, MB_H)
        geom["height"] = base_y + MB_H + MARGIN_Y

    return pos, rank, back, geom, (lane_of, lanes, pool_of_lane)


# ----------------------------------------------------------------------------
# Trasowanie krawedzi (waypoints)
# ----------------------------------------------------------------------------
def _anchor_right(p):
    x, y, w, h, cx, cy = p
    return (x + w, cy)


def _anchor_left(p):
    x, y, w, h, cx, cy = p
    return (x, cy)


def _anchor_bottom(p):
    x, y, w, h, cx, cy = p
    return (cx, y + h)


def _anchor_top(p):
    x, y, w, h, cx, cy = p
    return (cx, y)


def route_flow(src, tgt, rank, sid, tid):
    """Zwraca liste punktow (x,y) dla przeplywu sekwencji."""
    sr, tr = rank.get(sid, 0), rank.get(tid, 0)
    if tr > sr:  # do przodu
        sx, sy = _anchor_right(src)
        tx, ty = _anchor_left(tgt)
        if abs(sy - ty) < 1:
            return [(sx, sy), (tx, ty)]
        midx = (sx + tx) / 2.0
        return [(sx, sy), (midx, sy), (midx, ty), (tx, ty)]
    elif tr == sr:  # ten sam rank - polacz pionowo
        if src[5] <= tgt[5]:
            sx, sy = _anchor_bottom(src)
            tx, ty = _anchor_top(tgt)
        else:
            sx, sy = _anchor_top(src)
            tx, ty = _anchor_bottom(tgt)
        return [(sx, sy), (tx, ty)]
    else:  # wstecz (petla) - trasuj dolem
        sx, sy = _anchor_bottom(src)
        tx, ty = _anchor_bottom(tgt)
        low = max(sy, ty) + ROW_SLOT * 0.6
        return [(sx, sy), (sx, low), (tx, low), (tx, ty)]


# ----------------------------------------------------------------------------
# Emisja BPMN 2.0 XML (+ DI)
# ----------------------------------------------------------------------------
NS = (
    'xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" '
    'xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" '
    'xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" '
    'xmlns:di="http://www.omg.org/spec/DD/20100524/DI" '
    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
)


def _fid(flow):
    return flow.get("id") or ("Flow_%s_%s" % (flow["source"], flow["target"]))


def to_bpmn_xml(spec, pos, rank, geom, lanes_info):
    lane_of, lanes, pool_of_lane = lanes_info
    nodes = spec["nodes"]
    flows = spec["flows"]
    by_id = {n["id"]: n for n in nodes}
    use_collab = len(lanes) > 0

    inc, out = {}, {}
    for f in flows:
        out.setdefault(f["source"], []).append(_fid(f))
        inc.setdefault(f["target"], []).append(_fid(f))
    default_flow = {f["source"]: _fid(f) for f in flows if f.get("default")}

    L = []
    L.append('<?xml version="1.0" encoding="UTF-8"?>')
    L.append('<bpmn:definitions %s id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">' % NS)

    proc_id = spec["id"]
    pools_in = list(dict.fromkeys([p for (p, _l, _n) in lanes])) if use_collab else []
    if use_collab:
        L.append('  <bpmn:collaboration id="Collaboration_1">')
        for pid in pools_in:
            pname = next((n for (p, _l, n) in lanes if p == pid and n), "")
            # nazwa basenu z geom.pools
            for gp in geom["pools"]:
                if gp["id"] == pid:
                    pname = gp["name"] or pname
            L.append('    <bpmn:participant id="%s" name="%s" processRef="%s"/>' %
                     (pid, escape(pname), proc_id))
        # przeplywy komunikatu na poziomie kooperacji
        for mf in spec.get("messageFlows", []):
            mid = mf.get("id") or ("MFlow_%s_%s" % (mf["source"], mf["target"]))
            L.append('    <bpmn:messageFlow id="%s" name="%s" sourceRef="%s" targetRef="%s"/>' %
                     (mid, escape(mf.get("name", "")), mf["source"], mf["target"]))
        L.append('  </bpmn:collaboration>')

    L.append('  <bpmn:process id="%s" isExecutable="false">' % proc_id)

    # laneSet
    if use_collab:
        L.append('    <bpmn:laneSet id="LaneSet_1">')
        for (_pid, lid, lname) in lanes:
            L.append('      <bpmn:lane id="%s" name="%s">' % (lid, escape(lname)))
            for n in nodes:
                if lane_of.get(n["id"]) == lid and n["_kind"] in ("event", "gateway", "activity"):
                    L.append('        <bpmn:flowNodeRef>%s</bpmn:flowNodeRef>' % n["id"])
            L.append('      </bpmn:lane>')
        L.append('    </bpmn:laneSet>')

    # elementy przeplywowe
    for n in nodes:
        nid, ntype = n["id"], n["type"]
        nm = escape(n.get("name", ""))
        k = n["_kind"]
        if k in ("event", "gateway", "activity"):
            attrs = 'id="%s"' % nid
            if nm:
                attrs += ' name="%s"' % nm
            if ntype == "boundaryEvent":
                attrs += ' attachedToRef="%s"' % n.get("attachedTo", "")
                if not n.get("interrupting", True):
                    attrs += ' cancelActivity="false"'
            if ntype in ("exclusiveGateway", "inclusiveGateway", "complexGateway") and nid in default_flow:
                attrs += ' default="%s"' % default_flow[nid]
            children = []
            for fid in inc.get(nid, []):
                children.append('      <bpmn:incoming>%s</bpmn:incoming>' % fid)
            for fid in out.get(nid, []):
                children.append('      <bpmn:outgoing>%s</bpmn:outgoing>' % fid)
            et = n.get("eventType")
            if k == "event" and et in EVENT_DEFS:
                children.append('      <bpmn:%s/>' % EVENT_DEFS[et])
            # markery aktywnosci
            if k == "activity":
                mi = n.get("multiInstance")
                if mi in ("parallel", "sequential"):
                    seq = "true" if mi == "sequential" else "false"
                    children.append('      <bpmn:multiInstanceLoopCharacteristics isSequential="%s"/>' % seq)
                elif n.get("loop"):
                    children.append('      <bpmn:standardLoopCharacteristics/>')
            if children:
                L.append('    <bpmn:%s %s>' % (ntype, attrs))
                L.extend(children)
                L.append('    </bpmn:%s>' % ntype)
            else:
                L.append('    <bpmn:%s %s/>' % (ntype, attrs))
        elif k == "data":
            if ntype in ("dataStore", "dataStoreReference"):
                L.append('    <bpmn:dataStoreReference id="%s" name="%s"/>' % (nid, nm))
            else:
                L.append('    <bpmn:dataObjectReference id="%s" name="%s" dataObjectRef="%s_obj"/>' % (nid, nm, nid))
                L.append('    <bpmn:dataObject id="%s_obj"/>' % nid)
        elif k == "annotation":
            L.append('    <bpmn:textAnnotation id="%s"><bpmn:text>%s</bpmn:text></bpmn:textAnnotation>' % (nid, nm))

    # przeplywy sekwencji
    for f in flows:
        fid = _fid(f)
        nm = escape(f.get("name", ""))
        nat = ' name="%s"' % nm if nm else ""
        L.append('    <bpmn:sequenceFlow id="%s"%s sourceRef="%s" targetRef="%s"/>' %
                 (fid, nat, f["source"], f["target"]))
    # asocjacje (np. do adnotacji)
    for a in spec.get("associations", []):
        aid = a.get("id") or ("Assoc_%s_%s" % (a["source"], a["target"]))
        L.append('    <bpmn:association id="%s" sourceRef="%s" targetRef="%s"/>' %
                 (aid, a["source"], a["target"]))
    L.append('  </bpmn:process>')

    # ---------------- DI ----------------
    plane_el = "Collaboration_1" if use_collab else proc_id
    L.append('  <bpmndi:BPMNDiagram id="BPMNDiagram_1">')
    L.append('    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="%s">' % plane_el)

    # baseny i tory
    for gp in geom["pools"]:
        L.append('      <bpmndi:BPMNShape id="%s_di" bpmnElement="%s" isHorizontal="true">' % (gp["id"], gp["id"]))
        L.append('        <dc:Bounds x="%g" y="%g" width="%g" height="%g"/>' % (gp["x"], gp["y"], gp["w"], gp["h"]))
        L.append('      </bpmndi:BPMNShape>')
    for gl in geom["lanes"]:
        L.append('      <bpmndi:BPMNShape id="%s_di" bpmnElement="%s" isHorizontal="true">' % (gl["id"], gl["id"]))
        L.append('        <dc:Bounds x="%g" y="%g" width="%g" height="%g"/>' % (gl["x"], gl["y"], gl["w"], gl["h"]))
        L.append('      </bpmndi:BPMNShape>')

    # ksztalty wezlow
    for n in nodes:
        nid = n["id"]
        x, y, w, h, cx, cy = pos[nid]
        L.append('      <bpmndi:BPMNShape id="%s_di" bpmnElement="%s">' % (nid, nid))
        L.append('        <dc:Bounds x="%g" y="%g" width="%g" height="%g"/>' % (x, y, w, h))
        L.append('      </bpmndi:BPMNShape>')

    # krawedzie - przeplywy sekwencji
    for f in flows:
        fid = _fid(f)
        s, t = f["source"], f["target"]
        if s in pos and t in pos:
            wps = route_flow(pos[s], pos[t], rank, s, t)
            L.append('      <bpmndi:BPMNEdge id="%s_di" bpmnElement="%s">' % (fid, fid))
            for (wx, wy) in wps:
                L.append('        <di:waypoint x="%g" y="%g"/>' % (wx, wy))
            L.append('      </bpmndi:BPMNEdge>')
    # krawedzie - przeplywy komunikatu
    for mf in spec.get("messageFlows", []):
        mid = mf.get("id") or ("MFlow_%s_%s" % (mf["source"], mf["target"]))
        s, t = mf["source"], mf["target"]
        if s in pos and t in pos:
            sx, sy = _anchor_bottom(pos[s]) if pos[s][5] < pos[t][5] else _anchor_top(pos[s])
            tx, ty = _anchor_top(pos[t]) if pos[s][5] < pos[t][5] else _anchor_bottom(pos[t])
            L.append('      <bpmndi:BPMNEdge id="%s_di" bpmnElement="%s">' % (mid, mid))
            L.append('        <di:waypoint x="%g" y="%g"/>' % (sx, sy))
            L.append('        <di:waypoint x="%g" y="%g"/>' % (tx, ty))
            L.append('      </bpmndi:BPMNEdge>')
    # krawedzie - asocjacje
    for a in spec.get("associations", []):
        aid = a.get("id") or ("Assoc_%s_%s" % (a["source"], a["target"]))
        s, t = a["source"], a["target"]
        if s in pos and t in pos:
            L.append('      <bpmndi:BPMNEdge id="%s_di" bpmnElement="%s">' % (aid, aid))
            L.append('        <di:waypoint x="%g" y="%g"/>' % (pos[s][4], pos[s][5]))
            L.append('        <di:waypoint x="%g" y="%g"/>' % (pos[t][4], pos[t][5]))
            L.append('      </bpmndi:BPMNEdge>')

    L.append('    </bpmndi:BPMNPlane>')
    L.append('  </bpmndi:BPMNDiagram>')
    L.append('</bpmn:definitions>')
    return "\n".join(L)


# ----------------------------------------------------------------------------
# Podglad PNG/SVG (matplotlib)
# ----------------------------------------------------------------------------
def _wrap(text, n=14, cap=None):
    """Zawijanie do ~n znakow w linii. Dlugie slowa lamane po '-' i '/' (separator
    zostaje na koncu czesci, bez wstawiania spacji), a w ostatecznosci ciete twardo.
    Slowa do 'cap' znakow pozostawiane w calosci (domyslnie n+6 - zapas dla ksztaltow
    poziomych; dla pionowych etykiet torow podaj cap=n, by linia nie przekroczyla wysokosci)."""
    cap = (n + 6) if cap is None else cap
    atoms = []
    for w in text.split():
        if len(w) <= cap:
            atoms.append(w)
        else:
            for pt in re.split(r'(?<=[-/])', w):
                while len(pt) > cap:
                    atoms.append(pt[:cap]); pt = pt[cap:]
                if pt:
                    atoms.append(pt)
    lines, cur = [], ""
    for a in atoms:
        if not cur:
            cur = a
        else:
            sep = "" if cur[-1] in "-/" else " "
            if len(cur) + len(sep) + len(a) <= n:
                cur = cur + sep + a
            else:
                lines.append(cur); cur = a
    if cur:
        lines.append(cur)
    return "\n".join(lines) if lines else text


def render_preview(spec, pos, rank, geom, lanes_info, png_path, svg_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Circle, Polygon, Rectangle, FancyArrowPatch
    # czcionka z pelnym pokryciem polskich znakow (a c e l n o s z z + wersaliki)
    matplotlib.rcParams["font.family"] = "DejaVu Sans"
    matplotlib.rcParams["axes.unicode_minus"] = False

    by_id = {n["id"]: n for n in spec["nodes"]}
    W, H = geom["width"], geom["height"]
    fig_w = max(6, W / 90.0)
    fig_h = max(4, H / 90.0)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)  # y w dol
    ax.axis("off")
    ax.set_aspect("equal")

    LINE = PALETTE["ink"]
    FILL_ACT = PALETTE["task_fill"]
    EDGE_ACT = PALETTE["task_edge"]
    POOL_EDGE = PALETTE["pool_edge"]

    # baseny i tory
    for gp in geom["pools"]:
        ax.add_patch(Rectangle((gp["x"], gp["y"]), gp["w"], gp["h"],
                               fill=False, edgecolor=POOL_EDGE, lw=1.4))
        lw = gp.get("label_w", LANE_LABEL_W)
        ax.add_patch(Rectangle((gp["x"], gp["y"]), lw, gp["h"],
                               facecolor=PALETTE["lane_strip"], edgecolor=POOL_EDGE, lw=1.4))
        _pp = _per_chars(gp["h"], char_px=7.4)
        ax.text(gp["x"] + lw / 2.0, gp["y"] + gp["h"] / 2.0, _wrap(gp["name"], _pp, cap=_pp),
                rotation=90, va="center", ha="center", fontsize=10.5, linespacing=0.92,
                fontweight="bold", color=PALETTE["ink"])
    for gl in geom["lanes"]:
        ax.add_patch(Rectangle((gl["x"], gl["y"]), gl["w"], gl["h"],
                               fill=False, edgecolor=POOL_EDGE, lw=0.9))
        ax.add_patch(Rectangle((gl["x"], gl["y"]), geom["label_w"], gl["h"],
                               facecolor=PALETTE["lane_strip"], edgecolor=POOL_EDGE, lw=0.9))
        _lp = _per_chars(gl["h"])
        ax.text(gl["x"] + geom["label_w"] / 2.0, gl["y"] + gl["h"] / 2.0,
                _wrap(gl["name"], _lp, cap=_lp),
                rotation=90, va="center", ha="center", fontsize=9.5, linespacing=0.92,
                color=PALETTE["ink"])

    def draw_arrow(wps, style="seq"):
        for i in range(len(wps) - 1):
            x0, y0 = wps[i]
            x1, y1 = wps[i + 1]
            last = (i == len(wps) - 2)
            if style == "seq":
                arr = "-|>" if last else "-"
                ls = "-"
                color = LINE
            elif style == "msg":
                arr = "->" if last else "-"
                ls = (0, (5, 3))
                color = PALETTE["ink_soft"]
            else:  # assoc
                arr = "-" if last else "-"
                ls = (0, (1, 2))
                color = "#9AA2B1"
            ap = FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=arr,
                                 mutation_scale=12, color=color, lw=1.2,
                                 linestyle=ls, shrinkA=0, shrinkB=0)
            ax.add_patch(ap)

    # krawedzie najpierw (pod ksztaltami)
    for f in spec["flows"]:
        s, t = f["source"], f["target"]
        if s in pos and t in pos:
            wps = route_flow(pos[s], pos[t], rank, s, t)
            draw_arrow(wps, "seq")
            if f.get("default"):
                # znacznik galezi domyslnej - krotka kreska w poprzek poczatku
                (x0, y0), (x1, y1) = wps[0], wps[1]
                mxp, myp = x0 * 0.72 + x1 * 0.28, y0 * 0.72 + y1 * 0.28
                dx, dy = x1 - x0, y1 - y0
                ln = (dx * dx + dy * dy) ** 0.5 or 1.0
                px, py = -dy / ln, dx / ln
                ax.plot([mxp - px * 5, mxp + px * 5], [myp - py * 5, myp + py * 5],
                        color=PALETTE["ink"], lw=1.3)
            if f.get("name"):
                mx, my = wps[len(wps) // 2]
                ax.text(mx, my - 7, f["name"], fontsize=7, ha="center",
                        color=PALETTE["ink_soft"],
                        bbox=dict(boxstyle="round,pad=0.12", fc=PALETTE["label_bg"], ec="none"))
    for mf in spec.get("messageFlows", []):
        s, t = mf["source"], mf["target"]
        if s in pos and t in pos:
            sy = pos[s][5]
            ty = pos[t][5]
            a = _anchor_bottom(pos[s]) if sy < ty else _anchor_top(pos[s])
            b = _anchor_top(pos[t]) if sy < ty else _anchor_bottom(pos[t])
            draw_arrow([a, b], "msg")
            ax.add_patch(Circle(a, 3.2, fill=True, facecolor="white",
                                edgecolor=PALETTE["ink_soft"], lw=1.0))
    for a in spec.get("associations", []):
        s, t = a["source"], a["target"]
        if s in pos and t in pos:
            draw_arrow([(pos[s][4], pos[s][5]), (pos[t][4], pos[t][5])], "assoc")

    # ksztalty
    for n in spec["nodes"]:
        nid = n["id"]
        x, y, w, h, cx, cy = pos[nid]
        k = n["_kind"]
        name = n.get("name", "")
        if k == "event":
            if n["type"] == "startEvent":
                ecol, lw, fcol = PALETTE["start_edge"], 1.9, PALETTE["start_fill"]
            elif n["type"] == "endEvent":
                ecol, lw, fcol = PALETTE["end_edge"], 3.0, PALETTE["end_fill"]
            else:
                ecol, lw, fcol = PALETTE["evt_edge"], 1.6, PALETTE["evt_fill"]
            els = "--" if (n["type"] == "boundaryEvent" and not n.get("interrupting", True)) else "-"
            ax.add_patch(Circle((cx, cy), w / 2.0, fill=True, facecolor=fcol,
                                edgecolor=ecol, lw=lw, linestyle=els))
            if n["type"] in ("intermediateCatchEvent", "intermediateThrowEvent", "boundaryEvent"):
                ax.add_patch(Circle((cx, cy), w / 2.0 - 3.2, fill=False, edgecolor=ecol, lw=1.3, linestyle=els))
            et = n.get("eventType")
            if et in EVENT_GLYPH:
                ax.text(cx, cy, EVENT_GLYPH[et], ha="center", va="center", fontsize=8, color=ecol)
            if name:
                ax.text(cx, y + h + 10, _wrap(name, 16), ha="center", va="top",
                        fontsize=7.5, color=PALETTE["ink"])
        elif k == "gateway":
            d = w / 2.0
            ax.add_patch(Polygon([(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)],
                                 closed=True, fill=True, facecolor=PALETTE["gw_fill"],
                                 edgecolor=PALETTE["gw_edge"], lw=1.5))
            sym = {"exclusiveGateway": "X", "parallelGateway": "+", "inclusiveGateway": "O",
                   "eventBasedGateway": "\u25c7", "complexGateway": "*"}.get(n["type"], "")
            ax.text(cx, cy, sym, ha="center", va="center", fontsize=11,
                    fontweight="bold", color=PALETTE["gw_sym"])
            if name:
                ax.text(cx, y - 9, _wrap(name, 18), ha="center", va="bottom",
                        fontsize=7.5, color=PALETTE["ink"])
        elif k == "activity":
            act_lw = 3.0 if n["type"] == "callActivity" else 1.7  # call activity - gruba krawedz
            ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=10",
                                        fill=True, facecolor=FILL_ACT, edgecolor=EDGE_ACT, lw=act_lw))
            if n["type"] == "transaction":
                # transakcja - podwojna krawedz (wewnetrzny obrys)
                ax.add_patch(FancyBboxPatch((x + 3, y + 3), w - 6, h - 6,
                                            boxstyle="round,pad=0,rounding_size=8",
                                            fill=False, edgecolor=EDGE_ACT, lw=1.0))
            if n["type"] in TASK_GLYPH:
                ax.text(x + 9, y + 12, TASK_GLYPH[n["type"]], ha="left", va="center",
                        fontsize=7, color=EDGE_ACT,
                        bbox=dict(boxstyle="circle,pad=0.15", fc="white", ec=EDGE_ACT, lw=0.8))
            if n["type"] in ("subProcess", "transaction"):
                ax.text(cx, y + h - 8, "+", ha="center", va="center", fontsize=11, color=PALETTE["ink"],
                        bbox=dict(boxstyle="square,pad=0.1", fc="white", ec=PALETTE["ink"], lw=0.8))
            ax.text(cx, cy, _wrap(name, 16), ha="center", va="center", fontsize=8, color=PALETTE["ink"])
        elif k == "data":
            dfill, dedge = PALETTE["data_fill"], PALETTE["data_edge"]
            if n["type"] in ("dataStore", "dataStoreReference"):
                # cylinder
                from matplotlib.patches import Ellipse
                ax.add_patch(Rectangle((x, y + 6), w, h - 12, fill=True, facecolor=dfill,
                                       edgecolor=dedge, lw=1.2))
                ax.add_patch(Ellipse((cx, y + 6), w, 12, fill=True, facecolor=dfill, edgecolor=dedge, lw=1.2))
                ax.add_patch(Ellipse((cx, y + h - 6), w, 12, fill=True, facecolor=dfill, edgecolor=dedge, lw=1.2))
            else:
                fold = 10
                ax.add_patch(Polygon([(x, y), (x + w - fold, y), (x + w, y + fold),
                                      (x + w, y + h), (x, y + h)], closed=True,
                                     fill=True, facecolor=dfill, edgecolor=dedge, lw=1.2))
            if name:
                ax.text(cx, y + h + 9, _wrap(name, 18), ha="center", va="top",
                        fontsize=7, color=PALETTE["ink_soft"])
        elif k == "annotation":
            wrapped = _wrap(name, 42)
            nlines = wrapped.count("\n") + 1
            bh = max(h, nlines * 12 + 10)            # nawias rosnie z liczba linii
            by0 = cy - bh / 2.0
            ax.add_patch(Polygon([(x + 8, by0), (x, by0), (x, by0 + bh), (x + 8, by0 + bh)],
                                 closed=False, fill=False, edgecolor=PALETTE["ink_soft"], lw=1.2))
            ax.text(x + 12, cy, wrapped, ha="left", va="center",
                    fontsize=7.5, color=PALETTE["ink"])

    # metryka procesu (prawy dolny rog) - wg wzoru metryki dokumentu SZBI
    mb = geom.get("meta_box"); meta = spec.get("meta")
    if mb and meta:
        mx, my, mw, _ = mb
        owner_wr = _wrap(str(meta.get("owner", "")), 32)
        rows = [("Identyfikator", str(meta.get("kod", "")), 1),
                ("Właściciel procesu", owner_wr, owner_wr.count("\n") + 1),
                ("Klasyfikacja", str(meta.get("klas", "Wewnętrzna")), 1),
                ("Wersja / data", str(meta.get("wer", "")), 1)]
        TH = 17.0; LH = 10.5; PADR = 9.0; keyw = 86.0
        rhs = [ln * LH + PADR for (_, _, ln) in rows]
        mh = TH + sum(rhs)
        ax.add_patch(Rectangle((mx, my), mw, mh, fill=True, facecolor="white",
                               edgecolor=PALETTE["ink"], lw=1.2, clip_on=False))
        ax.add_patch(Rectangle((mx, my), mw, TH, fill=True, facecolor=PALETTE["lane_strip"],
                               edgecolor=PALETTE["ink"], lw=1.2, clip_on=False))
        ax.text(mx + mw / 2.0, my + TH / 2.0, "METRYKA PROCESU", ha="center", va="center",
                fontsize=7.6, fontweight="bold", color=PALETTE["ink"], clip_on=False)
        yy = my + TH
        for (kk, vv, ln), rh in zip(rows, rhs):
            if yy > my + TH + 0.1:
                ax.plot([mx, mx + mw], [yy, yy], color=PALETTE["pool_edge"], lw=0.5, clip_on=False)
            ax.plot([mx + keyw, mx + keyw], [yy, yy + rh], color=PALETTE["pool_edge"], lw=0.5, clip_on=False)
            ax.text(mx + 5, yy + rh / 2.0, kk, ha="left", va="center",
                    fontsize=6.7, color=PALETTE["ink_soft"], clip_on=False)
            ax.text(mx + keyw + 5, yy + rh / 2.0, vv, ha="left", va="center",
                    fontsize=6.8, color=PALETTE["ink"], clip_on=False, linespacing=0.95)
            yy += rh

    title = spec.get("name", "")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", loc="left", color=PALETTE["task_edge"])
    plt.tight_layout()
    fig.savefig(png_path, dpi=170, bbox_inches="tight", facecolor="white")
    fig.savefig(svg_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ----------------------------------------------------------------------------
# API i CLI
# ----------------------------------------------------------------------------
def generate(spec, out_basename):
    spec = normalize(spec)
    pos, rank, back, geom, lanes_info = layout(spec)
    xml = to_bpmn_xml(spec, pos, rank, geom, lanes_info)
    bpmn_path = out_basename + ".bpmn"
    png_path = out_basename + ".png"
    svg_path = out_basename + ".svg"
    with open(bpmn_path, "w", encoding="utf-8") as fh:
        fh.write(xml)
    render_preview(spec, pos, rank, geom, lanes_info, png_path, svg_path)
    return {"bpmn": bpmn_path, "png": png_path, "svg": svg_path}


DEMO = {
    "id": "Proces_Zamowienie",
    "name": "Obsługa zamówienia (demo)",
    "pools": [{"id": "Pool_Sklep", "name": "Sklep internetowy", "lanes": [
        {"id": "Lane_Sprzedaz", "name": "Sprzedaż"},
        {"id": "Lane_Magazyn", "name": "Magazyn"},
    ]}],
    "nodes": [
        {"id": "start", "type": "startEvent", "name": "Zamówienie wpłynęło", "eventType": "message", "lane": "Lane_Sprzedaz"},
        {"id": "sprawdz", "type": "userTask", "name": "Sprawdź zamówienie", "lane": "Lane_Sprzedaz"},
        {"id": "brama", "type": "exclusiveGateway", "name": "Towar dostępny?", "lane": "Lane_Sprzedaz"},
        {"id": "kompletuj", "type": "task", "name": "Skompletuj towar", "lane": "Lane_Magazyn"},
        {"id": "wyslij", "type": "serviceTask", "name": "Wyślij paczkę", "lane": "Lane_Magazyn"},
        {"id": "powiadom", "type": "sendTask", "name": "Powiadom o braku", "lane": "Lane_Sprzedaz"},
        {"id": "koniec_ok", "type": "endEvent", "name": "Zamówienie zrealizowane", "lane": "Lane_Magazyn"},
        {"id": "koniec_brak", "type": "endEvent", "name": "Zamówienie odrzucone", "eventType": "terminate", "lane": "Lane_Sprzedaz"},
    ],
    "flows": [
        {"source": "start", "target": "sprawdz"},
        {"source": "sprawdz", "target": "brama"},
        {"source": "brama", "target": "kompletuj", "name": "tak"},
        {"source": "brama", "target": "powiadom", "name": "nie"},
        {"source": "kompletuj", "target": "wyslij"},
        {"source": "wyslij", "target": "koniec_ok"},
        {"source": "powiadom", "target": "koniec_brak"},
    ],
}


def validate(spec):
    """Weryfikacja strukturalna modelu (operacjonalizacja FBPM 5.4).
    Zwraca liste uwag (po polsku). Pusta lista = brak zastrzezen."""
    EVENTS = {"startEvent", "intermediateCatchEvent", "intermediateThrowEvent",
              "boundaryEvent", "endEvent"}
    GATEWAYS = {"exclusiveGateway", "parallelGateway", "inclusiveGateway",
                "eventBasedGateway", "complexGateway"}
    DATA = {"dataObject", "dataObjectReference", "dataStore", "dataStoreReference"}
    ARTIFACTS = {"textAnnotation", "group"}
    known = EVENTS | GATEWAYS | DATA | ARTIFACTS | {
        "task", "userTask", "serviceTask", "sendTask", "receiveTask",
        "manualTask", "scriptTask", "businessRuleTask",
        "subProcess", "callActivity", "transaction"}

    def kind_of(t):
        if t in EVENTS: return "event"
        if t in GATEWAYS: return "gateway"
        if t in DATA: return "data"
        if t in ARTIFACTS: return "annotation"
        return "activity"

    nodes = spec.get("nodes", [])
    flows = spec.get("flows", [])
    warns = []
    label = {}
    ids = []
    for n in nodes:
        nid = n.get("id")
        ids.append(nid)
        label[nid] = n.get("name") or nid
    seen_id = set()
    for nid in ids:
        if nid in seen_id:
            warns.append("Zduplikowany identyfikator wezla: '%s'." % nid)
        seen_id.add(nid)
    idset = set(ids)

    for f in flows:
        if f.get("source") not in idset:
            warns.append("Przeplyw wskazuje nieistniejacy wezel zrodlowy: '%s'." % f.get("source"))
        if f.get("target") not in idset:
            warns.append("Przeplyw wskazuje nieistniejacy wezel docelowy: '%s'." % f.get("target"))

    types = {n.get("id"): n.get("type") for n in nodes}
    for nid, t in types.items():
        if t not in known:
            warns.append("Nieznany typ elementu '%s' (wezel '%s')." % (t, label[nid]))

    starts = [n["id"] for n in nodes if n.get("type") == "startEvent"]
    ends = [n["id"] for n in nodes if n.get("type") == "endEvent"]
    if not starts:
        warns.append("Brak zdarzenia poczatkowego (startEvent).")
    if not ends:
        warns.append("Brak zdarzenia koncowego (endEvent).")

    inc, out = {}, {}
    for f in flows:
        out.setdefault(f.get("source"), []).append(f.get("target"))
        inc.setdefault(f.get("target"), []).append(f.get("source"))

    for n in nodes:
        nid, t = n.get("id"), n.get("type")
        k = kind_of(t)
        if k not in ("event", "gateway", "activity") or t == "boundaryEvent":
            continue
        if t != "startEvent" and not inc.get(nid):
            warns.append("Element '%s' nie ma wejscia (wiszacy)." % label[nid])
        if t != "endEvent" and not out.get(nid):
            warns.append("Element '%s' nie ma wyjscia (wiszacy)." % label[nid])
        if k == "gateway" and len(inc.get(nid, [])) > 1 and len(out.get(nid, [])) > 1:
            warns.append("Bramka '%s' laczy rozgalezianie i scalanie - rozdziel na dwie bramki." % label[nid])

    # osiagalnosc od startu (z uwzglednieniem zdarzen brzegowych)
    host_boundaries = {}
    for n in nodes:
        if n.get("type") == "boundaryEvent":
            host_boundaries.setdefault(n.get("attachedTo"), []).append(n.get("id"))
    if starts:
        reached, stack = set(), list(starts)
        while stack:
            u = stack.pop()
            if u in reached:
                continue
            reached.add(u)
            for v in out.get(u, []):
                stack.append(v)
            for b in host_boundaries.get(u, []):
                reached.add(b)
                for v in out.get(b, []):
                    stack.append(v)
        for n in nodes:
            nid, t = n.get("id"), n.get("type")
            if kind_of(t) in ("event", "gateway", "activity") and t != "boundaryEvent" and nid not in reached:
                warns.append("Element '%s' nieosiagalny od startu procesu." % label[nid])

    # zdarzenia brzegowe - przyczepione do czynnosci
    for n in nodes:
        if n.get("type") == "boundaryEvent":
            h = n.get("attachedTo")
            if h not in idset or kind_of(types.get(h)) != "activity":
                warns.append("Zdarzenie brzegowe '%s' nie jest przyczepione do czynnosci (attachedTo)." % label[n.get("id")])

    # poprawnosc torow
    valid_lanes = {ln.get("id") for p in spec.get("pools", []) for ln in p.get("lanes", [])}
    if valid_lanes:
        for n in nodes:
            if n.get("lane") and n["lane"] not in valid_lanes:
                warns.append("Element '%s' wskazuje nieistniejacy tor '%s'." % (label[n.get("id")], n["lane"]))

    return warns


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generator diagramow BPMN 2.0 (.bpmn + .png/.svg)")
    ap.add_argument("--in", dest="infile", help="plik JSON ze specyfikacja procesu")
    ap.add_argument("--out", dest="out", help="bazowa sciezka wyjsciowa (bez rozszerzenia)")
    ap.add_argument("--demo", action="store_true", help="uzyj wbudowanego przykladu")
    ap.add_argument("--check", action="store_true", help="sprawdz poprawnosc strukturalna (bez generowania)")
    args = ap.parse_args(argv)

    if args.demo:
        spec = DEMO
    elif args.infile:
        with open(args.infile, encoding="utf-8") as fh:
            spec = json.load(fh)
    else:
        data = sys.stdin.read()
        spec = json.loads(data)

    if args.check:
        warns = validate(spec)
        if warns:
            print("Znaleziono %d uwag(i) strukturalnych:" % len(warns))
            for w in warns:
                print("  - " + w)
        else:
            print("OK - brak uwag strukturalnych.")
        return

    if not args.out:
        ap.error("wymagane --out (albo uzyj --check do samej weryfikacji)")
    res = generate(spec, args.out)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
