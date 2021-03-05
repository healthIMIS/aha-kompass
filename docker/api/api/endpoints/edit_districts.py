#!/usr/bin/env python3

# Corona-Info-App
# 
# © 2020 Tobias Höpp

# Include dependencies
from flask import request, jsonify

# Include modules
from main import api, db, jwt
from flask_jwt_extended import jwt_required
from models.districts import districts, regions
from models.cron import cron

#import utils
from utils.coloring import coloring
import json


# Endpoint definition
@api.route("/edit/district/<district_id>", methods=["GET", "POST"])
@jwt_required
def editDistrict(district_id):
    if request.method == "GET":
        d = districts.query.get(district_id)
        if(d == None):
            return "district_id not found", 404
        result = {
            "name": d.name,
            "incidence": d.incidence,
            "color": d.color,
            "links": json.loads(d.links),
            "region": d.region.name,
            "notes": d.notes
        }
        return jsonify(result), 200
    if request.method == "POST":
        d = districts.query.get(district_id)
        if(d == None):
            return "district_id not found", 404
        if request.form.get("name"):
            d.name = request.form.get("name")
        if request.form.get("incidence"):
            try:
                d.incidence = int(request.form.get("incidence"))
                d.color = coloring(int(request.form.get("incidence"))) # Automatically updates color
            except ValueError:
                return "ValueError: incidence is required to be a number", 400
        if request.form.get("color"):
            d.color = request.form.get("color")
        if request.form.get("links"):
            try:
                json.loads(request.form.get("links"))
            except ValueError as e:
                return "Invalid JSON in links", 400
            d.links = request.form.get("links")
        if request.form.get("notes"):
            d.notes = request.form.get("notes")
        db.session.commit()
        return "Success", 200

@api.route("/edit/district", methods=["GET"])
@jwt_required
def editListDist():
    if request.method == "GET":
        d = districts.query.all()
        result = []
        for di in d:
            appendend = {
                "id": di.id,
                "name": di.name,
                "name_de": di.name_de,
                "category": di.category,
                "incidence": di.incidence,
                "color": di.color,
                "region": {
                    "id": di.region_id,
                    "name": di.region.name
                }
            }
            if(request.args.get("geometry") == "true"):
                appendend["geometry"] = di.geometry
            result.append(appendend)
        return jsonify(result), 200

@api.route("/edit/region", methods=["GET"])
@jwt_required
def editListRegion():
    if request.method == "GET":
        d = regions.query.all()
        result = []
        for di in d:
            appendend = {
                "id": di.id,
                "name": di.name,
            }
            result.append(appendend)
        return jsonify(result), 200