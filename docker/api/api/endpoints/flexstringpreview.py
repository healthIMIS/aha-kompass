#!/usr/bin/env python3

# Corona-Info-App
# Endpoint zum server-side-evaluating der Configuration für preview im cms
# © 2020 Tobias Höpp.

# Include dependencies
from flask import request, jsonify

# Include modules
from main import api, jwt
from flask_jwt_extended import jwt_required
from models.measures import display
from utils.flexstring import flexstringParse
import json

# Endpoint definition
@api.route("/edit/displays/<display_id>/preview", methods=["POST"])
@jwt_required
def flexstringpreview(display_id):
    if request.method == "POST":
        #INPUTS:
        # configuration (formData / JSON)
        if request.json:
            inputs = request.json
        else:
            inputs = request.form.to_dict()

        di = display.query.get(display_id)
        if not di:
            return "Not found", 404

        if not "configuration" in inputs:
            return jsonify({"status": "RequiredValueError", "value":"configuration"}), 400

        if not isinstance(inputs.get("configuration"), dict):
            try:
                config = json.loads(inputs.get("configuration"))
            except ValueError:
                return jsonify({"status": "ValueError", "value":"configuration", "error": "invalid JSON"}), 400
        else:
            config = inputs.get("configuration")
        
        languageString = di.flexstring_german
        ok, res, epos = flexstringParse(languageString, config)
        if not ok:
            return jsonify({"status": "ValueError", "value":"configuration", "error": "flexstringParseError for string '"+languageString+"' with configuration '"+str(config)+"': "+res+" at Position "+str(epos)}), 400              
        print(json.dumps(res))
        return jsonify({"text":res}), 200