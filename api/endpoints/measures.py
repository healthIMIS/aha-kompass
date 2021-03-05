#!/usr/bin/env python3

# Corona-Info-App
# measures endpoint
# © 2020 Tobias Höpp.

# Include dependencies
from flask import request, jsonify

# Include modules
from main import api, db
from models.measures import displayGroup, display, displayGroupHasDisplay
from models.districts import districts
import json

# Endpoint definition
@api.route("/data/measures/lk/<KrS>", methods=["GET"])
def measures_lk(KrS):
    if request.method == "GET":
        d = districts.query.get(KrS)
        if(d == None):
            return "KrS not found", 404
        if(request.args.get("noLKDetails") == "1"):
            result = {
                "measures" : [],
                "sources": "Inzidenzwerte: Robert Koch-Institut (RKI), dl-de/by-2-0; Maßnahmen: Warn-App NINA des Bundesamt für Bevölkerungsschutz und Katastrophenhilfe (BKK), Bonn; Ausführliche Maßnahmen: Kompetenzzentrum Tourismus des Bundes, Lizenziert unter CC-BY 4.0."
            }
        else:
            links = []
            for l in d.links:
                links.append({
                    "href": l.href,
                    "title": l.title,
                })
            result = {
                "incidence" : d.incidence,
                "color" : d.color,
                "name" : d.name,
                "categroy": d.category,
                "links": links,
                "measures" : [],
                #"deactivate_region": d.deactivate_region, # Only for debugging!!!
                "sources": "Inzidenzwerte: Robert Koch-Institut (RKI), dl-de/by-2-0; Maßnahmen: Warn-App NINA des Bundesamt für Bevölkerungsschutz und Katastrophenhilfe (BKK), Bonn; Ausführliche Maßnahmen: Kompetenzzentrum Tourismus des Bundes, Lizenziert unter CC-BY 4.0."
            }

        # Hinweis hinzufügen
        if d.category in ["Kreisfreie Stadt", "Bezirk", "Stadtkreis"]:
            WebseiteOf = "der Stadt"
        else:
            WebseiteOf = "des Kreises"
        if request.args.get("measures") in [None, "all", "detail"]:
            result["measures"].append({
                    "title" : "Hinweis",
                    "text" : "*Auf regionaler Ebene kann es Sonderregelungen geben, die die unten aufgeführten landesweit gültigen Regeln ergänzen oder in Teilen aufheben.* \n** Informationen zu einigen Maßnahmen können daher auf dieser Seite ausgeblendet sein.** \n\n*Genauere Informationen können auf der [Webseite "+WebseiteOf+"]("+d.mainLink+") abgerufen werden.*",
                    "subtitle" : "",
                    "display_id" : -1,
                    "displayGroup_id": -1,
                    "isOFP": False,
                    #"color": "red",
                })

        if d.deactivate_region:
            defaultGroupsRequest = "select distinct dg1.displayGroup_id from districtHasGroup dg1 where dg1.district_id = :district_id and dg1.is_deleted = False"
        else:
            defaultGroupsRequest = "select distinct rg1.displayGroup_id from regionHasGroup rg1 where rg1.region_id = :region_id and rg1.is_deleted = False UNION select distinct dg1.displayGroup_id from districtHasGroup dg1 where dg1.district_id = :district_id and dg1.is_deleted = False"
        GroupsRequest = "select distinct ggd1.displayGroup_id from displayGroupHasDefault ggd1 where (select count(ggd2.default_id) from displayGroupHasDefault ggd2 where ggd1.displayGroup_id = ggd2.displayGroup_id and ggd2.default_id not in("+defaultGroupsRequest+")) = 0 UNION "+defaultGroupsRequest
        #ConfigDisplayRequest = "select distinct dgd1.display_id, dgd1.displayGroup_id from displayGroupHasDisplay dgd1 where dgd1.displayGroup_id in("+GroupsRequest+") and dgd1.displayGroup_id not in (select ov.overwrite_id from displayGroupOverwrites ov where ov.displayGroup_id in ("+GroupsRequest+")) ORDER BY (select di.weight from display di where di.id = dgd1.display_id), (select c1.name from display di left join categories c1 on di.category_id = c1.id where di.id = dgd1.display_id)"
        ConfigDisplayRequest = "select distinct dgd1.display_id, dgd1.displayGroup_id from displayGroupHasDisplay dgd1 where dgd1.displayGroup_id in("+GroupsRequest+") and dgd1.displayGroup_id not in (select ov.overwrite_id from displayGroupOverwrites ov where ov.displayGroup_id in ("+GroupsRequest+")) ORDER BY (select di.weight from display di where di.id = dgd1.display_id), (select di.title_de from display di where di.id = dgd1.display_id)" # TODO: Sort by language

        daten = db.session.execute(ConfigDisplayRequest, {"region_id":d.region_id,"district_id":d.id})
        for row in daten:
            di = display.query.get(row[0])
            if not di:
                return "Internal Server Error: display_id '"+str(row[0])+"' selected but not found", 500
            dghg = displayGroupHasDisplay.query.filter(displayGroupHasDisplay.display_id == row[0], displayGroupHasDisplay.displayGroup_id == row[1]).first() # TODO: Use one instead
            if not di:
                return "Internal Server Error: displayGroupHasDisplay not found", 500
            if request.args.get("measures") == None or (request.args.get("measures") in ["ofp", "all"] and di.is_OFP) or (request.args.get("measures") in ["detail", "all"] and not di.is_OFP):

                languageString = None
                languageSubtitle = None
                languageCategory = None
                    #initialisieren
                if(request.args.get("lang") == "de"):
                    languageString = dghg.text_de
                    languageSubtitle = dghg.subtitle_de
                    languageCategory = di.title_de
                elif(request.args.get("lang") == "en"):
                    languageString = dghg.text_en
                    languageSubtitle = dghg.subtitle_en
                    languageCategory = di.title_en
                    print(str(languageCategory))
                #Default German if no argument is given or string for requested language is empty
                if languageString in ["", None]:
                    languageString = dghg.text_de
                if languageSubtitle in ["", None]:
                    languageSubtitle = dghg.subtitle_de
                if languageCategory in ["", None]:
                    languageCategory = di.title_de

                appendend = {
                    "title" : languageCategory,
                    "text" : languageString,
                    "subtitle" : languageSubtitle,
                    "display_id" : di.id,
                    "displayGroup_id": row[1],
                    "isOFP": di.is_OFP,
                    #"color": "red",
                }
                result["measures"].append(appendend)

        # Hinweis am Ende hinzufügen
        # Hinweis hinzufügen
        if request.args.get("measures") == "ofp":
            result["measures"].append({
                    "title" : "Hinweis",
                    "text" : "*Auf regionaler Ebene kann es Sonderregelungen geben, die die hier aufgeführten Regeln ergänzen oder in Teilen aufheben.* \n\n*Genauere Informationen können auf der [Webseite "+WebseiteOf+"]("+d.mainLink+") abgerufen werden.*",
                    "subtitle" : "",
                    "display_id" : -1,
                    "displayGroup_id": -1,
                    "isOFP": True,
                    #"color": "red",
                })
        # Check if measures were detected. If not, use Fallback-Error
        if len(result["measures"]) == 1:
            result["measures"] = [{
                    "title" : "Hinweis",
                    "text" : "# Ein Fehler ist aufgetreten\n\n Aufgrund eines Server-Fehlers können hier zur Zeit leider keine Maßnahmen angezeigt werden. Das Problem sollte in wenigen Minuten behoben sein. \n\n Wir bitten um Entschuldigung. \n\n **Bitte versuchen Sie es in Kürze erneut, indem Sie die Seite neu laden.**\n\n *Informationen zu aktuellen Corona-Maßnahmen stehen auch auf der [Webseite "+WebseiteOf+" "+d.name+"]("+d.mainLink+") zur Verfügung.*",
                    "subtitle" : "",
                    "display_id" : -1,
                    "displayGroup_id": -1,
                    "isOFP": True,
                    #"color": "red",
                }]
        # Increment RequestCounter for stats
        d.requestCounter = districts.requestCounter+1
        db.session.commit()
        return jsonify(result), 200
#TODO: Use proper join and select instead of iterating
