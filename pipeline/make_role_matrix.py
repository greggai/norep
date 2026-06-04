#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_role_matrix.py - macierz pokrycia ról (SZBI i pełna) -> procesy, z manifestu."""
import json, os, csv
from collections import defaultdict
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
IDX=os.path.join(ROOT,"out","00_INDEKS")
P=json.load(open(os.path.join(IDX,"manifest.json"),encoding="utf-8"))["procesy"]
SR=json.load(open(os.path.join(ROOT,"data","szbi_roles.json"),encoding="utf-8"))
szbi_vocab=set(SR["role_szbi"]) | set(SR["mapowanie_proces_to_szbi"].values()) | {
    "Zespół reagowania IR","Administratorzy sieci","Koordynator BC","Właściciele ryzyka"}

role2proc=defaultdict(list)
for m in P:
    for r in m["tory"]:
        role2proc[r].append(m["kod"])

# 1) macierz ról SZBI -> procesy (MD + CSV)
szbi=sorted([(r,sorted(ks)) for r,ks in role2proc.items() if r in szbi_vocab], key=lambda x:(-len(x[1]),x[0]))
md=["# Macierz pokrycia ról SZBI → procesy","",
    f"Role z domeny SZBI (wg *Mapy dokumentacji SZBI v9.2*) użyte jako tory w modelach docelowych. "
    f"Łącznie ról SZBI w użyciu: **{len(szbi)}**.","",
    "| Rola (SZBI) | Procesów | Kody procesów |","|---|---:|---|"]
for r,ks in szbi:
    md.append(f"| {r} | {len(ks)} | {', '.join(ks)} |")
open(os.path.join(IDX,"macierz_rol_SZBI.md"),"w",encoding="utf-8").write("\n".join(md)+"\n")
with open(os.path.join(IDX,"macierz_rol_SZBI.csv"),"w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f,delimiter=";"); w.writerow(["Rola SZBI","Liczba procesów","Kody procesów"])
    for r,ks in szbi: w.writerow([r,len(ks),", ".join(ks)])

# 2) pełny indeks ról -> procesy (CSV)
allr=sorted(role2proc.items(), key=lambda x:(-len(x[1]),x[0]))
with open(os.path.join(IDX,"indeks_rol_pelny.csv"),"w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f,delimiter=";"); w.writerow(["Rola (tor)","SZBI?","Liczba procesów","Kody procesów"])
    for r,ks in allr: w.writerow([r,"tak" if r in szbi_vocab else "",len(ks),", ".join(sorted(ks))])
print(f"Macierz ról OK: {len(szbi)} ról SZBI, {len(allr)} ról łącznie")
