#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_docs_tobe.py - indeksy + README + legenda dla pakietu docelowych modeli procesów."""
import json, os, csv
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
IDX = os.path.join(ROOT, "out", "00_INDEKS")
M = json.load(open(os.path.join(IDX, "manifest.json"), encoding="utf-8"))
A = json.load(open(os.path.join(ROOT, "data", "assets.json"), encoding="utf-8")); AI, AW = A["AI"], A["AW"]
P = M["procesy"]

with open(os.path.join(IDX, "indeks_procesow.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["Kod","Proces","Warstwa","Grupa","Tory (role)","Wlasciciel","Komorka","Aktywa AI","Systemy","Dane medyczne","BPMN","PNG","PDF"])
    for m in P:
        w.writerow([m["kod"],m["proces"],m["warstwa"],m["grupa"]," / ".join(m["tory"]),m["wlasciciel"],m["komorka"],
                    ", ".join(m["aktywa_AI"]),m.get("systemy") or "",m.get("dane_medyczne") or "",
                    m["pliki"]["bpmn"],m["pliki"]["png"],m["pliki"]["pdf"]])

with open(os.path.join(IDX, "legenda_aktywow.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, delimiter=";"); w.writerow(["Typ","Kod","Nazwa","Kategoria/Typ","RODO","P","I","D"])
    for k,v in AI.items(): w.writerow(["AI",k,v.get("nazwa"),v.get("kat"),v.get("RODO"),v.get("P"),v.get("I"),v.get("D")])
    for k,v in AW.items(): w.writerow(["AW",k,v.get("nazwa"),v.get("typ"),"","","",""])

by = {}
for m in P: by.setdefault(m["warstwa"], {}).setdefault(m["grupa"], []).append(m)
lines = ["# Indeks procesów - docelowe modele procesów (wielotorowe BPMN)","",
         f"Procesów: **{len(P)}** · Formaty: BPMN + PNG + PDF · Walidacja: {sum(1 for m in P if not m['warnings'])}/{len(P)} bez uwag",""]
for wars in ["Zarządczy","Główny","Wspierający"]:
    if wars not in by: continue
    lines.append(f"## {wars} ({sum(len(v) for v in by[wars].values())})")
    for grupa in sorted(by[wars]):
        lines.append(f"\n### {grupa}\n\n| Kod | Proces | Tory (role) | Aktywa AI |\n|---|---|---|---|")
        for m in sorted(by[wars][grupa], key=lambda x: x["kod"]):
            lines.append(f"| {m['kod']} | {m['proces']} | {' / '.join(m['tory'])} | {len(m['aktywa_AI']) or '-'} |")
    lines.append("")
open(os.path.join(IDX, "indeks_procesow.md"), "w", encoding="utf-8").write("\n".join(lines))

n_ai = sum(1 for m in P if m["aktywa_AI"]); n_med = sum(1 for m in P if str(m.get("dane_medyczne") or "").strip().lower()=="tak")
avg_lanes = sum(len(m["tory"]) for m in P)/len(P)
roles = Counter(r for m in P for r in m["tory"])
README = f"""# EUROSOC · Docelowe modele procesów (BPMN 2.0) - SCM

**Podmiot:** Stobrawskie Centrum Medyczne Sp. z o.o. · **Źródło:** Rejestr procesów SCM (L2) + analiza
**Procesów:** {len(P)} · **Formaty:** `.bpmn` + `.png` + `.pdf` · **Średnio torów/proces:** {avg_lanes:.1f}

## Charakter modeli
Każdy z {len(P)} procesów to **odrębny, wielotorowy model docelowy** (BPMN 2.0) z:
- **torami = rolami/działami** (basen „SCM Sp. z o.o."), pokazującymi przekazania odpowiedzialności,
- **bramkami decyzyjnymi**, ścieżkami alternatywnymi, pętlami i **zdarzeniami brzegowymi** (wyjątki),
- **obiektami/magazynami danych** (artefakty procesu + aktywa informacyjne `AI-xx` z rejestru, w pasmie pod basenem),
- **stopką** z systemami (`AW`) i kategorią RODO - tylko kluczowe, czytelne informacje.

> **Status:** modele **referencyjne (docelowe)** - propozycja docelowego przebiegu do **walidacji z właścicielem
> procesu**. Opracowane na podstawie metadanych rejestru, otoczenia prawnego i dobrych praktyk; nie są zapisem
> zweryfikowanego stanu obecnego. (Adnotacja prowieniencji - tu, w README, świadomie nie na diagramach.)

## Organizacja
Foldery: `1_Zarzadczy_Z/`, `2_Glowny_G/`, `3_Wspierajacy_W/` → 25 grup (L1). Plik: `KOD__nazwa.*`.

## Zgodność nazewnictwa ról z SZBI
Role w torach z domeny **bezpieczeństwa informacji / IT / audytu / ryzyka / zmian** ujednolicono ze
słownikiem **Mapy dokumentacji SZBI v9.2** (te same nazwy w procesach i w dokumentacji SZBI), m.in.:
`IOD`, `Pełnomocnik ds. SZBI`, `Kierownik IT`, `Administratorzy IT`, `Administratorzy sieci`,
`Audytorzy wewnętrzni`, `Zespół reagowania IR`, `CAB`, `Koordynator BC`, `Właściciele ryzyka`,
`Właściciele procesów`, `Wnioskodawcy`. **Oryginalne nazwy jednostek** (Dział Personalno-Płacowy,
Dział Zamówień Publicznych, Radca prawny, Dział Organizacyjno-Prawny, Zarząd…) oraz **role
kliniczne/medyczne pozostają bez zmian**. Pełny słownik i mapowanie: `00_INDEKS/szbi_roles.json`.

## Aktywa i zgodność
Aktywa informacyjne z rejestru naniesione dla **{n_ai}/{len(P)}** procesów; **{n_med}** procesów dotyka danych
medycznych (art. 9 RODO). Pełne nazwy kodów: `00_INDEKS/legenda_aktywow.csv`.

## Glify (PNG/PDF)
Zadania: **U** user · **S** service · **Sd** send · **Rc** receive · **Mn** manual · **Br** business rule.
Zdarzenia: **M** komunikat · **T** czas · zdarzenie brzegowe = okrąg na krawędzi zadania (przerywany = nieprzerywające).
Dane: prostokąt z zagięciem = obiekt danych; walec = magazyn (rejestr/baza/archiwum).

## Zawartość `00_INDEKS/`
- `mapa_przegladowa.png` / `.pdf` - jednostronicowa architektura L0→L1→L2 (warstwy → grupy → procesy),
- `indeks_procesow.csv` / `.md` - {len(P)} procesów (kod, proces, tory/role, aktywa, pliki),
- `macierz_rol_SZBI.csv` / `.md` + `indeks_rol_pelny.csv` - pokrycie ról (SZBI i pełne) → procesy,
- `szbi_roles.json` - słownik ról SZBI v9.2 + mapowanie na role w procesach,
- `legenda_aktywow.csv` - słownik `AI-xx` / `AW-xx`,
- `RAPORT_QA.md` - wynik kontroli jakości (kompletność, poprawność BPMN, czytelność tekstu),
- `manifest.json` - metadane generowania (tory, aktywa, walidacja),
- `BRAKI_mapowania_BPMN.md` + `intake_mapowanie_procesow.csv` - co uzupełnić, by przejść od modelu docelowego do zweryfikowanego stanu obecnego.

Dodatkowo (poza folderem, w paczce nadrzędnej): **`EUROSOC_BPMN_docelowe_katalog_*.pdf`** - zbiorczy
katalog (okładka + mapa + spis treści + wszystkie diagramy) w wersji pełnej i per-warstwa.

## Najczęstsze role w torach
{chr(10).join(f"- {r}: {c}×" for r, c in roles.most_common(12))}
"""
open(os.path.join(IDX, "README.md"), "w", encoding="utf-8").write(README)
# dołącz słownik ról SZBI do pakietu
import shutil
_src = os.path.join(ROOT, "data", "szbi_roles.json")
if os.path.exists(_src):
    shutil.copy(_src, os.path.join(IDX, "szbi_roles.json"))
print("Docs OK:", len(P), "procesów,", n_ai, "z aktywami, śr. torów", round(avg_lanes,2))
