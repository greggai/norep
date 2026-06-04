#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_overview.py - jednostronicowa mapa przeglądowa L0->L1->L2 (równy aspekt: realne koła)."""
import os, sys, json, re
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); ROOT=os.path.dirname(HERE)
from build_pkg import L1
from bpmn_generator import _wrap
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
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

# rowny aspekt: jednostki danych = cale (16x9) -> kola sa kolami
fig,ax=plt.subplots(figsize=(16,9)); ax.set_xlim(0,16); ax.set_ylim(0,9)
ax.set_aspect("equal"); ax.axis("off")
ax.text(8,8.62,"Architektura procesów SCM — mapa przeglądowa",ha="center",fontsize=18,fontweight="bold",color="#363D4E")
ax.text(8,8.24,f"3 warstwy · 25 grup · {len(P)} procesów (docelowe modele BPMN)",ha="center",fontsize=11,color="#5B6475")

MARGIN=0.4; GAP=0.4; COLW=(16-2*MARGIN-2*GAP)/3.0
TOP=7.8; BOT=0.4; HEADY=7.42; START=7.0; PITCH=0.62; BH=0.50
for ci,(layer,prefs) in enumerate(ORDER.items()):
    edge,fill=COL[layer]; x=MARGIN+ci*(COLW+GAP)
    tot=sum(cnt.get(pr,0) for pr in prefs)
    ax.add_patch(FancyBboxPatch((x,BOT),COLW,TOP-BOT,boxstyle="round,pad=0,rounding_size=0.06",
                                fill=True,facecolor=fill,edgecolor=edge,lw=2))
    ax.text(x+COLW/2,HEADY,f"{layer.upper()}  ({tot})",ha="center",fontsize=13,fontweight="bold",color=edge)
    y=START
    for pr in prefs:
        nm=L1.get(pr,pr); n=cnt.get(pr,0)
        ax.add_patch(FancyBboxPatch((x+0.14,y-BH),COLW-0.28,BH-0.06,boxstyle="round,pad=0,rounding_size=0.04",
                                    fill=True,facecolor="white",edgecolor=edge,lw=1.1))
        ax.text(x+0.30,y-0.16,pr,ha="left",va="center",fontsize=10.5,fontweight="bold",color=edge)
        ax.text(x+0.30,y-0.355,_wrap(nm,34),ha="left",va="top",fontsize=7.3,color="#363D4E",linespacing=0.92)
        cxx,cyy=x+COLW-0.34,y-0.225
        ax.add_patch(Circle((cxx,cyy),0.15,facecolor=edge,edgecolor="none"))
        ax.text(cxx,cyy,str(n),ha="center",va="center",fontsize=8.6,color="white",fontweight="bold")
        y-=PITCH
ax.text(8,0.16,"L0 (warstwy) → L1 (grupy procesowe) → L2 (procesy).  Liczba w kółku = liczba procesów w grupie.",
        ha="center",fontsize=8.2,color="#5B6475")
fig.savefig(os.path.join(IDX,"mapa_przegladowa.png"),dpi=170,bbox_inches="tight",facecolor="white")
fig.savefig(os.path.join(IDX,"mapa_przegladowa.pdf"),bbox_inches="tight",facecolor="white")
plt.close(fig); print("Mapa przeglądowa OK (równy aspekt)")
