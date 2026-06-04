# Raport QA — pakiet docelowych modeli procesów SCM

Wygenerowano: 2026-06-04 14:37 · Procesów w rejestrze: **203**

## Kompletność
| Kontrola | Wynik | Status |
|---|---|---|
| Zgodność rejestr ↔ manifest | 203/203 (braki: 0, nadmiar: 0) | ✅ |
| Pliki `.bpmn` / `.png` / `.pdf` | 203 / 203 / 203 | ✅ |
| Brakujące pliki na dysku | 0 | ✅ |
| Błędy generowania (manifest) | 0 | ✅ |
| Procesy bez torów/nazwy | 0 | ✅ |

## Poprawność BPMN
| Kontrola | Wynik | Status |
|---|---|---|
| Walidacja struktury (start/koniec, osiągalność, bramki) | 203/203 bez uwag | ✅ |
| Pliki BPMN parsujące się jako XML | 203/203 | ✅ |

## Czytelność tekstu
| Kontrola | Wynik | Status |
|---|---|---|
| Ucięcia „…" w etykietach | 0 | ✅ |
| Linie tekstu poza obiektem/torem (po zawinięciu) | 0 | ✅ |
| Średnia liczba torów na proces | 2.41 | — |

## Nazewnictwo ról
Role z domeny bezpieczeństwa/IT/audytu/ryzyka ujednolicone ze słownikiem **SZBI v9.2**
(`szbi_roles.json`). Oryginalne nazwy jednostek i role kliniczne — bez zmian.

**Wniosek:** pakiet kompletny i spójny; wszystkie kontrole automatyczne zaliczone.
