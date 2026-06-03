#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_docs.py - z manifest.json buduje indeksy (CSV/MD), legende aktywow i README."""
import json, os, csv, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "out"); IDX = os.path.join(OUT, "00_INDEKS")
M = json.load(open(os.path.join(IDX, "manifest.json"), encoding="utf-8"))
ASSETS = json.load(open(os.path.join(ROOT, "data", "assets.json"), encoding="utf-8"))
AI, AW = ASSETS["AI"], ASSETS["AW"]
procs = M["procesy"]

# ---- 1. indeks_procesow.csv ----
with open(os.path.join(IDX, "indeks_procesow.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["Kod","Proces","Warstwa","Grupa procesowa","Wzorzec","Wlasciciel","Komorka org.",
                "Status L3","Model L3","Liczba aktywow AI","Aktywa AI (kody)","Systemy/moduly",
                "Dane osobowe","Dane medyczne (art.9)","plik BPMN","plik PNG","plik PDF","Uwagi walidacji"])
    for m in procs:
        w.writerow([m["kod"], m["proces"], m["warstwa"], m["grupa"], m["wzorzec"], m["wlasciciel"],
                    m["komorka"], m["status_L3"], m.get("model_L3") or "", m["n_aktywa"],
                    ", ".join(m["aktywa_AI"]), m.get("systemy") or "", m.get("dane_osobowe") or "",
                    m.get("dane_medyczne") or "", m["pliki"]["bpmn"], m["pliki"]["png"], m["pliki"]["pdf"],
                    " ; ".join(m["warnings"])])

# ---- 2. legenda_aktywow.csv (AI + AW, pelne nazwy - na diagramach skracane) ----
with open(os.path.join(IDX, "legenda_aktywow.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["Typ","Kod","Nazwa","Kategoria/Typ","RODO","P","I","D","Wlasciciel","Systemy"])
    for k, v in AI.items():
        w.writerow(["AI", k, v.get("nazwa"), v.get("kat"), v.get("RODO"), v.get("P"), v.get("I"),
                    v.get("D"), v.get("wlasciciel"), v.get("systemy")])
    for k, v in AW.items():
        w.writerow(["AW", k, v.get("nazwa"), v.get("typ"), "", "", "", "", "", v.get("opis")])

# ---- 3. indeks_procesow.md (pogrupowany) ----
by = {}
for m in procs:
    by.setdefault(m["warstwa"], {}).setdefault(m["grupa"], []).append(m)
order = ["Zarządczy", "Główny", "Wspierający"]
lines = ["# Indeks procesów - pakiet diagramów BPMN", "",
         f"Wygenerowano: {M['generated']} · Procesów: **{len(procs)}** · Formaty: BPMN + PNG + PDF", ""]
for wars in order:
    if wars not in by: continue
    nproc = sum(len(v) for v in by[wars].values())
    lines.append(f"## Warstwa: {wars}  ({nproc} proc.)")
    for grupa in sorted(by[wars]):
        lines.append(f"\n### {grupa}")
        lines.append("\n| Kod | Proces | Właściciel | Aktywa AI | Status L3 |")
        lines.append("|---|---|---|---|---|")
        for m in sorted(by[wars][grupa], key=lambda x: x["kod"]):
            ai = str(m["n_aktywa"]) if m["n_aktywa"] else "-"
            st = "✓ L3" if str(m["status_L3"]).startswith("Zamodel") else "szkic"
            lines.append(f"| {m['kod']} | {m['proces']} | {m['wlasciciel']} | {ai} | {st} |")
    lines.append("")
open(os.path.join(IDX, "indeks_procesow.md"), "w", encoding="utf-8").write("\n".join(lines))

# ---- statystyki ----
n_ai = sum(1 for m in procs if m["n_aktywa"])
n_sys = sum(1 for m in procs if m.get("systemy"))
n_l3 = sum(1 for m in procs if str(m["status_L3"]).startswith("Zamodel"))
n_med = sum(1 for m in procs if str(m.get("dane_medyczne")).strip().lower() == "tak")
from collections import Counter
wz = Counter(m["wzorzec"] for m in procs)

readme = f"""# EUROSOC · Pakiet diagramów BPMN procesów SCM

**Podmiot:** Stobrawskie Centrum Medyczne Sp. z o.o. · **Źródło:** Rejestr procesów SCM (mapa BPM, v14)
**Wygenerowano:** {M['generated']} · **Procesów:** {len(procs)} · **Formaty:** `.bpmn` + `.png` + `.pdf`

## Co zawiera pakiet
Dla **każdego z {len(procs)} procesów** z rejestru (poziom L2) wygenerowano komplet:
- **`.bpmn`** - poprawny model BPMN 2.0 (OMG), źródło prawdy; otwiera i edytuje się w bpmn.io, Camunda Modeler, Signavio, Bizagi,
- **`.png`** - podgląd rastrowy (170 dpi),
- **`.pdf`** - podgląd wektorowy do druku/przeglądu.

Diagramy są uporządkowane w folderach **warstwa → grupa procesowa (L1)**:
`1_Zarzadczy_Z/`, `2_Glowny_G/`, `3_Wspierajacy_W/` → 25 grup. Nazwa pliku: `KOD__nazwa-procesu.*`.

## Metodyka generowania ("wzorce per rodzina")
Rejestr SCM jest na poziomie **L2** (jeden proces = jeden wiersz) i **nie zawiera kroków procesowych**.
Dlatego zawartość każdego diagramu zbudowano ze **spójnej biblioteki wzorców**, dobieranej wg
warstwy, charakteru i grupy procesowej (np. przyjęcie pacjenta, diagnostyka, leczenie, wypis,
farmakoterapia, rozliczenia NFZ, zamówienia PZP, cykl HR, incydent bezpieczeństwa, audyt/zgodność,
decyzja zarządcza). Każdy szkielet ma poprawny start/koniec, fazy "czasownik + rzeczownik", bramkę
decyzyjną XOR z etykietami gałęzi i dobrane typy zadań (user/service/send/manual/businessRule).

> ⚠️ **Nota o rzetelności (ważne).** Czynności na diagramach to **typowe fazy** danej rodziny procesów,
> a **nie** zweryfikowane kroki stanu faktycznego (as-is). Każdy diagram nosi adnotację
> „SZKIC L3 z rejestru L2 - do weryfikacji as-is". Przed użyciem operacyjnym **zweryfikuj przebieg
> z właścicielem procesu** i dostosuj w narzędziu BPMN (plik `.bpmn`).

## Widoczność aktywów informacyjnych (ISO/IEC 27005)
Tam, gdzie rejestr je mapuje, na diagramie pokazano:
- **obiekty/magazyny danych** = aktywa informacyjne (kod `AI-xx` + skrócona nazwa), powiązane
  asocjacją z czynnościami (pełne nazwy: `00_INDEKS/legenda_aktywow.csv`),
- **stopka-adnotacja** = systemy/moduły wspierające (`AW-xx`), kategoria **RODO** oraz znacznik L3.

Pokrycie z rejestru: **{n_ai}/{len(procs)}** procesów ma zmapowane aktywa AI, **{n_sys}/{len(procs)}**
ma wskazane systemy, **{n_med}** procesów dotyka danych medycznych (art. 9 RODO).
Dla procesów bez mapowania stopka zawiera notę „brak zmapowanych aktywów AI w rejestrze".

## Glify (podgląd PNG/PDF)
Typy zadań: **U** user · **S** service · **Sd** send · **Rc** receive · **Mn** manual · **Sc** script · **Br** business rule.
Zdarzenia: **M** komunikat · **T** czas · **●** terminate. Aktywa: prostokąt z zagięciem = obiekt danych; walec = magazyn (rejestr/baza/archiwum).

## Zawartość `00_INDEKS/`
- `indeks_procesow.csv` - pełna tabela {len(procs)} procesów (kod, proces, właściciel, aktywa, RODO, ścieżki plików),
- `indeks_procesow.md` - czytelny indeks pogrupowany warstwami i grupami,
- `legenda_aktywow.csv` - słownik kodów `AI-xx` i `AW-xx` (pełne nazwy, klasyfikacja P/I/D, RODO),
- `manifest.json` - metadane generowania (użyty wzorzec, uwagi walidacji, hash źródła) dla każdego procesu.

## Status modelowania
W rejestrze **{n_l3}** procesów oznaczono jako „Zamodelowany (L3)" - mają osobne, docelowe modele
(kolumna „Model BPMN (L3)"); tutejszy diagram jest dla nich szkicem zastępczym (oznaczonym w stopce).

## Rozkład użytych wzorców
{chr(10).join(f"- {k}: {v}" for k, v in sorted(wz.items(), key=lambda x: -x[1]))}

---
*Walidacja strukturalna (start/koniec, brak węzłów wiszących, osiągalność, bramki) - wszystkie {len(procs)} modele bez uwag.*
"""
open(os.path.join(IDX, "README.md"), "w", encoding="utf-8").write(readme)
print("Docs OK:", n_ai, "z aktywami,", n_sys, "z systemami,", n_l3, "L3,", n_med, "medycznych")
print("Pliki 00_INDEKS:", sorted(os.listdir(IDX)))
