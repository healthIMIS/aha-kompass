#!/usr/bin/env python3

# Corona-Info-App
# Database Initialisation and update
# © 2020 Tobias Höpp
# Create ERD: eralchemy -i sqlite:///test.db -o erd_from_db.pdf

# Include utilities
import urllib
import json
from sqlalchemy import and_
import visvalingamwyatt as vw
from utils.markdownify import markdownify
import traceback
# Include db connection
from main import db

# Include models
from models.districts import districts, updateDistrictIncidence, createRegionIfNotExists, links
from models.measures import sources, regionHasGroup, createSource
from models.users import users

# Include utils
from utils.coloring import coloring
from utils.measure_update_utils import getOrmakeCategory, makeMeasure
from utils.update_nina import updateNINA
from utils.checkProduction import production

def setup():
    db.create_all()
    klarSchiffMachen() # Achtung! Bis zum Abschluss des Setups werden keine vollständigen Daten geliefert!!!
    initialize(overwriteLinks=True)
    update(do_push=False)
    db.session.commit()

###########################################################
# Los geht's
###########################################################
def update(do_push=True):
    try:
        update_rki()
    except Exception as e:
        print ("Error in update_rki():\n", e, "\n", traceback.format_exc())
    try:
        update_tourismus()
    except Exception as e:
        print ("Error in update_tourismus():\n", e, "\n", traceback.format_exc())
    if not production:
        db.session.commit() # updateNina will else fail due to threading and sqlite-limitations
    try:
        updateNINA(do_push=do_push)
    except Exception as e:
        print ("Error in updateNINA():\n", e, "\n", traceback.format_exc())
    db.session.commit()
def update_rki():
    print("Lade Aktuelle Daten des RKI herunter.")
    openURL = urllib.request.urlopen('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=cases7_per_100k,RS&returnGeometry=false&outSR=4326&f=json')
    #openURL = urllib.request.urlopen('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json')
    if(openURL.getcode()==200):
        data = json.loads(openURL.read())
        for kreis in data["features"]:
            updateDistrictIncidence(
                int(kreis["attributes"]["RS"]), 
                int(kreis["attributes"]["cases7_per_100k"]), 
                coloring(int(kreis["attributes"]["cases7_per_100k"]))
            )
    else:
        print("ERROR loading RKI-Daten")
        print(openURL)
def update_tourismus():
    print("Lade aktuelle Maßnahmen der Länder herunter.")
    openURL = urllib.request.urlopen('https://tourismus-wegweiser.de/json')
    if(openURL.getcode()==200):
        data = json.loads(openURL.read())
        #Alte Verknüpfungen löschen
        source_text = "https://tourismus-wegweiser.de/json"
        so = sources.query.filter(sources.text == source_text).first()
        if so: 
            #db.session.execute(regionHasGroup.__table__.update().where(and_(regionHasGroup.autolinked == True, regionHasGroup.source_id == so.id)).values(is_deleted=True))
            db.session.execute(regionHasGroup.__table__.delete().where(and_(regionHasGroup.autolinked == True, regionHasGroup.source_id == so.id)))
            db.session.flush()
        for d in data:
            region_id = createRegionIfNotExists(d["Bundesland"]).id
            for title in d["allgemein"]:
                mkdown = markdownify(d["allgemein"][title]["text"])
                makeMeasure(mkdown, region_id=region_id, title=title, source="https://tourismus-wegweiser.de/json")
            for m in d["tourismus"]:
                for title in m:
                    mkdown = ""
                    for index in ["Öffnung und Zugang", "Aufenthalt und Hygiene"]:
                        if m[title][index]["text"] != "":
                            mkdown += "# "+index+"\n"
                            mkdown += markdownify(m[title][index]["text"])
                                #TODO: use configuration instead for option to translate titles
                    if m[title]["Weitere Informationen"] != "":
                        mkdown += "# Weitere Informationen\n"
                            #TODO: use configuration instead for option to translate titles
                        if not isinstance(m[title]["Weitere Informationen"], str):
                            print(region_id, title, m[title]["Weitere Informationen"])
                        mkdown += markdownify(m[title]["Weitere Informationen"]) 
                    makeMeasure(mkdown, region_id=region_id, title=title, source="https://tourismus-wegweiser.de/json")
    else:
        print("ERROR loading Maßnahmen")
        print(openURL)
    db.session.flush()

def initialize(overwriteLinks=False):
    print("Lade Landkreise herunter. Das kann etwas dauern.")
    #openURL = urllib.request.urlopen('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=GEN,Shape__Length,cases7_per_100k,RS,BL,BEZ&outSR=4326&f=json')
    openURL = urllib.request.urlopen('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json')
    if(openURL.getcode()==200):
        data = json.loads(openURL.read())
        neueKreise = []
        for kreis in data["features"]:
            coordinates = []
            for ring in kreis["geometry"]["rings"]:
                a = vw.simplify(ring, ratio=0.1)
                for pair in a:
                    tmp = pair[0]
                    pair[0] = pair[1]
                    pair[1] = tmp
                coordinates.append(a)
            if not districts.query.get(int(kreis["attributes"]["RS"])):
                dnew = districts(
                    int(kreis["attributes"]["RS"]), 
                    kreis["attributes"]["GEN"],
                    int(kreis["attributes"]["cases7_per_100k"]),
                    coloring(int(kreis["attributes"]["cases7_per_100k"])),
                    coordinates,
                    kreis["attributes"]["BEZ"]
                    )
                dnew.region = createRegionIfNotExists(kreis["attributes"]["BL"])
                db.session.add(dnew)
                db.session.flush()
                neueKreise.append(int(kreis["attributes"]["RS"]))

        # Links zu den Kreisen erstellen
        mainLinks(neueKreise, overwrite=overwriteLinks)
                
        # Default - Categorien erstellen
        getOrmakeCategory("Kontaktbestimmungen", is_OFP = True, weight =-300, force=True)
        getOrmakeCategory("Geschäfte", is_OFP = True, weight =-200, force=True)
        #getOrmakeCategory("Private Feiern", is_OFP = True, weight =-100, force=True)
        getOrmakeCategory("Bußgelder", is_OFP = True, weight =200, force=True)
        getOrmakeCategory("Impf-Informationen", is_OFP = True, weight =300, force=True)
        db.session.flush()
    else:
        print("ERROR loading Landkreise")

def mainLinks(neueKreise, overwrite=False):
    sid = createSource("Initialisation").id
    with open('links.json') as f:
        data = json.load(f)
    if overwrite:
        db.session.execute(links.__table__.delete().where(links.source_id == sid))
    for d in data:
        if overwrite or d["id"] in neueKreise:
            di = districts.query.get(d["id"])
            di.mainLink = d["link"]
            if di.category in ["Kreisfreie Stadt", "Bezirk", "Stadtkreis"]:
                l = links("Zur Webseite der Stadt", d["link"], d["id"], sid)
            else:
                l = links("Zur Webseite des Kreises", d["link"], d["id"], sid)
            db.session.add(l)

def klarSchiffMachen():
    for tabelle in ["districtHasGroup", "displayGroupOverwrites", "displayGroupHasDisplay", "display", "regionHasGroup", "displayGroup"]: 
        cleanRequest = "DELETE FROM "+tabelle
        db.session.execute(cleanRequest)
    db.session.flush()