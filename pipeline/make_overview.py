#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_overview.py - jednostronicowa mapa przeglądowa L0->L1->L2 (warstwy -> grupy -> procesy)."""
import os, sys, json, re
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); ROOT=os.path.dirname(HERE)
from build_pkg import L1
from bpmn_generator import _wrap
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
matplotlib.rcParams["font.family"]="DejaVu Sans"
IDX=os.path.join(ROOT,"out","00_INDEKS")
P=json.load(open(os.path.join(IDX,"manifest.json"),encoding="utf-8"))["procesy"]

ORDER={"Zarządczy":["Z1","Z2","Z3","Z4","Z5","Z6"],
       "Główny":["G1","G2","G3","G4","G5","G6","G7","G8","G9","G10"],
       "Wspierający":["W1","W2","W3","W4","W5","W6","W7","W8","W9"]}
cnt={}
for m in P:
    pr=re.match(r"^([ZGW]\d+)",m["kod"]).group(1); cnt[pr]=cnt.get(pr,0)+1
COL={"Zarządczy":("#3A5B8C","#EDF2FB"),"Główny":("#2E9E6B","#E9F6EF"),"Wspierający":("#C2872B","#FBF0DA")}

fig,ax=plt.subplots(figsize=(15,9)); ax.set_xlim(0,3); ax.set_ylim(0,12); ax.axis("off")
ax.text(1.5,11.55,"Architektura procesów SCM — mapa przeglądowa",ha="center",fontsize=17,fontweight="bold",color="#363D4E")
ax.text(1.5,11.16,f"3 warstwy · 25 grup · {len(P)} procesów (modele to-be BPMN)",ha="center",fontsize=10.5,color="#5B6475")
for ci,(layer,prefs) in enumerate(ORDER.items()):
    edge,fill=COL[layer]; x=ci+0.06; w=0.88
    tot=sum(cnt.get(pr,0) for pr in prefs)
    ax.add_patch(FancyBboxPatch((x,0.3),w,10.25,boxstyle="round,pad=0,rounding_size=0.04",
                                fill=True,facecolor=fill,edgecolor=edge,lw=2))
    ax.text(x+w/2,10.18,f"{layer.upper()}  ({tot})",ha="center",fontsize=12.5,fontweight="bold",color=edge)
    y=9.55; bh=0.86
    for pr in prefs:
        nm=L1.get(pr,pr); n=cnt.get(pr,0)
        ax.add_patch(FancyBboxPatch((x+0.06,y-bh+0.12),w-0.12,bh-0.16,boxstyle="round,pad=0,rounding_size=0.03",
                                    fill=True,facecolor="white",edgecolor=edge,lw=1.1))
        ax.text(x+0.16,y-0.16,pr,ha="left",va="top",fontsize=10,fontweight="bold",color=edge)
        ax.text(x+0.16,y-0.42,_wrap(nm,30),ha="left",va="top",fontsize=7.4,color="#363D4E")
        ax.add_patch(plt.Circle((x+w-0.16,y-0.28),0.11,facecolor=edge,edgecolor="none"))
        ax.text(x+w-0.16,y-0.28,str(n),ha="center",va="center",fontsize=8.2,color="white",fontweight="bold")
        y-=bh
ax.text(1.5,0.12,"L0 (warstwy) → L1 (grupy procesowe) → L2 (procesy). Liczba w kółku = liczba procesów w grupie.",
        ha="center",fontsize=8,color="#5B6475")
plt.tight_layout()
fig.savefig(os.path.join(IDX,"mapa_przegladowa.png"),dpi=170,bbox_inches="tight",facecolor="white")
fig.savefig(os.path.join(IDX,"mapa_przegladowa.pdf"),bbox_inches="tight",facecolor="white")
plt.close(fig); print("Mapa przeglądowa OK")
