# Simply output the statistics

#!/usr/bin/env python3

# Corona-Info-App
# measures endpoint
# © 2020 Tobias Höpp.

# Include dependencies
from flask import request, jsonify

# Include modules
from main import api, db
from models.districts import districts
import json

# Endpoint definition
@api.route("/data/statistics", methods=["GET"])
def giveMeStats():
    if request.json:
        inputs = request.json
    else:
        inputs = request.form.to_dict()
    if inputs.get("authToken") != "DerAHAKompassIstSuperCool1!2020IMIS": #TODO: Use proper authentification once there is some.
        return "NotAuthorized", 401
    if request.method == "GET":
        d = districts.query.all()
        result = {"districts":[],"sum":0}
        for di in d:
            appendend = {
                "id": di.id,
                "name": di.name_de,
                "count": di.requestCounter,
            }
            result["districts"].append(appendend)
            result["sum"]+=di.requestCounter
        return jsonify(result), 200