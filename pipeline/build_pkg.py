#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pkg.py - automatyczny generator pakietu diagramow BPMN (.bpmn + .png + .pdf)
dla wszystkich procesow z rejestru SCM (poziom L2).

Wejscie:
  data/register.json  - 203 procesy (eksport z arkusza 'Rejestr procesow')
  data/assets.json    - katalogi aktywow informacyjnych (AI) i wspierajacych (AW)

Metoda (uzgodniona):
  - "Wzorce per rodzina": szkielet przeplywu dobierany wg prefiksu grupy procesowej
    (Z1..Z6, G1..G10, W1..W9) + warianty slowowe (incydent). Czynnosci to FAZY
    procesu (czasownik+rzeczownik), nie zweryfikowane kroki as-is -> kazdy diagram
    nosi adnotacje 'szkic L3 z rejestru L2 - do weryfikacji as-is'.
  - "Aktywa jako obiekty danych + adnotacja": aktywa informacyjne z kol. 'Aktywa
    informacyjne (kody)' renderowane jako obiekty/magazyny danych (kod AI + nazwa
    z katalogu) powiazane asocjacja z czynnosciami; adnotacje: wlasciciel, komorka
    org., systemy (AW), RODO, warstwa/charakter, status L3.

Wyjscie: out/<warstwa>/<grupa L1>/<KOD>__<nazwa>.{bpmn,png,pdf} + 00_INDEKS/*.
"""
import json, os, re, sys, shutil, hashlib, datetime, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bpmn_generator as G  # vendored skill generator

REG = json.load(open(os.path.join(ROOT, "data", "register.json"), encoding="utf-8"))
ASSETS = json.load(open(os.path.join(ROOT, "data", "assets.json"), encoding="utf-8"))
AI = ASSETS["AI"]; AW = ASSETS["AW"]
OUT = os.path.join(ROOT, "out")

# ---------------------------------------------------------------- helpers
_PL = str.maketrans({"ą":"a","ć":"c","ę":"e","ł":"l","ń":"n","ó":"o","ś":"s","ż":"z","ź":"z",
                     "Ą":"A","Ć":"C","Ę":"E","Ł":"L","Ń":"N","Ó":"O","Ś":"S","Ż":"Z","Ź":"Z"})
def slug(s, n=60):
    s = (s or "").translate(_PL)
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")
    return s[:n].strip("-") or "x"

def short(s, n=26):
    s = (s or "").strip()
    return s if len(s) <= n else s[:n-1] + "…"

WARSTWA_DIR = {"Zarządczy": "1_Zarzadczy_Z", "Główny": "2_Glowny_G", "Wspierający": "3_Wspierajacy_W"}
# kanoniczne nazwy 25 grup L1 (foldery) - prefiks -> nazwa
L1 = {
 "Z1":"Nadzor korporacyjny i strategia","Z2":"Systemy zgodnosci (ZSZ, SZBI, Akredytacja)",
 "Z3":"Zarzadzanie ryzykiem i ciagloscia dzialania","Z4":"Zgodnosc regulacyjna",
 "Z5":"Polityki, regulaminy i zarzadzanie zmiana","Z6":"Kontrakt NFZ i relacje zewnetrzne",
 "G1":"Wejscie pacjenta","G2":"Diagnostyka","G3":"Leczenie i rehabilitacja",
 "G4":"Wypis i kontynuacja opieki","G5":"Apteka szpitalna i farmakoterapia","G6":"Pielegniarstwo",
 "G7":"Higiena, epidemiologia, zakazenia","G8":"Dokumentacja medyczna i archiwum",
 "G9":"Rozliczenia swiadczen NFZ i statystyka","G10":"Transport medyczny",
 "W1":"Finanse i rachunkowosc","W2":"HR Kadry-Place","W3":"Zamowienia publiczne i zakupy",
 "W4":"IT cyfryzacja cyberbezpieczenstwo","W5":"Infrastruktura techniczna i media",
 "W6":"Sprawy organizacyjno-prawne","W7":"BHP P-POZ i sprawy obronne","W8":"Inwestycje i rozwoj",
 "W9":"Komunikacja i obsluga pacjenta nieklinicznego",
}
def prefix_of(kod):
    m = re.match(r"^([ZGW]\d+)", str(kod or ""))
    return m.group(1) if m else "X"

CODE_RE = re.compile(r"AI-\d+", re.I)
def parse_assets(s):
    return [c.upper() for c in CODE_RE.findall(str(s or ""))]

STORE_HINTS = ("rejestr","ewidencj","baza","repozytorium","archiw","kartotek","indeks","dziennik","ksieg")
def asset_node_type(code):
    nm = (AI.get(code, {}).get("nazwa") or "") + " " + (AI.get(code, {}).get("kat") or "")
    return "dataStore" if any(h in nm.lower() for h in STORE_HINTS) else "dataObjectReference"

# ---------------------------------------------------------------- wzorce
# Kazdy wzorzec: (start_name, start_evt, steps[(key,type,name)], ends[(key,name,evt)],
#                 edges[(src,tgt,label,default)], asset_hosts[keys])
def PAT(prefix):
    P = {}
    P["Z1"] = ("Inicjatywa / wniosek", "message",
        [("a1","userTask","Przygotuj materiały i analizę"),
         ("a2","userTask","Zaopiniuj wniosek"),
         ("g1","exclusiveGateway","Zatwierdzić?"),
         ("a3","sendTask","Zakomunikuj i wdróż decyzję")],
        [("e_ok","Decyzja podjęta",None),("e_no","Wniosek odrzucony",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","g1",None,0),
         ("g1","a3","tak",1),("g1","e_no","nie",0),("a3","e_ok",None,0)],
        ["a1","a2"])
    P["Z2"] = ("Plan audytów / przegląd", "timer",
        [("a1","userTask","Zaplanuj audyt / ocenę zgodności"),
         ("a2","manualTask","Przeprowadź audyt"),
         ("a3","businessRuleTask","Oceń niezgodności"),
         ("g1","exclusiveGateway","Niezgodności?"),
         ("a4","userTask","Uruchom działania korygujące"),
         ("a5","userTask","Przeprowadź przegląd zarządzania")],
        [("e_ok","Zgodność potwierdzona",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","g1",None,0),
         ("g1","a4","tak",0),("g1","a5","nie",1),("a4","a5",None,0),("a5","e_ok",None,0)],
        ["a2","a3"])
    P["Z3"] = ("Identyfikacja ryzyka / zdarzenia", "message",
        [("a1","userTask","Przeanalizuj i oceń ryzyko"),
         ("g1","exclusiveGateway","Akceptowalne?"),
         ("a2","userTask","Zaplanuj postępowanie z ryzykiem"),
         ("a3","serviceTask","Wdróż zabezpieczenia / plan ciągłości"),
         ("a4","userTask","Monitoruj i przeglądaj")],
        [("e_ok","Ryzyko pod kontrolą",None),("e_acc","Ryzyko zaakceptowane",None)],
        [("s","a1",None,0),("a1","g1",None,0),("g1","e_acc","tak",0),("g1","a2","nie",1),
         ("a2","a3",None,0),("a3","a4",None,0),("a4","e_ok",None,0)],
        ["a1","a2"])
    P["Z4"] = ("Wymóg / zdarzenie zgodności", "message",
        [("a1","businessRuleTask","Oceń zgodność i obowiązki"),
         ("g1","exclusiveGateway","Zgodne?"),
         ("a2","userTask","Wdróż środki naprawcze"),
         ("a3","sendTask","Raportuj organowi / interesariuszom"),
         ("a4","userTask","Nadzoruj utrzymanie zgodności")],
        [("e_ok","Zgodność zapewniona",None)],
        [("s","a1",None,0),("a1","g1",None,0),("g1","a4","tak",1),("g1","a2","nie",0),
         ("a2","a3",None,0),("a3","a4",None,0),("a4","e_ok",None,0)],
        ["a1","a2"])
    P["Z5"] = ("Inicjacja zmiany / polityki", "message",
        [("a1","userTask","Opracuj projekt regulacji"),
         ("a2","userTask","Przeprowadź konsultacje i opiniowanie"),
         ("g1","exclusiveGateway","Zatwierdzono?"),
         ("a3","serviceTask","Opublikuj i zakomunikuj"),
         ("a4","userTask","Wdróż i nadzoruj stosowanie")],
        [("e_ok","Regulacja obowiązuje",None),("e_rev","Skierowano do poprawy",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","g1",None,0),
         ("g1","a3","tak",1),("g1","e_rev","nie",0),("a3","a4",None,0),("a4","e_ok",None,0)],
        ["a1","a2"])
    P["Z6"] = ("Postępowanie / zapotrzebowanie NFZ", "timer",
        [("a1","userTask","Przygotuj ofertę i dane"),
         ("a2","userTask","Prowadź negocjacje / postępowanie"),
         ("g1","exclusiveGateway","Zawarto umowę?"),
         ("a3","userTask","Zawrzyj umowę / aneks"),
         ("a4","serviceTask","Realizuj i monitoruj kontrakt")],
        [("e_ok","Kontrakt realizowany",None),("e_no","Brak rozstrzygnięcia",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","g1",None,0),
         ("g1","a3","tak",1),("g1","e_no","nie",0),("a3","a4",None,0),("a4","e_ok",None,0)],
        ["a1","a4"])
    P["G1"] = ("Zgłoszenie / skierowanie pacjenta", "message",
        [("a1","userTask","Zweryfikuj tożsamość i uprawnienia"),
         ("a2","businessRuleTask","Zakwalifikuj do przyjęcia"),
         ("g1","exclusiveGateway","Kwalifikuje się?"),
         ("a3","userTask","Zarejestruj i załóż/aktualizuj dokumentację"),
         ("a4","sendTask","Skieruj do właściwej opieki")],
        [("e_ok","Pacjent przyjęty",None),("e_no","Pacjent niezakwalifikowany",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","g1",None,0),
         ("g1","a3","tak",1),("g1","e_no","nie",0),("a3","a4",None,0),("a4","e_ok",None,0)],
        ["a1","a3"])
    P["G2"] = ("Zlecenie badania", "message",
        [("a1","manualTask","Pobierz materiał / przygotuj pacjenta"),
         ("a2","manualTask","Wykonaj badanie"),
         ("a3","userTask","Opisz i autoryzuj wynik"),
         ("g1","exclusiveGateway","Powtórzyć badanie?"),
         ("a4","serviceTask","Przekaż wynik do dokumentacji")],
        [("e_ok","Wynik dostępny",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","g1",None,0),
         ("g1","a2","tak",0),("g1","a4","nie",1),("a4","e_ok",None,0)],
        ["a2","a3","a4"])
    P["G3"] = ("Kwalifikacja do leczenia / terapii", "message",
        [("a1","userTask","Ustal plan leczenia / terapii"),
         ("a2","manualTask","Realizuj świadczenia",{"loop":True}),
         ("a3","userTask","Oceń efekty i stan pacjenta"),
         ("g1","exclusiveGateway","Kontynuować leczenie?"),
         ("a4","userTask","Udokumentuj przebieg leczenia")],
        [("e_ok","Leczenie zakończone",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","g1",None,0),
         ("g1","a2","tak",0),("g1","a4","nie",1),("a4","e_ok",None,0)],
        ["a1","a2","a4"])
    P["G4"] = ("Decyzja o zakończeniu hospitalizacji", "message",
        [("a1","userTask","Wystaw dokumenty wypisowe"),
         ("a2","userTask","Określ zalecenia, recepty i skierowania"),
         ("a3","sendTask","Przekaż do kontynuacji opieki")],
        [("e_ok","Pacjent wypisany",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","e_ok",None,0)],
        ["a1","a2"])
    P["G5"] = ("Zapotrzebowanie / zlecenie leku", "message",
        [("a1","businessRuleTask","Zweryfikuj zlecenie (walidacja farmaceutyczna)"),
         ("g1","exclusiveGateway","Zatwierdzone?"),
         ("a2","manualTask","Przygotuj i wydaj produkt leczniczy"),
         ("a3","serviceTask","Zaewidencjonuj wydanie i obrót")],
        [("e_ok","Lek wydany",None),("e_no","Zlecenie do wyjaśnienia",None)],
        [("s","a1",None,0),("a1","g1",None,0),("g1","a2","tak",1),("g1","e_no","nie",0),
         ("a2","a3",None,0),("a3","e_ok",None,0)],
        ["a1","a3"])
    P["G6"] = ("Zlecenie / rozpoczęcie opieki", "message",
        [("a1","userTask","Oceń stan pacjenta"),
         ("a2","userTask","Zaplanuj opiekę pielęgniarską"),
         ("a3","manualTask","Wykonaj czynności opiekuńcze",{"loop":True}),
         ("a4","userTask","Udokumentuj opiekę")],
        [("e_ok","Opieka zrealizowana",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","a4",None,0),("a4","e_ok",None,0)],
        ["a1","a4"])
    P["G7"] = ("Sygnał / zdarzenie epidemiologiczne", "message",
        [("a1","userTask","Przeprowadź dochodzenie epidemiologiczne"),
         ("a2","businessRuleTask","Oceń ryzyko zakażenia"),
         ("g1","exclusiveGateway","Wymaga interwencji?"),
         ("a3","serviceTask","Wdróż działania zapobiegawcze"),
         ("a4","sendTask","Zaraportuj (SANEPID / rejestry)")],
        [("e_ok","Zagrożenie opanowane",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","g1",None,0),
         ("g1","a3","tak",1),("g1","a4","nie",0),("a3","a4",None,0),("a4","e_ok",None,0)],
        ["a1","a2","a4"])
    P["G8"] = ("Wniosek / zdarzenie dot. dokumentacji", "message",
        [("a1","businessRuleTask","Zweryfikuj podstawę i uprawnienia"),
         ("g1","exclusiveGateway","Podstawa zasadna?"),
         ("a2","userTask","Przygotuj / udostępnij / zarchiwizuj dokumentację"),
         ("a3","serviceTask","Zaewidencjonuj operację")],
        [("e_ok","Sprawa załatwiona",None),("e_no","Odmowa udostępnienia",None)],
        [("s","a1",None,0),("a1","g1",None,0),("g1","a2","tak",1),("g1","e_no","nie",0),
         ("a2","a3",None,0),("a3","e_ok",None,0)],
        ["a1","a2"])
    P["G9"] = ("Okres rozliczeniowy", "timer",
        [("a1","serviceTask","Zbierz dane o świadczeniach"),
         ("a2","businessRuleTask","Zwaliduj i zgrupuj (JGP / ryczałt)"),
         ("a3","sendTask","Prześlij komunikaty do NFZ"),
         ("g1","exclusiveGateway","Przyjęto bez błędów?"),
         ("a4","userTask","Skoryguj dane")],
        [("e_ok","Świadczenia rozliczone",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","g1",None,0),
         ("g1","e_ok","tak",1),("g1","a4","nie",0),("a4","a3",None,0)],
        ["a1","a2"])
    P["G10"] = ("Zlecenie transportu", "message",
        [("a1","userTask","Zaplanuj i przydziel transport"),
         ("a2","manualTask","Zrealizuj przewóz"),
         ("a3","userTask","Udokumentuj realizację")],
        [("e_ok","Transport zrealizowany",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","e_ok",None,0)],
        ["a1","a3"])
    P["W1"] = ("Dokument finansowy / zdarzenie księgowe", "message",
        [("a1","userTask","Zweryfikuj i zadekretuj dokument"),
         ("g1","exclusiveGateway","Zgodny?"),
         ("a2","serviceTask","Zaksięguj / zrealizuj płatność"),
         ("a3","serviceTask","Zarchiwizuj i ujmij w sprawozdaniu")],
        [("e_ok","Operacja zaksięgowana",None),("e_no","Zwrot do wyjaśnienia",None)],
        [("s","a1",None,0),("a1","g1",None,0),("g1","a2","tak",1),("g1","e_no","nie",0),
         ("a2","a3",None,0),("a3","e_ok",None,0)],
        ["a1","a3"])
    P["W2"] = ("Wniosek / zdarzenie kadrowe", "message",
        [("a1","userTask","Zweryfikuj formalnie i kompletność"),
         ("g1","exclusiveGateway","Spełnia wymogi?"),
         ("a2","userTask","Zrealizuj czynność kadrową"),
         ("a3","serviceTask","Zaktualizuj akta i naliczenia")],
        [("e_ok","Sprawa kadrowa załatwiona",None),("e_no","Wniosek zwrócony",None)],
        [("s","a1",None,0),("a1","g1",None,0),("g1","a2","tak",1),("g1","e_no","nie",0),
         ("a2","a3",None,0),("a3","e_ok",None,0)],
        ["a1","a3"])
    P["W3"] = ("Potrzeba zakupowa", "message",
        [("a1","businessRuleTask","Ustal tryb postępowania"),
         ("a2","userTask","Przeprowadź postępowanie"),
         ("g1","exclusiveGateway","Wybrano wykonawcę?"),
         ("a3","userTask","Zawrzyj umowę"),
         ("a4","manualTask","Odbierz dostawę / usługę")],
        [("e_ok","Zamówienie zrealizowane",None),("e_no","Postępowanie unieważnione",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","g1",None,0),
         ("g1","a3","tak",1),("g1","e_no","nie",0),("a3","a4",None,0),("a4","e_ok",None,0)],
        ["a1","a2","a3"])
    P["W4"] = ("Zgłoszenie / wniosek IT", "message",
        [("a1","userTask","Zarejestruj i sklasyfikuj zgłoszenie"),
         ("a2","userTask","Przeprowadź analizę / triage"),
         ("g1","exclusiveGateway","Zatwierdzić realizację?"),
         ("a3","serviceTask","Zrealizuj zmianę / naprawę"),
         ("a4","userTask","Zweryfikuj i zamknij")],
        [("e_ok","Zgłoszenie obsłużone",None),("e_no","Zgłoszenie odrzucone",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","g1",None,0),
         ("g1","a3","tak",1),("g1","e_no","nie",0),("a3","a4",None,0),("a4","e_ok",None,0)],
        ["a1","a3"])
    P["W5"] = ("Zgłoszenie / przegląd techniczny", "message",
        [("a1","userTask","Zdiagnozuj potrzebę / usterkę"),
         ("a2","manualTask","Wykonaj prace / konserwację"),
         ("a3","userTask","Odbierz prace i udokumentuj")],
        [("e_ok","Sprawność przywrócona",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","e_ok",None,0)],
        ["a2","a3"])
    P["W6"] = ("Sprawa / wniosek prawny", "message",
        [("a1","userTask","Przeanalizuj stan prawny"),
         ("a2","userTask","Opracuj dokument / opinię"),
         ("g1","exclusiveGateway","Zatwierdzono?"),
         ("a3","serviceTask","Zarejestruj i opublikuj")],
        [("e_ok","Sprawa załatwiona",None),("e_rev","Do poprawy",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","g1",None,0),
         ("g1","a3","tak",1),("g1","e_rev","nie",0),("a3","e_ok",None,0)],
        ["a1","a2"])
    P["W7"] = ("Wymóg / zdarzenie BHP", "message",
        [("a1","businessRuleTask","Oceń ryzyko / wymóg"),
         ("a2","userTask","Zaplanuj działania i szkolenia"),
         ("a3","manualTask","Zrealizuj działania zapobiegawcze"),
         ("a4","userTask","Udokumentuj i nadzoruj")],
        [("e_ok","Wymóg spełniony",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","a4",None,0),("a4","e_ok",None,0)],
        ["a1","a4"])
    P["W8"] = ("Inicjacja projektu / wniosek", "message",
        [("a1","userTask","Przygotuj wniosek / dokumentację projektu"),
         ("g1","exclusiveGateway","Zatwierdzono finansowanie?"),
         ("a2","userTask","Realizuj etapy projektu",{"loop":True}),
         ("a3","serviceTask","Rozlicz i odbierz projekt")],
        [("e_ok","Projekt zakończony",None),("e_no","Projekt wstrzymany",None)],
        [("s","a1",None,0),("a1","g1",None,0),("g1","a2","tak",1),("g1","e_no","nie",0),
         ("a2","a3",None,0),("a3","e_ok",None,0)],
        ["a1","a3"])
    P["W9"] = ("Zgłoszenie / zapytanie", "message",
        [("a1","userTask","Zarejestruj zgłoszenie"),
         ("a2","userTask","Obsłuż sprawę"),
         ("g1","exclusiveGateway","Wymaga eskalacji?"),
         ("a3","sendTask","Eskaluj do jednostki merytorycznej"),
         ("a4","sendTask","Udziel odpowiedzi zgłaszającemu")],
        [("e_ok","Sprawa zamknięta",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","g1",None,0),
         ("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","e_ok",None,0)],
        ["a1","a2"])
    return P.get(prefix)

def PAT_INCIDENT():
    return ("Wykrycie incydentu", "message",
        [("a1","userTask","Zarejestruj i sklasyfikuj incydent"),
         ("a2","businessRuleTask","Oceń wpływ i priorytet"),
         ("a3","serviceTask","Ogranicz skutki (containment)"),
         ("a4","manualTask","Usuń przyczynę i przywróć działanie"),
         ("g1","exclusiveGateway","Zgłosić organowi?"),
         ("a5","sendTask","Zgłoś (CSIRT / UODO / organ)"),
         ("a6","userTask","Przeprowadź przegląd poincydentalny")],
        [("e_ok","Incydent zamknięty",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","a4",None,0),("a4","g1",None,0),
         ("g1","a5","tak",0),("g1","a6","nie",1),("a5","a6",None,0),("a6","e_ok",None,0)],
        ["a1","a2","a5"])

def PAT_GENERIC():
    return ("Zdarzenie inicjujące", "message",
        [("a1","userTask","Przyjmij i zweryfikuj zgłoszenie"),
         ("a2","userTask","Zrealizuj czynności procesu"),
         ("g1","exclusiveGateway","Wynik poprawny?"),
         ("a3","serviceTask","Udokumentuj i zakończ")],
        [("e_ok","Proces zakończony",None),("e_no","Zwrot do korekty",None)],
        [("s","a1",None,0),("a1","a2",None,0),("a2","g1",None,0),
         ("g1","a3","tak",1),("g1","e_no","nie",0),("a3","e_ok",None,0)],
        ["a1","a2"])

def choose_pattern(proc):
    name = (proc.get("Proces") or "").lower()
    pref = prefix_of(proc.get("Kod"))
    if "incyden" in name or "kryzys" in name or ("reagowanie" in name and "cyber" in name):
        return "incydent", PAT_INCIDENT()
    p = PAT(pref)
    if p: return pref, p
    return "generic", PAT_GENERIC()

# ---------------------------------------------------------------- budowa spec
def build_spec(proc):
    kod = str(proc.get("Kod")); name = proc.get("Proces") or kod
    pat_key, pat = choose_pattern(proc)
    start_name, start_evt, steps, ends, edges, asset_hosts = pat

    nodes = [{"id":"s","type":"startEvent","name":start_name,"eventType":start_evt}]
    for st in steps:
        k, t, nm = st[0], st[1], st[2]
        opts = st[3] if len(st) > 3 else {}
        nd = {"id":k,"type":t,"name":nm}
        if opts.get("loop"): nd["loop"] = True
        nodes.append(nd)
    for k, nm, ev in ends:
        nd = {"id":k,"type":"endEvent","name":nm}
        if ev: nd["eventType"] = ev
        nodes.append(nd)

    flows = []
    for s, t, lab, dflt in edges:
        f = {"source":s,"target":t}
        if lab: f["name"] = lab
        if dflt: f["default"] = True
        flows.append(f)

    associations = []
    # aktywa informacyjne -> obiekty danych powiazane z czynnosciami (rozlozone rownomiernie)
    TASK_T = {"task","userTask","serviceTask","sendTask","receiveTask","manualTask","scriptTask","businessRuleTask"}
    task_keys = [st[0] for st in steps if st[1] in TASK_T] or [steps[0][0]]
    codes = parse_assets(proc.get("Aktywa informacyjne (kody)"))
    for i, c in enumerate(codes):
        did = "d_%s" % c.replace("-", "_")
        anm = "%s: %s" % (c, short(AI.get(c, {}).get("nazwa") or "aktyw informacyjny", 15))
        nodes.append({"id":did,"type":asset_node_type(c),"name":anm})
        associations.append({"source":did,"target":task_keys[i % len(task_keys)]})

    # adnotacje: meta (wlasciciel/komorka/warstwa + watermark) oraz systemy/RODO
    owner = proc.get("Właściciel (rola)") or "-"; unit = proc.get("Komórka org.") or "-"
    warstwa = proc.get("Warstwa") or ""; charakter = proc.get("Charakter") or ""
    status = proc.get("Status modelowania") or ""
    l3 = proc.get("Model BPMN (L3)")
    meta = "Właściciel: %s | Komórka: %s | %s / %s | SZKIC L3 z rejestru L2 - do weryfikacji as-is" % (
        owner, short(unit, 28), warstwa, charakter)
    nodes.append({"id":"n_meta","type":"textAnnotation","name":meta})  # stopka (bez asocjacji)

    sysraw = proc.get("Systemy / moduły (kody)")
    med = (proc.get("Dane medyczne (art. 9 RODO)") or "").strip().lower()
    os_ = (proc.get("Dane osobowe (RODO)") or "").strip().lower()
    rodo = "dane medyczne (art. 9 RODO)" if med == "tak" else ("dane osobowe (RODO)" if os_ == "tak" else "brak danych osobowych")
    parts = []
    if sysraw: parts.append("Systemy: %s" % short(str(sysraw), 46))
    parts.append("RODO: %s" % rodo)
    if not codes: parts.append("Brak zmapowanych aktywów AI w rejestrze")
    if l3: parts.append("Istnieje model L3: %s" % short(str(l3), 26))
    ann2 = " | ".join(parts)
    nodes.append({"id":"n_info","type":"textAnnotation","name":ann2})  # stopka (bez asocjacji)

    spec = {"id":"Proc_%s" % re.sub(r'[^A-Za-z0-9]','_', kod),
            "name":"%s  %s" % (kod, name),
            "nodes":nodes, "flows":flows, "associations":associations}
    return spec, pat_key, codes

# ---------------------------------------------------------------- main
def svg_to_pdf(svg, pdf):
    import cairosvg
    cairosvg.svg2pdf(url=svg, write_to=pdf)

def main():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    idx_dir = os.path.join(OUT, "00_INDEKS"); os.makedirs(idx_dir, exist_ok=True)
    manifest = []; errors = []
    for proc in REG:
        kod = str(proc.get("Kod"))
        try:
            spec, pat_key, codes = build_spec(proc)
            warns = G.validate(spec)
            pref = prefix_of(kod)
            wdir = WARSTWA_DIR.get(proc.get("Warstwa"), "9_Inne")
            gdir = "%s_%s" % (pref, slug(L1.get(pref, proc.get("Grupa procesowa") or "grupa"), 48))
            dest = os.path.join(OUT, wdir, gdir); os.makedirs(dest, exist_ok=True)
            base = os.path.join(dest, "%s__%s" % (kod, slug(proc.get("Proces"), 50)))
            res = G.generate(spec, base)
            svg_to_pdf(res["svg"], base + ".pdf")
            os.remove(res["svg"])  # SVG to tylko etap posredni do PDF
            manifest.append({
                "kod": kod, "proces": proc.get("Proces"), "warstwa": proc.get("Warstwa"),
                "grupa": proc.get("Grupa procesowa"), "wzorzec": pat_key,
                "wlasciciel": proc.get("Właściciel (rola)"), "komorka": proc.get("Komórka org."),
                "status_L3": proc.get("Status modelowania"), "model_L3": proc.get("Model BPMN (L3)"),
                "aktywa_AI": codes, "n_aktywa": len(codes),
                "systemy": proc.get("Systemy / moduły (kody)"),
                "dane_osobowe": proc.get("Dane osobowe (RODO)"),
                "dane_medyczne": proc.get("Dane medyczne (art. 9 RODO)"),
                "warnings": warns,
                "pliki": {k: os.path.relpath(base + ext, OUT) for k, ext in
                          (("bpmn",".bpmn"),("png",".png"),("pdf",".pdf"))},
            })
        except Exception as e:
            errors.append({"kod": kod, "error": str(e), "trace": traceback.format_exc()})
            print("ERR %s: %s" % (kod, e))
    json.dump({"generated": datetime.datetime.now().isoformat(timespec="seconds"),
               "liczba_procesow": len(manifest), "bledy": errors, "procesy": manifest},
              open(os.path.join(idx_dir, "manifest.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("OK: %d diagramow, %d bledow" % (len(manifest), len(errors)))
    nwarn = sum(1 for m in manifest if m["warnings"])
    print("Procesow z uwagami walidacji: %d" % nwarn)
    return manifest, errors

if __name__ == "__main__":
    main()
