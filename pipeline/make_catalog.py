#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_catalog.py - zbiorczy katalog PDF (okładka + mapa + spis treści + 203 diagramy).
Buduje katalog pełny oraz 3 per-warstwa. Diagramy osadzane z PNG (skalowane do strony)."""
import os, sys, json, datetime, re
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); ROOT=os.path.dirname(HERE)
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rcanvas
OUT=os.path.join(ROOT,"out"); IDX=os.path.join(OUT,"00_INDEKS")
P=json.load(open(os.path.join(IDX,"manifest.json"),encoding="utf-8"))["procesy"]
PG=landscape(A4); PW,PH=PG
INK="#363D4E"; SOFT="#5B6475"; ACC="#3A5B8C"
LAYER_DIR={"Zarządczy":"1_Zarzadczy_Z","Główny":"2_Glowny_G","Wspierający":"3_Wspierajacy_W"}
def _hex(c): return tuple(int(c[i:i+2],16)/255 for i in (1,3,5))

def order(procs):
    def key(m):
        mm_=re.match(r"^([ZGW])(\d+)\.(\d+)",m["kod"]); g={"Z":0,"G":1,"W":2}[mm_.group(1)]
        return (g,int(mm_.group(2)),int(mm_.group(3)))
    return sorted(procs,key=key)

def cover(c,title,sub,n):
    c.setFillColor(_hex(ACC)); c.rect(0,PH-46*mm,PW,46*mm,fill=1,stroke=0)
    c.setFillColor((1,1,1)); c.setFont("Helvetica-Bold",26); c.drawString(24*mm,PH-30*mm,"EUROSOC")
    c.setFont("Helvetica",13); c.drawString(24*mm,PH-39*mm,"Modele procesów to-be · BPMN 2.0")
    c.setFillColor(_hex(INK)); c.setFont("Helvetica-Bold",19); c.drawString(24*mm,PH-70*mm,title)
    c.setFillColor(_hex(SOFT)); c.setFont("Helvetica",12)
    c.drawString(24*mm,PH-80*mm,sub)
    c.drawString(24*mm,PH-88*mm,f"Procesów w katalogu: {n}    ·    Wygenerowano: {datetime.datetime.now():%Y-%m-%d}")
    ov=os.path.join(IDX,"mapa_przegladowa.png")
    if os.path.exists(ov):
        img=ImageReader(ov); iw,ih=img.getSize(); maxw=PW-48*mm; maxh=PH-150*mm
        s=min(maxw/iw,maxh/ih); w,h=iw*s,ih*s
        c.drawImage(img,(PW-w)/2,18*mm,w,h,preserveAspectRatio=True,mask='auto')
    c.setFont("Helvetica-Oblique",8.5); c.setFillColor(_hex(SOFT))
    c.drawString(24*mm,10*mm,"Modele referencyjne/to-be do walidacji z właścicielami procesów. Nazwy ról z domeny SZBI wg Mapy dokumentacji SZBI v9.2.")
    c.showPage()

def toc(c,procs):
    c.setFillColor(_hex(INK)); c.setFont("Helvetica-Bold",16); c.drawString(20*mm,PH-22*mm,"Spis treści")
    x0=20*mm; y=PH-32*mm; col_w=(PW-40*mm)/2; col=0; x=x0
    last_layer=last_grp=None
    c.setFont("Helvetica",8.2)
    for m in order(procs):
        pr=re.match(r"^([ZGW]\d+)",m["kod"]).group(1)
        if m["warstwa"]!=last_layer:
            last_layer=m["warstwa"]; last_grp=None
            if y<26*mm:
                col+=1; x=x0+col*col_w; y=PH-32*mm
                if col>1: c.showPage(); col=0; x=x0; y=PH-22*mm; c.setFont("Helvetica",8.2)
            c.setFillColor(_hex(ACC)); c.setFont("Helvetica-Bold",10); c.drawString(x,y,m["warstwa"].upper()); y-=5.2*mm; c.setFont("Helvetica",8.2)
        if pr!=last_grp:
            last_grp=pr; c.setFillColor(_hex(SOFT))
            c.drawString(x,y,f"  {pr} — {m['grupa'][:46] if m.get('grupa') else ''}"); y-=4.4*mm
        c.setFillColor(_hex(INK))
        c.drawString(x+3*mm,y,f"{m['kod']}  {m['proces'][:52]}"); y-=4.0*mm
        if y<20*mm:
            col+=1
            if col>1: c.showPage(); col=0; y=PH-22*mm; c.setFont("Helvetica",8.2)
            x=x0+col*col_w; y=PH-22*mm
    c.showPage()

def diagram_page(c,m,idx,total):
    png=os.path.join(OUT,m["pliki"]["png"])
    if not os.path.exists(png): return
    img=ImageReader(png); iw,ih=img.getSize()
    maxw=PW-24*mm; maxh=PH-26*mm; s=min(maxw/iw,maxh/ih); w,h=iw*s,ih*s
    c.drawImage(img,(PW-w)/2,(PH-h)/2-3*mm,w,h,preserveAspectRatio=True,mask='auto')
    c.setFillColor(_hex(SOFT)); c.setFont("Helvetica",7.5)
    c.drawString(12*mm,7*mm,f"{m['warstwa']} · {m.get('grupa','')}")
    c.drawRightString(PW-12*mm,7*mm,f"{m['kod']}   ·   {idx}/{total}")
    c.showPage()

def build(procs,outfile,title,sub):
    procs=order(procs); c=rcanvas.Canvas(outfile,pagesize=PG)
    cover(c,title,sub,len(procs)); toc(c,procs)
    for i,m in enumerate(procs,1): diagram_page(c,m,i,len(procs))
    c.save(); print(f"{os.path.basename(outfile):42} {os.path.getsize(outfile)/1e6:5.1f} MB ({len(procs)} diagr.)")

if __name__=="__main__":
    build(P,os.path.join(ROOT,"EUROSOC_BPMN_to-be_katalog_pelny.pdf"),
          "Katalog wszystkich procesów","Warstwy: Zarządcza · Główna · Wspierająca")
    for layer,d in LAYER_DIR.items():
        sub=order([m for m in P if m["warstwa"]==layer])
        build(sub,os.path.join(ROOT,f"EUROSOC_BPMN_to-be_katalog_{d.split('_',1)[1]}.pdf"),
              f"Katalog — warstwa {layer}","Modele to-be BPMN 2.0")
