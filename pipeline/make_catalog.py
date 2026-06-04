#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_catalog.py - zbiorczy katalog PDF z osadzonym fontem Unicode (DejaVu) oraz
nagłówkiem (ID + tytuł) i stopką (klasyfikacja + Strona X/Y) wg wzoru dokumentacji SZBI.
Buduje katalog pełny i 3 per-warstwa. Diagramy osadzane z PNG (skalowane, w obszarze
między nagłówkiem a stopką)."""
import os, sys, json, datetime, re
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); ROOT=os.path.dirname(HERE)
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rcanvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONTDIR=os.path.join(os.path.dirname(__import__("matplotlib").__file__),"mpl-data","fonts","ttf")
pdfmetrics.registerFont(TTFont("DV", os.path.join(FONTDIR,"DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DVB", os.path.join(FONTDIR,"DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DVO", os.path.join(FONTDIR,"DejaVuSans-Oblique.ttf")))
F,FB,FO="DV","DVB","DVO"

OUT=os.path.join(ROOT,"out"); IDX=os.path.join(OUT,"00_INDEKS")
P=json.load(open(os.path.join(IDX,"manifest.json"),encoding="utf-8"))["procesy"]
PG=landscape(A4); PW,PH=PG
INK=(0.21,0.24,0.31); SOFT=(0.36,0.39,0.46); ACC=(0.227,0.357,0.549); LINE=(0.68,0.71,0.76)
ORG="Stobrawskie Centrum Medyczne Sp. z o.o."; KLAS="Wewnętrzna"
DOC_ID="SCM-PROC-KAT-001"; DOC_TITLE="Katalog docelowych modeli procesów (BPMN 2.0)"
LAYER_DIR={"Zarządczy":"1_Zarzadczy_Z","Główny":"2_Glowny_G","Wspierający":"3_Wspierajacy_W"}

def order(procs):
    def key(m):
        z=re.match(r"^([ZGW])(\d+)\.(\d+)",m["kod"]); g={"Z":0,"G":1,"W":2}[z.group(1)]
        return (g,int(z.group(2)),int(z.group(3)))
    return sorted(procs,key=key)

def deco(c, page, total, scope):
    # naglowek: ID + tytul (lewo), zakres (prawo) + linia
    c.setFillColor(INK); c.setFont(FB,8); c.drawString(12*mm, PH-9*mm, DOC_ID)
    w=pdfmetrics.stringWidth(DOC_ID,FB,8)
    c.setFillColor(SOFT); c.setFont(F,8); c.drawString(12*mm+w+3*mm, PH-9*mm, DOC_TITLE)
    c.drawRightString(PW-12*mm, PH-9*mm, scope)
    c.setStrokeColor(LINE); c.setLineWidth(0.6)
    c.line(12*mm, PH-11*mm, PW-12*mm, PH-11*mm)
    # stopka: organizacja + klasyfikacja (lewo), strona (prawo) + linia
    c.line(12*mm, 12*mm, PW-12*mm, 12*mm)
    c.setFillColor(SOFT); c.setFont(F,7.5)
    c.drawString(12*mm, 7.5*mm, f"{ORG} — Klasyfikacja: {KLAS}")
    c.drawRightString(PW-12*mm, 7.5*mm, f"Strona {page} / {total}")

def cover(c, title, sub, n, scope):
    c.setFillColor(ACC); c.rect(0, PH-46*mm, PW, 46*mm, fill=1, stroke=0)
    c.setFillColor((1,1,1)); c.setFont(FB,26); c.drawString(20*mm, PH-28*mm, "EUROSOC")
    c.setFont(F,13); c.drawString(20*mm, PH-37*mm, "Docelowe modele procesów · BPMN 2.0")
    # plakietka klasyfikacji (prawy gorny rog pasa)
    c.setFont(FB,9); c.drawRightString(PW-20*mm, PH-16*mm, f"Klasyfikacja: {KLAS}")
    c.setFont(F,8.5); c.drawRightString(PW-20*mm, PH-22*mm, DOC_ID)
    c.setFillColor(INK); c.setFont(FB,19); c.drawString(20*mm, PH-66*mm, title)
    c.setFillColor(SOFT); c.setFont(F,12)
    c.drawString(20*mm, PH-75*mm, sub)
    c.drawString(20*mm, PH-83*mm, f"Procesów w katalogu: {n}    ·    {scope}    ·    {datetime.datetime.now():%Y-%m-%d}")
    ov=os.path.join(IDX,"mapa_przegladowa.png")
    if os.path.exists(ov):
        img=ImageReader(ov); iw,ih=img.getSize(); maxw=PW-40*mm; maxh=PH-150*mm
        s=min(maxw/iw, maxh/ih); w,h=iw*s, ih*s
        c.drawImage(img, (PW-w)/2, 20*mm, w, h, preserveAspectRatio=True, mask='auto')
    c.setFillColor(SOFT); c.setFont(FO,8.5)
    c.drawString(20*mm, 11*mm, "Modele referencyjne (docelowe) do walidacji z właścicielami procesów. Nazwy ról z domeny SZBI wg Mapy dokumentacji SZBI v9.2.")

def toc_entries(procs):
    E=[]; last_l=last_g=None
    for m in order(procs):
        if m["warstwa"]!=last_l: last_l=m["warstwa"]; last_g=None; E.append(("layer", m["warstwa"].upper()))
        pr=re.match(r"^([ZGW]\d+)",m["kod"]).group(1)
        if pr!=last_g: last_g=pr; E.append(("group", f"{pr} — {(m.get('grupa') or '')[:44]}"))
        E.append(("proc", f"{m['kod']}  {m['proces'][:60]}"))
    return E

PERCOL=46
def draw_toc(c, chunk, first):
    if first:
        c.setFillColor(ACC); c.setFont(FB,14); c.drawString(12*mm, PH-19*mm, "Spis treści")
    x0=12*mm; colw=(PW-24*mm)/2.0
    for ci in range(2):
        col=chunk[ci*PERCOL:(ci+1)*PERCOL]; x=x0+ci*colw; y=PH-26*mm
        for typ,txt in col:
            if typ=="layer": c.setFont(FB,9.5); c.setFillColor(ACC); c.drawString(x, y, txt)
            elif typ=="group": c.setFont(F,8); c.setFillColor(SOFT); c.drawString(x+2*mm, y, txt)
            else: c.setFont(F,8); c.setFillColor(INK); c.drawString(x+4*mm, y, txt)
            y-=9.5

def draw_diagram(c, m):
    png=os.path.join(OUT, m["pliki"]["png"])
    if not os.path.exists(png): return
    img=ImageReader(png); iw,ih=img.getSize()
    band_top=PH-15*mm; band_bot=16*mm; maxw=PW-24*mm; maxh=band_top-band_bot
    s=min(maxw/iw, maxh/ih); w,h=iw*s, ih*s
    c.drawImage(img, (PW-w)/2, band_bot+(maxh-h)/2, w, h, preserveAspectRatio=True, mask='auto')

def build(procs, outfile, title, sub, scope):
    procs=order(procs)
    pages=[("cover",None)]
    ent=toc_entries(procs); per=PERCOL*2
    chunks=[ent[i:i+per] for i in range(0,len(ent),per)] or [[]]
    for j,ch in enumerate(chunks): pages.append(("toc",(ch,j==0)))
    for m in procs: pages.append(("diag",m))
    total=len(pages)
    c=rcanvas.Canvas(outfile, pagesize=PG)
    for pi,(kind,data) in enumerate(pages,1):
        if kind=="cover": cover(c,title,sub,len(procs),scope)
        elif kind=="toc": draw_toc(c,data[0],data[1]); deco(c,pi,total,scope)
        else: draw_diagram(c,data); deco(c,pi,total,scope)
        c.showPage()
    c.save(); print(f"{os.path.basename(outfile):46} {os.path.getsize(outfile)/1e6:5.1f} MB ({len(procs)} diagr., {total} str.)")

if __name__=="__main__":
    build(P, os.path.join(ROOT,"EUROSOC_BPMN_docelowe_katalog_pelny.pdf"),
          "Katalog wszystkich procesów", "Warstwy: Zarządcza · Główna · Wspierająca", "Wszystkie warstwy")
    for layer,d in LAYER_DIR.items():
        sub=[m for m in P if m["warstwa"]==layer]
        build(sub, os.path.join(ROOT,f"EUROSOC_BPMN_docelowe_katalog_{d.split('_',1)[1]}.pdf"),
              f"Katalog — warstwa {layer}", "Docelowe modele procesów · BPMN 2.0", f"Warstwa: {layer}")
