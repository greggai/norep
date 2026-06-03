#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_zips.py - pakuje out/ w ZIP-y do dostawy:
  - EUROSOC_BPMN_pakiet_procesow_SCM_v1.zip  (pelny, wszystkie warstwy)
  - EUROSOC_BPMN_{1_Zarzadczy,2_Glowny,3_Wspierajacy}.zip  (per warstwa, samowystarczalne
    - kazda paczka zawiera wlasny folder 00_INDEKS).
Uruchom po build_pkg.py + make_docs.py.
"""
import zipfile, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
LAYERS = ["1_Zarzadczy_Z", "2_Glowny_G", "3_Wspierajacy_W"]

def addtree(z, base, arcroot):
    n = 0
    for dp, _, fs in os.walk(base):
        for fn in sorted(fs):
            full = os.path.join(dp, fn)
            z.write(full, os.path.join(arcroot, os.path.relpath(full, OUT)))
            n += 1
    return n

def build(zname, dirs):
    root = zname[:-4]
    path = os.path.join(ROOT, zname)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        n = 0
        for d in dirs:
            n += addtree(z, os.path.join(OUT, d), root)
    print(f"{zname:42} {os.path.getsize(path)/1e6:5.1f} MB ({n} plikow)")

if __name__ == "__main__":
    build("EUROSOC_BPMN_pakiet_procesow_SCM_v1.zip", ["00_INDEKS"] + LAYERS)
    for d in LAYERS:
        build("EUROSOC_BPMN_%s.zip" % d.rsplit("_", 1)[0], ["00_INDEKS", d])
