# EUROSOC · Pakiet diagramów BPMN procesów SCM

**Podmiot:** Stobrawskie Centrum Medyczne Sp. z o.o. · **Źródło:** Rejestr procesów SCM (mapa BPM, v14)
**Wygenerowano:** 2026-06-03T20:57:20 · **Procesów:** 203 · **Formaty:** `.bpmn` + `.png` + `.pdf`

## Co zawiera pakiet
Dla **każdego z 203 procesów** z rejestru (poziom L2) wygenerowano komplet:
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

Pokrycie z rejestru: **56/203** procesów ma zmapowane aktywa AI, **60/203**
ma wskazane systemy, **90** procesów dotyka danych medycznych (art. 9 RODO).
Dla procesów bez mapowania stopka zawiera notę „brak zmapowanych aktywów AI w rejestrze".

## Glify (podgląd PNG/PDF)
Typy zadań: **U** user · **S** service · **Sd** send · **Rc** receive · **Mn** manual · **Sc** script · **Br** business rule.
Zdarzenia: **M** komunikat · **T** czas · **●** terminate. Aktywa: prostokąt z zagięciem = obiekt danych; walec = magazyn (rejestr/baza/archiwum).

## Zawartość `00_INDEKS/`
- `indeks_procesow.csv` - pełna tabela 203 procesów (kod, proces, właściciel, aktywa, RODO, ścieżki plików),
- `indeks_procesow.md` - czytelny indeks pogrupowany warstwami i grupami,
- `legenda_aktywow.csv` - słownik kodów `AI-xx` i `AW-xx` (pełne nazwy, klasyfikacja P/I/D, RODO),
- `manifest.json` - metadane generowania (użyty wzorzec, uwagi walidacji, hash źródła) dla każdego procesu.

## Status modelowania
W rejestrze **16** procesów oznaczono jako „Zamodelowany (L3)" - mają osobne, docelowe modele
(kolumna „Model BPMN (L3)"); tutejszy diagram jest dla nich szkicem zastępczym (oznaczonym w stopce).

## Rozkład użytych wzorców
- G3: 23
- W2: 14
- W4: 14
- Z1: 11
- W5: 11
- Z4: 10
- W1: 10
- Z2: 9
- G1: 9
- W7: 9
- G5: 8
- G7: 8
- G2: 7
- W3: 7
- G8: 6
- W6: 6
- W8: 6
- G6: 5
- G9: 5
- W9: 5
- Z3: 4
- G4: 4
- incydent: 3
- Z5: 3
- Z6: 3
- G10: 3

---
*Walidacja strukturalna (start/koniec, brak węzłów wiszących, osiągalność, bramki) - wszystkie 203 modele bez uwag.*
