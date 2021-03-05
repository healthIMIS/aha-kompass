#!/usr/bin/env python3

# Corona-Info-App
# Geo-Endpoint
# © 2020 Tobias Höpp

# Include dependencies
from flask import request, jsonify

# Include modules
from main import api
from models.districts import districts
from utils.coloring import colors
import json

# Endpoint definition
@api.route("/data/geo/lk", methods=["GET"])
def geo_lk():
    if request.method == "GET":
        d = districts.query.all()
        result = {"districts": [], "colors": colors, "sources": "Inzidenzwerte: Robert Koch-Institut (RKI), dl-de/by-2-0"}
        for di in d:
            appendend = {
                "id": di.id,
                "name": di.name_de,
                "incidence": di.incidence,
                "color": di.color,
            }
            if(request.args.get("geometry") == "true"):
                appendend["geometry"] = di.geometry
            result["districts"].append(appendend)
        return jsonify(result), 200