#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_tobe_all.py - generuje wielotorowe modele docelowe dla wszystkich 203 procesow.
   --check : tylko walidacja (szybko). bez flagi : pelne generowanie .bpmn/.png/.pdf + foldery.
"""
import json, os, sys, shutil, datetime, traceback
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpmn_generator as G
from tobe_engine import mk
from tobe_models import model_for
from build_pkg import slug, WARSTWA_DIR, L1, prefix_of, svg_to_pdf
ROOT = os.path.dirname(HERE)
REG = json.load(open(os.path.join(ROOT, "data", "register.json"), encoding="utf-8"))

def spec_for(proc):
    lanes, nodes, flows, data = model_for(proc)
    return mk(str(proc["Kod"]), proc.get("Proces") or str(proc["Kod"]), proc, lanes, nodes, flows, data)

def check():
    bad = 0; warned = 0
    for proc in REG:
        kod = str(proc["Kod"])
        try:
            spec = spec_for(proc); warns = G.validate(spec)
            if warns:
                warned += 1; print("UWAGI %s: %s" % (kod, " | ".join(warns)))
        except Exception as e:
            bad += 1; print("BŁĄD %s: %s" % (kod, e))
    print("=== CHECK: %d procesów, %d z błędami, %d z uwagami ===" % (len(REG), bad, warned))
    return bad, warned

def build():
    OUT = os.path.join(ROOT, "out")
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    idx = os.path.join(OUT, "00_INDEKS"); os.makedirs(idx, exist_ok=True)
    manifest = []; errors = []
    for proc in REG:
        kod = str(proc["Kod"])
        try:
            spec = spec_for(proc); warns = G.validate(spec)
            pref = prefix_of(kod)
            wdir = WARSTWA_DIR.get(proc.get("Warstwa"), "9_Inne")
            gdir = "%s_%s" % (pref, slug(L1.get(pref, proc.get("Grupa procesowa") or "grupa"), 48))
            dest = os.path.join(OUT, wdir, gdir); os.makedirs(dest, exist_ok=True)
            base = os.path.join(dest, "%s__%s" % (kod, slug(proc.get("Proces"), 50)))
            res = G.generate(spec, base); svg_to_pdf(res["svg"], base + ".pdf"); os.remove(res["svg"])
            lanes = spec["pools"][0]["lanes"]
            manifest.append({"kod": kod, "proces": proc.get("Proces"), "warstwa": proc.get("Warstwa"),
                             "grupa": proc.get("Grupa procesowa"), "tory": [l["name"] for l in lanes],
                             "wlasciciel": proc.get("Właściciel (rola)"), "komorka": proc.get("Komórka org."),
                             "aktywa_AI": __import__("re").findall(r"AI-\d+", str(proc.get("Aktywa informacyjne (kody)") or "")),
                             "systemy": proc.get("Systemy / moduły (kody)"),
                             "dane_medyczne": proc.get("Dane medyczne (art. 9 RODO)"), "warnings": warns,
                             "pliki": {k: os.path.relpath(base + e, OUT) for k, e in (("bpmn",".bpmn"),("png",".png"),("pdf",".pdf"))}})
        except Exception as e:
            errors.append({"kod": kod, "error": str(e), "trace": traceback.format_exc()}); print("ERR %s: %s" % (kod, e))
    json.dump({"generated": datetime.datetime.now().isoformat(timespec="seconds"), "model": "docelowy (wielotorowy)",
               "liczba_procesow": len(manifest), "bledy": errors, "procesy": manifest},
              open(os.path.join(idx, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK: %d modeli, %d błędów, %d z uwagami" % (len(manifest), len(errors), sum(1 for m in manifest if m["warnings"])))
    return manifest, errors

if __name__ == "__main__":
    if "--check" in sys.argv: check()
    else: build()
