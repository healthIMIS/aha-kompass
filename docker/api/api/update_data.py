#!/usr/bin/env python3

# Corona-Info-App
# Database init script
# © 2020 Tobias Höpp

# Include utilities
import urllib
import json
from sqlalchemy import and_
import bs4
import visvalingamwyatt as vw
# Include db connection
from main import db, api

# Include models
from models.districts import districts, updateDistrictIncidence, createRegionIfNotExists
from models.measures import sources, regionHasGroup, categories, display, createSource
from utils.measure_utils import createDefaultGroup
from models.users import users

# Include utils
from utils.coloring import coloring

#@api.before_first_request
def setup():
    db.create_all()
    initialize()
    update()

# Definitions
def makeMeasure(text, region_id, display_id=None, title=None):
    if display_id == None:
        if title == None:
            return 0, "Neither display_id nor title given"
        c = categories.query.filter(categories.name == title).first()
                # Prüfen, ob eine gleichnamige Kategorie schon existiert (Ausschlaggebend ist IMMER der Name in deutscher Sprache.)
        if not c:
            # Fehler schmeißen!!!
            # Wenn keine Kategorie existiert, erstellen
            c = categories(title)
            db.session.add(c)
            db.session.flush()
                # Erzeuge neue Kategorie
            d = display("$_text_",None, category_id=c.id, is_default=True, varlist={"text":{"type":"str"}}) 
            db.session.add(d)
                # Erzeuge Default-Display für die neue Kategorie
            db.session.flush()

        d = display.query.filter(display.category_id == c.id, display.is_default == True).first()
            # Display-Id ermitteln
        if not d:
            return 0, "No default display found for this category. This is due to a data integrety error."
            # TODO: add to log
        display_id = d.id
    rr = createDefaultGroup(display_id,{"text": text})
    if not rr.ok:
        return 0, "Error: createDefaultGroup: "+rr.etxt
    g = rr.val
    #dhg = regionHasGroup.query.get({"region_id": region_id, "displayGroup_id": g.id})
    dhg = regionHasGroup.query.filter(regionHasGroup.region_id == region_id, regionHasGroup.displayGroup_id == g.id).first()
    if not dhg:
        # Check if link between region and Group already exists
        dhg = regionHasGroup(region_id, g.id)
        db.session.add(dhg)
        db.session.flush()
            # Create new Link
    dhg.source_id = createSource("https://tourismus-wegweiser.de/json").id
    dhg.autolinked = True
    dhg.is_deleted = False



###########################################################
# Los geht's
###########################################################
def update():
    print("Lade Aktuelle Daten des RKI herunter.")
    openURL = urllib.request.urlopen('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=cases7_per_100k,RS&returnGeometry=false&outSR=4326&f=json')
    if(openURL.getcode()==200):
        data = json.loads(openURL.read())
        for kreis in data["features"]:
            updateDistrictIncidence(
                int(kreis["attributes"]["RS"]), 
                int(kreis["attributes"]["cases7_per_100k"]), 
                coloring(int(kreis["attributes"]["cases7_per_100k"]))
            )
    else:
        print("ERROR loading Landkreise")
        print(openURL)

    print("Lade aktuelle Maßnahmen der Länder herunter.")
    openURL = urllib.request.urlopen('https://tourismus-wegweiser.de/json')
    if(openURL.getcode()==200):
        data = json.loads(openURL.read())
        #Alte Verknüpfungen löschen
        source_text = "https://tourismus-wegweiser.de/json"
        so = sources.query.filter(sources.text == source_text).first()
        if so: 
            db.session.execute(regionHasGroup.__table__.update().where(and_(regionHasGroup.autolinked == True, regionHasGroup.source_id == so.id)).values(is_deleted=True)) #TODO: mark as deleted instead of actually deleting it
            db.session.flush()
        for d in data:
            region_id = createRegionIfNotExists(d["Bundesland"]).id
            for title in d["allgemein"]:
                html_soup = bs4.BeautifulSoup(d["allgemein"][title]["text"], 'html.parser')
                mkdown = ""
                for c in html_soup.contents:
                    mk = ""
                    for l in c:
                        if isinstance(l, bs4.element.Tag):
                            if l.name == "a":
                                mk+= "["+l.string+"]("+l["href"]+")"
                            else:
                                Exception("Unhandeled tag")
                        elif isinstance(l, bs4.element.NavigableString):
                            mk += str(l)
                    if mk != "":
                        mkdown += "* "+mk+"\n"    
                m = makeMeasure(mkdown, region_id, title=title)
            for m in d["tourismus"]:
                for title in m:
                    mkdown = ""
                    for index in ["Öffnung und Zugang", "Aufenthalt und Hygiene"]:
                        if m[title][index]["text"] != "":
                            mkdown += "# "+index+"\n"
                                #TODO: use configuration instead for option to translate titles
                            html_soup = bs4.BeautifulSoup(m[title][index]["text"], 'html.parser')
                            for c in html_soup.contents:
                                mk = ""
                                for l in c:
                                    if isinstance(l, bs4.element.Tag):
                                        if l.name == "a":
                                            mk+= "["+l.string+"]("+l["href"]+")"
                                        else:
                                            Exception("Unhandeled tag")
                                    elif isinstance(l, bs4.element.NavigableString):
                                        mk += str(l)
                                if mk != "":
                                    mkdown += mk+"\n" 
                    if m[title]["Weitere Informationen"] != "":
                        mkdown += "# Weitere Informationen\n"
                            #TODO: use configuration instead for option to translate titles
                        html_soup = bs4.BeautifulSoup(m[title][index]["text"], 'html.parser')
                        for c in html_soup.contents:
                            mk = ""
                            for l in c:
                                if isinstance(l, bs4.element.Tag):
                                    if l.name == "a":
                                        mk+= "["+l.string+"]("+l["href"]+")"
                                    else:
                                        Exception("Unhandeled tag")
                                elif isinstance(l, bs4.element.NavigableString):
                                    mk += str(l)
                            if mk != "":
                                mkdown += mk+"\n" 
                    m = makeMeasure(mkdown, region_id, title=title)

        db.session.commit()
    else:
        print("ERROR loading Maßnahmen")
        print(openURL)


def initialize():
    print("Lade Landkreise herunter. Das kann etwas dauern.")
    openURL = urllib.request.urlopen('https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=GEN,Shape__Length,cases7_per_100k,RS,BL,BEZ&outSR=4326&f=json')
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
                    [],
                    coordinates,
                    kreis["attributes"]["BEZ"]
                    )
                dnew.region = createRegionIfNotExists(kreis["attributes"]["BL"])
                db.session.add(dnew)
                db.session.flush()
                neueKreise.append(int(kreis["attributes"]["RS"]))
        with open('links.json') as f:
            data = json.load(f)
        for d in data:
            if d["id"] in neueKreise:
                dist = districts.query.get(d["id"])
                dist.links = [{"href": d["link"],"title": "Zur Webseite des Kreises"}]
        if not users.query.filter(users.username == "cms").first(): #TODO: REMOVE THIS FOR PRODUCTION!!!! (and add hashing)
            u = users("cms","pw") 
            db.session.add(u)
        db.session.commit()
    else:
        print("ERROR loading Landkreise")
    
