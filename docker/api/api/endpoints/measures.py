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
from utils.flexstring import flexstringParse, mergeConfig
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
                "measures" : []
            }
        else:
            result = {
                "incidence" : d.incidence,
                "color" : d.color,
                "name" : d.name,
                "categroy": d.category,
                "links": d.links,
                "measures" : [],
                "deactivate_region": d.deactivate_region, # Only for debugging!!!
            }

        if d.deactivate_region:
            defaultGroupsRequest = "select distinct dg1.displayGroup_id from districtHasGroup dg1 where dg1.district_id = :district_id and dg1.is_deleted = False"
        else:
            defaultGroupsRequest = "select distinct rg1.displayGroup_id from regionHasGroup rg1 where rg1.region_id = :region_id and rg1.is_deleted = False UNION select distinct dg1.displayGroup_id from districtHasGroup dg1 where dg1.district_id = :district_id and dg1.is_deleted = False"
        GroupsRequest = "select distinct ggd1.displayGroup_id from displayGroupHasDefault ggd1 where (select count(ggd2.default_id) from displayGroupHasDefault ggd2 where ggd1.displayGroup_id = ggd2.displayGroup_id and ggd2.default_id not in("+defaultGroupsRequest+")) = 0 UNION "+defaultGroupsRequest
        ConfigDisplayRequest = "select distinct dgd1.display_id, dgd1.configuration, dgd1.displayGroup_id from displayGroupHasDisplay dgd1 where dgd1.displayGroup_id in("+GroupsRequest+") and dgd1.displayGroup_id not in (select ov.overwrite_id from displayGroupOverwrites ov where ov.displayGroup_id in ("+GroupsRequest+")) ORDER BY (select di.weight from display di where di.id = dgd1.display_id), (select c1.name from display di left join categories c1 on di.category_id = c1.id where di.id = dgd1.display_id)"

        daten = db.session.execute(ConfigDisplayRequest, {"region_id":d.region_id,"district_id":d.id})
        lastDisplayID = None
        lastConfiguration = None
        for row in daten:
            config = json.loads(row[1])
            di = display.query.get(row[0])
            if not di:
                return "Internal Server Error: display_id '"+str(row[0])+"' selected but not found", 500
            if request.args.get("measures") == None or (request.args.get("measures") in ["ofp", "all"] and di.is_OFP) or (request.args.get("measures") in ["detail", "all"] and not di.is_OFP):

                merged = False
                if di.is_mergable:
                    if lastDisplayID == di.id:
                        c = mergeConfig(config,lastConfiguration)
                        if c:
                            merged = True
                            config = c
                            # Displays mergen. Wenn merge nicht erfolgreich, beide anzeigen

                languageString = None
                languageSubtitle = None
                languageCategory = None
                    #initialisieren
                if(request.args.get("lang") == "de"):
                    languageString = di.flexstring_german
                    languageSubtitle = di.subtitle_german
                    languageCategory = di.category.name
                elif(request.args.get("lang") == "en"):
                    languageString = di.flexstring_english
                    languageSubtitle = di.subtitle_english
                    languageCategory = di.category.name_english
                    print(str(languageCategory))
                #Default German if no argument is given or string for requested language is empty
                if languageString in ["", None]:
                    languageString = di.flexstring_german
                if languageSubtitle in ["", None]:
                    languageSubtitle = di.subtitle_german
                if languageCategory in ["", None]:
                    languageCategory = di.category.name

                ok, res, epos = flexstringParse(languageString, config)
                if not ok:
                    return jsonify({"status": "InternalServerError", "error": "flexstringParseError for string '"+languageString+"' with configuration '"+str(config)+"': "+res+" at Position "+str(epos)}), 500
                appendend = {
                    "title" : languageCategory,
                    "text" : res,
                    "subtitle" : languageSubtitle,
                    "display_id" : di.id,
                    "displayGroup_id": row[2],
                    "isOFP": di.is_OFP
                }
                if merged:
                    result["measures"][-1] = appendend
                else:
                    result["measures"].append(appendend)
                lastDisplayID = di.id
                lastConfiguration = config

        return jsonify(result), 200
#TODO: Use proper join and select instead of iterating
