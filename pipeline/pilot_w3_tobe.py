#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pilot_w3_tobe.py - PILOT: 7 wielotorowych modeli to-be grupy W3 (Zamowienia publiczne).
Kazdy proces = ODREBNY przebieg z realnymi rolami w torach, bramkami, wyjatkami i artefaktami.
Modele referencyjne/to-be (propozycja do walidacji), nie deklaracja as-is.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bpmn_generator as G
from build_pkg import parse_assets, asset_node_type, short, AI, slug, svg_to_pdf

REG = {str(p["Kod"]): p for p in json.load(open(os.path.join(ROOT, "data", "register.json"), encoding="utf-8"))}

# Role (tory) wspolne dla grupy zamowien
WN="Komórka wnioskująca"; DZP="Dział Zamówień Publicznych"; KOM="Komisja przetargowa"
RP="Radca prawny"; KZ="Kierownik Zamawiającego (Zarząd)"; DFK="Dział Finansowo-Księgowy"
MAG="Magazyn"; DI="Dział Informatyki"

# Model: kod, lanes (kolejnosc gora->dol), nodes [(id,type,name,lane,opts)], flows [(s,t,label,default)],
#        data [(id,type,name,host)]
MODELS = [
{"kod":"W3.01","lanes":[WN,DZP,KZ],
 "nodes":[
   ("s","startEvent","Rozpoczęcie rocznego planowania zamówień",WN,{"eventType":"timer"}),
   ("a1","userTask","Zgłoś potrzeby zakupowe na rok",WN,{}),
   ("a2","userTask","Zagreguj potrzeby i oszacuj wartości",DZP,{}),
   ("a3","businessRuleTask","Ustal tryby i progi (PZP)",DZP,{}),
   ("a4","userTask","Sporządź projekt planu postępowań",DZP,{}),
   ("g1","exclusiveGateway","Zatwierdzić plan?",KZ,{}),
   ("a5","userTask","Skoryguj projekt planu",DZP,{}),
   ("a6","serviceTask","Opublikuj plan (BZP / e-Zamówienia)",DZP,{}),
   ("a7","userTask","Monitoruj i aktualizuj plan",DZP,{"loop":True}),
   ("e1","endEvent","Plan postępowań obowiązuje",DZP,{})],
 "flows":[("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","a4",None,0),
   ("a4","g1",None,0),("g1","a6","tak",1),("g1","a5","nie",0),("a5","a4",None,0),
   ("a6","a7",None,0),("a7","e1",None,0)],
 "data":[("d1","dataObjectReference","Potrzeby zakupowe","a1"),
   ("d2","dataObjectReference","Plan postępowań","a4")]},

{"kod":"W3.02","lanes":[WN,DZP,KOM,RP,KZ],
 "nodes":[
   ("s","startEvent","Wniosek o wszczęcie postępowania",WN,{"eventType":"message"}),
   ("a1","userTask","Opisz przedmiot zamówienia i potrzebę",WN,{}),
   ("a2","userTask","Przygotuj SWZ i warunki udziału",DZP,{}),
   ("a3","userTask","Zaopiniuj SWZ pod kątem prawnym",RP,{}),
   ("a4","userTask","Zatwierdź wszczęcie postępowania",KZ,{}),
   ("a5","serviceTask","Opublikuj ogłoszenie (BZP/TED, e-Zamówienia)",DZP,{}),
   ("a6","receiveTask","Przyjmij oferty",DZP,{}),
   ("a7","userTask","Oceń oferty i zbadaj przesłanki wykluczenia",KOM,{}),
   ("g1","exclusiveGateway","Oferty ważne?",KOM,{}),
   ("a8","businessRuleTask","Wybierz najkorzystniejszą ofertę",KOM,{}),
   ("a9","userTask","Zatwierdź wybór wykonawcy",KZ,{}),
   ("a10","userTask","Sporządź umowę",RP,{}),
   ("a11","sendTask","Zawrzyj umowę z wykonawcą",DZP,{}),
   ("a12","sendTask","Unieważnij postępowanie",DZP,{}),
   ("b1","boundaryEvent","Odwołanie do KIO","",{"attachedTo":"a7","eventType":"message","interrupting":False}),
   ("a13","userTask","Obsłuż odwołanie (KIO)",RP,{}),
   ("e1","endEvent","Umowa zawarta",DZP,{}),
   ("e2","endEvent","Postępowanie unieważnione",DZP,{})],
 "flows":[("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","a4",None,0),
   ("a4","a5",None,0),("a5","a6",None,0),("a6","a7",None,0),("a7","g1",None,0),
   ("g1","a8","tak",1),("g1","a12","nie",0),("a8","a9",None,0),("a9","a10",None,0),
   ("a10","a11",None,0),("a11","e1",None,0),("a12","e2",None,0),("b1","a13",None,0),("a13","a7",None,0)],
 "data":[("d1","dataObjectReference","SWZ","a2"),("d2","dataObjectReference","Oferty","a6"),
   ("d3","dataObjectReference","Protokół postępowania","a8"),("d4","dataObjectReference","Umowa","a10")]},

{"kod":"W3.03","lanes":[WN,DZP,KZ],
 "nodes":[
   ("s","startEvent","Wniosek o zakup podprogowy",WN,{"eventType":"message"}),
   ("a1","userTask","Uzasadnij potrzebę i oszacuj wartość",WN,{}),
   ("a2","businessRuleTask","Ustal tryb wg regulaminu wewnętrznego",DZP,{}),
   ("a3","sendTask","Przeprowadź rozeznanie rynku / zaproś oferty",DZP,{}),
   ("a4","receiveTask","Zbierz oferty",DZP,{}),
   ("a5","userTask","Porównaj oferty i sporządź notatkę",DZP,{}),
   ("g1","exclusiveGateway","Zatwierdzić wybór?",KZ,{}),
   ("a6","sendTask","Udziel zamówienia / zawrzyj umowę",DZP,{}),
   ("e1","endEvent","Zamówienie udzielone",DZP,{}),
   ("e2","endEvent","Odstąpiono od zakupu",KZ,{})],
 "flows":[("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","a4",None,0),
   ("a4","a5",None,0),("a5","g1",None,0),("g1","a6","tak",1),("g1","e2","nie",0),("a6","e1",None,0)],
 "data":[("d1","dataObjectReference","Oferty","a4"),("d2","dataObjectReference","Notatka z rozeznania","a5")]},

{"kod":"W3.04","lanes":[WN,DZP,DFK],
 "nodes":[
   ("s","startEvent","Zapotrzebowanie bieżące",WN,{"eventType":"message"}),
   ("a1","userTask","Złóż i uzasadnij zapotrzebowanie",WN,{}),
   ("a2","userTask","Zweryfikuj zapotrzebowanie i budżet",DZP,{}),
   ("g1","exclusiveGateway","W ramach umowy / limitu?",DZP,{}),
   ("a3","sendTask","Złóż zamówienie u dostawcy",DZP,{}),
   ("a4","userTask","Przeprowadź wybór dostawcy",DZP,{}),
   ("a5","manualTask","Odbierz dostawę / usługę",WN,{}),
   ("a6","serviceTask","Zarejestruj fakturę i rozlicz",DFK,{}),
   ("e1","endEvent","Zakup rozliczony",DFK,{})],
 "flows":[("s","a1",None,0),("a1","a2",None,0),("a2","g1",None,0),("g1","a3","tak",1),
   ("g1","a4","nie",0),("a4","a3",None,0),("a3","a5",None,0),("a5","a6",None,0),("a6","e1",None,0)],
 "data":[("d1","dataObjectReference","Zapotrzebowanie","a1"),("d2","dataObjectReference","Faktura","a6")]},

{"kod":"W3.05","lanes":[WN,DZP,RP],
 "nodes":[
   ("s","startEvent","Potrzeba zawarcia / zmiany umowy",WN,{"eventType":"message"}),
   ("a1","userTask","Zdefiniuj wymagania umowne",WN,{}),
   ("a2","userTask","Opracuj / zweryfikuj projekt umowy",RP,{}),
   ("a3","userTask","Negocjuj warunki z dostawcą",DZP,{}),
   ("a4","sendTask","Zawrzyj umowę / aneks",DZP,{}),
   ("a5","serviceTask","Zarejestruj umowę w repozytorium (CLM)",DZP,{}),
   ("a6","userTask","Monitoruj realizację i SLA",WN,{"loop":True}),
   ("g1","exclusiveGateway","Zbliża się termin / wygaśnięcie?",DZP,{}),
   ("a7","userTask","Uruchom odnowienie lub wypowiedzenie",DZP,{}),
   ("b1","boundaryEvent","Alert terminu umowy","",{"attachedTo":"a6","eventType":"timer","interrupting":False}),
   ("e1","endEvent","Umowa odnowiona / zamknięta",DZP,{})],
 "flows":[("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","a4",None,0),
   ("a4","a5",None,0),("a5","a6",None,0),("a6","g1",None,0),("g1","a7","tak",1),
   ("g1","a6","nie",0),("a7","e1",None,0),("b1","a7",None,0)],
 "data":[("d1","dataStore","Repozytorium umów (CLM)","a5"),("d2","dataObjectReference","Umowa / aneks","a4")]},

{"kod":"W3.06","lanes":[MAG,DFK],
 "nodes":[
   ("s","startEvent","Operacja magazynowa (przyjęcie / wydanie)",MAG,{"eventType":"message"}),
   ("g1","exclusiveGateway","Rodzaj operacji?",MAG,{}),
   ("a1","manualTask","Przyjmij i skontroluj dostawę (PZ)",MAG,{}),
   ("a2","serviceTask","Zaewidencjonuj przyjęcie (PZ)",MAG,{}),
   ("a3","manualTask","Skompletuj i wydaj towar (RW/WZ)",MAG,{}),
   ("a4","serviceTask","Zaewidencjonuj wydanie (RW/WZ)",MAG,{}),
   ("a5","userTask","Zaktualizuj stany magazynowe",MAG,{}),
   ("a6","serviceTask","Uzgodnij wartościowo z księgowością",DFK,{}),
   ("e1","endEvent","Operacja magazynowa zakończona",MAG,{})],
 "flows":[("s","g1",None,0),("g1","a1","przyjęcie",1),("g1","a3","wydanie",0),
   ("a1","a2",None,0),("a2","a5",None,0),("a3","a4",None,0),("a4","a5",None,0),
   ("a5","a6",None,0),("a6","e1",None,0)],
 "data":[("d1","dataStore","Kartoteka magazynowa","a5"),("d2","dataObjectReference","Dokument PZ/RW/WZ","a2")]},

{"kod":"W3.07","lanes":[DZP,DI],
 "nodes":[
   ("s","startEvent","Czynność na Platformie e-Zamówienia",DZP,{"eventType":"message"}),
   ("a1","userTask","Przygotuj dokumenty do publikacji",DZP,{}),
   ("a2","userTask","Zapewnij dostępy i wsparcie techniczne",DI,{}),
   ("a3","serviceTask","Opublikuj postępowanie na platformie",DZP,{}),
   ("a4","receiveTask","Obsłuż pytania i komunikację z wykonawcami",DZP,{}),
   ("a5","serviceTask","Zarchiwizuj dokumentację postępowania",DZP,{}),
   ("e1","endEvent","Postępowanie obsłużone na platformie",DZP,{})],
 "flows":[("s","a1",None,0),("a1","a2",None,0),("a2","a3",None,0),("a3","a4",None,0),
   ("a4","a5",None,0),("a5","e1",None,0)],
 "data":[("d1","dataStore","Platforma e-Zamówienia","a3"),("d2","dataObjectReference","Dokumentacja postępowania","a5")]},
]

def build(model):
    kod = model["kod"]; proc = REG.get(kod, {})
    name = proc.get("Proces", kod)
    lane_ids = {nm: "L%d" % i for i, nm in enumerate(model["lanes"])}
    pool = {"id":"P1","name":"SCM Sp. z o.o.","lanes":[{"id":lane_ids[nm],"name":nm} for nm in model["lanes"]]}
    nodes=[]; associations=[]
    for nid, typ, nm, lane, opts in model["nodes"]:
        nd = {"id":nid,"type":typ,"name":nm}
        if typ == "boundaryEvent":
            nd["attachedTo"] = opts.get("attachedTo")
            if "interrupting" in opts: nd["interrupting"] = opts["interrupting"]
        else:
            nd["lane"] = lane_ids[lane]
        if opts.get("eventType"): nd["eventType"] = opts["eventType"]
        if opts.get("loop"): nd["loop"] = True
        nodes.append(nd)
    flows=[]
    for s,t,lab,dflt in model["flows"]:
        f={"source":s,"target":t}
        if lab: f["name"]=lab
        if dflt: f["default"]=True
        flows.append(f)
    # artefakty + ewentualne aktywa AI z rejestru
    for did,typ,nm,host in model.get("data",[]):
        nodes.append({"id":did,"type":typ,"name":nm}); associations.append({"source":did,"target":host})
    for i,c in enumerate(parse_assets(proc.get("Aktywa informacyjne (kody)"))):
        did="ai_%s"%c.replace("-","_")
        nodes.append({"id":did,"type":asset_node_type(c),"name":"%s: %s"%(c,short(AI.get(c,{}).get("nazwa") or "",15))})
        hosts=[n[0] for n in model["nodes"] if n[1].endswith("Task")]
        associations.append({"source":did,"target":hosts[i%len(hosts)]})
    # stopka: systemy + RODO
    sysraw=proc.get("Systemy / moduły (kody)")
    med=(proc.get("Dane medyczne (art. 9 RODO)") or "").strip().lower()
    os_=(proc.get("Dane osobowe (RODO)") or "").strip().lower()
    parts=[]
    if sysraw: parts.append("Systemy: %s"%short(str(sysraw),52))
    if med=="tak": parts.append("RODO: dane medyczne (art. 9)")
    elif os_=="tak": parts.append("RODO: dane osobowe")
    if parts: nodes.append({"id":"n_info","type":"textAnnotation","name":" · ".join(parts)})
    return {"id":"Proc_%s"%re.sub(r'[^A-Za-z0-9]','_',kod),"name":"%s  %s"%(kod,name),
            "pools":[pool],"nodes":nodes,"flows":flows,"associations":associations}

def main():
    out=os.path.join(ROOT,"out_pilot","W3_Zamowienia_publiczne_to-be"); os.makedirs(out,exist_ok=True)
    for m in MODELS:
        spec=build(m); warns=G.validate(spec)
        base=os.path.join(out,"%s__%s"%(m["kod"],slug(REG.get(m["kod"],{}).get("Proces"),46)))
        res=G.generate(spec,base); svg_to_pdf(res["svg"],base+".pdf"); os.remove(res["svg"])
        print(f"{m['kod']:7} tory={len(m['lanes'])} węzły={len(spec['nodes'])} uwagi={len(warns)}" + ("  !"+";".join(warns) if warns else ""))
    print("PILOT W3 ->", out)

if __name__=="__main__": main()
