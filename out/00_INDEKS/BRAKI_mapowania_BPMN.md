# Braki danych do PEŁNEGO mapowania procesów w BPMN — rejestr SCM

> Cel dokumentu: wskazać **dokładnie, czego brakuje w pliku xlsx**, aby zamodelować
> każdy z 203 procesów jako **odrębny, kompletny i poprawny model BPMN 2.0** zgodnie ze
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
| Kod, nazwa, warstwa, charakter, grupa (L1) | 203/203 | tożsamość, foldery, dobór wzorca |
| Właściciel (rola) — 1 na proces | 203/203 | **tor (lane)** |
| Komórka organizacyjna — 1 na proces | 203/203 | **basen (pool)** |
| Flagi RODO (dane osobowe / medyczne art. 9) | 203/203 | adnotacja zgodności (osob.: 158, med.: 90) |
| Aktywa informacyjne (kody AI) | 56/203 | **obiekty danych** powiązane z czynnościami |
| Systemy / moduły (kody AW) | 60/203 | adnotacja (systemy wspierające) |
| Uwagi / warianty | 16/203 | kontekst, warianty (np. kanały AI) |
| Ref. modelu L3 (nazwa pliku) | 16/203 | wskazanie istniejącego modelu docelowego |
| Mapa komórka→grupa (`Indeks dział-proces`) | tak | role/komórki uczestniczące w grupie |
| Otoczenie prawne (akty per obszar) | tak | podstawy prawne (kontekst zgodności) |

## 3. Czego brakuje — wg metody 5 kroków modelowania (skill)
| Krok metody | Co potrzebne do modelu | Stan w xlsx | Luka |
|---|---|---|---|
| **1. Granice** | zdarzenie początkowe i końcowe + **wyzwalacz** (typ: komunikat/czas/sygnał) | brak | **KRYTYCZNA** |
| **2. Czynności i zdarzenia** | uporządkowana **lista kroków** („czasownik+rzeczownik") | 0/203 | **KRYTYCZNA — główny brak** |
| **3. Zasoby i przekazania → TORY** | **która rola/dział wykonuje który krok** (handoffy) | tylko 1 właściciel na CAŁY proces, nie per krok | **KRYTYCZNA — to jest brak „torów z działami"** |
| **4. Przepływ sterowania** | kolejność, **bramki** (XOR/AND/OR), warunki gałęzi, pętle | brak | **KRYTYCZNA** |
| **5. Elementy dodatkowe** | dane **per krok**, komunikaty między basenami, **wyjątki** | aktywa tylko zbiorczo dla 56 proc.; brak message flow; brak wyjątków | WYSOKA |
| **+ Portfel / miary** | Znaczenie / Kondycja / Wykonalność / Priorytet | **0/203 (puste)** | ŚREDNIA (selekcja, nie rysunek) |
| **+ Powiązania międzyprocesowe** | wejścia/wyjścia, granice między procesami | luźne wzmianki w Uwagach | ŚREDNIA |

### Dlaczego „tory z działami" nie wynikają w pełni z arkusza
Rejestr podaje **jedną** odpowiedzialną komórkę i **jedną** rolę na cały proces — wystarcza to na
**jeden tor** (i tyle dziś rysujemy). Diagram wielotorowy z **przekazaniami** wymaga informacji,
**kto wykonuje każdy pojedynczy krok** (np. w diagnostyce: lekarz zlecający → pracownia → opisujący;
w przyjęciu: rejestracja → pielęgniarka → lekarz). Tego przypisania krok→rola w arkuszu **nie ma** —
arkusz `Indeks dział-proces` mapuje komórki tylko do **grup**, nie do kroków.

## 4. Braki cząstkowe — listy procesów
**Bez zmapowanych aktywów informacyjnych (147/203)** — do uzupełnienia kolumna „Aktywa AI per krok":
  Z1.01, Z1.02, Z1.03, Z1.04, Z1.05, Z1.06, Z1.07, Z1.08, Z1.09, Z1.10, Z1.11, Z2.01, Z2.02, Z2.03, Z2.04, Z2.05, Z2.06, Z2.07
  Z2.08, Z3.01, Z3.02, Z3.03, Z3.04, Z3.05, Z4.01, Z4.02, Z4.03, Z4.04, Z4.05, Z4.06, Z4.07, Z4.08, Z4.09, Z4.10, Z5.01, Z5.02
  Z5.03, Z5.04, Z6.01, Z6.02, Z6.03, G5.01, G5.02, G5.03, G5.04, G5.05, G5.06, G5.07, G5.08, G6.01, G6.02, G6.03, G6.04, G6.05
  G7.01, G7.02, G7.03, G7.04, G7.05, G7.06, G7.07, G7.08, G9.01, G9.02, G9.03, G9.04, G9.05, G10.01, G10.02, G10.03, W1.01, W1.02
  W1.03, W1.04, W1.05, W1.06, W1.07, W1.08, W1.09, W1.10, W2.01, W2.02, W2.03, W2.04, W2.05, W2.06, W2.07, W2.08, W2.09, W2.10
  W2.11, W2.12, W2.13, W2.14, W3.01, W3.02, W3.03, W3.04, W3.05, W3.06, W3.07, W4.02, W4.03, W4.04, W4.05, W4.06, W4.07, W4.08
  W4.09, W4.11, W4.12, W5.01, W5.02, W5.03, W5.04, W5.05, W5.06, W5.07, W5.08, W5.09, W5.10, W5.11, W6.02, W6.03, W6.04, W6.05
  W6.06, W7.01, W7.02, W7.03, W7.04, W7.05, W7.06, W7.07, W7.08, W7.09, W8.01, W8.02, W8.03, W8.04, W8.05, W8.06, W9.01, W9.02
  W9.03, W9.04, W9.05

**Bez wskazanych systemów (143/203)**:
  Z1.01, Z1.02, Z1.03, Z1.04, Z1.05, Z1.06, Z1.07, Z1.08, Z1.09, Z1.10, Z1.11, Z2.01, Z2.02, Z2.03, Z2.04, Z2.05, Z2.06, Z2.07
  Z2.08, Z3.01, Z3.02, Z3.03, Z3.04, Z3.05, Z4.01, Z4.02, Z4.03, Z4.04, Z4.05, Z4.06, Z4.07, Z4.08, Z4.09, Z4.10, Z5.01, Z5.02
  Z5.03, Z5.04, Z6.01, Z6.02, Z6.03, G5.01, G5.02, G5.03, G5.04, G5.05, G5.06, G5.07, G5.08, G6.01, G6.02, G6.03, G6.04, G6.05
  G7.01, G7.02, G7.03, G7.04, G7.05, G7.06, G7.07, G7.08, G9.01, G9.02, G9.03, G9.04, G9.05, G10.01, G10.02, G10.03, W1.01, W1.02
  W1.03, W1.04, W1.05, W1.06, W1.07, W1.08, W1.09, W1.10, W2.01, W2.02, W2.03, W2.04, W2.05, W2.06, W2.07, W2.08, W2.09, W2.10
  W2.11, W2.12, W2.13, W2.14, W3.01, W3.02, W3.03, W3.04, W3.05, W3.06, W3.07, W4.02, W4.03, W4.07, W4.09, W4.11, W4.12, W5.01
  W5.02, W5.03, W5.04, W5.05, W5.06, W5.07, W5.08, W5.09, W5.10, W5.11, W6.02, W6.03, W6.04, W6.05, W6.06, W7.01, W7.02, W7.03
  W7.04, W7.05, W7.06, W7.07, W7.08, W7.09, W8.01, W8.02, W8.03, W8.04, W8.05, W8.06, W9.01, W9.02, W9.03, W9.04, W9.05

**Dotyczy wszystkich 203 procesów:** brak kroków, ról-per-krok, bramek, zdarzeń/wyzwalaczy i wyjątków
(sekcja 3) oraz miar portfela (0/203).

## 5. Jak uzupełnić — formularz `intake_mapowanie_procesow.csv`
Jeden wiersz na proces; kolumny „znane" są **prewypełnione** z rejestru, kolumny „DO UZUPEŁNIENIA" są puste:

| Kolumna (DO UZUPEŁNIENIA) | Co wpisać | Po co |
|---|---|---|
| `Zdarzenie_startowe` + `Typ_startu` | czym proces się zaczyna (np. „wpłynął wniosek"); typ: message/timer/signal/none | krok 1 — granice |
| `Kroki` | kroki po kolei, rozdzielone `\|`, styl „czasownik+rzeczownik" | krok 2 — czynności |
| `Role_per_krok` | rola/dział dla każdego kroku, w tej samej kolejności, `\|` | krok 3 — **tory/przekazania** |
| `Bramki_decyzje` | decyzje: `po kroku N: pytanie? -> tak: ... / nie: ...` | krok 4 — sterowanie |
| `Wyjatki` | zdarzenia brzegowe/wyjątki (np. „timeout", „odrzucenie") | krok 5 |
| `Zdarzenia_koncowe` | jeden lub kilka stanów końcowych | krok 1 — granice |
| `Aktywa_per_krok` | które AI-xx powstają/są używane w którym kroku | krok 5 — dane |
| `Komunikaty_miedzyprocesowe` | wejścia/wyjścia do innych procesów lub stron zewn. | powiązania |
| `Znaczenie/Kondycja/Wykonalnosc` | skala 1–5 (portfel) | priorytetyzacja |

**Minimum, by uzyskać pełny, odrębny model:** `Kroki` + `Role_per_krok` + `Bramki_decyzje` +
`Zdarzenia_koncowe`. Reszta podnosi wierność i kompletność.

## 6. Warianty realizacji pełnego mapowania
- **A. Uzupełnienie intake** (najwierniejsze as-is) — właściciele procesów wypełniają `intake_*.csv`;
  generuję pełne, wielotorowe, odrębne modele BPMN + PNG + PDF.
- **B. Istniejące modele L3** — dostarczasz 16 plików `.bpmn` z kolumny „Model BPMN (L3)";
  wkomponowuję realne przepływy zamiast szkieletów.
- **C. Wzorcowe modele to-be** — przygotowuję odrębne, kompletne propozycje przebiegu per proces
  na bazie metadanych + `Otoczenie prawne` + dobrych praktyk branżowych; jako **propozycja do
  walidacji** z właścicielem (nie deklaracja stanu as-is). Najszybsze do uzyskania „pełnych i różnych"
  diagramów bez czekania na warsztaty.

*Uwaga dot. rzetelności: dla podmiotu leczniczego nie „dopowiadam" kroków klinicznych jako stanu
faktycznego. Wariant C oznacza jawnie modele referencyjne/to-be do zatwierdzenia.*
