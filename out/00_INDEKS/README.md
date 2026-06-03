# EUROSOC · Modele procesów to-be (BPMN 2.0) - SCM

**Podmiot:** Stobrawskie Centrum Medyczne Sp. z o.o. · **Źródło:** Rejestr procesów SCM (L2) + analiza
**Procesów:** 203 · **Formaty:** `.bpmn` + `.png` + `.pdf` · **Średnio torów/proces:** 2.4

## Charakter modeli
Każdy z 203 procesów to **odrębny, wielotorowy model to-be** (BPMN 2.0) z:
- **torami = rolami/działami** (basen „SCM Sp. z o.o."), pokazującymi przekazania odpowiedzialności,
- **bramkami decyzyjnymi**, ścieżkami alternatywnymi, pętlami i **zdarzeniami brzegowymi** (wyjątki),
- **obiektami/magazynami danych** (artefakty procesu + aktywa informacyjne `AI-xx` z rejestru, w pasmie pod basenem),
- **stopką** z systemami (`AW`) i kategorią RODO - tylko kluczowe, czytelne informacje.

> **Status:** modele **referencyjne / to-be** - propozycja docelowego przebiegu do **walidacji z właścicielem
> procesu**. Opracowane na podstawie metadanych rejestru, otoczenia prawnego i dobrych praktyk; nie są zapisem
> zweryfikowanego stanu as-is. (Adnotacja prowieniencji - tu, w README, świadomie nie na diagramach.)

## Organizacja
Foldery: `1_Zarzadczy_Z/`, `2_Glowny_G/`, `3_Wspierajacy_W/` → 25 grup (L1). Plik: `KOD__nazwa.*`.

## Aktywa i zgodność
Aktywa informacyjne z rejestru naniesione dla **56/203** procesów; **90** procesów dotyka danych
medycznych (art. 9 RODO). Pełne nazwy kodów: `00_INDEKS/legenda_aktywow.csv`.

## Glify (PNG/PDF)
Zadania: **U** user · **S** service · **Sd** send · **Rc** receive · **Mn** manual · **Br** business rule.
Zdarzenia: **M** komunikat · **T** czas · zdarzenie brzegowe = okrąg na krawędzi zadania (przerywany = nieprzerywające).
Dane: prostokąt z zagięciem = obiekt danych; walec = magazyn (rejestr/baza/archiwum).

## Zawartość `00_INDEKS/`
- `indeks_procesow.csv` / `.md` - 203 procesów (kod, proces, tory/role, aktywa, pliki),
- `legenda_aktywow.csv` - słownik `AI-xx` / `AW-xx`,
- `manifest.json` - metadane generowania (tory, aktywa, walidacja),
- `BRAKI_mapowania_BPMN.md` + `intake_mapowanie_procesow.csv` - co uzupełnić, by przejść z to-be do zweryfikowanego as-is.

## Najczęstsze role w torach
- Zarząd: 42×
- Dział Informatyki: 22×
- Dział Personalno-Płacowy: 17×
- Dział Finansowo-Księgowy: 17×
- Dział Techniczny: 16×
- Pielęgniarka: 15×
- Dział Organizacyjno-Prawny: 14×
- Dział Rozliczeń Świadczeń: 9×
- Dział Zamówień Publicznych: 9×
- Lekarz: 9×
- Sekcja Dokumentacji Medycznej: 8×
- Rada Nadzorcza: 7×
