#!/usr/bin/env python3

# Corona-Info-App
# measure_utils
# © 2020 Tobias Höpp.
from flask import request, jsonify
from models.measures import displayGroup, displayGroupHasDisplay, display, districtHasGroup, regionHasGroup, createSource
from main import db
import json

class dR_():
    ok = bool
    etxt = str
    def __init__(self, ok, etxt=None, val=None):
        self.ok = ok
        self.etxt = etxt
        self.val = val

# Utils for Measures (Default_groups)
def createDefaultGroup(display_id, text_de, replicats_id=None, deduplication=True,subtitle=None):
# Create a new default_group (includes Deduplication)
    #INPUT:
    # display_id (int)
    # configuration (dict)
    # replicates_id (int)
    d = display.query.get(display_id)
    if not d:
        #check if display_id is valid
        return dR_(0, "Invalid display_id: '"+str(display_id)+"'") 
    if deduplication:
        m = displayGroupHasDisplay.query.filter(displayGroupHasDisplay.display_id == display_id, displayGroupHasDisplay.text_de == text_de, displayGroupHasDisplay.subtitle_de==subtitle, displayGroupHasDisplay.displayGroup.has(displayGroup.is_default == 1)).first()
            # Deduplication: Check if already exists
    if (not deduplication) or (not m):
        # It does not already exist. Or: deduplication should not be applied
        if deduplication:
            g = displayGroup(is_default=1)
        else:
            g = displayGroup(is_default=2)
                # correctly set the measure not to deduplicate
        db.session.add(g)
        db.session.flush()
            # Create Group
        m = displayGroupHasDisplay(g.id,display_id,text_de)
        if subtitle != None:
            m.subtitle_de = subtitle
        # TODO: Use defaultmeasure with string instead!
        db.session.add(m)
        db.session.flush()
            # Create Display-Link
    if replicats_id != None:
        #Add replication ID
        rp = displayGroup.query.get(replicats_id)
        if rp == None:
            # Check if replicats_id is valid
            return dR_(0, "Invalid replicates_id")
        m.displayGroup.replication_of.append(rp)
    return dR_(1, val=m.displayGroup)
        





##########################################
#Endpoint-Funktionsgeneralisierungen (Return = Return der API)
##########################################
def deleteMeasure(inputs, group_id, district_id=None, region_id=None):
    #INPUT:
    # remove: boolean ('true' / 'false')
    # undo: boolean ('true' / 'false')
    if district_id != None and region_id == None:
        is_district = True
    elif district_id == None and region_id != None:
        is_district = False
    else:
        return "Internal Server Error: deleteMeasure being called with nonsense arguments.", 500
    #Measure von Kreis löschen
    #TODO: Ablaufdatum hinzufügen.
    if is_district:
        dg = districtHasGroup.query.get({"district_id": district_id, "displayGroup_id": group_id})
    else:
        dg = regionHasGroup.query.get({"region_id": region_id, "displayGroup_id": group_id})
    if not dg:
        return "Not found", 404
    if "undo" in inputs and "remove" in inputs:
        return "To many arguments", 400
    
    if "undo" in inputs:
        undo = False
        if isinstance(inputs.get("undo"), bool):
            if inputs.get("undo"):
                undo = True
        else:
            if inputs.get("undo") == "true":
                undo = True
            elif inputs.get("undo") != "false":
                return jsonify({"status": "ValueError", "value": "undo", "error": "use 'true' or 'false' for boolean value"}), 400
        if undo:
            dg.is_deleted = False
            db.session.commit()
            return jsonify({"status": "Marked as not Deleted again"}), 201
    if "remove" in inputs:
        remove = False
        if isinstance(inputs.get("remove"), bool):
            if inputs.get("remove"):
                remove = True
        else:
            if inputs.get("remove") == "true":
                remove = True
            elif inputs.get("remove") != "false":
                return jsonify({"status": "ValueError", "value": "remove", "error": "use 'true' or 'false' for boolean value"}), 400
        if remove:
            db.session.delete(dg)
            db.session.commit()
            return jsonify({"status": "Successfully deleted"}), 200
    dg.is_deleted = True
    db.session.commit()
    return jsonify({"status": "Successfully deleted"}), 200

def modifyMeasure(inputs, group_id, district_id=None, region_id=None):
    if district_id != None and region_id == None:
        is_district = True
    elif district_id == None and region_id != None:
        is_district = False
    else:
        return "Internal Server Error: modifyMeasure being called with nonsense arguments.", 500
    #Measure von Kreis bearbeiten = löschen und neu erstellen. oder bearbeiten, falls detatched
    #INPUTS:
    #   source (highly recommended)
    #   display_id
    #   configuration (JSON)
    #   no_dedup (true or false)

    # 1) Alte Maßnahme löschen = trennen (1): Alte Maßnahme holen. Löschen passiert erst während des erstellens der neuen.
    if is_district:
        dhg1 = districtHasGroup.query.get({"district_id": district_id, "displayGroup_id": group_id})
    else:
        dhg1 = regionHasGroup.query.get({"region_id": region_id, "displayGroup_id": group_id})
    if not dhg1:
        return "Not found", 404
    if dhg1.is_deleted:
        return "Measure is marked as deleted", 403
    
    if "display_id" in inputs:
        disp = display.query.get(inputs.get("display_id"))
        if not disp:
            #check if display_id is valid
            return jsonify({"status": "ValueError", "value": "display_id", "error": "Not found'"}), 400
    else:
        disp =  dhg1.displayGroup.displayLink[0].display

    if "configuration" in inputs:
        if not isinstance(inputs.get("configuration"), dict):
            try:
                configuration = json.loads(inputs.get("configuration"))
            except ValueError:
                return "Invalid JSON in configuration", 400
        else:
            configuration = inputs.get("configuration")
    else:
        configuration = dhg1.displayGroup.displayLink[0].configuration

    if "no_dedup" in inputs:

        if isinstance(inputs.get("no_dedup"), bool):
            if inputs.get("no_dedup"):
                deduplication = False
            else:
                deduplication = True
        else:
            if inputs.get("no_dedup") == "true":
                deduplication = False
            elif inputs.get("no_dedup") == "false":
                deduplication = True
            else:
                return jsonify({"status": "ValueError", "value": "no_dedup", "error": "boolean: use 'true' or 'false'"}), 400
    else:
        if dhg1.displayGroup.is_default == 2:
            deduplication = False
        else:
            deduplication = True
    
    if "source" in inputs:
        if inputs.get("source") != "":
            source_id = createSource(inputs.get("source")).id
        else:
            source_id = None
    else:
        source_id = dhg1.source_id

    # 2) Check ob alte Maßnahme detatched. Dann direkt ändern. sonst mit Löschen und neu-erstellen
    if not (dhg1.displayGroup.is_default == 2 and deduplication == True) and not dhg1.displayGroup.default_of and not dhg1.displayGroup.overwritten_by and len(dhg1.displayGroup.regionLink) + len(dhg1.displayGroup.districtLink) == 1:
        # erste veroderung sorgt dafür, dass bei änderung von deduplication von false auf true die maßnahme neu erstellt wird, um von der deduplication gebrauch zu machen
        # Prüfen, ob Maßnahme nicht als default besteht und auch von keiner anderen überschrieben wird und nur zu einem Landkreis oder Land gehört
        # Änderungen direkt schreiben 
        dhg1.source_id = source_id
        if "display_id" in inputs:
            dhg1.displayGroup.displayLink[0].display = disp
                #Update DisplayGroup
        if "configuration" in inputs or "display_id" in inputs:
            ok, err = validateConfig(configuration,disp.varlist)
            if not ok:
                return jsonify({"status": "ValueError", "value": "configuration", "error": "Invalid configuration for display '"+str(disp.id)+"': "+err}), 400
            dhg1.displayGroup.displayLink[0].configuration = configuration
                #Update configuration
        if "no_dedup" in inputs:
            if deduplication:
                dhg1.displayGroup.is_default = 1
            else:
                dhg1.displayGroup.is_default = 2
        db.session.commit()
        return jsonify({"status": "Done", "displayGroup_id": group_id, "comment": "reused"}), 201
    
    # 3) Neue Maßnahme erstellen (wenn nicht geändert werden durfte)
    if  (dhg1.displayGroup.is_default == 2 and deduplication == False or dhg1.displayGroup.is_default == 1 and deduplication == True) and disp.id == dhg1.displayGroup.displayLink[0].display_id and configuration == dhg1.displayGroup.displayLink[0].configuration:
        # Wenn sich nichts geändert hat kann einfach nur die quelle aktualisiert werden, falls die Maßnahme zu mehreren Kreisen / Regionen gehört.
        dhg1.source_id = source_id
            #still update source
        return jsonify({"status": "Done", "displayGroup_id": group_id, "comment": "Already existed"}), 200
    rr = createDefaultGroup(disp.id,configuration,replicats_id=dhg1.displayGroup.id,deduplication=deduplication)
    if not rr.ok:
        return "Error: createDefaultGroup: "+rr.etxt, 400
    if dhg1.displayGroup.is_default == 2 and deduplication == True:
        # löscht die alte Maßnahme, die zuvor nicht dedupliziert worden war
        db.session.delete(dhg1.displayGroup.displayLink[0])
        db.session.delete(dhg1)
    else:    
        dhg1.is_deleted = True
            #Mark as deleted
    db.session.flush()

    g = rr.val
    if is_district:
        dhg2 = districtHasGroup.query.get({"district_id": district_id, "displayGroup_id": g.id})
    else:
        dhg2 = regionHasGroup.query.get({"region_id": region_id, "displayGroup_id": g.id})
    if not dhg2:
        # Check if link between district/region and Group already exists ()
        if is_district:
            dhg2 = districtHasGroup(district_id, g.id)
        else:
            dhg2 = regionHasGroup(region_id, g.id)
        db.session.add(dhg2)
        db.session.flush()
            # Create new Link
    dhg2.source_id = source_id
    dhg2.is_deleted = False
        # Mark as not deleted
    db.session.commit()
    return jsonify({"status": "Done", "displayGroup_id": g.id}), 201

def getMeasures(district_id=None, region_id=None):
    if district_id != None and region_id == None:
        is_district = True
    elif district_id == None and region_id != None:
        is_district = False
    else:
        return "Internal Server Error: getMeasures being called with nonsense arguments.", 500
    
    if is_district:
        dhgs = districtHasGroup.query.filter(districtHasGroup.district_id == district_id)
    else:
        dhgs = regionHasGroup.query.filter(regionHasGroup.region_id == region_id)
    result = []
    for dhg in dhgs:
        if dhg.displayGroup.is_default == 2:
            deduplication = False
        else:
            deduplication = True
        if dhg.source:
            source = {"id": dhg.source.id,"text": dhg.source.text}
        else:
            source = {}
        d = dhg.displayGroup.displayLink[0].display
        # TODO: decide, what is really necessary.
        res = {
            "id": dhg.displayGroup.id,
            "name": dhg.displayGroup.name,
            "configuration": dhg.displayGroup.displayLink[0].configuration,
            "autolinked": dhg.autolinked,
            "deduplication": deduplication,
            "source": source,
            "is_deleted": dhg.is_deleted,
            "replication_of":[],
            "overwritten_by":[],
            "replicats_into":[],
            "default_of":[],
            "display": {
                "id": dhg.displayGroup.displayLink[0].display_id,
                "title": dhg.displayGroup.displayLink[0].display.title_de,
                "subtitle":dhg.displayGroup.displayLink[0].subtitle_de,
                "text": dhg.displayGroup.displayLink[0].text_de,
                "name": d.name,
                "isOFP": d.is_OFP,
                "is_deprecated": d.is_deprecated,
                "deprecated_by": d.deprecated_by_id,
                "is_mergable": d.is_mergable,
                "is_default": d.is_default,
                "weight": d.weight,              
            }
        }
        for r in dhg.displayGroup.replication_of:
            res["replication_of"].append(r.id)
        for r in dhg.displayGroup.replicats_into:
            res["replicats_into"].append(r.id)
        for r in dhg.displayGroup.default_of:
            res["default_of"].append(r.id)
        for r in dhg.displayGroup.overwritten_by:
            res["overwritten_by"].append(r.id)
        result.append(res)
    return jsonify(result), 200

def getMeasure(group_id, district_id=None, region_id=None):
    if district_id != None and region_id == None:
        is_district = True
    elif district_id == None and region_id != None:
        is_district = False
    else:
        return "Internal Server Error: getMeasure being called with nonsense arguments.", 500
    if is_district:
        dhg = districtHasGroup.query.get({"district_id": district_id, "displayGroup_id": group_id})
    else:
        dhg = regionHasGroup.query.get({"region_id": region_id, "displayGroup_id": group_id})
    if not dhg:
        return "Not found", 404
    if dhg.displayGroup.is_default == 2:
        deduplication = False
    else:
        deduplication = True
    if dhg.source:
        source = {"id": dhg.source.id,"text": dhg.source.text}
    else:
        source = {}
    res = {
        "name": dhg.displayGroup.name,
        "display_id": dhg.displayGroup.displayLink[0].display_id,
        "configuration": dhg.displayGroup.displayLink[0].configuration,
        "autolinked": dhg.autolinked,
        "deduplication": deduplication,
        "source": source,
        "is_deleted": dhg.is_deleted,
        "replication_of":[],
        "overwritten_by":[],
        "replicats_into":[],
        "default_of":[]
    }
    for r in dhg.displayGroup.replication_of:
        res["replication_of"].append(r.id)
    for r in dhg.displayGroup.replicats_into:
        res["replicats_into"].append(r.id)
    for r in dhg.displayGroup.default_of:
        res["default_of"].append(r.id)
    for r in dhg.displayGroup.overwritten_by:
        res["overwritten_by"].append(r.id)
    return jsonify(res), 200


def createMeasure(inputs={}, district_id=None, region_id=None):
    if district_id != None and region_id == None:
        is_district = True
    elif district_id == None and region_id != None:
        is_district = False
    else:
        return "Internal Server Error: createMeasure being called with nonsense arguments.", 500
    #INPUTS:
    #   source (highly recommended)
    #   display_id*
    #   configuration* (JSON)
    #   replicats_id (highly not recommended to use) #TODO: Remove?
    #   no_dedup (true or false)

    # check for required values
    if not all(e in inputs for e in ("display_id", "configuration")):
        return "Error: Required values missing", 400
    if not isinstance(inputs.get("configuration"), dict):
        try:
            configuration = json.loads(inputs.get("configuration"))
        except ValueError:
            return "Invalid JSON in configuration", 400
    else:
        configuration = inputs.get("configuration")
    display_id =inputs.get("display_id")

    if "replicats_id" in inputs:
        replicats_id = inputs.get("replicats_id")
    else:
        replicats_id = None
    
    if "no_dedup" in inputs:
        if isinstance(inputs.get("no_dedup"), bool):
            if inputs.get("no_dedup"):
                deduplication = False
            else:
                deduplication = True
        else:
            if inputs.get("no_dedup") == "true":
                deduplication = False
            elif inputs.get("no_dedup") == "false":
                deduplication = True
            else:
                return jsonify({"status": "ValueError", "value": "no_dedup", "error": "boolean: use 'true' or 'false'"}), 400
    else:
        deduplication = True

    rr = createDefaultGroup(display_id,configuration,replicats_id=replicats_id,deduplication=deduplication)
    if not rr.ok:
        return "Error: createDefaultGroup: "+rr.etxt, 400
    g = rr.val
    if is_district:
        dhg = districtHasGroup.query.get({"district_id": district_id, "displayGroup_id": g.id})
    else:
        dhg = regionHasGroup.query.get({"region_id": region_id, "displayGroup_id": g.id})
    if not dhg:
        # Check if link between district/region and Group already exists
        if is_district:
            dhg = districtHasGroup(district_id, g.id)
        else:
            dhg = regionHasGroup(region_id, g.id)
        db.session.add(dhg)
        db.session.flush()
            # Create new Link
    if "source" in inputs:
        dhg.source_id = createSource(inputs.get("source")).id
    db.session.commit()
    return jsonify({"status": "Done", "displayGroup_id": g.id}), 201    