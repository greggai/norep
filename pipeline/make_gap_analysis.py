#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_gap_analysis.py - analiza braków danych do PEŁNEGO mapowania BPMN
   + formularz intake (1 wiersz/proces) do uzupełnienia przez właścicieli procesów.
   Wynik: out/00_INDEKS/BRAKI_mapowania_BPMN.md, out/00_INDEKS/intake_mapowanie_procesow.csv
"""
import json, os, csv, re
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
IDX = os.path.join(ROOT, "out", "00_INDEKS"); os.makedirs(IDX, exist_ok=True)
REG = json.load(open(os.path.join(ROOT, "data", "register.json"), encoding="utf-8"))
N = len(REG)

def has(p, k): return bool(str(p.get(k) or "").strip())
n_ai   = sum(1 for p in REG if has(p, "Aktywa informacyjne (kody)"))
n_sys  = sum(1 for p in REG if has(p, "Systemy / moduły (kody)"))
n_uw   = sum(1 for p in REG if has(p, "Uwagi"))
n_l3   = sum(1 for p in REG if str(p.get("Status modelowania","")).startswith("Zamodel"))
n_med  = sum(1 for p in REG if str(p.get("Dane medyczne (art. 9 RODO)") or "").strip().lower()=="tak")
n_os   = sum(1 for p in REG if str(p.get("Dane osobowe (RODO)") or "").strip().lower()=="tak")
no_ai  = [p["Kod"] for p in REG if not has(p, "Aktywa informacyjne (kody)")]
no_sys = [p["Kod"] for p in REG if not has(p, "Systemy / moduły (kody)")]
n_own  = len(set(p["Właściciel (rola)"] for p in REG))
n_unit = len(set(p["Komórka org."] for p in REG))

def codes_block(codes, per=18):
    return "\n".join("  " + ", ".join(codes[i:i+per]) for i in range(0, len(codes), per))

md = f"""# Braki danych do PEŁNEGO mapowania procesów w BPMN — rejestr SCM

> Cel dokumentu: wskazać **dokładnie, czego brakuje w pliku xlsx**, aby zamodelować
> każdy z {N} procesów jako **odrębny, kompletny i poprawny model BPMN 2.0** zgodnie ze
> skillem (metoda 5 kroków + warstwa aktywów ISO 27005 + reguły 7PMG). Dołączony formularz
> `intake_mapowanie_procesow.csv` pozwala uzupełnić te braki w ustrukturyzowany sposób.

## 1. Wniosek (TL;DR)
Załączony rejestr to **poziom L2 — katalog nazwanych procesów z metadanymi** (jeden wiersz =
jeden proces). Zweryfikowano twardo: brak ukrytych arkuszy, komentarzy, scaleń i kolumn poza 18.
**Z samego xlsx nie da się wygenerować odrębnych, w pełni zmapowanych przepływów**, ponieważ
brakuje całej **warstwy przepływu**: listy kroków, ich kolejności, logiki decyzji (bramek),
przypisania ról do poszczególnych kroków (tory/przekazania), zdarzeń i ścieżek wyjątków.
To dlatego procesy w obrębie jednej grupy mają ten sam szkielet — odróżniają je dziś tylko
metadane (tor/komórka, aktywa, systemy), a nie rzeczywisty przebieg.

## 2. Co arkusz JUŻ dostarcza (punkt wyjścia — wykorzystane na diagramach)
| Dana | Pokrycie | Zastosowanie w modelu |
|---|---|---|
| Kod, nazwa, warstwa, charakter, grupa (L1) | {N}/{N} | tożsamość, foldery, dobór wzorca |
| Właściciel (rola) — 1 na proces | {N}/{N} | **tor (lane)** |
| Komórka organizacyjna — 1 na proces | {N}/{N} | **basen (pool)** |
| Flagi RODO (dane osobowe / medyczne art. 9) | {N}/{N} | adnotacja zgodności (osob.: {n_os}, med.: {n_med}) |
| Aktywa informacyjne (kody AI) | {n_ai}/{N} | **obiekty danych** powiązane z czynnościami |
| Systemy / moduły (kody AW) | {n_sys}/{N} | adnotacja (systemy wspierające) |
| Uwagi / warianty | {n_uw}/{N} | kontekst, warianty (np. kanały AI) |
| Ref. modelu L3 (nazwa pliku) | {n_l3}/{N} | wskazanie istniejącego modelu docelowego |
| Mapa komórka→grupa (`Indeks dział-proces`) | tak | role/komórki uczestniczące w grupie |
| Otoczenie prawne (akty per obszar) | tak | podstawy prawne (kontekst zgodności) |

## 3. Czego brakuje — wg metody 5 kroków modelowania (skill)
| Krok metody | Co potrzebne do modelu | Stan w xlsx | Luka |
|---|---|---|---|
| **1. Granice** | zdarzenie początkowe i końcowe + **wyzwalacz** (typ: komunikat/czas/sygnał) | brak | **KRYTYCZNA** |
| **2. Czynności i zdarzenia** | uporządkowana **lista kroków** („czasownik+rzeczownik") | 0/{N} | **KRYTYCZNA — główny brak** |
| **3. Zasoby i przekazania → TORY** | **która rola/dział wykonuje który krok** (handoffy) | tylko 1 właściciel na CAŁY proces, nie per krok | **KRYTYCZNA — to jest brak „torów z działami"** |
| **4. Przepływ sterowania** | kolejność, **bramki** (XOR/AND/OR), warunki gałęzi, pętle | brak | **KRYTYCZNA** |
| **5. Elementy dodatkowe** | dane **per krok**, komunikaty między basenami, **wyjątki** | aktywa tylko zbiorczo dla {n_ai} proc.; brak message flow; brak wyjątków | WYSOKA |
| **+ Portfel / miary** | Znaczenie / Kondycja / Wykonalność / Priorytet | **0/{N} (puste)** | ŚREDNIA (selekcja, nie rysunek) |
| **+ Powiązania międzyprocesowe** | wejścia/wyjścia, granice między procesami | luźne wzmianki w Uwagach | ŚREDNIA |

### Dlaczego „tory z działami" nie wynikają w pełni z arkusza
Rejestr podaje **jedną** odpowiedzialną komórkę i **jedną** rolę na cały proces — wystarcza to na
**jeden tor** (i tyle dziś rysujemy). Diagram wielotorowy z **przekazaniami** wymaga informacji,
**kto wykonuje każdy pojedynczy krok** (np. w diagnostyce: lekarz zlecający → pracownia → opisujący;
w przyjęciu: rejestracja → pielęgniarka → lekarz). Tego przypisania krok→rola w arkuszu **nie ma** —
arkusz `Indeks dział-proces` mapuje komórki tylko do **grup**, nie do kroków.

## 4. Braki cząstkowe — listy procesów
**Bez zmapowanych aktywów informacyjnych ({len(no_ai)}/{N})** — do uzupełnienia kolumna „Aktywa AI per krok":
{codes_block(no_ai)}

**Bez wskazanych systemów ({len(no_sys)}/{N})**:
{codes_block(no_sys)}

**Dotyczy wszystkich {N} procesów:** brak kroków, ról-per-krok, bramek, zdarzeń/wyzwalaczy i wyjątków
(sekcja 3) oraz miar portfela (0/{N}).

## 5. Jak uzupełnić — formularz `intake_mapowanie_procesow.csv`
Jeden wiersz na proces; kolumny „znane" są **prewypełnione** z rejestru, kolumny „DO UZUPEŁNIENIA" są puste:

| Kolumna (DO UZUPEŁNIENIA) | Co wpisać | Po co |
|---|---|---|
| `Zdarzenie_startowe` + `Typ_startu` | czym proces się zaczyna (np. „wpłynął wniosek"); typ: message/timer/signal/none | krok 1 — granice |
| `Kroki` | kroki po kolei, rozdzielone `\\|`, styl „czasownik+rzeczownik" | krok 2 — czynności |
| `Role_per_krok` | rola/dział dla każdego kroku, w tej samej kolejności, `\\|` | krok 3 — **tory/przekazania** |
| `Bramki_decyzje` | decyzje: `po kroku N: pytanie? -> tak: ... / nie: ...` | krok 4 — sterowanie |
| `Wyjatki` | zdarzenia brzegowe/wyjątki (np. „timeout", „odrzucenie") | krok 5 |
| `Zdarzenia_koncowe` | jeden lub kilka stanów końcowych | krok 1 — granice |
| `Aktywa_per_krok` | które AI-xx powstają/są używane w którym kroku | krok 5 — dane |
| `Komunikaty_miedzyprocesowe` | wejścia/wyjścia do innych procesów lub stron zewn. | powiązania |
| `Znaczenie/Kondycja/Wykonalnosc` | skala 1–5 (portfel) | priorytetyzacja |

**Minimum, by uzyskać pełny, odrębny model:** `Kroki` + `Role_per_krok` + `Bramki_decyzje` +
`Zdarzenia_koncowe`. Reszta podnosi wierność i kompletność.

## 6. Warianty realizacji pełnego mapowania
- **A. Uzupełnienie intake** (najwierniejszy stan obecny) — właściciele procesów wypełniają `intake_*.csv`;
  generuję pełne, wielotorowe, odrębne modele BPMN + PNG + PDF.
- **B. Istniejące modele L3** — dostarczasz {n_l3} plików `.bpmn` z kolumny „Model BPMN (L3)";
  wkomponowuję realne przepływy zamiast szkieletów.
- **C. Wzorcowe modele docelowe** — przygotowuję odrębne, kompletne propozycje przebiegu per proces
  na bazie metadanych + `Otoczenie prawne` + dobrych praktyk branżowych; jako **propozycja do
  walidacji** z właścicielem (nie deklaracja stanu obecnego). Najszybsze do uzyskania „pełnych i różnych"
  diagramów bez czekania na warsztaty.

*Uwaga dot. rzetelności: dla podmiotu leczniczego nie „dopowiadam" kroków klinicznych jako stanu
faktycznego. Wariant C oznacza jawnie modele referencyjne (docelowe) do zatwierdzenia.*
"""
open(os.path.join(IDX, "BRAKI_mapowania_BPMN.md"), "w", encoding="utf-8").write(md)

# ---- intake CSV ----
cols_known = ["Kod","Proces","Warstwa","Charakter","Grupa procesowa",
              "[znane] Wlasciciel (tor)","[znane] Komorka org. (basen)",
              "[znane] Aktywa AI","[znane] Systemy","[znane] RODO dane osobowe","[znane] RODO dane medyczne",
              "[znane] Ref. model L3"]
cols_fill = ["Zdarzenie_startowe","Typ_startu (message/timer/signal/none)","Kroki (1|2|3...)",
             "Role_per_krok (1|2|3...)","Bramki_decyzje (po kroku N: pytanie -> tak:.. / nie:..)",
             "Wyjatki","Zdarzenia_koncowe (1|2..)","Aktywa_per_krok (krok:AI-xx)",
             "Komunikaty_miedzyprocesowe","Znaczenie 1-5","Kondycja 1-5","Wykonalnosc 1-5","Uwagi"]
with open(os.path.join(IDX, "intake_mapowanie_procesow.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, delimiter=";"); w.writerow(cols_known + cols_fill)
    for p in REG:
        w.writerow([p["Kod"], p["Proces"], p["Warstwa"], p["Charakter"], p["Grupa procesowa"],
                    p["Właściciel (rola)"], p["Komórka org."], p.get("Aktywa informacyjne (kody)") or "",
                    p.get("Systemy / moduły (kody)") or "", p.get("Dane osobowe (RODO)") or "",
                    p.get("Dane medyczne (art. 9 RODO)") or "", p.get("Model BPMN (L3)") or ""]
                   + [""]*len(cols_fill))
print(f"OK. Braki: aktywa {N-n_ai}, systemy {N-n_sys}, kroki/role/bramki {N} (wszystkie), KPI {N}.")
print("Pliki:", [x for x in sorted(os.listdir(IDX)) if 'BRAK' in x or 'intake' in x])
