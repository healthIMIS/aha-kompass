#!/usr/bin/env python3

# Corona-Info-App
# 
# © 2020 Tobias Höpp

# Include dependencies

from flask import request, jsonify

# Include modules
from main import api, db, jwt
from flask_jwt_extended import jwt_required
from models.measures import displayGroup, display
from utils.edit_display_utils import addDefaultGroups, addOverwriteGroups, addDisplayConfigs, removeDefaultGroups, removeOverwriteGroups, removeDisplayConfigs, modifyDisplayConfigs
import json


# Endpoints for Groups
@api.route("/edit/groups/<group_id>", methods=["PUT", "GET", "DELETE"])
@jwt_required
def modifyGroup(group_id):
    dg = displayGroup.query.get(group_id)
    if not dg:
        return "Not found", 404
    if request.method == "PUT":
        #INPUTS:
        #   group_id* (in Pfad) (ONLY allowed for groups, that are NOT default-groups!)
        #   name
        #   default_groups_add
        #   default_groups_remove
        #   overwrite_groups_add
        #   overwrite_groups_remove
        #   displayConfigs_add
        #   displayConfigs_modify
        #   displayConfigs_remove
        if dg.is_default:
            #Default-Groups are not allowed in this endpoint. Use Measures-Endpoint instead.
            return "group_id not allowed: Group is Default-Group (Measure)", 403
        # 0) Modify group itself
        if "name" in request.form:
            dg.name = request.form.get("name")

        # 1) Remove displayGroup from various links
        if "default_groups_remove" in request.form:
            #Remove default_groups from displayGroup
            try:
                default_groups = json.loads(request.form.get("default_groups_remove"))
            except ValueError:
                return "Invalid JSON in default_groups_remove", 400
            rr = removeDefaultGroups(default_groups,dg)
            if not rr.ok:
                return "Error: removeDefaultGroups: "+rr.etxt, 400
        if "overwrite_groups_remove" in request.form:
            #Remove overwrite_groups from displayGroup
            try:
                overwrite_groups = json.loads(request.form.get("overwrite_groups_remove"))
            except ValueError:
                return "Invalid JSON in overwrite_groups_remove", 400
            rr = removeOverwriteGroups(overwrite_groups,dg)
            if not rr.ok:
                return "Error: removeOverwriteGroups: "+rr.etxt, 400
        if "displayConfigs_remove" in request.form:
            #Remove displayConfigs (and Display) from displayGroup
            try:
                displayConfigs = json.loads(request.form.get("displayConfigs_remove"))
            except ValueError:
                return "Invalid JSON in displayConfigs", 400
            rr = removeDisplayConfigs(displayConfigs,dg)
            if not rr.ok:
                return "Error: removeDisplayConfigs: "+rr.etxt, 400

        # 2) Modify displayGroup links
        if "displayConfigs_modify" in request.form:
            #modify displayConfigs of displayGroup's Display
            try:
                displayConfigs = json.loads(request.form.get("displayConfigs_modify"))
            except ValueError:
                return "Invalid JSON in displayConfigs", 400
            rr = modifyDisplayConfigs(displayConfigs,dg)
            if not rr.ok:
                return "Error: modifyDisplayConfigs: "+rr.etxt, 400

        # 3) Add displayGroup to various links
        if "default_groups_add" in request.form:
            #Add default_groups to displayGroup
            try:
                default_groups = json.loads(request.form.get("default_groups_add"))
            except ValueError:
                return "Invalid JSON in default_groups_add", 400
            rr = addDefaultGroups(default_groups,dg)
            if not rr.ok:
                return "Error: addDefaultGroups: "+rr.etxt, 400
        if "overwrite_groups_add" in request.form:
            #Add overwrite_groups to displayGroup
            try:
                overwrite_groups = json.loads(request.form.get("overwrite_groups_add"))
            except ValueError:
                return "Invalid JSON in overwrite_groups_add", 400
            rr = addOverwriteGroups(overwrite_groups,dg)
            if not rr.ok:
                return "Error: addOverwriteGroups: "+rr.etxt, 400
        if "displayConfigs_add" in request.form:
            #Add displayConfigs (and Display) to displayGroup
            try:
                displayConfigs = json.loads(request.form.get("displayConfigs_add"))
            except ValueError:
                return "Invalid JSON in displayConfigs_add", 400
            rr = addDisplayConfigs(displayConfigs,dg)
            if not rr.ok:
                return "Error: addDisplayConfigs: "+rr.etxt, 400
        db.session.commit()
        return jsonify({"status": "Done"}), 201

    elif request.method == "GET":
        if dg.is_default:
            if dg.is_default == 2:
                deduplication = False
            else:
                deduplication = True
            result = {
                "name": dg.name,
                "is_default": True,
                "deduplication": deduplication,
                "replication_of":[],
                "replicates_into":[],
                "overwritten_by":[],
                "default_of":[],
                "regionLink":[],
                "districtLink":[],
                "displayLink":[],
            }
            for r in dg.displayLink:
                result["displayLink"].append({
                    "display_id": r.display_id,
                    "configuration": r.configuration
                })
            for r in dg.replication_of:
                result["replication_of"].append(r.id)
            for r in dg.replicats_into:
                result["replicats_into"].append(r.id)
            for r in dg.default_of:
                result["default_of"].append(r.id)
            for r in dg.overwritten_by:
                result["overwritten_by"].append(r.id)
            for r in dg.regionLink:
                if r.source:
                    source = {"id": r.source.id,"text": r.source.text}
                else:
                    source = {}
                result["regionLink"].append({
                    "region_id": r.region_id,
                    "region_name": r.region.name,
                    "autolinked": r.autolinked,
                    "source": source,
                    "is_deleted": r.is_deleted,
                })
            for r in dg.districtLink:
                if r.source:
                    source = {"id": r.source.id,"text": r.source.text}
                else:
                    source = {}
                result["regionLink"].append({
                    "region_id": r.region_id,
                    "district_name": r.region.name,
                    "autolinked": r.autolinked,
                    "source": source,
                    "is_deleted": r.is_deleted,
                })
            return jsonify(result), 200
        else:
            
            result = {
                "name": dg.name,
                "is_default": False,
                "replication_of":[],
                "replicates_into":[],
                "overwritten_by":[],
                "overwrites":[],
                "default":[],
                "regions":[],
                "districts":[],
                "displayLink":[],
            }
            for r in dg.displayLink:
                result["displayLink"].append({
                    "display_id": r.display_id,
                    "configuration": r.configuration
                })
            for r in dg.replication_of:
                result["replication_of"].append(r.id)
            for r in dg.replicats_into:
                result["replicats_into"].append(r.id)
            for r in dg.default:
                appendend = {
                    "id": r.id,
                    "regions": [],
                    "districts": []
                }
                for r2 in r.regionLink:
                    appendend["regions"].append({"id":r2.region_id,"is_deleted":r2.is_deleted})
                for r2 in r.districtLink:
                    appendend["regions"].append({"id":r2.district_id,"is_deleted":r2.is_deleted})
                result["default"].append(appendend)
            for r in dg.overwrites:
                result["overwrites"].append(r.id)
            for r in dg.overwritten_by:
                result["overwritten_by"].append(r.id)

            return jsonify(result), 200
    elif request.method == "DELETE":
        if dg.is_default:
            return "group_id not allowed: Group is Default-Group (Measure)", 403
        for dl in dg.displayLink:
            db.session.delete(dl)
        db.session.delete(dg)
        db.session.commit()
        return "Deleted", 200

@api.route("/edit/groups", methods=["POST","GET"])
@jwt_required
def createGroup():
# Zum Erstellen neuer Gruppen
    if request.method == "POST":
        #INPUTS:
        #   name
        #   replicats_id (INT) (only one, no array!) (highly not recommended to use)
        #   default_groups
        #   overwrite_groups
        #   displayConfigs
        if "name" in request.form:
            name = request.form.get("name")
        else:
            name = None

        # Create displayGroup
        dg = displayGroup(name=name)
        db.session.add(dg)
        db.session.flush()
        if "replicats_id" in request.form:
            rp = displayGroup.query.get(request.form.get("replicats_id"))
            if rp == None:
                # Check if replicats_id is valid
                return "Invalid replicates_id", 400
            dg.replication_of.append(rp) #TODO: Test this

        # Add displayGroup to various links
        if "default_groups" in request.form:
            #Add default_groups to displayGroup
            try:
                default_groups = json.loads(request.form.get("default_groups"))
            except ValueError:
                return "Invalid JSON in default_groups", 400
            rr = addDefaultGroups(default_groups,dg)
            if not rr.ok:
                return "Error: addDefaultGroups: "+rr.etxt, 400
        
        if "overwrite_groups" in request.form:
            #Add overwrite_groups to displayGroup
            try:
                overwrite_groups = json.loads(request.form.get("overwrite_groups"))
            except ValueError:
                return "Invalid JSON in overwrite_groups", 400
            rr = addOverwriteGroups(overwrite_groups,dg)
            if not rr.ok:
                return "Error: addOverwriteGroups: "+rr.etxt, 400
        
        if "displayConfigs" in request.form:
            #Add displayConfigs (and Display) to displayGroup
            try:
                displayConfigs = json.loads(request.form.get("displayConfigs"))
            except ValueError:
                return "Invalid JSON in displayConfigs", 400
            rr = addDisplayConfigs(displayConfigs,dg)
            if not rr.ok:
                return "Error: addDisplayConfigs: "+rr.etxt, 400
        db.session.commit()
        
        return jsonify({"status": "Done", "displayGroup_id": dg.id}), 201
    elif request.method == "GET":
        dgs = displayGroup.query.filter(displayGroup.is_default == 0).all()
        result = []
        for dg in dgs:
            res = {
                "id": dg.id,
                "name": dg.name,
                "replication_of":[],
                "overwrites":[],
                "displayLink":[],
                "defaults":[],
            }
            for r in dg.displayLink:
                res["displayLink"].append({
                    "display_id": r.display_id,
                    "configuration": r.configuration
                })
            for r in dg.replication_of:
                res["replication_of"].append(r.id)
            for r in dg.overwrites:
                res["overwrites"].append(r.id)
            for r in dg.default:
                res["defaults"].append(r.id)
            result.append(res)
        return jsonify(result), 200
