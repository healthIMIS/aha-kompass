#!/usr/bin/env python3

# Corona-Info-App
# 
# © 2020 Tobias Höpp

# Include dependencies

from flask import request, jsonify

# Include modules
from main import api, jwt
from flask_jwt_extended import jwt_required
from utils.measure_utils import deleteMeasure, modifyMeasure, createMeasure, getMeasures, getMeasure
from models.districts import districts, regions

# Endpoints for measures
# Districts
@api.route("/edit/measures/district/<district_id>", methods=["PUT", "GET"]) #TODO: Use POST instead (?)
@jwt_required
def createMeasureForDistrict(district_id):
# Zum Erstellen der Default-Groups und verknüpfen mit Landkreis (Beinhaltet deduplizierung)
    if not districts.query.get(district_id):
        return "Not found", 404
    if request.method == "PUT":
        #INPUTS:
        #   source (highly recommended)
        #   display_id*
        #   configuration* (JSON)
        #   replicats_id (highly not recommended to use) #TODO: Remove?
        #   no_dedup (true or false) [Wenn false, werden keine automatischen gruppen gesucht]
        
        # Unify Form and JSON-Input
        if request.json:
            inputs = request.json
        else:
            inputs = request.form.to_dict()
        return createMeasure(inputs, district_id=district_id)
    elif request.method == "GET":
        return getMeasures(district_id=district_id)

@api.route("/edit/measures/district/<district_id>/<group_id>", methods=["DELETE", "PUT", "GET"])
@jwt_required
def editMeasureFromDistrict(district_id, group_id):
# Zum Bearbeiten=Löschen und neu erstellen / Löschen =Trennen der Default-Groups
    if request.method == "DELETE":
        #INPUTS:
        # remove: boolean ('true' / 'false')
        # undo: boolean ('true' / 'false')
        #Measure von Kreis löschen
        if request.json:
            inputs = request.json
        else:
            inputs = request.form.to_dict()
        return deleteMeasure(inputs, group_id,district_id=district_id)
    elif request.method == "PUT":
        #Measure von Kreis bearbeiten = löschen und neu erstellen.
        #INPUTS:
        #   source (highly recommended)
        #   display_id
        #   configuration (JSON)
        #   no_dedup (true or false) [Wenn false, werden keine automatischen gruppen gesucht]
        if request.json:
            inputs = request.json
        else:
            inputs = request.form.to_dict()
        return modifyMeasure(inputs, group_id,district_id=district_id)
    elif request.method == "GET":
        return getMeasure(group_id,district_id=district_id)

# Regions #TODO: Test this!
@api.route("/edit/measures/region/<region_id>", methods=["PUT", "GET"]) #TODO: Use POST instead (?)
@jwt_required
def createMeasureForRegion(region_id):
# Zum Erstellen der Default-Groups und verknüpfen mit Landkreis (Beinhaltet deduplizierung)
    if not regions.query.get(region_id):
        return "Not found", 404
    if request.method == "PUT":
        #INPUTS:
        #   source (highly recommended)
        #   display_id*
        #   configuration* (JSON)
        #   replicats_id (highly not recommended to use) #TODO: Remove?
        #   no_dedup (true or false) [Wenn false, werden keine automatischen gruppen gesucht]
        
        if request.json:
            inputs = request.json
        else:
            inputs = request.form.to_dict()
        return createMeasure(inputs, region_id=region_id)
    elif request.method == "GET":
        return getMeasures(region_id=region_id)

@api.route("/edit/measures/region/<region_id>/<group_id>", methods=["DELETE", "PUT", "GET"])
@jwt_required
def editMeasureFromRegion(region_id, group_id):
# Zum Bearbeiten=Löschen und neu erstellen / Löschen =Trennen der Default-Groups
    if request.method == "DELETE":
        #INPUTS:
        # remove: boolean ('true' / 'false')
        # undo: boolean ('true' / 'false')
        #Measure von Kreis löschen
        if request.json:
            inputs = request.json
        else:
            inputs = request.form.to_dict()
        return deleteMeasure(inputs, group_id,region_id=region_id)
    elif request.method == "PUT":
        #Measure von Kreis bearbeiten = löschen und neu erstellen.
        #INPUTS:
        #   source (highly recommended)
        #   display_id
        #   configuration (JSON)
        #   no_dedup (true or false) [Wenn false, werden keine automatischen gruppen gesucht]
        if request.json:
            inputs = request.json
        else:
            inputs = request.form.to_dict()
        return modifyMeasure(inputs, group_id,region_id=region_id)
    elif request.method == "GET":
        return getMeasure(group_id,region_id=region_id)