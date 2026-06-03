#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tobe_models.py - wielotorowe modele to-be dla 203 procesow SCM.
Kazda funkcja g_XX(proc) zwraca (lanes, nodes, flows, data); model_for(proc) dobiera ja po prefiksie.
"""
import re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from tobe_engine import C
from pilot_w3_tobe import MODELS as _W3

def _k(p): return str(p["Kod"])
def prefix(p):
    m = re.match(r"^([ZGW]\d+)", _k(p)); return m.group(1) if m else "X"

# ============================ WARSTWA ZARZADCZA (Z) ============================
def g_Z1(p):
    k = _k(p)
    if k == "Z1.01":
        L = ["Zarząd", "Zgromadzenie Wspólników"]
        n = [("s","startEvent","Sprawa wymagająca decyzji właścicielskiej","Zarząd",{"eventType":"message"}),
             ("a1","userTask","Przygotuj wniosek i analizę","Zarząd",{}),
             ("a2","sendTask","Zwołaj Zgromadzenie Wspólników","Zarząd",{}),
             ("a3","userTask","Rozpatrz sprawę","Zgromadzenie Wspólników",{}),
             ("g1","exclusiveGateway","Podjąć uchwałę?","Zgromadzenie Wspólników",{}),
             ("a4","userTask","Podejmij i zaprotokołuj uchwałę","Zgromadzenie Wspólników",{}),
             ("e1","endEvent","Decyzja właścicielska podjęta","Zgromadzenie Wspólników",{}),
             ("e2","endEvent","Sprawa odroczona","Zgromadzenie Wspólników",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a4","tak",1),("a4","e1",None,0),("g1","e2","odroczyć",0)]
        return L,n,f,[("d1","dataObjectReference","Uchwała ZW","a4")]
    if k == "Z1.02":
        L = ["Zarząd","Rada Nadzorcza","Zgromadzenie Wspólników"]
        n = [("s","startEvent","Zamknięcie roku obrotowego","Zarząd",{"eventType":"timer"}),
             ("a1","userTask","Sporządź roczne sprawozdanie finansowe","Zarząd",{}),
             ("a2","userTask","Oceń sprawozdanie i wniosek o podział wyniku","Rada Nadzorcza",{}),
             ("a3","userTask","Zatwierdź sprawozdanie i podział wyniku","Zgromadzenie Wspólników",{}),
             ("g1","exclusiveGateway","Zatwierdzono?","Zgromadzenie Wspólników",{}),
             ("a4","sendTask","Złóż sprawozdanie do KRS/akta","Zarząd",{}),
             ("e1","endEvent","Sprawozdanie zatwierdzone i złożone","Zarząd",{}),
             ("e2","endEvent","Skierowano do korekty","Zarząd",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a4","tak",1),("a4","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Sprawozdanie finansowe","a1")]
    if k in ("Z1.03","Z1.05"):  # powolywanie organow
        organ, kto = ("Rady Nadzorczej","Zgromadzenie Wspólników") if k=="Z1.03" else ("Zarządu","Rada Nadzorcza")
        L = [kto, "Dział Organizacyjno-Prawny"]
        n = [("s","startEvent","Potrzeba zmiany w składzie "+organ,kto,{"eventType":"message"}),
             ("a1","userTask","Zgłoś kandydaturę / wniosek",kto,{}),
             ("a2","userTask","Zweryfikuj wymogi formalne","Dział Organizacyjno-Prawny",{}),
             ("g1","exclusiveGateway","Spełnia wymogi?",kto,{}),
             ("a3","userTask","Podejmij uchwałę o powołaniu/odwołaniu",kto,{}),
             ("a4","sendTask","Zgłoś zmianę do KRS","Dział Organizacyjno-Prawny",{}),
             ("e1","endEvent","Zmiana w składzie dokonana","Dział Organizacyjno-Prawny",{}),
             ("e2","endEvent","Wniosek odrzucony",kto,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","a4",None,0),("a4","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Uchwała","a3")]
    if k in ("Z1.04","Z1.06"):  # nadzor RN
        L = ["Zarząd","Rada Nadzorcza"]
        nm = "Nadzór nad działalnością Spółki" if k=="Z1.04" else "Opiniowanie sprawozdań i decyzji"
        n = [("s","startEvent","Cykl nadzoru / wniosek o opinię","Rada Nadzorcza",{"eventType":"timer"}),
             ("a1","userTask","Przekaż informacje i materiały","Zarząd",{}),
             ("a2","userTask","Przeanalizuj działalność i ryzyka","Rada Nadzorcza",{}),
             ("g1","exclusiveGateway","Zastrzeżenia?","Rada Nadzorcza",{}),
             ("a3","sendTask","Wydaj zalecenia / wnioski","Rada Nadzorcza",{}),
             ("a4","userTask","Sporządź opinię / protokół","Rada Nadzorcza",{}),
             ("e1","endEvent","Nadzór zrealizowany","Rada Nadzorcza",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Protokół / zalecenia RN","a4")]
    if k in ("Z1.07","Z1.08"):  # zarzadzanie/planowanie strategiczne
        L = ["Zarząd","Dyrektorzy pionów","Rada Nadzorcza"]
        plan = "operacyjny" if k=="Z1.07" else "strategiczny i rzeczowo-finansowy"
        n = [("s","startEvent","Cykl planistyczny","Zarząd",{"eventType":"timer"}),
             ("a1","userTask","Zbierz cele i dane z pionów","Dyrektorzy pionów",{}),
             ("a2","userTask","Opracuj plan "+plan,"Zarząd",{}),
             ("a3","userTask","Zaopiniuj plan","Rada Nadzorcza",{}),
             ("g1","exclusiveGateway","Plan zaakceptowany?","Zarząd",{}),
             ("a4","sendTask","Zakomunikuj i wdróż plan","Zarząd",{}),
             ("a5","userTask","Monitoruj realizację","Zarząd",{"loop":True}),
             ("e1","endEvent","Plan w realizacji","Zarząd",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a4","tak",1),("a4","a5",None,0),("a5","e1",None,0),("g1","a2","do poprawy",0)]
        return L,n,f,[("d1","dataObjectReference","Plan / strategia","a2")]
    if k == "Z1.09":
        L = ["Zarząd","Dział Organizacyjno-Prawny"]
        n = [("s","startEvent","Sprawa wymagająca reprezentacji","Zarząd",{"eventType":"message"}),
             ("a1","userTask","Ustal zakres i umocowanie","Dział Organizacyjno-Prawny",{}),
             ("g1","exclusiveGateway","Wymaga pełnomocnictwa?","Zarząd",{}),
             ("a2","userTask","Udziel pełnomocnictwa","Zarząd",{}),
             ("a3","sendTask","Reprezentuj Spółkę / złóż oświadczenie","Zarząd",{}),
             ("e1","endEvent","Spółka zareprezentowana","Zarząd",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Pełnomocnictwo / oświadczenie","a3")]
    if k == "Z1.10":
        L = ["Dział Organizacyjno-Prawny","Zarząd"]
        n = [("s","startEvent","Obowiązek sprawozdawczy (KRS/BIP)","Dział Organizacyjno-Prawny",{"eventType":"timer"}),
             ("a1","userTask","Zbierz dane i dokumenty","Dział Organizacyjno-Prawny",{}),
             ("a2","userTask","Przygotuj zgłoszenie/publikację","Dział Organizacyjno-Prawny",{}),
             ("a3","userTask","Zatwierdź treść","Zarząd",{}),
             ("a4","serviceTask","Złóż do KRS / opublikuj w BIP","Dział Organizacyjno-Prawny",{}),
             ("e1","endEvent","Obowiązek sprawozdawczy spełniony","Dział Organizacyjno-Prawny",{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataObjectReference","Zgłoszenie KRS / wpis BIP","a2")]
    # Z1.11 kontrola zarzadcza
    L = ["Dyrektorzy pionów","Zarząd"]
    n = [("s","startEvent","Roczny cykl kontroli zarządczej","Zarząd",{"eventType":"timer"}),
         ("a1","userTask","Wyznacz cele i zidentyfikuj ryzyka","Dyrektorzy pionów",{}),
         ("a2","userTask","Zaprojektuj mechanizmy kontrolne","Dyrektorzy pionów",{}),
         ("a3","manualTask","Realizuj i monitoruj kontrole","Dyrektorzy pionów",{"loop":True}),
         ("a4","userTask","Oceń funkcjonowanie kontroli","Zarząd",{}),
         ("g1","exclusiveGateway","Zapewnienie wystarczające?","Zarząd",{}),
         ("a5","userTask","Zaplanuj działania doskonalące","Zarząd",{}),
         ("a6","sendTask","Złóż oświadczenie o stanie kontroli zarządczej","Zarząd",{}),
         ("e1","endEvent","Kontrola zarządcza udokumentowana","Zarząd",{})]
    f = C("s","a1","a2","a3","a4","g1")+[("g1","a6","tak",1),("g1","a5","nie",0),("a5","a6",None,0),("a6","e1",None,0)]
    return L,n,f,[("d1","dataObjectReference","Oświadczenie o kontroli zarządczej","a6"),
                  ("d2","dataObjectReference","Rejestr ryzyk","a1")]

def g_Z2(p):
    k = _k(p)
    if k in ("Z2.02","Z2.07"):  # audyty wewnetrzne
        sysn = "ZSZ (ISO 9001/14001)" if k=="Z2.02" else "SZBI (ISO 27001)"
        L = ["Audytor wewnętrzny","Audytowana komórka","Pełnomocnik systemu"]
        n = [("s","startEvent","Plan audytów "+sysn,"Pełnomocnik systemu",{"eventType":"timer"}),
             ("a1","userTask","Zaplanuj audyt (zakres, kryteria)","Audytor wewnętrzny",{}),
             ("a2","manualTask","Przeprowadź audyt","Audytor wewnętrzny",{}),
             ("a3","userTask","Przedstaw ustalenia","Audytowana komórka",{}),
             ("g1","exclusiveGateway","Niezgodności?","Audytor wewnętrzny",{}),
             ("a4","userTask","Uzgodnij i wdroż działania korygujące","Audytowana komórka",{}),
             ("a5","userTask","Sporządź raport z audytu","Audytor wewnętrzny",{}),
             ("e1","endEvent","Audyt zamknięty","Pełnomocnik systemu",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a4","tak",0),("g1","a5","nie",1),("a4","a5",None,0),("a5","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Raport z audytu","a5"),("d2","dataObjectReference","Karty niezgodności","a4")]
    if k in ("Z2.03",):  # przeglad zarzadzania
        L = ["Pełnomocnik systemu","Zarząd"]
        n = [("s","startEvent","Termin przeglądu zarządzania","Pełnomocnik systemu",{"eventType":"timer"}),
             ("a1","userTask","Zbierz dane wejściowe do przeglądu","Pełnomocnik systemu",{}),
             ("a2","userTask","Przeprowadź przegląd zarządzania","Zarząd",{}),
             ("a3","userTask","Wyznacz cele i działania doskonalące","Zarząd",{}),
             ("a4","sendTask","Zakomunikuj decyzje i przydziel zasoby","Pełnomocnik systemu",{}),
             ("e1","endEvent","Przegląd zarządzania zakończony","Pełnomocnik systemu",{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataObjectReference","Protokół przeglądu zarządzania","a2")]
    if k in ("Z2.01","Z2.06"):  # utrzymanie systemu
        sysn = "ZSZ (ISO 9001/14001)" if k=="Z2.01" else "SZBI (ISO 27001)"
        L = ["Pełnomocnik systemu","Właściciele procesów","Zarząd"]
        n = [("s","startEvent","Utrzymanie/rozwój "+sysn,"Pełnomocnik systemu",{"eventType":"timer"}),
             ("a1","userTask","Aktualizuj dokumentację systemu","Pełnomocnik systemu",{}),
             ("a2","userTask","Nadzoruj realizację wymagań","Właściciele procesów",{}),
             ("a3","userTask","Monitoruj cele i wskaźniki","Pełnomocnik systemu",{"loop":True}),
             ("g1","exclusiveGateway","Cele osiągane?","Pełnomocnik systemu",{}),
             ("a4","userTask","Uruchom działania korygujące","Właściciele procesów",{}),
             ("e1","endEvent","System utrzymany","Zarząd",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","e1","tak",1),("g1","a4","nie",0),("a4","a3",None,0)]
        return L,n,f,[("d1","dataObjectReference","Dokumentacja systemu","a1"),("d2","dataStore","Rejestr celów i wskaźników","a3")]
    if k in ("Z2.04","Z2.05"):  # akredytacja CMJ
        L = ["Pełnomocnik ds. Akredytacji","Komórki kliniczne","Zarząd"]
        op = "Przygotuj i utrzymaj akredytację" if k=="Z2.04" else "Wdroż standardy w komórkach"
        n = [("s","startEvent","Cykl akredytacyjny CMJ","Pełnomocnik ds. Akredytacji",{"eventType":"timer"}),
             ("a1","userTask",op,"Pełnomocnik ds. Akredytacji",{}),
             ("a2","manualTask","Wdroż i samooceń standardy","Komórki kliniczne",{}),
             ("a3","manualTask","Przeprowadź przegląd przygotowania","Pełnomocnik ds. Akredytacji",{}),
             ("g1","exclusiveGateway","Gotowość do wizyty?","Zarząd",{}),
             ("a4","userTask","Uzupełnij braki","Komórki kliniczne",{}),
             ("a5","receiveTask","Przyjmij wizytę akredytacyjną","Pełnomocnik ds. Akredytacji",{}),
             ("e1","endEvent","Standardy akredytacyjne spełnione","Pełnomocnik ds. Akredytacji",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a5","tak",1),("g1","a4","nie",0),("a4","a3",None,0),("a5","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Zestaw standardów / samoocena","a2")]
    if k == "Z2.08":  # autoryzacja NFZ / jakosc
        L = ["Pełnomocnik ds. Jakości","Komórki kliniczne","Zarząd"]
        n = [("s","startEvent","Wymóg wewn. systemu zarządzania jakością","Pełnomocnik ds. Jakości",{"eventType":"timer"}),
             ("a1","userTask","Wdroż wymagania ustawy o jakości","Pełnomocnik ds. Jakości",{}),
             ("a2","manualTask","Monitoruj wskaźniki jakości i bezpieczeństwa","Komórki kliniczne",{}),
             ("a3","userTask","Oceń spełnienie warunków autoryzacji","Pełnomocnik ds. Jakości",{}),
             ("g1","exclusiveGateway","Warunki spełnione?","Zarząd",{}),
             ("a4","userTask","Wdroż działania naprawcze","Komórki kliniczne",{}),
             ("a5","sendTask","Złóż wniosek/oświadczenie do NFZ","Pełnomocnik ds. Jakości",{}),
             ("e1","endEvent","Autoryzacja jakości potwierdzona","Pełnomocnik ds. Jakości",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a5","tak",1),("g1","a4","nie",0),("a4","a3",None,0),("a5","e1",None,0)]
        return L,n,f,[("d1","dataStore","Rejestr wskaźników jakości","a2")]
    # Z2.09 nadzor nad AI (ISO 42001) - planowany
    L = ["Pełnomocnik ds. ZSZ","Dział Informatyki","Zarząd"]
    n = [("s","startEvent","Wdrożenie/zmiana systemu AI","Pełnomocnik ds. ZSZ",{"eventType":"message"}),
         ("a1","userTask","Zarejestruj system AI","Pełnomocnik ds. ZSZ",{}),
         ("a2","businessRuleTask","Oceń ryzyko AI (AI Act, KEL)","Pełnomocnik ds. ZSZ",{}),
         ("g1","exclusiveGateway","Ryzyko akceptowalne?","Zarząd",{}),
         ("a3","userTask","Określ środki nadzoru i wymogi","Pełnomocnik ds. ZSZ",{}),
         ("a4","manualTask","Monitoruj modele i jakość","Dział Informatyki",{"loop":True}),
         ("e1","endEvent","System AI pod nadzorem","Pełnomocnik ds. ZSZ",{}),
         ("e2","endEvent","System AI niedopuszczony","Zarząd",{})]
    f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","a4",None,0),("a4","e1",None,0),("g1","e2","nie",0)]
    return L,n,f,[("d1","dataStore","Rejestr systemów AI","a1")]

def g_Z3(p):
    k = _k(p)
    if k == "Z3.04":  # incydent/kryzys
        L = ["Zespół reagowania","Zarząd","Komórki merytoryczne"]
        n = [("s","startEvent","Wykrycie incydentu / sytuacji kryzysowej","Zespół reagowania",{"eventType":"message"}),
             ("a1","userTask","Zarejestruj i sklasyfikuj zdarzenie","Zespół reagowania",{}),
             ("a2","businessRuleTask","Oceń wpływ i uruchom poziom reagowania","Zespół reagowania",{}),
             ("g1","exclusiveGateway","Sytuacja kryzysowa?","Zarząd",{}),
             ("a3","userTask","Powołaj sztab kryzysowy","Zarząd",{}),
             ("a4","manualTask","Prowadź działania ograniczające skutki","Komórki merytoryczne",{}),
             ("a5","userTask","Przywróć normalne działanie","Komórki merytoryczne",{}),
             ("a6","userTask","Przeprowadź przegląd poincydentalny","Zespół reagowania",{}),
             ("e1","endEvent","Incydent zamknięty","Zespół reagowania",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),
             ("a4","a5",None,0),("a5","a6",None,0),("a6","e1",None,0)]
        return L,n,f,[("d1","dataStore","Rejestr incydentów","a1")]
    if k == "Z3.03":  # BCP/DRP
        L = ["Pełnomocnik ds. SZBI","Dział Informatyki","Zarząd"]
        n = [("s","startEvent","Cykl planów ciągłości","Pełnomocnik ds. SZBI",{"eventType":"timer"}),
             ("a1","userTask","Wykonaj analizę BIA","Pełnomocnik ds. SZBI",{}),
             ("a2","userTask","Opracuj plany BCP/DRP","Pełnomocnik ds. SZBI",{}),
             ("a3","userTask","Zatwierdź plany","Zarząd",{}),
             ("a4","manualTask","Przeprowadź testy i ćwiczenia","Dział Informatyki",{}),
             ("g1","exclusiveGateway","Testy zaliczone?","Pełnomocnik ds. SZBI",{}),
             ("a5","userTask","Zaktualizuj plany","Pełnomocnik ds. SZBI",{}),
             ("e1","endEvent","Plany ciągłości gotowe","Pełnomocnik ds. SZBI",{})]
        f = C("s","a1","a2","a3","a4","g1")+[("g1","e1","tak",1),("g1","a5","nie",0),("a5","a4",None,0)]
        return L,n,f,[("d1","dataObjectReference","Plan BCP/DRP","a2")]
    if k == "Z3.05":  # zdarzenia niepozadane no-fault
        L = ["Personel zgłaszający","Pełnomocnik ds. Jakości","Zespół ds. bezpieczeństwa"]
        n = [("s","startEvent","Wystąpienie zdarzenia niepożądanego","Personel zgłaszający",{"eventType":"message"}),
             ("a1","userTask","Zgłoś zdarzenie (no-fault)","Personel zgłaszający",{}),
             ("a2","userTask","Zarejestruj i sklasyfikuj zdarzenie","Pełnomocnik ds. Jakości",{}),
             ("a3","businessRuleTask","Przeprowadź analizę przyczyn źródłowych","Zespół ds. bezpieczeństwa",{}),
             ("g1","exclusiveGateway","Wymaga działań systemowych?","Zespół ds. bezpieczeństwa",{}),
             ("a4","userTask","Wdroż rekomendacje i monitoruj","Pełnomocnik ds. Jakości",{}),
             ("e1","endEvent","Zdarzenie przeanalizowane","Pełnomocnik ds. Jakości",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a4","tak",1),("a4","e1",None,0),("g1","e1","nie",0)]
        return L,n,f,[("d1","dataStore","Rejestr zdarzeń niepożądanych","a2")]
    # Z3.01 ryzyka oper./strat., Z3.02 ryzyka SZBI
    sysn = "operacyjnych i strategicznych" if k=="Z3.01" else "bezpieczeństwa informacji"
    L = ["Komórki merytoryczne","Koordynator ryzyka","Zarząd"]
    n = [("s","startEvent","Cykl zarządzania ryzykiem","Koordynator ryzyka",{"eventType":"timer"}),
         ("a1","userTask","Zidentyfikuj ryzyka "+sysn,"Komórki merytoryczne",{}),
         ("a2","businessRuleTask","Oceń ryzyka (prawdopod./skutek)","Koordynator ryzyka",{}),
         ("g1","exclusiveGateway","Ryzyko akceptowalne?","Zarząd",{}),
         ("a3","userTask","Zaplanuj postępowanie z ryzykiem","Komórki merytoryczne",{}),
         ("a4","userTask","Monitoruj ryzyka i mierniki","Koordynator ryzyka",{"loop":True}),
         ("e1","endEvent","Ryzyka pod kontrolą","Koordynator ryzyka",{})]
    f = C("s","a1","a2","g1")+[("g1","a4","tak",1),("g1","a3","nie",0),("a3","a4",None,0),("a4","e1",None,0)]
    return L,n,f,[("d1","dataStore","Rejestr ryzyk","a2")]

def g_Z4(p):
    k = _k(p)
    if k == "Z4.04":  # naruszenie RODO
        L = ["Zgłaszający","Inspektor Ochrony Danych","Zarząd"]
        n = [("s","startEvent","Podejrzenie naruszenia ochrony danych","Zgłaszający",{"eventType":"message"}),
             ("a1","userTask","Zgłoś naruszenie do IOD","Zgłaszający",{}),
             ("a2","businessRuleTask","Oceń ryzyko dla osób","Inspektor Ochrony Danych",{}),
             ("g1","exclusiveGateway","Wysokie ryzyko / wymagana notyfikacja?","Inspektor Ochrony Danych",{}),
             ("a3","sendTask","Zgłoś do UODO (72h)","Inspektor Ochrony Danych",{}),
             ("a4","sendTask","Zawiadom osoby, których dane dotyczą","Inspektor Ochrony Danych",{}),
             ("a5","userTask","Wdroż środki zaradcze i wpisz do rejestru","Inspektor Ochrony Danych",{}),
             ("e1","endEvent","Naruszenie obsłużone","Inspektor Ochrony Danych",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a5","nie",1),("a3","a4",None,0),("a4","a5",None,0),("a5","e1",None,0)]
        return L,n,f,[("d1","dataStore","Rejestr naruszeń","a5")]
    if k == "Z4.02":  # prawa osob
        L = ["Wnioskodawca","Sekcja Dokumentacji Medycznej","Inspektor Ochrony Danych"]
        n = [("s","startEvent","Wniosek o realizację prawa (RODO)","Wnioskodawca",{"eventType":"message"}),
             ("a1","userTask","Zarejestruj i zweryfikuj tożsamość","Sekcja Dokumentacji Medycznej",{}),
             ("a2","businessRuleTask","Oceń zasadność i podstawę","Inspektor Ochrony Danych",{}),
             ("g1","exclusiveGateway","Żądanie zasadne?","Inspektor Ochrony Danych",{}),
             ("a3","userTask","Zrealizuj żądanie","Sekcja Dokumentacji Medycznej",{}),
             ("a4","sendTask","Udziel odpowiedzi wnioskodawcy","Sekcja Dokumentacji Medycznej",{}),
             ("e1","endEvent","Prawo zrealizowane","Sekcja Dokumentacji Medycznej",{}),
             ("e2","endEvent","Odmowa z uzasadnieniem","Inspektor Ochrony Danych",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","a4",None,0),("a4","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Wniosek osoby","a1")]
    if k == "Z4.03":  # DPIA
        L = ["Komórka przetwarzająca","Inspektor Ochrony Danych","Zarząd"]
        n = [("s","startEvent","Nowe/zmienione przetwarzanie wysokiego ryzyka","Komórka przetwarzająca",{"eventType":"message"}),
             ("a1","userTask","Opisz operacje przetwarzania","Komórka przetwarzająca",{}),
             ("a2","businessRuleTask","Przeprowadź ocenę skutków (DPIA)","Inspektor Ochrony Danych",{}),
             ("g1","exclusiveGateway","Ryzyko szczątkowe akceptowalne?","Zarząd",{}),
             ("a3","userTask","Zaprojektuj dodatkowe zabezpieczenia","Komórka przetwarzająca",{}),
             ("a4","sendTask","(Opcjonalnie) konsultuj z UODO","Inspektor Ochrony Danych",{}),
             ("e1","endEvent","DPIA zakończona","Inspektor Ochrony Danych",{})]
        f = C("s","a1","a2","g1")+[("g1","e1","tak",1),("g1","a3","nie",0),("a3","a4",None,0),("a4","a2",None,0)]
        return L,n,f,[("d1","dataObjectReference","Raport DPIA","a2")]
    if k == "Z4.05":  # KSC
        L = ["Pełnomocnik ds. SZBI","Dział Informatyki","Organ KSC (CSIRT)"]
        n = [("s","startEvent","Obowiązek/zdarzenie KSC","Pełnomocnik ds. SZBI",{"eventType":"message"}),
             ("a1","businessRuleTask","Oceń zgodność z wymogami KSC","Pełnomocnik ds. SZBI",{}),
             ("g1","exclusiveGateway","Spełnione?","Pełnomocnik ds. SZBI",{}),
             ("a2","userTask","Wdroż środki techniczne i organizacyjne","Dział Informatyki",{}),
             ("a3","sendTask","Raportuj do CSIRT/organu","Pełnomocnik ds. SZBI",{}),
             ("a4","manualTask","Nadzoruj utrzymanie zgodności","Pełnomocnik ds. SZBI",{"loop":True}),
             ("e1","endEvent","Zgodność KSC utrzymana","Pełnomocnik ds. SZBI",{})]
        f = C("s","a1","g1")+[("g1","a3","tak",1),("g1","a2","nie",0),("a2","a3",None,0),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataStore","Rejestr zgodności KSC","a1")]
    if k == "Z4.07":  # prawa pacjenta/skargi
        L = ["Pacjent / Skarżący","Pełnomocnik ds. Praw Pacjenta","Komórka merytoryczna"]
        n = [("s","startEvent","Wpływ skargi / zapytania pacjenta","Pacjent / Skarżący",{"eventType":"message"}),
             ("a1","userTask","Zarejestruj skargę","Pełnomocnik ds. Praw Pacjenta",{}),
             ("a2","userTask","Wyjaśnij sprawę z komórką","Komórka merytoryczna",{}),
             ("g1","exclusiveGateway","Skarga zasadna?","Pełnomocnik ds. Praw Pacjenta",{}),
             ("a3","userTask","Zaplanuj działania naprawcze","Komórka merytoryczna",{}),
             ("a4","sendTask","Udziel odpowiedzi skarżącemu","Pełnomocnik ds. Praw Pacjenta",{}),
             ("e1","endEvent","Skarga rozpatrzona","Pełnomocnik ds. Praw Pacjenta",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataStore","Rejestr skarg","a1")]
    if k == "Z4.10":  # FKZM
        L = ["Pacjent / RPP","Pełnomocnik ds. Praw Pacjenta","Komórki kliniczne"]
        n = [("s","startEvent","Zdarzenie medyczne / wniosek FKZM","Pacjent / RPP",{"eventType":"message"}),
             ("a1","userTask","Zarejestruj zdarzenie","Pełnomocnik ds. Praw Pacjenta",{}),
             ("a2","userTask","Zbierz dokumentację i wyjaśnienia","Komórki kliniczne",{}),
             ("a3","sendTask","Współpracuj z RPP / przekaż stanowisko","Pełnomocnik ds. Praw Pacjenta",{}),
             ("a4","userTask","Wdroż zalecenia i wpisz do rejestru","Komórki kliniczne",{}),
             ("e1","endEvent","Sprawa FKZM obsłużona","Pełnomocnik ds. Praw Pacjenta",{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataStore","Rejestr zaleceń i wdrożeń","a4")]
    if k == "Z4.08":  # dostepnosc
        L = ["Pełnomocnik ds. Dostępności","Komórki organizacyjne","Zarząd"]
        n = [("s","startEvent","Wymóg/zgłoszenie dot. dostępności","Pełnomocnik ds. Dostępności",{"eventType":"message"}),
             ("a1","businessRuleTask","Oceń dostępność (arch./cyfr./inf.-kom.)","Pełnomocnik ds. Dostępności",{}),
             ("g1","exclusiveGateway","Bariery zidentyfikowane?","Pełnomocnik ds. Dostępności",{}),
             ("a2","userTask","Zaplanuj usprawnienia / dostęp alternatywny","Komórki organizacyjne",{}),
             ("a3","sendTask","Opublikuj deklarację dostępności","Pełnomocnik ds. Dostępności",{}),
             ("e1","endEvent","Dostępność zapewniona","Pełnomocnik ds. Dostępności",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Deklaracja dostępności","a3")]
    if k == "Z4.09":  # doradztwo prawne
        L = ["Komórka wnioskująca","Radca prawny"]
        n = [("s","startEvent","Zapytanie prawne / sprawa","Komórka wnioskująca",{"eventType":"message"}),
             ("a1","userTask","Sprecyzuj zapytanie i przekaż dokumenty","Komórka wnioskująca",{}),
             ("a2","userTask","Przeanalizuj stan prawny","Radca prawny",{}),
             ("g1","exclusiveGateway","Sprawa sądowa?","Radca prawny",{}),
             ("a3","sendTask","Reprezentuj w postępowaniu","Radca prawny",{}),
             ("a4","userTask","Wydaj opinię / poradę","Radca prawny",{}),
             ("e1","endEvent","Sprawa prawna obsłużona","Radca prawny",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Opinia prawna","a4")]
    if k == "Z4.06":  # informacje niejawne
        L = ["Pełnomocnik ds. OIN","Komórki organizacyjne"]
        n = [("s","startEvent","Wpływ/wytworzenie informacji niejawnej","Pełnomocnik ds. OIN",{"eventType":"message"}),
             ("a1","businessRuleTask","Nadaj klauzulę i zarejestruj","Pełnomocnik ds. OIN",{}),
             ("a2","userTask","Zapewnij środki ochrony","Komórki organizacyjne",{}),
             ("a3","manualTask","Nadzoruj obieg i przechowywanie","Pełnomocnik ds. OIN",{"loop":True}),
             ("e1","endEvent","Informacja niejawna chroniona","Pełnomocnik ds. OIN",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataStore","Rejestr informacji niejawnych","a1")]
    # Z4.01 nadzor RODO
    L = ["Inspektor Ochrony Danych","Komórki przetwarzające","Zarząd"]
    n = [("s","startEvent","Cykl nadzoru nad ochroną danych","Inspektor Ochrony Danych",{"eventType":"timer"}),
         ("a1","userTask","Prowadź rejestr czynności (RCPD)","Inspektor Ochrony Danych",{}),
         ("a2","manualTask","Monitoruj zgodność przetwarzania","Komórki przetwarzające",{"loop":True}),
         ("g1","exclusiveGateway","Nieprawidłowości?","Inspektor Ochrony Danych",{}),
         ("a3","userTask","Wydaj zalecenia i nadzoruj wdrożenie","Inspektor Ochrony Danych",{}),
         ("a4","sendTask","Raportuj do Zarządu","Inspektor Ochrony Danych",{}),
         ("e1","endEvent","Nadzór RODO zrealizowany","Inspektor Ochrony Danych",{})]
    f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","e1",None,0)]
    return L,n,f,[("d1","dataStore","Rejestr czynności przetwarzania","a1")]

def g_Z5(p):
    k = _k(p)
    if k in ("Z5.01","Z5.02"):  # regulamin / procedury
        co = "regulaminu organizacyjnego" if k=="Z5.01" else "zarządzeń i procedur wewnętrznych"
        L = ["Komórka inicjująca","Dział Organizacyjno-Prawny","Zarząd"]
        n = [("s","startEvent","Potrzeba opracowania/zmiany "+co,"Komórka inicjująca",{"eventType":"message"}),
             ("a1","userTask","Opracuj projekt regulacji","Dział Organizacyjno-Prawny",{}),
             ("a2","userTask","Przeprowadź konsultacje i opiniowanie","Komórka inicjująca",{}),
             ("g1","exclusiveGateway","Zatwierdzić?","Zarząd",{}),
             ("a3","serviceTask","Opublikuj i zakomunikuj","Dział Organizacyjno-Prawny",{}),
             ("a4","userTask","Nadzoruj stosowanie","Dział Organizacyjno-Prawny",{}),
             ("e1","endEvent","Regulacja obowiązuje","Dział Organizacyjno-Prawny",{}),
             ("e2","endEvent","Skierowano do poprawy","Komórka inicjująca",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","a4",None,0),("a4","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataStore","Rejestr regulacji wewnętrznych","a3")]
    if k == "Z5.03":  # zmiana organizacyjna
        L = ["Zarząd","Dział Personalno-Płacowy","Rada Nadzorcza"]
        n = [("s","startEvent","Inicjatywa zmiany organizacyjnej","Zarząd",{"eventType":"message"}),
             ("a1","userTask","Opracuj koncepcję zmiany (struktura/etaty)","Zarząd",{}),
             ("a2","userTask","Oceń skutki kadrowe i kosztowe","Dział Personalno-Płacowy",{}),
             ("a3","userTask","Zaopiniuj zmianę","Rada Nadzorcza",{}),
             ("g1","exclusiveGateway","Zatwierdzić zmianę?","Zarząd",{}),
             ("a4","sendTask","Wdroż zmianę i zaktualizuj dokumenty","Dział Personalno-Płacowy",{}),
             ("e1","endEvent","Zmiana wdrożona","Zarząd",{}),
             ("e2","endEvent","Zmiana wstrzymana","Zarząd",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a4","tak",1),("a4","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Projekt zmiany organizacyjnej","a1")]
    # Z5.04 zarzadzanie wiedza
    L = ["Pracownicy / Eksperci","Pełnomocnik ds. Jakości"]
    n = [("s","startEvent","Wniosek z doświadczeń / potrzeba wiedzy","Pracownicy / Eksperci",{"eventType":"message"}),
         ("a1","userTask","Zbierz wnioski i dobre praktyki","Pracownicy / Eksperci",{}),
         ("a2","userTask","Skataloguj wiedzę w bazie","Pełnomocnik ds. Jakości",{}),
         ("a3","sendTask","Udostępnij i przekaż kompetencje","Pełnomocnik ds. Jakości",{}),
         ("e1","endEvent","Wiedza zarządzana","Pełnomocnik ds. Jakości",{})]
    f = C("s","a1","a2","a3","e1")
    return L,n,f,[("d1","dataStore","Baza wiedzy organizacyjnej","a2")]

def g_Z6(p):
    k = _k(p)
    if k == "Z6.01":  # umowy NFZ
        L = ["Dział Rozliczeń Świadczeń","Zarząd","NFZ (zewn.)"]
        n = [("s","startEvent","Postępowanie/aneksowanie umowy NFZ","Dział Rozliczeń Świadczeń",{"eventType":"timer"}),
             ("a1","userTask","Przygotuj ofertę i dane o potencjale","Dział Rozliczeń Świadczeń",{}),
             ("a2","userTask","Prowadź negocjacje z NFZ","Zarząd",{}),
             ("g1","exclusiveGateway","Uzgodniono warunki?","Zarząd",{}),
             ("a3","userTask","Zawrzyj umowę / aneks","Zarząd",{}),
             ("a4","manualTask","Realizuj i monitoruj kontrakt","Dział Rozliczeń Świadczeń",{"loop":True}),
             ("e1","endEvent","Kontrakt NFZ w realizacji","Dział Rozliczeń Świadczeń",{}),
             ("e2","endEvent","Brak rozstrzygnięcia","Zarząd",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","a4",None,0),("a4","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Umowa z NFZ","a3")]
    if k == "Z6.02":  # organy nadzoru
        L = ["Organ (zewn.)","Zarząd","Komórki merytoryczne"]
        n = [("s","startEvent","Wystąpienie/kontrola organu","Organ (zewn.)",{"eventType":"message"}),
             ("a1","userTask","Zarejestruj i przydziel sprawę","Zarząd",{}),
             ("a2","userTask","Przygotuj dane i wyjaśnienia","Komórki merytoryczne",{}),
             ("a3","sendTask","Udziel odpowiedzi organowi","Zarząd",{}),
             ("g1","exclusiveGateway","Zalecenia do wdrożenia?","Zarząd",{}),
             ("a4","userTask","Wdroż zalecenia","Komórki merytoryczne",{}),
             ("e1","endEvent","Sprawa z organem zamknięta","Zarząd",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a4","tak",0),("g1","e1","nie",1),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Korespondencja z organem","a3")]
    # Z6.03 komunikacja korporacyjna/media
    L = ["Komórka inicjująca","Zarząd","Dział Organizacyjno-Prawny"]
    n = [("s","startEvent","Potrzeba komunikatu / zapytanie mediów","Komórka inicjująca",{"eventType":"message"}),
         ("a1","userTask","Przygotuj treść komunikatu","Dział Organizacyjno-Prawny",{}),
         ("g1","exclusiveGateway","Zatwierdzić publikację?","Zarząd",{}),
         ("a2","sendTask","Opublikuj / przekaż mediom","Dział Organizacyjno-Prawny",{}),
         ("e1","endEvent","Komunikat opublikowany","Dział Organizacyjno-Prawny",{}),
         ("e2","endEvent","Komunikat wstrzymany","Zarząd",{})]
    f = C("s","a1","g1")+[("g1","a2","tak",1),("a2","e1",None,0),("g1","e2","nie",0)]
    return L,n,f,[("d1","dataObjectReference","Komunikat / oświadczenie","a1")]

# ============================ WARSTWA GLOWNA (G) ============================
def g_G1(p):
    k = _k(p)
    if k == "G1.01":
        L = ["Izba Przyjęć","Pielęgniarka","Lekarz IP"]
        n = [("s","startEvent","Przybycie pacjenta w stanie nagłym","Izba Przyjęć",{"eventType":"message"}),
             ("a1","userTask","Zarejestruj pacjenta i ustal tożsamość","Izba Przyjęć",{}),
             ("a2","manualTask","Wykonaj triaż i pomiary","Pielęgniarka",{}),
             ("a3","userTask","Zbadaj i zleć diagnostykę","Lekarz IP",{}),
             ("g1","exclusiveGateway","Wymaga hospitalizacji?","Lekarz IP",{}),
             ("a4","sendTask","Skieruj i przekaż na oddział","Lekarz IP",{}),
             ("a5","userTask","Zaopatrz i wypisz z zaleceniami","Lekarz IP",{}),
             ("e1","endEvent","Pacjent przyjęty na oddział","Lekarz IP",{}),
             ("e2","endEvent","Pacjent zaopatrzony ambulatoryjnie","Lekarz IP",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a4","tak",1),("a4","e1",None,0),("g1","a5","nie",0),("a5","e2",None,0)]
        return L,n,f,[("d1","dataObjectReference","Karta Izby Przyjęć","a1"),("d2","dataObjectReference","Dokumentacja medyczna","a3")]
    if k == "G1.02":
        L = ["Pielęgniarka triażu","Lekarz IP"]
        n = [("s","startEvent","Pacjent oczekujący w Izbie Przyjęć","Pielęgniarka triażu",{"eventType":"message"}),
             ("a1","manualTask","Oceń stan (skala ESI/Manchester)","Pielęgniarka triażu",{}),
             ("a2","businessRuleTask","Przydziel kategorię pilności","Pielęgniarka triażu",{}),
             ("g1","exclusiveGateway","Stan zagrożenia życia?","Pielęgniarka triażu",{}),
             ("a3","sendTask","Skieruj do pilnej interwencji","Lekarz IP",{}),
             ("a4","userTask","Skieruj do kolejki wg kategorii","Pielęgniarka triażu",{}),
             ("e1","endEvent","Pacjent skategoryzowany","Pielęgniarka triażu",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","e1",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Karta triażu","a2")]
    if k == "G1.03":
        L = ["Lekarz IP","Oddział docelowy"]
        n = [("s","startEvent","Decyzja o możliwej hospitalizacji","Lekarz IP",{"eventType":"message"}),
             ("a1","userTask","Oceń wskazania do hospitalizacji","Lekarz IP",{}),
             ("g1","exclusiveGateway","Kwalifikuje się?","Lekarz IP",{}),
             ("a2","sendTask","Uzgodnij przyjęcie z oddziałem","Lekarz IP",{}),
             ("a3","userTask","Przyjmij pacjenta na oddział","Oddział docelowy",{}),
             ("a4","userTask","Skieruj do leczenia ambulatoryjnego","Lekarz IP",{}),
             ("e1","endEvent","Pacjent zakwalifikowany i przyjęty","Oddział docelowy",{}),
             ("e2","endEvent","Skierowany ambulatoryjnie","Lekarz IP",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",1),("a2","a3",None,0),("a3","e1",None,0),("g1","a4","nie",0),("a4","e2",None,0)]
        return L,n,f,[("d1","dataObjectReference","Skierowanie / kwalifikacja","a1")]
    if k == "G1.04":
        L = ["Lekarz IP","Zespół Transportu Medycznego","Podmiot docelowy"]
        n = [("s","startEvent","Potrzeba przekazania pacjenta","Lekarz IP",{"eventType":"message"}),
             ("a1","businessRuleTask","Oceń wskazania i wybierz podmiot","Lekarz IP",{}),
             ("a2","sendTask","Uzgodnij przyjęcie w podmiocie","Podmiot docelowy",{}),
             ("g1","exclusiveGateway","Podmiot przyjmuje?","Lekarz IP",{}),
             ("a3","userTask","Zorganizuj transport sanitarny","Zespół Transportu Medycznego",{}),
             ("a4","sendTask","Przekaż pacjenta i dokumentację","Lekarz IP",{}),
             ("a5","userTask","Znajdź inny podmiot","Lekarz IP",{}),
             ("e1","endEvent","Pacjent przekazany","Lekarz IP",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","a4",None,0),("a4","e1",None,0),("g1","a5","nie",0),("a5","a2",None,0)]
        return L,n,f,[("d1","dataObjectReference","Karta przekazania","a4")]
    if k == "G1.05":
        L = ["Punkt Przyjęć Planowych","Koordynator PPP","Lekarz rehabilitacji"]
        n = [("s","startEvent","Wpływ skierowania na rehabilitację","Punkt Przyjęć Planowych",{"eventType":"message"}),
             ("a1","userTask","Zarejestruj skierowanie","Punkt Przyjęć Planowych",{}),
             ("a2","businessRuleTask","Zweryfikuj kompletność i uprawnienia","Koordynator PPP",{}),
             ("g1","exclusiveGateway","Skierowanie kompletne?","Koordynator PPP",{}),
             ("a3","userTask","Wpisz na listę oczekujących","Koordynator PPP",{}),
             ("a4","sendTask","Powiadom o terminie przyjęcia","Punkt Przyjęć Planowych",{}),
             ("a5","sendTask","Zwróć do uzupełnienia","Punkt Przyjęć Planowych",{}),
             ("e1","endEvent","Przyjęcie planowe zarejestrowane","Koordynator PPP",{}),
             ("e2","endEvent","Skierowanie do uzupełnienia","Punkt Przyjęć Planowych",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","a4",None,0),("a4","e1",None,0),("g1","a5","nie",0),("a5","e2",None,0)]
        return L,n,f,[("d1","dataObjectReference","Skierowanie","a1")]
    if k == "G1.06":
        L = ["Lekarz rehabilitacji","Zespół rehabilitacyjny"]
        n = [("s","startEvent","Zgłoszenie do programu rehabilitacji","Lekarz rehabilitacji",{"eventType":"message"}),
             ("a1","userTask","Oceń stan i wskazania","Lekarz rehabilitacji",{}),
             ("a2","businessRuleTask","Zakwalifikuj do programu","Lekarz rehabilitacji",{}),
             ("g1","exclusiveGateway","Kwalifikuje się?","Lekarz rehabilitacji",{}),
             ("a3","userTask","Ustal wstępne cele i plan","Zespół rehabilitacyjny",{}),
             ("a4","sendTask","Wskaż alternatywę / skieruj dalej","Lekarz rehabilitacji",{}),
             ("e1","endEvent","Zakwalifikowany do programu","Zespół rehabilitacyjny",{}),
             ("e2","endEvent","Niezakwalifikowany","Lekarz rehabilitacji",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","a4","nie",0),("a4","e2",None,0)]
        return L,n,f,[("d1","dataObjectReference","Karta kwalifikacji","a2")]
    if k == "G1.07":
        L = ["Koordynator PPP","Dział Rozliczeń Świadczeń"]
        n = [("s","startEvent","Prowadzenie listy oczekujących","Koordynator PPP",{"eventType":"timer"}),
             ("a1","userTask","Wpisuj i aktualizuj zgłoszenia","Koordynator PPP",{}),
             ("a2","businessRuleTask","Ustal kolejność wg kryteriów","Koordynator PPP",{}),
             ("a3","serviceTask","Sprawozdaj listę do NFZ/AOTMiT","Dział Rozliczeń Świadczeń",{}),
             ("g1","exclusiveGateway","Konieczna zmiana terminu?","Koordynator PPP",{}),
             ("a4","sendTask","Powiadom pacjentów o zmianie","Koordynator PPP",{}),
             ("e1","endEvent","Lista oczekujących prowadzona","Koordynator PPP",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a4","tak",0),("g1","e1","nie",1),("a4","a1",None,0)]
        return L,n,f,[("d1","dataStore","Lista oczekujących","a1")]
    if k == "G1.08":
        L = ["Rejestracja","Pacjent"]
        n = [("s","startEvent","Zgłoszenie rejestracji","Pacjent",{"eventType":"message"}),
             ("g1","exclusiveGateway","Kanał zgłoszenia?","Rejestracja",{}),
             ("c1","userTask","Obsłuż rejestrację osobistą","Rejestracja",{}),
             ("c2","userTask","Obsłuż rejestrację telefoniczną","Rejestracja",{}),
             ("c3","serviceTask","Obsłuż e-rejestrację","Rejestracja",{}),
             ("a1","userTask","Zidentyfikuj pacjenta i zweryfikuj uprawnienia (eWUŚ)","Rejestracja",{}),
             ("a2","userTask","Ustal termin i zarejestruj wizytę","Rejestracja",{}),
             ("a3","sendTask","Potwierdź termin (SMS/e-mail)","Rejestracja",{}),
             ("e1","endEvent","Pacjent zarejestrowany","Rejestracja",{})]
        f = [("s","g1",None,0),("g1","c1","osobista",1),("g1","c2","telefoniczna",0),("g1","c3","e-rejestracja",0)]+\
            [("c1","a1",None,0),("c2","a1",None,0),("c3","a1",None,0)]+C("a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Zgłoszenie/termin","a2")]
    # G1.09 POZ
    L = ["Rejestracja POZ","Pielęgniarka POZ","Lekarz POZ"]
    n = [("s","startEvent","Zgłoszenie pacjenta POZ","Rejestracja POZ",{"eventType":"message"}),
         ("a1","userTask","Sprawdź deklarację i eWUŚ","Rejestracja POZ",{}),
         ("g1","exclusiveGateway","Aktywna deklaracja?","Rejestracja POZ",{}),
         ("a2","userTask","Odbierz deklarację POZ","Pielęgniarka POZ",{}),
         ("a3","userTask","Wykonaj świadczenie POZ","Lekarz POZ",{}),
         ("e1","endEvent","Pacjent POZ obsłużony","Lekarz POZ",{})]
    f = C("s","a1","g1")+[("g1","a3","tak",1),("g1","a2","nie",0),("a2","a3",None,0),("a3","e1",None,0)]
    return L,n,f,[("d1","dataObjectReference","Deklaracja POZ","a2")]

def g_G2(p):
    k = _k(p)
    if k in ("G2.01","G2.02","G2.03","G2.07"):  # badania wykonywane w pracowni
        meta = {"G2.01":("badania obrazowego (RTG/TK/USG)","Technik","Lekarz radiolog"),
                "G2.02":("badania czynnościowego","Pielęgniarka","Lekarz"),
                "G2.03":("badania endoskopowego","Pielęgniarka","Lekarz endoskopista"),
                "G2.07":("badania obrazowego ze wspomaganiem AI","Technik","Lekarz radiolog")}[k]
        opis, wyk, opi = meta
        L = ["Lekarz zlecający","Pracownia diagnostyczna","Lekarz opisujący"]
        ai_step = []
        n = [("s","startEvent","Zlecenie "+opis,"Lekarz zlecający",{"eventType":"message"}),
             ("a1","userTask","Zweryfikuj zlecenie i przygotuj pacjenta","Pracownia diagnostyczna",{}),
             ("a2","manualTask","Wykonaj badanie ("+wyk+")","Pracownia diagnostyczna",{}),
             ("a3","userTask","Opisz i autoryzuj wynik","Lekarz opisujący",{}),
             ("g1","exclusiveGateway","Wynik wymaga powtórzenia?","Lekarz opisujący",{}),
             ("a4","serviceTask","Przekaż wynik do dokumentacji","Pracownia diagnostyczna",{}),
             ("e1","endEvent","Wynik dostępny dla zlecającego","Lekarz zlecający",{})]
        if k == "G2.07":
            n.insert(3,("a2b","serviceTask","Prześlij obrazy (DICOM) do analizy AI w PUI","Pracownia diagnostyczna",{}))
            f = C("s","a1","a2","a2b","a3","g1")+[("g1","a2","tak",0),("g1","a4","nie",1),("a4","e1",None,0)]
        else:
            f = C("s","a1","a2","a3","g1")+[("g1","a2","tak",0),("g1","a4","nie",1),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Zlecenie badania","a1"),("d2","dataObjectReference","Wynik / opis","a3")]
    if k == "G2.04":  # laboratoryjne
        L = ["Lekarz prowadzący","Pielęgniarka","Laboratorium"]
        n = [("s","startEvent","Zlecenie badań laboratoryjnych","Lekarz prowadzący",{"eventType":"message"}),
             ("a1","manualTask","Pobierz materiał i opisz próbki","Pielęgniarka",{}),
             ("a2","serviceTask","Wykonaj oznaczenia","Laboratorium",{}),
             ("g1","exclusiveGateway","Wynik krytyczny?","Laboratorium",{}),
             ("a3","sendTask","Zgłoś wartość krytyczną","Laboratorium",{}),
             ("a4","userTask","Odbierz i zinterpretuj wyniki","Lekarz prowadzący",{}),
             ("e1","endEvent","Wyniki w dokumentacji","Lekarz prowadzący",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Zlecenie / próbki","a1"),("d2","dataObjectReference","Wynik laboratoryjny","a4")]
    if k == "G2.05":  # umowa z lab zewn
        L = ["Dział Zamówień Publicznych","Dyrektor ds. Lecznictwa","Laboratorium zewn."]
        n = [("s","startEvent","Potrzeba/zmiana umowy z laboratorium","Dyrektor ds. Lecznictwa",{"eventType":"message"}),
             ("a1","userTask","Określ zakres badań i wymagania","Dyrektor ds. Lecznictwa",{}),
             ("a2","userTask","Przeprowadź wybór i negocjacje","Dział Zamówień Publicznych",{}),
             ("a3","sendTask","Zawrzyj umowę o świadczenie","Dział Zamówień Publicznych",{}),
             ("a4","manualTask","Monitoruj jakość i SLA","Dyrektor ds. Lecznictwa",{"loop":True}),
             ("e1","endEvent","Umowa z laboratorium realizowana","Dział Zamówień Publicznych",{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataObjectReference","Umowa z laboratorium","a3")]
    # G2.06 kontrola jakosci/kalibracja
    L = ["Inspektor Ochrony Radiologicznej","Dział Techniczny","Pracownia"]
    n = [("s","startEvent","Harmonogram kontroli/kalibracji","Inspektor Ochrony Radiologicznej",{"eventType":"timer"}),
         ("a1","manualTask","Wykonaj testy specjalistyczne/podstawowe","Pracownia",{}),
         ("a2","businessRuleTask","Oceń wyniki kontroli jakości","Inspektor Ochrony Radiologicznej",{}),
         ("g1","exclusiveGateway","Parametry w normie?","Inspektor Ochrony Radiologicznej",{}),
         ("a3","manualTask","Zleć kalibrację / serwis","Dział Techniczny",{}),
         ("a4","userTask","Udokumentuj i dopuść do użytku","Inspektor Ochrony Radiologicznej",{}),
         ("e1","endEvent","Sprzęt dopuszczony","Inspektor Ochrony Radiologicznej",{})]
    f = C("s","a1","a2","g1")+[("g1","a4","tak",1),("g1","a3","nie",0),("a3","a4",None,0),("a4","e1",None,0)]
    return L,n,f,[("d1","dataObjectReference","Protokół kontroli jakości","a2")]

def g_G3(p):
    k = _k(p)
    HOSP = {"G3.01":("Oddział Chorób Wewnętrznych","Lekarz prowadzący"),
            "G3.03":("Oddział Geriatrii","Lekarz geriatra"),
            "G3.04":("Oddział Chorób Płuc","Lekarz pulmonolog"),
            "G3.05":("Oddział Chorób Płuc dla Dzieci","Lekarz pediatra-pulmonolog"),
            "G3.06":("Oddział Reumatologii","Lekarz reumatolog")}
    if k in HOSP:
        ward, doc = HOSP[k]
        L = [doc, "Pielęgniarka", "Diagnostyka"]
        n = [("s","startEvent","Przyjęcie pacjenta - "+ward,doc,{"eventType":"message"}),
             ("a1","userTask","Zbierz wywiad i zbadaj pacjenta",doc,{}),
             ("a2","sendTask","Zleć badania diagnostyczne",doc,{}),
             ("a3","manualTask","Wykonaj badania","Diagnostyka",{}),
             ("a4","userTask","Ustal rozpoznanie i plan leczenia",doc,{}),
             ("a5","manualTask","Realizuj leczenie i opiekę","Pielęgniarka",{"loop":True}),
             ("a6","userTask","Oceń efekty leczenia",doc,{}),
             ("g1","exclusiveGateway","Cel leczenia osiągnięty?",doc,{}),
             ("a7","userTask","Przygotuj pacjenta do wypisu",doc,{}),
             ("e1","endEvent","Leczenie zakończone - do wypisu",doc,{})]
        f = C("s","a1","a2","a3","a4","a5","a6","g1")+[("g1","a7","tak",1),("a7","e1",None,0),("g1","a5","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Historia choroby","a1"),
                      ("d2","dataObjectReference","Karta zleceń lekarskich","a4"),
                      ("d3","dataObjectReference","Wyniki badań","a3")]
    if k in ("G3.07","G3.08"):
        ward = "oddział" if k=="G3.07" else "oddział kliniczny"
        L = ["Lekarz rehabilitacji","Fizjoterapeuta","Zespół rehabilitacyjny"]
        n = [("s","startEvent","Rozpoczęcie rehabilitacji ("+ward+")","Lekarz rehabilitacji",{"eventType":"message"}),
             ("a1","userTask","Oceń stan i ustal cele","Lekarz rehabilitacji",{}),
             ("a2","userTask","Opracuj Plan Rehabilitacji Indywidualnej (PRI)","Zespół rehabilitacyjny",{}),
             ("a3","manualTask","Realizuj zabiegi wg PRI","Fizjoterapeuta",{"loop":True}),
             ("a4","userTask","Oceń postępy na spotkaniu zespołu","Zespół rehabilitacyjny",{}),
             ("g1","exclusiveGateway","Cele osiągnięte?","Lekarz rehabilitacji",{}),
             ("a5","userTask","Zmodyfikuj PRI","Zespół rehabilitacyjny",{}),
             ("a6","userTask","Zamknij rehabilitację i udokumentuj","Lekarz rehabilitacji",{}),
             ("e1","endEvent","Rehabilitacja zakończona","Lekarz rehabilitacji",{})]
        f = C("s","a1","a2","a3","a4","g1")+[("g1","a6","tak",1),("a6","e1",None,0),("g1","a5","nie",0),("a5","a3",None,0)]
        return L,n,f,[("d1","dataObjectReference","Plan Rehabilitacji (PRI)","a2")]
    if k == "G3.02":
        L = ["Zespół geriatryczny","Lekarz geriatra"]
        n = [("s","startEvent","Skierowanie do oceny geriatrycznej","Lekarz geriatra",{"eventType":"message"}),
             ("a1","manualTask","Przeprowadź testy przesiewowe i wywiad","Zespół geriatryczny",{}),
             ("a2","userTask","Oceń sprawność, funkcje i choroby współistniejące","Lekarz geriatra",{}),
             ("a3","businessRuleTask","Sporządź Całościową Ocenę Geriatryczną (CGA)","Lekarz geriatra",{}),
             ("a4","userTask","Ustal plan opieki geriatrycznej","Zespół geriatryczny",{}),
             ("e1","endEvent","Ocena geriatryczna gotowa","Lekarz geriatra",{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataObjectReference","Karta CGA","a3")]
    if k == "G3.09":
        L = ["Lekarz zlecający","Lekarz konsultujący"]
        n = [("s","startEvent","Zlecenie konsultacji specjalistycznej","Lekarz zlecający",{"eventType":"message"}),
             ("a1","userTask","Sprecyzuj pytanie kliniczne","Lekarz zlecający",{}),
             ("g1","exclusiveGateway","Konsultacja zewnętrzna?","Lekarz zlecający",{}),
             ("a2","userTask","Wykonaj konsultację i badanie","Lekarz konsultujący",{}),
             ("a3","sendTask","Zorganizuj konsultację zewnętrzną","Lekarz zlecający",{}),
             ("a4","userTask","Wydaj zalecenia konsultacyjne","Lekarz konsultujący",{}),
             ("e1","endEvent","Konsultacja zrealizowana","Lekarz zlecający",{})]
        f = C("s","a1","g1")+[("g1","a2","nie",1),("g1","a3","tak",0),("a3","a2",None,0),("a2","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Karta konsultacji","a4")]
    if k == "G3.10":
        L = ["Oddział kierujący","Oddział przyjmujący","Zespół Transportu Medycznego"]
        n = [("s","startEvent","Decyzja o przekazaniu pacjenta","Oddział kierujący",{"eventType":"message"}),
             ("a1","userTask","Przygotuj dokumentację przekazania","Oddział kierujący",{}),
             ("a2","sendTask","Uzgodnij przyjęcie","Oddział przyjmujący",{}),
             ("g1","exclusiveGateway","Przekazanie wewnętrzne?","Oddział kierujący",{}),
             ("a3","userTask","Przekaż na inny oddział","Oddział przyjmujący",{}),
             ("a4","userTask","Zorganizuj transport do podmiotu zewn.","Zespół Transportu Medycznego",{}),
             ("e1","endEvent","Pacjent przekazany","Oddział przyjmujący",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","wewn.",1),("a3","e1",None,0),("g1","a4","zewn.",0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Karta przekazania","a1")]
    if k == "G3.11":
        L = ["Lekarz","Pielęgniarka","Sekcja Dokumentacji Medycznej"]
        n = [("s","startEvent","Stwierdzenie zgonu pacjenta","Lekarz",{"eventType":"message"}),
             ("a1","userTask","Stwierdź zgon i ustal przyczynę","Lekarz",{}),
             ("a2","userTask","Wystaw kartę zgonu","Lekarz",{}),
             ("g1","exclusiveGateway","Wymagane zgłoszenie / sekcja?","Lekarz",{}),
             ("a3","sendTask","Zgłoś i zorganizuj sekcję","Lekarz",{}),
             ("a4","manualTask","Przygotuj ciało i dokumentację","Pielęgniarka",{}),
             ("a5","sendTask","Przekaż do chłodni / firmie pogrzebowej","Sekcja Dokumentacji Medycznej",{}),
             ("e1","endEvent","Postępowanie ze zgonem zakończone","Sekcja Dokumentacji Medycznej",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","a5",None,0),("a5","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Karta zgonu","a2")]
    if k == "G3.12":
        L = ["Lekarz prowadzący","Sekcja Dokumentacji Medycznej"]
        n = [("s","startEvent","Świadczenie wymagające zgody","Lekarz prowadzący",{"eventType":"message"}),
             ("a1","userTask","Poinformuj pacjenta (świadoma zgoda)","Lekarz prowadzący",{}),
             ("g1","exclusiveGateway","Zgoda udzielona?","Lekarz prowadzący",{}),
             ("a2","userTask","Odbierz i zarchiwizuj zgodę","Sekcja Dokumentacji Medycznej",{}),
             ("a3","userTask","Odnotuj sprzeciw / odmowę","Lekarz prowadzący",{}),
             ("e1","endEvent","Zgoda udokumentowana","Sekcja Dokumentacji Medycznej",{}),
             ("e2","endEvent","Odmowa udokumentowana","Lekarz prowadzący",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",1),("a2","e1",None,0),("g1","a3","nie",0),("a3","e2",None,0)]
        return L,n,f,[("d1","dataObjectReference","Formularz zgody","a2")]
    if k in ("G3.13","G3.16"):
        poz = k == "G3.16"
        rej = "Rejestracja POZ" if poz else "Rejestracja"; doc = "Lekarz POZ" if poz else "Lekarz specjalista"
        L = [rej, doc]
        n = [("s","startEvent","Pacjent na wizytę","Pacjent" if False else rej,{"eventType":"message"}),
             ("a1","userTask","Przygotuj dokumentację wizyty",rej,{}),
             ("a2","userTask","Przeprowadź wywiad i badanie",doc,{}),
             ("g1","exclusiveGateway","Potrzebna diagnostyka / leczenie?",doc,{}),
             ("a3","sendTask","Zleć badania / wystaw recepty i skierowania",doc,{}),
             ("a4","userTask","Udokumentuj wizytę i zalecenia",doc,{}),
             ("e1","endEvent","Wizyta zakończona",doc,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Dokumentacja wizyty","a4")]
    if k == "G3.14":
        L = ["Pielęgniarka","Lekarz"]
        n = [("s","startEvent","Zlecenie świadczenia zabiegowego","Lekarz",{"eventType":"message"}),
             ("a1","userTask","Zweryfikuj zlecenie i przygotuj pacjenta","Pielęgniarka",{}),
             ("a2","manualTask","Wykonaj świadczenie zabiegowe","Lekarz",{}),
             ("a3","userTask","Udokumentuj i poinstruuj pacjenta","Pielęgniarka",{}),
             ("e1","endEvent","Świadczenie zrealizowane","Lekarz",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Opis zabiegu","a3")]
    if k == "G3.15":
        L = ["Lekarz","System P1 / ZUS"]
        n = [("s","startEvent","Potrzeba wystawienia e-dokumentu","Lekarz",{"eventType":"message"}),
             ("g1","exclusiveGateway","Rodzaj dokumentu?","Lekarz",{}),
             ("c1","userTask","Wystaw e-receptę","Lekarz",{}),
             ("c2","userTask","Wystaw e-skierowanie","Lekarz",{}),
             ("c3","userTask","Wystaw e-ZLA / zaświadczenie","Lekarz",{}),
             ("a1","serviceTask","Prześlij dokument do P1 / ZUS","System P1 / ZUS",{}),
             ("a2","sendTask","Przekaż pacjentowi (kod / wydruk)","Lekarz",{}),
             ("e1","endEvent","E-dokument wystawiony","Lekarz",{})]
        f = [("s","g1",None,0),("g1","c1","e-recepta",1),("g1","c2","e-skierowanie",0),("g1","c3","e-ZLA/zaśw.",0),
             ("c1","a1",None,0),("c2","a1",None,0),("c3","a1",None,0)]+C("a1","a2","e1")
        return L,n,f,[("d1","dataObjectReference","E-dokument","a1")]
    if k == "G3.17":
        L = ["Pielęgniarka POZ","Lekarz POZ"]
        n = [("s","startEvent","Zlecenie / plan opieki POZ","Lekarz POZ",{"eventType":"message"}),
             ("a1","userTask","Zaplanuj świadczenia środowiskowe","Pielęgniarka POZ",{}),
             ("a2","manualTask","Wykonaj świadczenia (iniekcje, opatrunki, wizyty domowe)","Pielęgniarka POZ",{"loop":True}),
             ("a3","userTask","Udokumentuj świadczenia","Pielęgniarka POZ",{}),
             ("e1","endEvent","Świadczenia pielęgniarskie zrealizowane","Pielęgniarka POZ",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Dokumentacja świadczeń","a3")]
    if k == "G3.18":
        L = ["Pielęgniarka medycyny szkolnej","Lekarz POZ"]
        n = [("s","startEvent","Harmonogram profilaktyki szkolnej","Pielęgniarka medycyny szkolnej",{"eventType":"timer"}),
             ("a1","manualTask","Wykonaj testy przesiewowe i bilanse","Pielęgniarka medycyny szkolnej",{}),
             ("g1","exclusiveGateway","Wykryto nieprawidłowości?","Pielęgniarka medycyny szkolnej",{}),
             ("a2","sendTask","Skieruj do lekarza / poradni","Lekarz POZ",{}),
             ("a3","userTask","Prowadź edukację i udokumentuj","Pielęgniarka medycyny szkolnej",{}),
             ("e1","endEvent","Profilaktyka zrealizowana","Pielęgniarka medycyny szkolnej",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Karta profilaktyki","a1")]
    if k == "G3.19":
        L = ["Pielęgniarka POZ","Lekarz POZ"]
        n = [("s","startEvent","Termin bilansu / szczepienia","Pielęgniarka POZ",{"eventType":"timer"}),
             ("a1","userTask","Zweryfikuj kalendarz szczepień i bilansów","Pielęgniarka POZ",{}),
             ("a2","userTask","Przeprowadź badanie bilansowe","Lekarz POZ",{}),
             ("g1","exclusiveGateway","Kwalifikacja do szczepienia?","Lekarz POZ",{}),
             ("a3","manualTask","Wykonaj szczepienie","Pielęgniarka POZ",{}),
             ("a4","userTask","Udokumentuj (karta / PSO / e-Karta Szczepień)","Pielęgniarka POZ",{}),
             ("e1","endEvent","Bilans/szczepienie zrealizowane","Pielęgniarka POZ",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","a4",None,0),("g1","a4","nie",0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Karta szczepień / bilans","a4")]
    if k in ("G3.20","G3.21"):
        ger = k == "G3.21"
        doc = "Zespół geriatryczny" if ger else "Lekarz rehabilitacji"; wyk = "Pielęgniarka" if ger else "Fizjoterapeuta"
        opis = "dziennej opieki geriatrycznej" if ger else "rehabilitacji w ośrodku dziennym"
        L = [doc, wyk]
        n = [("s","startEvent","Kwalifikacja do "+opis,doc,{"eventType":"message"}),
             ("a1","userTask","Zakwalifikuj i ustal plan",""+doc,{}),
             ("a2","manualTask","Realizuj świadczenia wg planu",wyk,{"loop":True}),
             ("a3","userTask","Oceń postępy",doc,{}),
             ("g1","exclusiveGateway","Kontynuować cykl?",doc,{}),
             ("a4","userTask","Zakończ i udokumentuj",doc,{}),
             ("e1","endEvent","Opieka dzienna zrealizowana",doc,{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a2","tak",0),("g1","a4","nie",1),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Plan i karta świadczeń","a1")]
    if k == "G3.22":
        L = ["Fizjoterapeuta","Lekarz rehabilitacji"]
        n = [("s","startEvent","Zlecenie zabiegu rehabilitacji","Lekarz rehabilitacji",{"eventType":"message"}),
             ("a1","userTask","Zweryfikuj zlecenie i plan zabiegów","Fizjoterapeuta",{}),
             ("g1","exclusiveGateway","Modalność zabiegu?","Fizjoterapeuta",{}),
             ("c1","manualTask","Wykonaj fizykoterapię","Fizjoterapeuta",{}),
             ("c2","manualTask","Wykonaj kinezyterapię","Fizjoterapeuta",{}),
             ("c3","manualTask","Wykonaj hydro-/krioterapię / masaż","Fizjoterapeuta",{}),
             ("c4","manualTask","Zrealizuj rehabilitację domową","Fizjoterapeuta",{}),
             ("a2","userTask","Udokumentuj i oceń efekt","Fizjoterapeuta",{}),
             ("e1","endEvent","Zabieg zrealizowany","Fizjoterapeuta",{})]
        f = [("s","a1",None,0),("a1","g1",None,0),("g1","c1","fizyko",1),("g1","c2","kinezy",0),
             ("g1","c3","hydro/krio/masaż",0),("g1","c4","domowa",0),
             ("c1","a2",None,0),("c2","a2",None,0),("c3","a2",None,0),("c4","a2",None,0),("a2","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Karta zabiegów","a2")]
    # G3.23 kompleksowa diagnoza funkcjonalna
    L = ["Zespół interdyscyplinarny","Lekarz"]
    n = [("s","startEvent","Skierowanie do diagnozy funkcjonalnej","Lekarz",{"eventType":"message"}),
         ("a1","manualTask","Przeprowadź ocenę interdyscyplinarną","Zespół interdyscyplinarny",{}),
         ("a2","businessRuleTask","Sporządź diagnozę funkcjonalną","Lekarz",{}),
         ("a3","userTask","Opracuj plan usprawniania","Zespół interdyscyplinarny",{}),
         ("e1","endEvent","Diagnoza funkcjonalna gotowa","Lekarz",{})]
    f = C("s","a1","a2","a3","e1")
    return L,n,f,[("d1","dataObjectReference","Diagnoza funkcjonalna / plan","a2")]

def g_G4(p):
    k = _k(p)
    if k == "G4.01":
        L = ["Lekarz prowadzący","Pielęgniarka","Sekcja Dokumentacji Medycznej"]
        n = [("s","startEvent","Decyzja o wypisie","Lekarz prowadzący",{"eventType":"message"}),
             ("a1","userTask","Sporządź epikryzę i kartę wypisu","Lekarz prowadzący",{}),
             ("a2","userTask","Wystaw recepty, skierowania, zalecenia","Lekarz prowadzący",{}),
             ("a3","userTask","Poinstruuj pacjenta i przekaż dokumenty","Pielęgniarka",{}),
             ("a4","serviceTask","Zarejestruj wypis w systemie","Sekcja Dokumentacji Medycznej",{}),
             ("e1","endEvent","Pacjent wypisany","Sekcja Dokumentacji Medycznej",{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataObjectReference","Karta wypisu / epikryza","a1")]
    if k == "G4.02":
        L = ["Pielęgniarka","Lekarz"]
        n = [("s","startEvent","Przygotowanie pacjenta do wypisu","Pielęgniarka",{"eventType":"message"}),
             ("a1","userTask","Oceń potrzeby edukacyjne","Pielęgniarka",{}),
             ("a2","manualTask","Przekaż zalecenia i przeszkol pacjenta/opiekuna","Pielęgniarka",{}),
             ("g1","exclusiveGateway","Zrozumienie potwierdzone?","Pielęgniarka",{}),
             ("a3","userTask","Udokumentuj edukację","Pielęgniarka",{}),
             ("e1","endEvent","Edukacja zrealizowana","Pielęgniarka",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","a2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Karta edukacji","a3")]
    if k == "G4.03":
        L = ["Lekarz prowadzący","Koordynator opieki","Podmiot przejmujący"]
        n = [("s","startEvent","Planowanie kontynuacji opieki","Lekarz prowadzący",{"eventType":"message"}),
             ("a1","businessRuleTask","Określ formę kontynuacji (POZ/AOS/długoterminowa)","Lekarz prowadzący",{}),
             ("a2","sendTask","Uzgodnij przejęcie opieki","Koordynator opieki",{}),
             ("a3","sendTask","Przekaż dokumentację do podmiotu","Podmiot przejmujący",{}),
             ("e1","endEvent","Opieka przekazana","Koordynator opieki",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Skierowanie / karta kontynuacji","a2")]
    # G4.04 turnusy / wyroby medyczne
    L = ["Lekarz","Koordynator"]
    n = [("s","startEvent","Potrzeba zaopatrzenia / turnusu","Lekarz",{"eventType":"message"}),
         ("a1","userTask","Oceń wskazania","Lekarz",{}),
         ("a2","userTask","Wystaw wniosek / zlecenie na wyroby","Lekarz",{}),
         ("g1","exclusiveGateway","Wymaga potwierdzenia NFZ?","Lekarz",{}),
         ("a3","sendTask","Prześlij do potwierdzenia (eZWM/NFZ)","Koordynator",{}),
         ("a4","sendTask","Przekaż dokument pacjentowi","Koordynator",{}),
         ("e1","endEvent","Wniosek wystawiony","Koordynator",{})]
    f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","e1",None,0)]
    return L,n,f,[("d1","dataObjectReference","Wniosek / zlecenie","a2")]

def g_G5(p):
    k = _k(p)
    if k in ("G5.01","G5.08"):
        loc = "szpitala" if k=="G5.01" else "szpitala rehabilitacyjnego (POK)"
        kier = "Kierownik Apteki" if k=="G5.01" else "Kierownik Działu Farmacji"
        L = [kier,"Dostawca (zewn.)","Dział Finansowo-Księgowy"]
        n = [("s","startEvent","Potrzeba uzupełnienia zapasów "+loc,kier,{"eventType":"timer"}),
             ("a1","userTask","Określ zapotrzebowanie i stany","" +kier,{}),
             ("a2","sendTask","Złóż zamówienie do dostawcy","Dostawca (zewn.)",{}),
             ("a3","manualTask","Przyjmij i skontroluj dostawę",kier,{}),
             ("g1","exclusiveGateway","Dostawa zgodna?",kier,{}),
             ("a4","sendTask","Reklamuj dostawę","Dostawca (zewn.)",{}),
             ("a5","serviceTask","Zaewidencjonuj i rozlicz","Dział Finansowo-Księgowy",{}),
             ("e1","endEvent","Zapasy uzupełnione",kier,{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a5","tak",1),("a5","e1",None,0),("g1","a4","nie",0),("a4","a3",None,0)]
        return L,n,f,[("d1","dataObjectReference","Zamówienie / dostawa","a2"),("d2","dataStore","Ewidencja apteczna","a5")]
    if k == "G5.02":
        L = ["Komitet Terapeutyczny","Apteka"]
        n = [("s","startEvent","Przegląd receptariusza","Apteka",{"eventType":"timer"}),
             ("a1","userTask","Zbierz wnioski o zmiany","Apteka",{}),
             ("a2","businessRuleTask","Oceń skuteczność i bezpieczeństwo","Komitet Terapeutyczny",{}),
             ("g1","exclusiveGateway","Zaktualizować receptariusz?","Komitet Terapeutyczny",{}),
             ("a3","serviceTask","Zaktualizuj i opublikuj receptariusz","Apteka",{}),
             ("e1","endEvent","Receptariusz aktualny","Apteka",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","e1","nie",0)]
        return L,n,f,[("d1","dataStore","Receptariusz szpitalny","a3")]
    if k == "G5.03":
        L = ["Oddział","Apteka"]
        n = [("s","startEvent","Zamówienie oddziałowe na leki","Oddział",{"eventType":"message"}),
             ("a1","userTask","Złóż zapotrzebowanie","Oddział",{}),
             ("a2","businessRuleTask","Zweryfikuj zamówienie i dostępność","Apteka",{}),
             ("a3","manualTask","Skompletuj i wydaj leki","Apteka",{}),
             ("a4","serviceTask","Zaewidencjonuj wydanie","Apteka",{}),
             ("e1","endEvent","Leki wydane na oddział","Apteka",{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataObjectReference","Zapotrzebowanie oddziałowe","a1")]
    if k == "G5.04":
        L = ["Farmaceuta","Lekarz"]
        n = [("s","startEvent","Zlecenie leku recepturowego","Lekarz",{"eventType":"message"}),
             ("a1","businessRuleTask","Zweryfikuj recepturę i wykonalność","Farmaceuta",{}),
             ("g1","exclusiveGateway","Wykonalne i bezpieczne?","Farmaceuta",{}),
             ("a2","sendTask","Skonsultuj z lekarzem","Lekarz",{}),
             ("a3","manualTask","Sporządź lek recepturowy","Farmaceuta",{}),
             ("a4","userTask","Wydaj i udokumentuj","Farmaceuta",{}),
             ("e1","endEvent","Lek recepturowy wydany","Farmaceuta",{})]
        f = C("s","a1","g1")+[("g1","a3","tak",1),("a3","a4",None,0),("a4","e1",None,0),("g1","a2","nie",0),("a2","a1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Receptura","a3")]
    if k == "G5.05":
        L = ["Apteka","Oddział"]
        n = [("s","startEvent","Obrót środkami odurzającymi/psychotropowymi","Oddział",{"eventType":"message"}),
             ("a1","businessRuleTask","Zweryfikuj uprawnienia i zapotrzebowanie","Apteka",{}),
             ("a2","manualTask","Wydaj za pokwitowaniem","Apteka",{}),
             ("a3","manualTask","Prowadź ewidencję i kontrolę stanów","Apteka",{"loop":True}),
             ("e1","endEvent","Obrót udokumentowany","Apteka",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataStore","Ewidencja środków odurzających","a3")]
    if k == "G5.06":
        L = ["Farmaceuta kliniczny","Lekarz","Pielęgniarka"]
        n = [("s","startEvent","Włączenie do opieki farmaceutycznej","Farmaceuta kliniczny",{"eventType":"message"}),
             ("a1","userTask","Przeanalizuj farmakoterapię","Farmaceuta kliniczny",{}),
             ("g1","exclusiveGateway","Wykryto problem lekowy?","Farmaceuta kliniczny",{}),
             ("a2","sendTask","Zarekomenduj zmianę lekarzowi","Lekarz",{}),
             ("a3","manualTask","Monitoruj terapię i edukuj","Pielęgniarka",{"loop":True}),
             ("e1","endEvent","Opieka farmaceutyczna prowadzona","Farmaceuta kliniczny",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Plan opieki farmaceutycznej","a1")]
    # G5.07 pharmacovigilance
    L = ["Personel zgłaszający","Apteka / Lekarz"]
    n = [("s","startEvent","Podejrzenie niepożądanego działania leku","Personel zgłaszający",{"eventType":"message"}),
         ("a1","userTask","Zarejestruj zgłoszenie NDL","Personel zgłaszający",{}),
         ("a2","userTask","Oceń i uzupełnij dane","Apteka / Lekarz",{}),
         ("a3","sendTask","Zgłoś do URPL / podmiotu odpowiedzialnego","Apteka / Lekarz",{}),
         ("e1","endEvent","NDL zgłoszone","Apteka / Lekarz",{})]
    f = C("s","a1","a2","a3","e1")
    return L,n,f,[("d1","dataObjectReference","Zgłoszenie NDL","a1")]

def g_G6(p):
    k = _k(p)
    if k == "G6.01":
        L = ["Pielęgniarka"]
        n = [("s","startEvent","Objęcie pacjenta opieką","Pielęgniarka",{"eventType":"message"}),
             ("a1","userTask","Rozpoznaj problemy pielęgnacyjne","Pielęgniarka",{}),
             ("a2","userTask","Zaplanuj opiekę","Pielęgniarka",{}),
             ("a3","manualTask","Realizuj plan opieki","Pielęgniarka",{"loop":True}),
             ("a4","userTask","Oceń efekty opieki","Pielęgniarka",{}),
             ("g1","exclusiveGateway","Cele osiągnięte?","Pielęgniarka",{}),
             ("a5","userTask","Udokumentuj proces pielęgnowania","Pielęgniarka",{}),
             ("e1","endEvent","Proces pielęgnowania zakończony","Pielęgniarka",{})]
        f = C("s","a1","a2","a3","a4","g1")+[("g1","a5","tak",1),("a5","e1",None,0),("g1","a2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Karta opieki pielęgniarskiej","a2")]
    if k == "G6.02":
        L = ["Przełożona Pielęgniarek","Pielęgniarki"]
        n = [("s","startEvent","Cykl nadzoru nad jakością opieki","Przełożona Pielęgniarek",{"eventType":"timer"}),
             ("a1","userTask","Opracuj/aktualizuj standardy opieki","Przełożona Pielęgniarek",{}),
             ("a2","manualTask","Przeprowadź audyty pielęgniarskie","Pielęgniarki",{}),
             ("g1","exclusiveGateway","Odchylenia od standardu?","Przełożona Pielęgniarek",{}),
             ("a3","userTask","Wdroż działania naprawcze","Pielęgniarki",{}),
             ("e1","endEvent","Jakość opieki nadzorowana","Przełożona Pielęgniarek",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","e1","nie",1),("a3","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Standardy opieki","a1")]
    if k == "G6.03":
        L = ["Przełożona Pielęgniarek","Dział Personalno-Płacowy"]
        n = [("s","startEvent","Planowanie grafików i obsady","Przełożona Pielęgniarek",{"eventType":"timer"}),
             ("a1","businessRuleTask","Ustal normy obsady","Przełożona Pielęgniarek",{}),
             ("a2","userTask","Sporządź grafik","Przełożona Pielęgniarek",{}),
             ("g1","exclusiveGateway","Obsada wystarczająca?","Przełożona Pielęgniarek",{}),
             ("a3","userTask","Uruchom zastępstwa / dyżury","Przełożona Pielęgniarek",{}),
             ("a4","serviceTask","Zatwierdź i przekaż do kadr","Dział Personalno-Płacowy",{}),
             ("e1","endEvent","Grafik obowiązuje","Dział Personalno-Płacowy",{})]
        f = C("s","a1","a2","g1")+[("g1","a4","tak",1),("g1","a3","nie",0),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Grafik / normy obsady","a2")]
    if k == "G6.04":
        L = ["Przełożona Pielęgniarek","Pielęgniarka"]
        n = [("s","startEvent","Planowanie rozwoju zawodowego","Przełożona Pielęgniarek",{"eventType":"timer"}),
             ("a1","userTask","Zidentyfikuj potrzeby szkoleniowe","Przełożona Pielęgniarek",{}),
             ("a2","userTask","Zaplanuj szkolenia / specjalizacje","Przełożona Pielęgniarek",{}),
             ("a3","manualTask","Realizuj rozwój","Pielęgniarka",{}),
             ("a4","userTask","Udokumentuj kompetencje","Przełożona Pielęgniarek",{}),
             ("e1","endEvent","Rozwój zawodowy udokumentowany","Przełożona Pielęgniarek",{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataStore","Rejestr kompetencji","a4")]
    # G6.05 dietetyka
    L = ["Dietetyk","Oddział / Kuchnia"]
    n = [("s","startEvent","Zlecenie diety","Oddział / Kuchnia",{"eventType":"message"}),
         ("a1","businessRuleTask","Ustal dietę i zapotrzebowanie","Dietetyk",{}),
         ("a2","sendTask","Przekaż zlecenie do kuchni/cateringu","Oddział / Kuchnia",{}),
         ("a3","manualTask","Monitoruj stan odżywienia","Dietetyk",{"loop":True}),
         ("e1","endEvent","Żywienie zaplanowane i monitorowane","Dietetyk",{})]
    f = C("s","a1","a2","a3","e1")
    return L,n,f,[("d1","dataObjectReference","Karta diety","a1")]

def g_G7(p):
    k = _k(p)
    if k == "G7.01":
        L = ["Pielęgniarka epidemiologiczna","Oddziały","Komitet ds. Zakażeń"]
        n = [("s","startEvent","Nadzór nad zakażeniami szpitalnymi","Pielęgniarka epidemiologiczna",{"eventType":"timer"}),
             ("a1","manualTask","Monitoruj i rejestruj zakażenia","Oddziały",{}),
             ("g1","exclusiveGateway","Przekroczenie progu / ognisko?","Pielęgniarka epidemiologiczna",{}),
             ("a2","userTask","Wdroż dochodzenie i działania p/epidemiczne","Pielęgniarka epidemiologiczna",{}),
             ("a3","userTask","Analizuj trendy i raportuj","Komitet ds. Zakażeń",{}),
             ("e1","endEvent","Zakażenia pod nadzorem","Pielęgniarka epidemiologiczna",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
        return L,n,f,[("d1","dataStore","Rejestr zakażeń","a1")]
    if k == "G7.02":
        L = ["Laboratorium","Pielęgniarka epidemiologiczna"]
        n = [("s","startEvent","Wykrycie drobnoustroju alarmowego","Laboratorium",{"eventType":"message"}),
             ("a1","userTask","Zarejestruj w rejestrze alarmowym","Pielęgniarka epidemiologiczna",{}),
             ("a2","sendTask","Powiadom oddział i wdroż izolację","Pielęgniarka epidemiologiczna",{}),
             ("a3","sendTask","Raportuj do PSSE","Pielęgniarka epidemiologiczna",{}),
             ("e1","endEvent","Drobnoustrój alarmowy obsłużony","Pielęgniarka epidemiologiczna",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataStore","Rejestr drobnoustrojów alarmowych","a1")]
    if k == "G7.03":
        L = ["Komitet Antybiotykowy","Lekarze","Apteka"]
        n = [("s","startEvent","Polityka antybiotykowa (cykl)","Komitet Antybiotykowy",{"eventType":"timer"}),
             ("a1","userTask","Opracuj / aktualizuj rekomendacje","Komitet Antybiotykowy",{}),
             ("a2","manualTask","Monitoruj zużycie antybiotyków","Apteka",{}),
             ("g1","exclusiveGateway","Odchylenia od polityki?","Komitet Antybiotykowy",{}),
             ("a3","sendTask","Interwencja / konsultacja","Lekarze",{}),
             ("e1","endEvent","Polityka antybiotykowa nadzorowana","Komitet Antybiotykowy",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","e1","nie",1),("a3","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Rekomendacje antybiotykowe","a1")]
    if k == "G7.04":
        L = ["Personel sterylizacji","Dział Techniczny"]
        n = [("s","startEvent","Materiał do dekontaminacji","Personel sterylizacji",{"eventType":"message"}),
             ("a1","manualTask","Przeprowadź mycie i dezynfekcję","Personel sterylizacji",{}),
             ("a2","manualTask","Sterylizuj i kontroluj proces","Personel sterylizacji",{}),
             ("g1","exclusiveGateway","Wynik kontroli prawidłowy?","Personel sterylizacji",{}),
             ("a3","userTask","Zwolnij i wydaj materiał","Personel sterylizacji",{}),
             ("e1","endEvent","Materiał sterylny wydany","Personel sterylizacji",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","a1","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Protokół sterylizacji","a2")]
    if k == "G7.05":
        L = ["Personel / DHiE","Dział Techniczny","Odbiorca (zewn.)"]
        n = [("s","startEvent","Wytworzenie odpadów medycznych","Personel / DHiE",{"eventType":"message"}),
             ("a1","manualTask","Segreguj i znakuj odpady","Personel / DHiE",{}),
             ("a2","manualTask","Magazynuj zgodnie z wymogami","Dział Techniczny",{}),
             ("a3","sendTask","Przekaż do utylizacji (BDO/KPO)","Odbiorca (zewn.)",{}),
             ("e1","endEvent","Odpady przekazane do utylizacji","Dział Techniczny",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Karta przekazania odpadów (KPO)","a3")]
    if k == "G7.06":
        L = ["Pielęgniarka epidemiologiczna","Personel"]
        n = [("s","startEvent","Monitoring higieny rąk (cykl)","Pielęgniarka epidemiologiczna",{"eventType":"timer"}),
             ("a1","manualTask","Obserwuj zgodność higieny rąk","Pielęgniarka epidemiologiczna",{}),
             ("a2","businessRuleTask","Oblicz wskaźniki zgodności","Pielęgniarka epidemiologiczna",{}),
             ("g1","exclusiveGateway","Poniżej celu?","Pielęgniarka epidemiologiczna",{}),
             ("a3","userTask","Prowadź szkolenia i promocję","Personel",{}),
             ("e1","endEvent","Higiena rąk monitorowana","Pielęgniarka epidemiologiczna",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","e1","nie",1),("a3","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Wskaźniki higieny rąk","a2")]
    if k == "G7.07":
        L = ["Pielęgniarka epidemiologiczna","Lekarz","Medycyna pracy"]
        n = [("s","startEvent","Ekspozycja zawodowa / ognisko","Pielęgniarka epidemiologiczna",{"eventType":"message"}),
             ("a1","businessRuleTask","Oceń ekspozycję / sytuację","Pielęgniarka epidemiologiczna",{}),
             ("g1","exclusiveGateway","Wymaga profilaktyki / działań?","Lekarz",{}),
             ("a2","sendTask","Wdroż profilaktykę poekspozycyjną","Medycyna pracy",{}),
             ("a3","userTask","Udokumentuj i raportuj","Pielęgniarka epidemiologiczna",{}),
             ("e1","endEvent","Postępowanie antyepidemiczne zakończone","Pielęgniarka epidemiologiczna",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Karta ekspozycji","a3")]
    # G7.08 szkolenia zakazenia
    L = ["Dział Higieny i Epidemiologii","Personel"]
    n = [("s","startEvent","Plan szkoleń (zakażenia)","Dział Higieny i Epidemiologii",{"eventType":"timer"}),
         ("a1","userTask","Zaplanuj szkolenia","Dział Higieny i Epidemiologii",{}),
         ("a2","manualTask","Przeprowadź szkolenia","Personel",{}),
         ("a3","userTask","Udokumentuj uczestnictwo","Dział Higieny i Epidemiologii",{}),
         ("e1","endEvent","Szkolenia zrealizowane","Dział Higieny i Epidemiologii",{})]
    f = C("s","a1","a2","a3","e1")
    return L,n,f,[("d1","dataObjectReference","Lista obecności / zaświadczenia","a3")]

def g_G8(p):
    k = _k(p)
    if k == "G8.01":
        L = ["Personel medyczny","System EDM / P1"]
        n = [("s","startEvent","Zdarzenie medyczne do udokumentowania","Personel medyczny",{"eventType":"message"}),
             ("a1","userTask","Wytwórz wpis w dokumentacji","Personel medyczny",{}),
             ("g1","exclusiveGateway","Postać elektroniczna (EDM)?","Personel medyczny",{}),
             ("a2","serviceTask","Zapisz w EDM i podpisz elektronicznie","System EDM / P1",{}),
             ("a3","manualTask","Prowadź dokumentację papierową","Personel medyczny",{}),
             ("a4","serviceTask","Zindeksuj i udostępnij w systemie","System EDM / P1",{}),
             ("e1","endEvent","Dokumentacja zarejestrowana","System EDM / P1",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",1),("g1","a3","nie",0),("a2","a4",None,0),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataStore","EDM / dokumentacja medyczna","a2")]
    if k == "G8.02":
        L = ["Wnioskodawca","Sekcja Dokumentacji Medycznej"]
        n = [("s","startEvent","Wniosek o udostępnienie dokumentacji","Wnioskodawca",{"eventType":"message"}),
             ("a1","businessRuleTask","Zweryfikuj uprawnienia i podstawę","Sekcja Dokumentacji Medycznej",{}),
             ("g1","exclusiveGateway","Wniosek zasadny?","Sekcja Dokumentacji Medycznej",{}),
             ("a2","userTask","Przygotuj i wydaj kopię / wyciąg","Sekcja Dokumentacji Medycznej",{}),
             ("a3","serviceTask","Zaewidencjonuj udostępnienie","Sekcja Dokumentacji Medycznej",{}),
             ("e1","endEvent","Dokumentacja udostępniona","Sekcja Dokumentacji Medycznej",{}),
             ("e2","endEvent","Odmowa udostępnienia","Sekcja Dokumentacji Medycznej",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",1),("a2","a3",None,0),("a3","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Wniosek o udostępnienie","a1"),("d2","dataStore","Rejestr udostępnień","a3")]
    if k == "G8.03":
        L = ["Sekcja Dokumentacji Medycznej"]
        n = [("s","startEvent","Dokumentacja zakończona do archiwizacji","Sekcja Dokumentacji Medycznej",{"eventType":"message"}),
             ("a1","userTask","Przyjmij i uporządkuj dokumentację","Sekcja Dokumentacji Medycznej",{}),
             ("a2","userTask","Zarchiwizuj wg kategorii i okresu","Sekcja Dokumentacji Medycznej",{}),
             ("a3","manualTask","Zabezpiecz i ewidencjonuj","Sekcja Dokumentacji Medycznej",{}),
             ("e1","endEvent","Dokumentacja zarchiwizowana","Sekcja Dokumentacji Medycznej",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataStore","Archiwum dokumentacji","a2")]
    if k == "G8.04":
        L = ["Sekcja Dokumentacji Medycznej","Zarząd"]
        n = [("s","startEvent","Upływ okresu przechowywania","Sekcja Dokumentacji Medycznej",{"eventType":"timer"}),
             ("a1","userTask","Wytypuj dokumentację do brakowania","Sekcja Dokumentacji Medycznej",{}),
             ("g1","exclusiveGateway","Zgoda na brakowanie?","Zarząd",{}),
             ("a2","manualTask","Zniszcz protokolarnie","Sekcja Dokumentacji Medycznej",{}),
             ("a3","userTask","Sporządź protokół brakowania","Sekcja Dokumentacji Medycznej",{}),
             ("e1","endEvent","Dokumentacja wybrakowana","Sekcja Dokumentacji Medycznej",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",1),("a2","a3",None,0),("a3","e1",None,0),("g1","a1","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Protokół brakowania","a3")]
    if k == "G8.05":
        L = ["System EDM","Dział Informatyki","Platforma P1"]
        n = [("s","startEvent","Zdarzenie do wymiany z P1","System EDM",{"eventType":"message"}),
             ("a1","serviceTask","Zmapuj i wyślij zdarzenie medyczne do P1","Dział Informatyki",{}),
             ("g1","exclusiveGateway","Potwierdzenie P1?","Platforma P1",{}),
             ("a2","userTask","Obsłuż błąd i ponów wysyłkę","Dział Informatyki",{}),
             ("a3","serviceTask","Zaktualizuj status w EDM / IKP","System EDM",{}),
             ("e1","endEvent","Dane wymienione z P1","System EDM",{})]
        f = C("s","a1","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","a2","nie",0),("a2","a1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Zdarzenie medyczne (P1)","a1")]
    # G8.06 digitalizacja
    L = ["Sekcja Dokumentacji Medycznej","Dział Informatyki"]
    n = [("s","startEvent","Dokumentacja papierowa do digitalizacji","Sekcja Dokumentacji Medycznej",{"eventType":"message"}),
         ("a1","manualTask","Zeskanuj dokumentację","Sekcja Dokumentacji Medycznej",{}),
         ("a2","userTask","Podpisz i zindeksuj (cyfrowy równoważny)","Sekcja Dokumentacji Medycznej",{}),
         ("a3","serviceTask","Załaduj do EDM / P1","Dział Informatyki",{}),
         ("e1","endEvent","Dokumentacja zdigitalizowana","Dział Informatyki",{})]
    f = C("s","a1","a2","a3","e1")
    return L,n,f,[("d1","dataStore","EDM (dokument cyfrowy)","a3")]

def g_G9(p):
    k = _k(p)
    if k == "G9.01":
        L = ["Dział Rozliczeń Świadczeń","NFZ (system)"]
        n = [("s","startEvent","Cykl sprawozdawczy do NFZ","Dział Rozliczeń Świadczeń",{"eventType":"timer"}),
             ("a1","serviceTask","Zbierz i zwaliduj dane świadczeń","Dział Rozliczeń Świadczeń",{}),
             ("a2","sendTask","Wyślij komunikaty SWIAD / KOLEJKI","NFZ (system)",{}),
             ("g1","exclusiveGateway","Przyjęto bez błędów?","NFZ (system)",{}),
             ("a3","userTask","Skoryguj błędy","Dział Rozliczeń Świadczeń",{}),
             ("e1","endEvent","Sprawozdanie przyjęte","Dział Rozliczeń Świadczeń",{})]
        f = C("s","a1","a2","g1")+[("g1","e1","tak",1),("g1","a3","nie",0),("a3","a2",None,0)]
        return L,n,f,[("d1","dataObjectReference","Komunikaty SWIAD","a1")]
    if k == "G9.02":
        L = ["Dział Rozliczeń Świadczeń","NFZ","Dział Finansowo-Księgowy"]
        n = [("s","startEvent","Okres rozliczeniowy","Dział Rozliczeń Świadczeń",{"eventType":"timer"}),
             ("a1","businessRuleTask","Zgrupuj świadczenia (JGP / ryczałt / AOS)","Dział Rozliczeń Świadczeń",{}),
             ("a2","sendTask","Wyślij rachunek / zestawienie","NFZ",{}),
             ("g1","exclusiveGateway","Zaakceptowane przez NFZ?","NFZ",{}),
             ("a3","userTask","Wyjaśnij i skoryguj","Dział Rozliczeń Świadczeń",{}),
             ("a4","serviceTask","Zaksięguj rozliczenie","Dział Finansowo-Księgowy",{}),
             ("e1","endEvent","Świadczenia rozliczone","Dział Finansowo-Księgowy",{})]
        f = C("s","a1","a2","g1")+[("g1","a4","tak",1),("a4","e1",None,0),("g1","a3","nie",0),("a3","a2",None,0)]
        return L,n,f,[("d1","dataObjectReference","Zestawienie rozliczeniowe","a1")]
    if k == "G9.03":
        L = ["Dział Rozliczeń Świadczeń","GUS / MZ"]
        n = [("s","startEvent","Obowiązek sprawozdawczości statystycznej","Dział Rozliczeń Świadczeń",{"eventType":"timer"}),
             ("a1","serviceTask","Zbierz dane statystyczne","Dział Rozliczeń Świadczeń",{}),
             ("a2","userTask","Sporządź sprawozdania (MZ-29, MZ-11, GUS)","Dział Rozliczeń Świadczeń",{}),
             ("a3","sendTask","Prześlij do MZ / GUS","GUS / MZ",{}),
             ("e1","endEvent","Sprawozdania statystyczne złożone","Dział Rozliczeń Świadczeń",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Sprawozdania statystyczne","a2")]
    if k == "G9.04":
        L = ["NFZ","Dział Rozliczeń Świadczeń","Zarząd"]
        n = [("s","startEvent","Zawiadomienie o kontroli NFZ","NFZ",{"eventType":"message"}),
             ("a1","userTask","Przygotuj dokumentację i dane","Dział Rozliczeń Świadczeń",{}),
             ("a2","receiveTask","Uczestnicz w kontroli","Dział Rozliczeń Świadczeń",{}),
             ("g1","exclusiveGateway","Zalecenia / zastrzeżenia?","Zarząd",{}),
             ("a3","userTask","Złóż zastrzeżenia / wdroż zalecenia","Dział Rozliczeń Świadczeń",{}),
             ("e1","endEvent","Kontrola NFZ obsłużona","Dział Rozliczeń Świadczeń",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","e1","nie",1),("a3","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Protokół kontroli","a2")]
    # G9.05 faktury komercyjne
    L = ["Dział Rozliczeń Świadczeń","Dział Finansowo-Księgowy"]
    n = [("s","startEvent","Świadczenie komercyjne","Dział Rozliczeń Świadczeń",{"eventType":"message"}),
         ("a1","userTask","Ustal należność i dane do faktury","Dział Rozliczeń Świadczeń",{}),
         ("a2","serviceTask","Wystaw fakturę","Dział Finansowo-Księgowy",{}),
         ("a3","sendTask","Przekaż fakturę i monitoruj płatność","Dział Finansowo-Księgowy",{}),
         ("e1","endEvent","Świadczenie zafakturowane","Dział Finansowo-Księgowy",{})]
    f = C("s","a1","a2","a3","e1")
    return L,n,f,[("d1","dataObjectReference","Faktura","a2")]

def g_G10(p):
    k = _k(p)
    if k == "G10.01":
        L = ["Zlecający","Dyspozytor","Zespół Transportu Medycznego"]
        n = [("s","startEvent","Zlecenie transportu sanitarnego","Zlecający",{"eventType":"message"}),
             ("a1","businessRuleTask","Zakwalifikuj tryb (planowy / pilny)","Dyspozytor",{}),
             ("a2","userTask","Zaplanuj i przydziel zespół","Dyspozytor",{}),
             ("a3","manualTask","Zrealizuj przewóz","Zespół Transportu Medycznego",{}),
             ("a4","userTask","Udokumentuj transport","Zespół Transportu Medycznego",{}),
             ("e1","endEvent","Transport zrealizowany","Zespół Transportu Medycznego",{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataObjectReference","Karta zlecenia transportu","a1")]
    if k == "G10.02":
        L = ["Punkt pobrań","Zespół Transportu Medycznego","Laboratorium"]
        n = [("s","startEvent","Materiał biologiczny do przewozu","Punkt pobrań",{"eventType":"message"}),
             ("a1","userTask","Zabezpiecz i opisz próbki","Punkt pobrań",{}),
             ("a2","manualTask","Przewieź w warunkach kontrolowanych","Zespół Transportu Medycznego",{}),
             ("a3","sendTask","Przekaż do laboratorium","Laboratorium",{}),
             ("e1","endEvent","Materiał dostarczony","Laboratorium",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Protokół przekazania próbek","a1")]
    # G10.03 utrzymanie pojazdow
    L = ["Zespół Transportu Medycznego","Dział Techniczny"]
    n = [("s","startEvent","Monitoring stanu pojazdów","Zespół Transportu Medycznego",{"eventType":"timer"}),
         ("a1","userTask","Monitoruj przeglądy i stan techniczny","Zespół Transportu Medycznego",{}),
         ("g1","exclusiveGateway","Wymaga serwisu?","Zespół Transportu Medycznego",{}),
         ("a2","manualTask","Zleć i wykonaj serwis","Dział Techniczny",{}),
         ("a3","userTask","Udokumentuj sprawność","Zespół Transportu Medycznego",{}),
         ("e1","endEvent","Pojazdy sprawne","Zespół Transportu Medycznego",{})]
    f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
    return L,n,f,[("d1","dataObjectReference","Karta pojazdu","a3")]

# ============================ WARSTWA WSPIERAJACA (W) ============================
def g_W1(p):
    k = _k(p)
    if k == "W1.01":
        L = ["Główny Księgowy","Dział Finansowo-Księgowy","Zarząd"]
        n = [("s","startEvent","Cykl polityki rachunkowości","Główny Księgowy",{"eventType":"timer"}),
             ("a1","userTask","Opracuj / aktualizuj politykę rachunkowości","Główny Księgowy",{}),
             ("a2","userTask","Zatwierdź politykę","Zarząd",{}),
             ("a3","manualTask","Prowadź księgi rachunkowe","Dział Finansowo-Księgowy",{"loop":True}),
             ("a4","userTask","Kontroluj poprawność zapisów","Główny Księgowy",{}),
             ("e1","endEvent","Księgi prowadzone zgodnie z polityką","Główny Księgowy",{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataObjectReference","Polityka rachunkowości","a1"),("d2","dataStore","Księgi rachunkowe","a3")]
    if k == "W1.02":
        L = ["Komórki / Dyrektorzy","Główny Księgowy","Zarząd"]
        n = [("s","startEvent","Cykl budżetowy","Główny Księgowy",{"eventType":"timer"}),
             ("a1","userTask","Zbierz plany komórek","Komórki / Dyrektorzy",{}),
             ("a2","userTask","Skonsoliduj plan rzeczowo-finansowy","Główny Księgowy",{}),
             ("g1","exclusiveGateway","Zatwierdzić plan?","Zarząd",{}),
             ("a3","sendTask","Zakomunikuj i monitoruj wykonanie","Główny Księgowy",{}),
             ("e1","endEvent","Budżet obowiązuje","Główny Księgowy",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","a2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Plan rzeczowo-finansowy","a2")]
    if k == "W1.03":
        L = ["Dział Finansowo-Księgowy","Dział Rozliczeń Świadczeń"]
        n = [("s","startEvent","Dokument przychodowy (NFZ/komercja)","Dział Finansowo-Księgowy",{"eventType":"message"}),
             ("a1","userTask","Zweryfikuj i zadekretuj dokument","Dział Finansowo-Księgowy",{}),
             ("a2","serviceTask","Zaksięguj przychód","Dział Finansowo-Księgowy",{}),
             ("a3","userTask","Uzgodnij z rozliczeniami","Dział Rozliczeń Świadczeń",{}),
             ("e1","endEvent","Przychód zaksięgowany","Dział Finansowo-Księgowy",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Dokument przychodowy","a1")]
    if k == "W1.04":
        L = ["Dział Finansowo-Księgowy","Radca prawny"]
        n = [("s","startEvent","Monitoring należności","Dział Finansowo-Księgowy",{"eventType":"timer"}),
             ("a1","userTask","Monitoruj salda i terminy","Dział Finansowo-Księgowy",{}),
             ("g1","exclusiveGateway","Należność przeterminowana?","Dział Finansowo-Księgowy",{}),
             ("a2","sendTask","Wyślij wezwanie do zapłaty","Dział Finansowo-Księgowy",{}),
             ("g2","exclusiveGateway","Zapłacono?","Dział Finansowo-Księgowy",{}),
             ("a3","sendTask","Skieruj do windykacji sądowej","Radca prawny",{}),
             ("e1","endEvent","Należność uregulowana / w windykacji","Dział Finansowo-Księgowy",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","e1","nie",1),("a2","g2",None,0),
             ("g2","e1","tak",1),("g2","a3","nie",0),("a3","e1",None,0)]
        return L,n,f,[("d1","dataStore","Rejestr należności","a1")]
    if k == "W1.05":
        L = ["Komórka zamawiająca","Dział Finansowo-Księgowy"]
        n = [("s","startEvent","Wpływ faktury zakupowej","Dział Finansowo-Księgowy",{"eventType":"message"}),
             ("a1","userTask","Zarejestruj fakturę","Dział Finansowo-Księgowy",{}),
             ("a2","businessRuleTask","Dopasuj fakturę-zamówienie-dostawę (3-way)","Dział Finansowo-Księgowy",{}),
             ("g1","exclusiveGateway","Zgodność potwierdzona?","Dział Finansowo-Księgowy",{}),
             ("a3","serviceTask","Zrealizuj płatność","Dział Finansowo-Księgowy",{}),
             ("a4","sendTask","Wyjaśnij rozbieżność z komórką","Komórka zamawiająca",{}),
             ("e1","endEvent","Zobowiązanie uregulowane","Dział Finansowo-Księgowy",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","a4","nie",0),("a4","a2",None,0)]
        return L,n,f,[("d1","dataObjectReference","Faktura zakupowa","a1")]
    if k == "W1.06":
        L = ["Dział Finansowo-Księgowy","Dział Rozliczeń Świadczeń"]
        n = [("s","startEvent","Cykl rachunku kosztów","Dział Finansowo-Księgowy",{"eventType":"timer"}),
             ("a1","userTask","Zbierz koszty wg ośrodków","Dział Finansowo-Księgowy",{}),
             ("a2","businessRuleTask","Skalkuluj koszty świadczeń","Dział Finansowo-Księgowy",{}),
             ("a3","sendTask","Sprawozdaj do AOTMiT","Dział Rozliczeń Świadczeń",{}),
             ("e1","endEvent","Rachunek kosztów sporządzony","Dział Finansowo-Księgowy",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Kalkulacja kosztów","a2")]
    if k == "W1.07":
        L = ["Dział Finansowo-Księgowy","Główny Księgowy","US / GUS"]
        n = [("s","startEvent","Obowiązek sprawozdawczy (US/JPK/GUS)","Dział Finansowo-Księgowy",{"eventType":"timer"}),
             ("a1","userTask","Przygotuj dane i deklaracje","Dział Finansowo-Księgowy",{}),
             ("a2","userTask","Zweryfikuj i zatwierdź","Główny Księgowy",{}),
             ("a3","serviceTask","Wyślij (JPK / US / GUS)","US / GUS",{}),
             ("e1","endEvent","Sprawozdania złożone","Główny Księgowy",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Deklaracje / JPK","a1")]
    if k == "W1.08":
        L = ["Dział Finansowo-Księgowy","Komisja inwentaryzacyjna"]
        n = [("s","startEvent","Plan inwentaryzacji","Dział Finansowo-Księgowy",{"eventType":"timer"}),
             ("a1","userTask","Zarządź inwentaryzację","Dział Finansowo-Księgowy",{}),
             ("a2","manualTask","Przeprowadź spis z natury","Komisja inwentaryzacyjna",{}),
             ("a3","businessRuleTask","Rozlicz różnice inwentaryzacyjne","Dział Finansowo-Księgowy",{}),
             ("g1","exclusiveGateway","Różnice istotne?","Dział Finansowo-Księgowy",{}),
             ("a4","userTask","Wyjaśnij i zaksięguj różnice","Dział Finansowo-Księgowy",{}),
             ("e1","endEvent","Inwentaryzacja rozliczona","Dział Finansowo-Księgowy",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a4","tak",0),("g1","e1","nie",1),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Arkusze spisowe","a2")]
    if k == "W1.09":
        L = ["Dział Finansowo-Księgowy"]
        n = [("s","startEvent","Zmiana w środkach trwałych","Dział Finansowo-Księgowy",{"eventType":"message"}),
             ("a1","userTask","Zaewidencjonuj środek trwały / WNiP","Dział Finansowo-Księgowy",{}),
             ("a2","businessRuleTask","Ustal stawkę i metodę amortyzacji","Dział Finansowo-Księgowy",{}),
             ("a3","serviceTask","Naliczaj amortyzację","Dział Finansowo-Księgowy",{"loop":True}),
             ("e1","endEvent","Środek trwały w ewidencji","Dział Finansowo-Księgowy",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataStore","Ewidencja środków trwałych","a1")]
    # W1.10 kasa
    L = ["Dział Finansowo-Księgowy"]
    n = [("s","startEvent","Operacja kasowa","Dział Finansowo-Księgowy",{"eventType":"message"}),
         ("a1","userTask","Przyjmij / wypłać gotówkę za pokwitowaniem","Dział Finansowo-Księgowy",{}),
         ("a2","serviceTask","Sporządź i zaksięguj raport kasowy","Dział Finansowo-Księgowy",{}),
         ("e1","endEvent","Operacja kasowa rozliczona","Dział Finansowo-Księgowy",{})]
    f = C("s","a1","a2","e1")
    return L,n,f,[("d1","dataObjectReference","Raport kasowy","a2")]

def g_W2(p):
    k = _k(p)
    DPP = "Dział Personalno-Płacowy"
    if k == "W2.01":
        L = ["Kierownicy komórek",DPP,"Zarząd"]
        n = [("s","startEvent","Cykl planowania zatrudnienia",DPP,{"eventType":"timer"}),
             ("a1","userTask","Zgłoś zapotrzebowanie na etaty","Kierownicy komórek",{}),
             ("a2","userTask","Skonsoliduj plan zatrudnienia",DPP,{}),
             ("g1","exclusiveGateway","Zatwierdzić plan?","Zarząd",{}),
             ("a3","userTask","Uruchom rekrutacje wg planu",DPP,{}),
             ("e1","endEvent","Plan zatrudnienia przyjęty",DPP,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","a2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Plan etatów","a2")]
    if k == "W2.02":
        L = ["Komórka wnioskująca",DPP]
        n = [("s","startEvent","Wakat / potrzeba rekrutacji",DPP,{"eventType":"message"}),
             ("a1","sendTask","Opublikuj ogłoszenie",DPP,{}),
             ("a2","userTask","Zbierz i oceń aplikacje",DPP,{}),
             ("a3","userTask","Przeprowadź rozmowy kwalifikacyjne","Komórka wnioskująca",{}),
             ("g1","exclusiveGateway","Wybrano kandydata?","Komórka wnioskująca",{}),
             ("a4","sendTask","Złóż ofertę zatrudnienia",DPP,{}),
             ("e1","endEvent","Kandydat wyłoniony",DPP,{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a4","tak",1),("a4","e1",None,0),("g1","a1","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Aplikacje kandydatów","a2")]
    if k == "W2.03":
        L = ["Kandydat / Pracownik",DPP]
        n = [("s","startEvent","Decyzja o zatrudnieniu",DPP,{"eventType":"message"}),
             ("a1","userTask","Zbierz dokumenty i dane","Kandydat / Pracownik",{}),
             ("a2","businessRuleTask","Ustal formę umowy (UoP / cywilnoprawna)",DPP,{}),
             ("a3","userTask","Sporządź i podpisz umowę",DPP,{}),
             ("a4","serviceTask","Zgłoś do ZUS i załóż akta",DPP,{}),
             ("e1","endEvent","Pracownik zatrudniony",DPP,{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataObjectReference","Umowa","a3")]
    if k == "W2.04":
        L = [DPP,"Kierownik komórki","Dział Informatyki"]
        n = [("s","startEvent","Nowy pracownik",DPP,{"eventType":"message"}),
             ("a1","userTask","Przygotuj dokumenty i szkolenie wstępne",DPP,{}),
             ("a2","sendTask","Nadaj dostępy i sprzęt","Dział Informatyki",{}),
             ("a3","manualTask","Wdroż na stanowisku","Kierownik komórki",{}),
             ("a4","userTask","Potwierdź zakończenie adaptacji",DPP,{}),
             ("e1","endEvent","Pracownik wdrożony",DPP,{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataObjectReference","Lista kontrolna onboarding","a1")]
    if k == "W2.05":
        L = [DPP,"Dział Finansowo-Księgowy"]
        n = [("s","startEvent","Cykl płacowy",DPP,{"eventType":"timer"}),
             ("a1","userTask","Zbierz dane (czas pracy, nieobecności)",DPP,{}),
             ("a2","businessRuleTask","Nalicz wynagrodzenia (ZUS / PIT)",DPP,{}),
             ("g1","exclusiveGateway","Naliczenia poprawne?",DPP,{}),
             ("a3","userTask","Skoryguj naliczenia",DPP,{}),
             ("a4","serviceTask","Zrealizuj wypłaty i deklaracje","Dział Finansowo-Księgowy",{}),
             ("e1","endEvent","Wynagrodzenia wypłacone",DPP,{})]
        f = C("s","a1","a2","g1")+[("g1","a4","tak",1),("a4","e1",None,0),("g1","a3","nie",0),("a3","a2",None,0)]
        return L,n,f,[("d1","dataObjectReference","Lista płac","a2")]
    if k == "W2.06":
        L = ["Kierownicy komórek",DPP]
        n = [("s","startEvent","Cykl ewidencji czasu pracy",DPP,{"eventType":"timer"}),
             ("a1","userTask","Rejestruj czas pracy i grafiki","Kierownicy komórek",{}),
             ("a2","userTask","Zweryfikuj i zatwierdź ewidencję",DPP,{}),
             ("g1","exclusiveGateway","Nieprawidłowości?",DPP,{}),
             ("a3","userTask","Wyjaśnij i skoryguj","Kierownicy komórek",{}),
             ("e1","endEvent","Ewidencja zatwierdzona",DPP,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","e1","nie",1),("a3","e1",None,0)]
        return L,n,f,[("d1","dataStore","Ewidencja czasu pracy","a1")]
    if k == "W2.07":
        L = ["Pracownik","Przełożony",DPP]
        n = [("s","startEvent","Wniosek urlopowy / nieobecność","Pracownik",{"eventType":"message"}),
             ("a1","userTask","Złóż wniosek","Pracownik",{}),
             ("g1","exclusiveGateway","Zaakceptowano?","Przełożony",{}),
             ("a2","serviceTask","Zarejestruj nieobecność",DPP,{}),
             ("e1","endEvent","Nieobecność zarejestrowana",DPP,{}),
             ("e2","endEvent","Wniosek odrzucony","Przełożony",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",1),("a2","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Wniosek urlopowy","a1")]
    if k == "W2.08":
        L = ["Pracownik","Komisja Socjalna",DPP]
        n = [("s","startEvent","Wniosek o świadczenie socjalne (ZFŚS)","Pracownik",{"eventType":"message"}),
             ("a1","userTask","Złóż wniosek","Pracownik",{}),
             ("a2","businessRuleTask","Oceń wg kryterium dochodowego","Komisja Socjalna",{}),
             ("g1","exclusiveGateway","Przyznać świadczenie?","Komisja Socjalna",{}),
             ("a3","serviceTask","Wypłać świadczenie",DPP,{}),
             ("e1","endEvent","Świadczenie przyznane",DPP,{}),
             ("e2","endEvent","Wniosek odrzucony","Komisja Socjalna",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Wniosek ZFŚS","a1")]
    if k == "W2.09":
        L = [DPP,"Pracownik"]
        n = [("s","startEvent","Plan szkoleń obowiązkowych",DPP,{"eventType":"timer"}),
             ("a1","userTask","Zidentyfikuj wymagane szkolenia",DPP,{}),
             ("a2","userTask","Zaplanuj i zorganizuj szkolenia",DPP,{}),
             ("a3","manualTask","Realizuj szkolenia","Pracownik",{}),
             ("g1","exclusiveGateway","Wszyscy przeszkoleni?",DPP,{}),
             ("a4","userTask","Zaktualizuj rejestr szkoleń",DPP,{}),
             ("e1","endEvent","Szkolenia zrealizowane",DPP,{})]
        f = C("s","a1","a2","a3","g1")+[("g1","a4","tak",1),("a4","e1",None,0),("g1","a2","nie",0)]
        return L,n,f,[("d1","dataStore","Rejestr szkoleń","a4")]
    if k == "W2.10":
        L = ["Pracownik",DPP]
        n = [("s","startEvent","Zdarzenie PPK (zapis / rezygnacja)","Pracownik",{"eventType":"message"}),
             ("a1","userTask","Obsłuż deklarację PPK",DPP,{}),
             ("a2","serviceTask","Nalicz i przekaż składki",DPP,{}),
             ("e1","endEvent","PPK obsłużone",DPP,{})]
        f = C("s","a1","a2","e1")
        return L,n,f,[("d1","dataObjectReference","Deklaracja PPK","a1")]
    if k == "W2.11":
        L = [DPP]
        n = [("s","startEvent","Zmiana / dokument kadrowy",DPP,{"eventType":"message"}),
             ("a1","userTask","Zaktualizuj akta osobowe",DPP,{}),
             ("a2","manualTask","Archiwizuj zgodnie z okresem",DPP,{}),
             ("e1","endEvent","Akta zaktualizowane",DPP,{})]
        f = C("s","a1","a2","e1")
        return L,n,f,[("d1","dataStore","Akta osobowe","a1")]
    if k == "W2.12":
        L = ["Pracownik",DPP,"Jednostka medycyny pracy"]
        n = [("s","startEvent","Skierowanie na badania profilaktyczne",DPP,{"eventType":"timer"}),
             ("a1","userTask","Wystaw skierowanie",DPP,{}),
             ("a2","manualTask","Wykonaj badania profilaktyczne","Jednostka medycyny pracy",{}),
             ("g1","exclusiveGateway","Zdolny do pracy?","Jednostka medycyny pracy",{}),
             ("a3","userTask","Dopuść do pracy i zarejestruj",DPP,{}),
             ("a4","userTask","Wdroż działania (przeniesienie/ograniczenia)",DPP,{}),
             ("e1","endEvent","Badania rozliczone",DPP,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","a4","nie",0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Orzeczenie lekarskie","a2")]
    if k == "W2.13":
        L = ["Przełożony / DPP","Radca prawny",DPP]
        n = [("s","startEvent","Zdarzenie dyscyplinarne / wypowiedzenie","Przełożony / DPP",{"eventType":"message"}),
             ("a1","userTask","Ustal stan faktyczny","Przełożony / DPP",{}),
             ("a2","userTask","Oceń podstawy prawne","Radca prawny",{}),
             ("g1","exclusiveGateway","Działanie zasadne?","Radca prawny",{}),
             ("a3","userTask","Sporządź i wręcz dokument",DPP,{}),
             ("a4","serviceTask","Rozlicz i wyrejestruj",DPP,{}),
             ("e1","endEvent","Sprawa zakończona",DPP,{}),
             ("e2","endEvent","Odstąpiono od działania","Radca prawny",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","a4",None,0),("a4","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Dokumentacja sprawy","a1")]
    # W2.14 dyzury lekarskie
    L = ["Kierownicy komórek medycznych",DPP]
    n = [("s","startEvent","Cykl planowania dyżurów","Kierownicy komórek medycznych",{"eventType":"timer"}),
         ("a1","businessRuleTask","Ustal obsadę dyżurów","Kierownicy komórek medycznych",{}),
         ("a2","userTask","Sporządź harmonogram dyżurów","Kierownicy komórek medycznych",{}),
         ("g1","exclusiveGateway","Obsada pełna?","Kierownicy komórek medycznych",{}),
         ("a3","userTask","Uzupełnij / uzgodnij dyżury","Kierownicy komórek medycznych",{}),
         ("a4","serviceTask","Zatwierdź i rozlicz dyżury",DPP,{}),
         ("e1","endEvent","Grafik dyżurów obowiązuje",DPP,{})]
    f = C("s","a1","a2","g1")+[("g1","a4","tak",1),("g1","a3","nie",0),("a3","a4",None,0),("a4","e1",None,0)]
    return L,n,f,[("d1","dataObjectReference","Harmonogram dyżurów","a2")]

def g_W4(p):
    k = _k(p); DI = "Dział Informatyki"
    if k == "W4.01":
        L = ["Użytkownik",DI]
        n = [("s","startEvent","Zgłoszenie IT","Użytkownik",{"eventType":"message"}),
             ("a1","userTask","Zarejestruj i sklasyfikuj zgłoszenie",DI,{}),
             ("g1","exclusiveGateway","Rozwiązanie 1. linii?",DI,{}),
             ("a2","userTask","Rozwiąż na 1. linii wsparcia",DI,{}),
             ("a3","userTask","Eskaluj do 2. linii / specjalisty",DI,{}),
             ("a4","userTask","Zweryfikuj rozwiązanie i zamknij",DI,{}),
             ("e1","endEvent","Zgłoszenie obsłużone",DI,{})]
        f = C("s","a1","g1")+[("g1","a2","tak",1),("g1","a3","nie",0),("a2","a4",None,0),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataStore","Rejestr zgłoszeń (ITSM)","a1")]
    if k == "W4.02":
        L = [DI,"Dostawca / serwis"]
        n = [("s","startEvent","Potrzeba/zmiana w systemach HIS/RIS/PACS/LIS",DI,{"eventType":"message"}),
             ("a1","userTask","Przyjmij i opisz zmianę",DI,{}),
             ("a2","businessRuleTask","Oceń wpływ na systemy kliniczne",DI,{}),
             ("g1","exclusiveGateway","Wymaga dostawcy?",DI,{}),
             ("a3","sendTask","Zleć zmianę dostawcy","Dostawca / serwis",{}),
             ("a4","userTask","Wdroż i przetestuj zmianę",DI,{}),
             ("e1","endEvent","Zmiana wdrożona",DI,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataStore","HIS/RIS/PACS/LIS","a4")]
    if k == "W4.03":
        L = [DI,"Platforma P1"]
        n = [("s","startEvent","Wymóg integracji z P1",DI,{"eventType":"message"}),
             ("a1","userTask","Skonfiguruj interfejs (e-recepta/e-skierowanie/e-ZLA)",DI,{}),
             ("a2","serviceTask","Przetestuj wymianę z P1","Platforma P1",{}),
             ("g1","exclusiveGateway","Testy zaliczone?",DI,{}),
             ("a3","serviceTask","Uruchom produkcyjnie i monitoruj",DI,{}),
             ("e1","endEvent","Integracja P1 działa",DI,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","a1","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Konfiguracja integracji","a1")]
    if k == "W4.04":
        L = ["Wnioskujący / Przełożony",DI,"Administrator Bezpieczeństwa"]
        n = [("s","startEvent","Wniosek o dostęp / uprawnienia","Wnioskujący / Przełożony",{"eventType":"message"}),
             ("a1","userTask","Złóż wniosek o dostęp","Wnioskujący / Przełożony",{}),
             ("a2","businessRuleTask","Zweryfikuj zasadność i rozdział obowiązków","Administrator Bezpieczeństwa",{}),
             ("g1","exclusiveGateway","Zatwierdzić?","Administrator Bezpieczeństwa",{}),
             ("a3","serviceTask","Nadaj / zmień uprawnienia",DI,{}),
             ("a4","manualTask","Przeglądaj uprawnienia okresowo","Administrator Bezpieczeństwa",{"loop":True}),
             ("e1","endEvent","Dostęp nadany i nadzorowany",DI,{}),
             ("e2","endEvent","Wniosek odrzucony","Administrator Bezpieczeństwa",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","a4",None,0),("a4","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataStore","Rejestr uprawnień (IAM)","a3")]
    if k == "W4.05":
        L = [DI]
        n = [("s","startEvent","Harmonogram kopii zapasowych",DI,{"eventType":"timer"}),
             ("a1","serviceTask","Wykonaj kopie zapasowe",DI,{}),
             ("a2","businessRuleTask","Zweryfikuj integralność kopii",DI,{}),
             ("g1","exclusiveGateway","Kopia poprawna?",DI,{}),
             ("a3","manualTask","Powtórz / napraw kopię",DI,{}),
             ("a4","manualTask","Wykonaj test odtwarzania",DI,{"loop":True}),
             ("e1","endEvent","Kopie i odtwarzanie sprawdzone",DI,{})]
        f = C("s","a1","a2","g1")+[("g1","a4","tak",1),("a4","e1",None,0),("g1","a3","nie",0),("a3","a1",None,0)]
        return L,n,f,[("d1","dataStore","Repozytorium kopii zapasowych","a1")]
    if k == "W4.06":
        L = [DI,"Administrator Bezpieczeństwa"]
        n = [("s","startEvent","Bieżące bezpieczeństwo operacyjne",DI,{"eventType":"timer"}),
             ("a1","manualTask","Utrzymuj zabezpieczenia (patch, hardening)",DI,{}),
             ("a2","manualTask","Analizuj logi i alerty","Administrator Bezpieczeństwa",{}),
             ("g1","exclusiveGateway","Wykryto zagrożenie?","Administrator Bezpieczeństwa",{}),
             ("a3","sendTask","Eskaluj do reagowania na incydent","Administrator Bezpieczeństwa",{}),
             ("e1","endEvent","Środowisko zabezpieczone",DI,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","e1","nie",1),("a3","e1",None,0)]
        return L,n,f,[("d1","dataStore","Logi bezpieczeństwa","a2")]
    if k == "W4.07":
        L = [DI,"Administrator Bezpieczeństwa","Pełnomocnik ds. SZBI"]
        n = [("s","startEvent","Alert / zgłoszenie incydentu cyber","Administrator Bezpieczeństwa",{"eventType":"message"}),
             ("a1","userTask","Zarejestruj i sklasyfikuj incydent","Administrator Bezpieczeństwa",{}),
             ("a2","businessRuleTask","Oceń wpływ i priorytet","Administrator Bezpieczeństwa",{}),
             ("a3","serviceTask","Ogranicz skutki (izolacja)",DI,{}),
             ("a4","manualTask","Usuń przyczynę i przywróć działanie",DI,{}),
             ("g1","exclusiveGateway","Zgłosić do CSIRT/organu (KSC)?","Pełnomocnik ds. SZBI",{}),
             ("a5","sendTask","Zgłoś incydent (KSC/CSIRT)","Pełnomocnik ds. SZBI",{}),
             ("a6","userTask","Przeprowadź przegląd poincydentalny","Pełnomocnik ds. SZBI",{}),
             ("e1","endEvent","Incydent cyber zamknięty","Administrator Bezpieczeństwa",{})]
        f = C("s","a1","a2","a3","a4","g1")+[("g1","a5","tak",0),("g1","a6","nie",1),("a5","a6",None,0),("a6","e1",None,0)]
        return L,n,f,[("d1","dataStore","Rejestr incydentów cyber","a1")]
    if k == "W4.08":
        L = [DI]
        n = [("s","startEvent","Zgłoszenie / zmiana infrastruktury",DI,{"eventType":"message"}),
             ("a1","userTask","Zdiagnozuj i zaplanuj zmianę",DI,{}),
             ("g1","exclusiveGateway","Wymaga okna serwisowego?",DI,{}),
             ("a2","sendTask","Zaplanuj okno i powiadom",DI,{}),
             ("a3","manualTask","Wykonaj zmianę / naprawę",DI,{}),
             ("a4","userTask","Zweryfikuj działanie",DI,{}),
             ("e1","endEvent","Infrastruktura sprawna",DI,{})]
        f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataStore","CMDB / ewidencja infrastruktury","a4")]
    if k == "W4.09":
        L = ["Użytkownik",DI]
        n = [("s","startEvent","Zgłoszenie dot. łączności","Użytkownik",{"eventType":"message"}),
             ("a1","userTask","Zdiagnozuj problem",DI,{}),
             ("a2","manualTask","Usuń usterkę / skonfiguruj",DI,{}),
             ("a3","userTask","Potwierdź działanie z użytkownikiem","Użytkownik",{}),
             ("e1","endEvent","Łączność przywrócona",DI,{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Zgłoszenie łączności","a1")]
    if k == "W4.10":
        L = [DI,"Pacjent / Użytkownik"]
        n = [("s","startEvent","Potrzeba usługi e-zdrowia",DI,{"eventType":"message"}),
             ("a1","userTask","Skonfiguruj usługę (teleporada / e-rejestracja)",DI,{}),
             ("a2","serviceTask","Uruchom i zintegruj kanał",DI,{}),
             ("a3","manualTask","Wspieraj użytkowników",DI,{"loop":True}),
             ("e1","endEvent","Usługa e-zdrowia działa",DI,{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Konfiguracja usługi","a1")]
    if k == "W4.11":
        L = ["Wnioskujący",DI,"Komitet zmian (CAB)"]
        n = [("s","startEvent","Wniosek o zmianę (RFC)","Wnioskujący",{"eventType":"message"}),
             ("a1","userTask","Zarejestruj zmianę",DI,{}),
             ("a2","businessRuleTask","Oceń ryzyko i wpływ",DI,{}),
             ("g1","exclusiveGateway","Zatwierdzić (CAB)?","Komitet zmian (CAB)",{}),
             ("a3","manualTask","Wdroż zmianę wg planu",DI,{}),
             ("a4","userTask","Zweryfikuj i zaktualizuj CMDB",DI,{}),
             ("e1","endEvent","Zmiana wdrożona",DI,{}),
             ("e2","endEvent","Zmiana odrzucona","Komitet zmian (CAB)",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","a4",None,0),("a4","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Wniosek RFC","a1")]
    if k == "W4.12":
        L = ["Komórka merytoryczna",DI]
        n = [("s","startEvent","Potrzeba publikacji / aktualizacji WWW/BIP","Komórka merytoryczna",{"eventType":"message"}),
             ("a1","userTask","Przygotuj treść","Komórka merytoryczna",{}),
             ("a2","userTask","Zweryfikuj zgodność (WCAG / BIP)",DI,{}),
             ("a3","serviceTask","Opublikuj treść",DI,{}),
             ("e1","endEvent","Treść opublikowana",DI,{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Treść do publikacji","a1")]
    if k == "W4.13":
        L = ["SOC (zewn.)","Administrator Bezpieczeństwa"]
        n = [("s","startEvent","Monitorowanie SOC 24/7","SOC (zewn.)",{"eventType":"timer"}),
             ("a1","manualTask","Monitoruj zdarzenia i alerty","SOC (zewn.)",{}),
             ("g1","exclusiveGateway","Alert istotny?","SOC (zewn.)",{}),
             ("a2","sendTask","Triage i eskalacja do reagowania","SOC (zewn.)",{}),
             ("a3","userTask","Rejestruj i raportuj","Administrator Bezpieczeństwa",{}),
             ("e1","endEvent","Monitoring zrealizowany","Administrator Bezpieczeństwa",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
        return L,n,f,[("d1","dataStore","Zdarzenia SOC/SIEM","a1")]
    if k == "W4.14":
        L = [DI,"Administrator Bezpieczeństwa"]
        n = [("s","startEvent","Cykl zarządzania podatnościami",DI,{"eventType":"timer"}),
             ("a1","serviceTask","Skanuj podatności / wykonaj testy",DI,{}),
             ("a2","businessRuleTask","Oceń i priorytetyzuj podatności","Administrator Bezpieczeństwa",{}),
             ("g1","exclusiveGateway","Podatności krytyczne?","Administrator Bezpieczeństwa",{}),
             ("a3","manualTask","Remediuj podatności",DI,{}),
             ("a4","userTask","Raportuj wyniki i testy","Administrator Bezpieczeństwa",{}),
             ("e1","endEvent","Podatności obsłużone",DI,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataStore","Rejestr podatności","a2")]
    # W4.15 monitoring srodowiska IT/HIS
    L = [DI]
    n = [("s","startEvent","Monitoring środowiska IT i HIS",DI,{"eventType":"timer"}),
         ("a1","manualTask","Monitoruj dostępność i wydajność",DI,{}),
         ("g1","exclusiveGateway","Przekroczenie progu?",DI,{}),
         ("a2","sendTask","Generuj alert i reaguj",DI,{}),
         ("a3","userTask","Rejestruj zdarzenia",DI,{}),
         ("e1","endEvent","Środowisko monitorowane",DI,{})]
    f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
    return L,n,f,[("d1","dataStore","Metryki dostępności","a1")]

def g_W5(p):
    k = _k(p); DT = "Dział Techniczny"
    if k == "W5.01":
        L = [DT]
        n = [("s","startEvent","Plan eksploatacji obiektów",DT,{"eventType":"timer"}),
             ("a1","userTask","Planuj eksploatację i przeglądy",DT,{}),
             ("a2","manualTask","Realizuj utrzymanie obiektów",DT,{"loop":True}),
             ("a3","userTask","Dokumentuj stan obiektów",DT,{}),
             ("e1","endEvent","Obiekty utrzymane",DT,{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataStore","Książka obiektu","a3")]
    if k == "W5.02":
        L = [DT,"Uprawniony specjalista"]
        n = [("s","startEvent","Harmonogram przeglądów budynków",DT,{"eventType":"timer"}),
             ("a1","userTask","Zaplanuj przeglądy okresowe",DT,{}),
             ("a2","manualTask","Przeprowadź przegląd","Uprawniony specjalista",{}),
             ("g1","exclusiveGateway","Stwierdzono usterki?",DT,{}),
             ("a3","manualTask","Zleć i wykonaj naprawy",DT,{}),
             ("a4","userTask","Wpisz do książki obiektu",DT,{}),
             ("e1","endEvent","Przegląd udokumentowany",DT,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Protokół przeglądu","a2")]
    if k == "W5.03":
        L = [DT,"Serwis (zewn.)"]
        n = [("s","startEvent","Monitoring aparatury medycznej",DT,{"eventType":"timer"}),
             ("a1","userTask","Monitoruj paszporty i terminy przeglądów",DT,{}),
             ("g1","exclusiveGateway","Termin przeglądu / serwisu?",DT,{}),
             ("a2","sendTask","Zleć przegląd / serwis","Serwis (zewn.)",{}),
             ("a3","manualTask","Odbierz i dopuść do użytku",DT,{}),
             ("e1","endEvent","Aparatura sprawna",DT,{})]
        f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","e1","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
        return L,n,f,[("d1","dataStore","Paszporty techniczne","a1")]
    if k == "W5.04":
        L = [DT]
        n = [("s","startEvent","Monitoring mediów i gazów medycznych",DT,{"eventType":"timer"}),
             ("a1","manualTask","Monitoruj zużycie mediów",DT,{}),
             ("g1","exclusiveGateway","Awaria / przekroczenie?",DT,{}),
             ("a2","sendTask","Reaguj i zgłoś dostawcy",DT,{}),
             ("a3","userTask","Rozliczaj media",DT,{}),
             ("e1","endEvent","Media zapewnione",DT,{})]
        f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Rozliczenie mediów","a3")]
    if k == "W5.05":
        L = [DT,"Serwis (zewn.)"]
        n = [("s","startEvent","Kontrola wentylacji i klimatyzacji",DT,{"eventType":"timer"}),
             ("a1","manualTask","Kontroluj parametry powietrza (bloki / sale)",DT,{}),
             ("g1","exclusiveGateway","Parametry poza normą?",DT,{}),
             ("a2","sendTask","Zleć serwis HVAC","Serwis (zewn.)",{}),
             ("a3","userTask","Udokumentuj kontrole",DT,{}),
             ("e1","endEvent","Czystość powietrza zapewniona",DT,{})]
        f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Protokół kontroli HVAC","a3")]
    if k == "W5.06":
        L = [DT,"Dostawca usługi"]
        n = [("s","startEvent","Zapotrzebowanie na usługę pralniczą",DT,{"eventType":"message"}),
             ("a1","userTask","Przekaż bieliznę brudną",DT,{}),
             ("a2","manualTask","Zrealizuj / odbierz pranie","Dostawca usługi",{}),
             ("a3","userTask","Skontroluj jakość i rozlicz",DT,{}),
             ("e1","endEvent","Usługa pralnicza zrealizowana",DT,{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Zlecenie pralni","a1")]
    if k == "W5.07":
        L = [DT,"Dział Higieny i Epidemiologii"]
        n = [("s","startEvent","Plan utrzymania czystości",DT,{"eventType":"timer"}),
             ("a1","manualTask","Realizuj sprzątanie wg planu",DT,{}),
             ("a2","manualTask","Kontroluj standardy higieny","Dział Higieny i Epidemiologii",{}),
             ("g1","exclusiveGateway","Odchylenia od standardu?",DT,{}),
             ("a3","userTask","Wdroż działania naprawcze",DT,{}),
             ("e1","endEvent","Czystość utrzymana",DT,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","e1","nie",1),("a3","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Plan higieny","a1")]
    if k == "W5.08":
        L = ["Dietetyk","Dostawca cateringu",DT]
        n = [("s","startEvent","Zapotrzebowanie na żywienie","Dietetyk",{"eventType":"message"}),
             ("a1","userTask","Przekaż zapotrzebowanie i diety","Dietetyk",{}),
             ("a2","manualTask","Przygotuj i dostarcz posiłki","Dostawca cateringu",{}),
             ("a3","manualTask","Kontroluj jakość i HACCP",DT,{}),
             ("e1","endEvent","Żywienie zrealizowane",DT,{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Jadłospis / diety","a1")]
    if k == "W5.09":
        L = [DT,"Odbiorca odpadów (zewn.)"]
        n = [("s","startEvent","Cykl gospodarki odpadami",DT,{"eventType":"timer"}),
             ("a1","manualTask","Segreguj i ewidencjonuj odpady",DT,{}),
             ("a2","sendTask","Przekaż do odbioru (BDO)","Odbiorca odpadów (zewn.)",{}),
             ("a3","userTask","Rozlicz i dokumentuj",DT,{}),
             ("e1","endEvent","Odpady zagospodarowane",DT,{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Karta przekazania (BDO)","a2")]
    if k == "W5.10":
        L = [DT]
        n = [("s","startEvent","Zlecenie transportu pomocniczego",DT,{"eventType":"message"}),
             ("a1","userTask","Zaplanuj i przydziel pojazd",DT,{}),
             ("a2","manualTask","Zrealizuj transport",DT,{}),
             ("a3","userTask","Rozlicz i utrzymuj pojazdy",DT,{}),
             ("e1","endEvent","Transport pomocniczy zrealizowany",DT,{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Karta drogowa","a2")]
    # W5.11 ochrona fizyczna
    L = [DT,"Służba ochrony"]
    n = [("s","startEvent","Realizacja ochrony obiektów",DT,{"eventType":"timer"}),
         ("a1","manualTask","Realizuj ochronę i monitoring","Służba ochrony",{}),
         ("g1","exclusiveGateway","Zdarzenie bezpieczeństwa?","Służba ochrony",{}),
         ("a2","sendTask","Interweniuj i zgłoś","Służba ochrony",{}),
         ("a3","userTask","Dokumentuj zdarzenia",DT,{}),
         ("e1","endEvent","Obiekty chronione",DT,{})]
    f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
    return L,n,f,[("d1","dataObjectReference","Rejestr zdarzeń ochrony","a3")]

def g_W6(p):
    k = _k(p); DOP = "Dział Organizacyjno-Prawny"
    if k == "W6.01":
        L = ["Komórka inicjująca",DOP,"Zarząd"]
        n = [("s","startEvent","Potrzeba dokumentu wewnętrznego","Komórka inicjująca",{"eventType":"message"}),
             ("a1","userTask","Opracuj projekt dokumentu","Komórka inicjująca",{}),
             ("a2","userTask","Sprawdź pod kątem formalnym",DOP,{}),
             ("g1","exclusiveGateway","Zatwierdzić?","Zarząd",{}),
             ("a3","serviceTask","Zarejestruj i opublikuj",DOP,{}),
             ("e1","endEvent","Dokument obowiązuje",DOP,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","a1","nie",0)]
        return L,n,f,[("d1","dataStore","Rejestr dokumentów wewnętrznych","a3")]
    if k == "W6.02":
        L = [DOP,"Komórka merytoryczna"]
        n = [("s","startEvent","Wpływ korespondencji",DOP,{"eventType":"message"}),
             ("a1","userTask","Zarejestruj w dzienniku",DOP,{}),
             ("a2","userTask","Dekretuj i przekaż",DOP,{}),
             ("a3","userTask","Załatw sprawę","Komórka merytoryczna",{}),
             ("a4","sendTask","Wyślij korespondencję wychodzącą",DOP,{}),
             ("e1","endEvent","Sprawa kancelaryjna załatwiona",DOP,{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataStore","Dziennik korespondencji","a1")]
    if k == "W6.03":
        L = [DOP]
        n = [("s","startEvent","Zdarzenie do wpisu w rejestrze",DOP,{"eventType":"message"}),
             ("a1","userTask","Zweryfikuj i wpisz do rejestru",DOP,{}),
             ("a2","manualTask","Utrzymuj i udostępniaj rejestr",DOP,{"loop":True}),
             ("e1","endEvent","Rejestr aktualny",DOP,{})]
        f = C("s","a1","a2","e1")
        return L,n,f,[("d1","dataStore","Rejestr wewnętrzny","a1")]
    if k == "W6.04":
        L = ["Komórka przekazująca",DOP]
        n = [("s","startEvent","Przekazanie akt do archiwum","Komórka przekazująca",{"eventType":"message"}),
             ("a1","userTask","Przygotuj i przekaż akta","Komórka przekazująca",{}),
             ("a2","userTask","Przyjmij i zewidencjonuj",DOP,{}),
             ("a3","manualTask","Przechowuj, udostępniaj, brakuj",DOP,{"loop":True}),
             ("e1","endEvent","Akta w archiwum zakładowym",DOP,{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataStore","Archiwum zakładowe","a2")]
    if k == "W6.05":
        L = [DOP,"Radca prawny","Zarząd"]
        n = [("s","startEvent","Sprawa korporacyjna (KRS/BIP/walne)","Zarząd",{"eventType":"message"}),
             ("a1","userTask","Przygotuj dokumentację korporacyjną",DOP,{}),
             ("a2","userTask","Zaopiniuj prawnie","Radca prawny",{}),
             ("a3","sendTask","Złóż / opublikuj (KRS / BIP)",DOP,{}),
             ("e1","endEvent","Sprawa korporacyjna załatwiona",DOP,{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Dokumentacja korporacyjna","a1")]
    # W6.06 informacja publiczna
    L = ["Wnioskodawca",DOP]
    n = [("s","startEvent","Wniosek o informację publiczną","Wnioskodawca",{"eventType":"message"}),
         ("a1","userTask","Zarejestruj wniosek",DOP,{}),
         ("a2","businessRuleTask","Oceń zakres i ograniczenia",DOP,{}),
         ("g1","exclusiveGateway","Udostępnić?",DOP,{}),
         ("a3","sendTask","Udostępnij informację",DOP,{}),
         ("a4","userTask","Wydaj decyzję odmowną",DOP,{}),
         ("e1","endEvent","Informacja udostępniona",DOP,{}),
         ("e2","endEvent","Decyzja odmowna wydana",DOP,{})]
    f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","a4","nie",0),("a4","e2",None,0)]
    return L,n,f,[("d1","dataObjectReference","Wniosek UDIP","a1")]

def g_W7(p):
    k = _k(p)
    if k == "W7.01":
        L = ["Kierownicy komórek","Stanowisko BHP"]
        n = [("s","startEvent","Cykl oceny ryzyka zawodowego","Stanowisko BHP",{"eventType":"timer"}),
             ("a1","userTask","Zbierz dane o stanowiskach","Kierownicy komórek",{}),
             ("a2","businessRuleTask","Oceń ryzyko zawodowe","Stanowisko BHP",{}),
             ("g1","exclusiveGateway","Ryzyko akceptowalne?","Stanowisko BHP",{}),
             ("a3","userTask","Zaplanuj środki ograniczające","Kierownicy komórek",{}),
             ("a4","userTask","Udokumentuj i zapoznaj pracowników","Stanowisko BHP",{}),
             ("e1","endEvent","Ryzyko zawodowe ocenione","Stanowisko BHP",{})]
        f = C("s","a1","a2","g1")+[("g1","a4","tak",1),("g1","a3","nie",0),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Karta oceny ryzyka","a2")]
    if k == "W7.02":
        L = ["Poszkodowany / Kierownik","Stanowisko BHP","Zespół powypadkowy"]
        n = [("s","startEvent","Zgłoszenie wypadku","Poszkodowany / Kierownik",{"eventType":"message"}),
             ("a1","userTask","Zgłoś i zabezpiecz miejsce","Poszkodowany / Kierownik",{}),
             ("a2","userTask","Ustal okoliczności i przyczyny","Zespół powypadkowy",{}),
             ("a3","businessRuleTask","Zakwalifikuj wypadek","Zespół powypadkowy",{}),
             ("a4","sendTask","Sporządź dokumentację i zgłoś (ZUS/PIP)","Stanowisko BHP",{}),
             ("e1","endEvent","Postępowanie powypadkowe zakończone","Stanowisko BHP",{})]
        f = C("s","a1","a2","a3","a4","e1")
        return L,n,f,[("d1","dataStore","Rejestr wypadków","a4")]
    if k == "W7.03":
        L = ["Stanowisko BHP","Dział Personalno-Płacowy","Pracownik"]
        n = [("s","startEvent","Potrzeba szkolenia BHP","Stanowisko BHP",{"eventType":"timer"}),
             ("a1","userTask","Zaplanuj szkolenia (wstępne/okresowe)","Stanowisko BHP",{}),
             ("a2","manualTask","Przeprowadź szkolenie","Pracownik",{}),
             ("a3","serviceTask","Zarejestruj w aktach","Dział Personalno-Płacowy",{}),
             ("e1","endEvent","Szkolenie BHP zrealizowane","Stanowisko BHP",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Zaświadczenie BHP","a3")]
    if k == "W7.04":
        L = ["Komórka","Stanowisko BHP","Dział Zamówień Publicznych"]
        n = [("s","startEvent","Zapotrzebowanie na środki ochrony","Komórka",{"eventType":"message"}),
             ("a1","businessRuleTask","Określ wymagane ŚOI","Stanowisko BHP",{}),
             ("a2","sendTask","Zamów ŚOI","Dział Zamówień Publicznych",{}),
             ("a3","manualTask","Wydaj i ewidencjonuj","Stanowisko BHP",{}),
             ("e1","endEvent","ŚOI zapewnione","Stanowisko BHP",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataStore","Ewidencja ŚOI","a3")]
    if k == "W7.05":
        L = ["Stanowisko P-POŻ","Zarząd"]
        n = [("s","startEvent","Cykl planów P-POŻ","Stanowisko P-POŻ",{"eventType":"timer"}),
             ("a1","userTask","Opracuj / aktualizuj plany i instrukcje","Stanowisko P-POŻ",{}),
             ("a2","userTask","Zatwierdź plany","Zarząd",{}),
             ("a3","sendTask","Zakomunikuj i wywieś","Stanowisko P-POŻ",{}),
             ("e1","endEvent","Plany P-POŻ obowiązują","Stanowisko P-POŻ",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Plan ewakuacji / instrukcja","a1")]
    if k == "W7.06":
        L = ["Stanowisko P-POŻ","Dział Techniczny"]
        n = [("s","startEvent","Harmonogram przeglądów P-POŻ","Stanowisko P-POŻ",{"eventType":"timer"}),
             ("a1","userTask","Zaplanuj przeglądy","Stanowisko P-POŻ",{}),
             ("a2","manualTask","Przeprowadź przegląd sprzętu/instalacji","Dział Techniczny",{}),
             ("g1","exclusiveGateway","Sprawne?","Stanowisko P-POŻ",{}),
             ("a3","manualTask","Zleć naprawę / wymianę","Dział Techniczny",{}),
             ("a4","userTask","Udokumentuj przegląd","Stanowisko P-POŻ",{}),
             ("e1","endEvent","Sprzęt P-POŻ sprawny","Stanowisko P-POŻ",{})]
        f = C("s","a1","a2","g1")+[("g1","a4","tak",1),("g1","a3","nie",0),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Protokół przeglądu P-POŻ","a2")]
    if k == "W7.07":
        L = ["Stanowisko P-POŻ","Personel"]
        n = [("s","startEvent","Plan ćwiczeń P-POŻ","Stanowisko P-POŻ",{"eventType":"timer"}),
             ("a1","userTask","Zaplanuj ćwiczenia ewakuacyjne","Stanowisko P-POŻ",{}),
             ("a2","manualTask","Przeprowadź ćwiczenia / szkolenia","Personel",{}),
             ("a3","userTask","Oceń i udokumentuj","Stanowisko P-POŻ",{}),
             ("e1","endEvent","Ćwiczenia zrealizowane","Stanowisko P-POŻ",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Protokół ćwiczeń","a3")]
    if k == "W7.08":
        L = ["Stanowisko ds. Obronnych","Zarząd"]
        n = [("s","startEvent","Cykl planowania obronnego (OC/MOB)","Stanowisko ds. Obronnych",{"eventType":"timer"}),
             ("a1","userTask","Opracuj plany OC / MOB","Stanowisko ds. Obronnych",{}),
             ("a2","userTask","Zatwierdź i aktualizuj","Zarząd",{}),
             ("a3","manualTask","Realizuj zadania obronne","Stanowisko ds. Obronnych",{"loop":True}),
             ("e1","endEvent","Zadania obronne realizowane","Stanowisko ds. Obronnych",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Plan OC / MOB","a1")]
    # W7.09 wspolpraca z organami obronnymi
    L = ["Stanowisko ds. Obronnych","Organ obronny (zewn.)"]
    n = [("s","startEvent","Wystąpienie organu obronnego","Organ obronny (zewn.)",{"eventType":"message"}),
         ("a1","userTask","Przygotuj dane i odpowiedź","Stanowisko ds. Obronnych",{}),
         ("a2","sendTask","Przekaż organowi (WSzW / ZW)","Organ obronny (zewn.)",{}),
         ("a3","userTask","Realizuj zalecenia","Stanowisko ds. Obronnych",{}),
         ("e1","endEvent","Sprawa obronna obsłużona","Stanowisko ds. Obronnych",{})]
    f = C("s","a1","a2","a3","e1")
    return L,n,f,[("d1","dataObjectReference","Korespondencja obronna","a2")]

def g_W8(p):
    k = _k(p); DIR = "Dyrektor ds. Inwestycji i Rozwoju"
    if k == "W8.01":
        L = [DIR,"Zarząd"]
        n = [("s","startEvent","Cykl planowania inwestycji",DIR,{"eventType":"timer"}),
             ("a1","userTask","Zidentyfikuj i oszacuj potrzeby inwestycyjne",DIR,{}),
             ("a2","userTask","Opracuj program inwestycji",DIR,{}),
             ("g1","exclusiveGateway","Zatwierdzić program?","Zarząd",{}),
             ("a3","userTask","Włącz do planu i monitoruj",DIR,{}),
             ("e1","endEvent","Program inwestycji przyjęty",DIR,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","a2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Program inwestycji","a2")]
    if k == "W8.02":
        L = [DIR,"Dział Zamówień Publicznych","Wykonawca"]
        n = [("s","startEvent","Decyzja o realizacji inwestycji",DIR,{"eventType":"message"}),
             ("a1","userTask","Przygotuj dokumentację projektową",DIR,{}),
             ("a2","sendTask","Wyłoń wykonawcę (PZP)","Dział Zamówień Publicznych",{}),
             ("a3","manualTask","Realizuj i nadzoruj roboty","Wykonawca",{"loop":True}),
             ("b1","boundaryEvent","Opóźnienie harmonogramu","",{"attachedTo":"a3","eventType":"timer","interrupting":False}),
             ("a4","userTask","Uruchom działania naprawcze",DIR,{}),
             ("a5","userTask","Odbierz inwestycję",DIR,{}),
             ("e1","endEvent","Inwestycja oddana do użytku",DIR,{})]
        f = C("s","a1","a2","a3","a5","e1")+[("b1","a4",None,0),("a4","a3",None,0)]
        return L,n,f,[("d1","dataObjectReference","Dokumentacja projektowa","a1")]
    if k == "W8.03":
        L = [DIR,"Instytucja finansująca"]
        n = [("s","startEvent","Nabór / możliwość dofinansowania",DIR,{"eventType":"message"}),
             ("a1","userTask","Opracuj wniosek o dofinansowanie",DIR,{}),
             ("a2","sendTask","Złóż wniosek","Instytucja finansująca",{}),
             ("g1","exclusiveGateway","Przyznano środki?","Instytucja finansująca",{}),
             ("a3","userTask","Podpisz umowę o dofinansowanie",DIR,{}),
             ("e1","endEvent","Dofinansowanie pozyskane",DIR,{}),
             ("e2","endEvent","Wniosek odrzucony",DIR,{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Wniosek o dofinansowanie","a1")]
    if k == "W8.04":
        L = ["Dyrektor ds. Inwestycji","Dział Finansowo-Księgowy","Instytucja finansująca"]
        n = [("s","startEvent","Etap rozliczenia projektu","Dyrektor ds. Inwestycji",{"eventType":"timer"}),
             ("a1","userTask","Zbierz dokumenty rozliczeniowe","Dział Finansowo-Księgowy",{}),
             ("a2","userTask","Sporządź wniosek o płatność","Dyrektor ds. Inwestycji",{}),
             ("a3","sendTask","Złóż rozliczenie do instytucji","Instytucja finansująca",{}),
             ("g1","exclusiveGateway","Zaakceptowano?","Instytucja finansująca",{}),
             ("a4","userTask","Uzupełnij / skoryguj","Dyrektor ds. Inwestycji",{}),
             ("e1","endEvent","Projekt rozliczony","Dyrektor ds. Inwestycji",{})]
        f = C("s","a1","a2","a3","g1")+[("g1","e1","tak",1),("g1","a4","nie",0),("a4","a3",None,0)]
        return L,n,f,[("d1","dataObjectReference","Wniosek o płatność","a2")]
    if k == "W8.05":
        L = ["Dyrektor ds. Inwestycji","Dyrektor ds. Lecznictwa","Zarząd"]
        n = [("s","startEvent","Pomysł na nową usługę / oddział","Dyrektor ds. Inwestycji",{"eventType":"message"}),
             ("a1","userTask","Przeprowadź analizę wykonalności","Dyrektor ds. Inwestycji",{}),
             ("a2","businessRuleTask","Oceń zasoby i zgodność","Dyrektor ds. Lecznictwa",{}),
             ("g1","exclusiveGateway","Uruchomić usługę?","Zarząd",{}),
             ("a3","userTask","Wdroż nową usługę","Dyrektor ds. Lecznictwa",{}),
             ("e1","endEvent","Usługa uruchomiona","Dyrektor ds. Lecznictwa",{}),
             ("e2","endEvent","Odstąpiono od uruchomienia","Zarząd",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",1),("a3","e1",None,0),("g1","e2","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Analiza wykonalności","a1")]
    # W8.06 wspolpraca naukowo-kliniczna
    L = ["Dyrektor ds. Lecznictwa","Dyrektor ds. Inwestycji","Partner naukowy"]
    n = [("s","startEvent","Inicjatywa współpracy naukowej","Dyrektor ds. Lecznictwa",{"eventType":"message"}),
         ("a1","userTask","Określ zakres współpracy","Dyrektor ds. Lecznictwa",{}),
         ("a2","userTask","Zawrzyj porozumienie","Partner naukowy",{}),
         ("a3","manualTask","Realizuj projekty kliniczno-naukowe","Dyrektor ds. Inwestycji",{"loop":True}),
         ("e1","endEvent","Współpraca realizowana","Dyrektor ds. Lecznictwa",{})]
    f = C("s","a1","a2","a3","e1")
    return L,n,f,[("d1","dataObjectReference","Porozumienie o współpracy","a2")]

def g_W9(p):
    k = _k(p)
    if k == "W9.01":
        L = ["Pacjent","Pełnomocnik ds. Praw Pacjenta","Komórka merytoryczna"]
        n = [("s","startEvent","Wpływ skargi / reklamacji pacjenta","Pacjent",{"eventType":"message"}),
             ("a1","userTask","Zarejestruj skargę / wniosek","Pełnomocnik ds. Praw Pacjenta",{}),
             ("a2","userTask","Wyjaśnij sprawę z komórką","Komórka merytoryczna",{}),
             ("g1","exclusiveGateway","Skarga zasadna?","Pełnomocnik ds. Praw Pacjenta",{}),
             ("a3","userTask","Zaplanuj działania naprawcze","Komórka merytoryczna",{}),
             ("a4","sendTask","Udziel odpowiedzi pacjentowi","Pełnomocnik ds. Praw Pacjenta",{}),
             ("e1","endEvent","Skarga rozpatrzona","Pełnomocnik ds. Praw Pacjenta",{})]
        f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","e1",None,0)]
        return L,n,f,[("d1","dataStore","Rejestr skarg i wniosków","a1")]
    if k == "W9.02":
        L = ["Pełnomocnik ds. Praw Pacjenta","Personel / Pacjenci"]
        n = [("s","startEvent","Plan edukacji o prawach pacjenta","Pełnomocnik ds. Praw Pacjenta",{"eventType":"timer"}),
             ("a1","userTask","Opracuj materiały informacyjne","Pełnomocnik ds. Praw Pacjenta",{}),
             ("a2","manualTask","Prowadź edukację","Personel / Pacjenci",{}),
             ("a3","serviceTask","Udostępnij informacje (tablice / WWW)","Pełnomocnik ds. Praw Pacjenta",{}),
             ("e1","endEvent","Edukacja zrealizowana","Pełnomocnik ds. Praw Pacjenta",{})]
        f = C("s","a1","a2","a3","e1")
        return L,n,f,[("d1","dataObjectReference","Materiały informacyjne","a1")]
    if k == "W9.03":
        L = ["Pełnomocnik ds. Dostępności","Komórki organizacyjne"]
        n = [("s","startEvent","Cykl audytu dostępności","Pełnomocnik ds. Dostępności",{"eventType":"timer"}),
             ("a1","manualTask","Przeprowadź audyt dostępności","Pełnomocnik ds. Dostępności",{}),
             ("g1","exclusiveGateway","Zidentyfikowano bariery?","Pełnomocnik ds. Dostępności",{}),
             ("a2","userTask","Zaplanuj i wdroż poprawę","Komórki organizacyjne",{}),
             ("a3","userTask","Zaktualizuj deklarację / raport","Pełnomocnik ds. Dostępności",{}),
             ("e1","endEvent","Dostępność poprawiona","Pełnomocnik ds. Dostępności",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",0),("g1","a3","nie",1),("a2","a3",None,0),("a3","e1",None,0)]
        return L,n,f,[("d1","dataObjectReference","Raport dostępności","a3")]
    if k == "W9.04":
        L = ["Zarząd","Dział Organizacyjno-Prawny","Dział Informatyki"]
        n = [("s","startEvent","Potrzeba komunikacji zewnętrznej","Dział Organizacyjno-Prawny",{"eventType":"message"}),
             ("a1","userTask","Przygotuj treść komunikatu","Dział Organizacyjno-Prawny",{}),
             ("g1","exclusiveGateway","Zatwierdzić publikację?","Zarząd",{}),
             ("a2","serviceTask","Opublikuj (WWW / BIP / media)","Dział Informatyki",{}),
             ("e1","endEvent","Komunikat opublikowany","Dział Informatyki",{})]
        f = C("s","a1","g1")+[("g1","a2","tak",1),("a2","e1",None,0),("g1","a1","nie",0)]
        return L,n,f,[("d1","dataObjectReference","Komunikat","a1")]
    # W9.05 ankiety satysfakcji
    L = ["Pełnomocnik ds. Akredytacji","Pacjenci","Pełnomocnik ds. Praw Pacjenta"]
    n = [("s","startEvent","Cykl badania satysfakcji","Pełnomocnik ds. Akredytacji",{"eventType":"timer"}),
         ("a1","manualTask","Przeprowadź badanie ankietowe","Pacjenci",{}),
         ("a2","businessRuleTask","Przeanalizuj wyniki","Pełnomocnik ds. Akredytacji",{}),
         ("g1","exclusiveGateway","Obszary do poprawy?","Pełnomocnik ds. Akredytacji",{}),
         ("a3","userTask","Zaplanuj działania doskonalące","Pełnomocnik ds. Praw Pacjenta",{}),
         ("a4","sendTask","Opublikuj wyniki","Pełnomocnik ds. Akredytacji",{}),
         ("e1","endEvent","Badanie satysfakcji zamknięte","Pełnomocnik ds. Akredytacji",{})]
    f = C("s","a1","a2","g1")+[("g1","a3","tak",0),("g1","a4","nie",1),("a3","a4",None,0),("a4","e1",None,0)]
    return L,n,f,[("d1","dataObjectReference","Wyniki ankiet","a2")]

def g_W3(p):
    m = next(x for x in _W3 if x["kod"] == _k(p))
    return m["lanes"], m["nodes"], m["flows"], m.get("data", [])

GROUPS = {"Z1":g_Z1,"Z2":g_Z2,"Z3":g_Z3,"Z4":g_Z4,"Z5":g_Z5,"Z6":g_Z6,
          "G1":g_G1,"G2":g_G2,"G3":g_G3,"G4":g_G4,"G5":g_G5,"G6":g_G6,"G7":g_G7,"G8":g_G8,"G9":g_G9,"G10":g_G10,
          "W1":g_W1,"W2":g_W2,"W3":g_W3,"W4":g_W4,"W5":g_W5,"W6":g_W6,"W7":g_W7,"W8":g_W8,"W9":g_W9}

def model_for(proc):
    fn = GROUPS.get(prefix(proc))
    if not fn:
        L = ["Realizator"]
        n = [("s","startEvent","Zdarzenie inicjujące","Realizator",{"eventType":"message"}),
             ("a1","userTask","Zrealizuj czynności procesu","Realizator",{}),
             ("e1","endEvent","Proces zakończony","Realizator",{})]
        return L,n,C("s","a1","e1"),[]
    return fn(proc)
