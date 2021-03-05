#!/usr/bin/env python3

# Corona-Info-App
# 
# © 2020 Tobias Höpp

# Include dependencies

from flask import request, jsonify

# Include modules
from main import api, db, jwt
from flask_jwt_extended import jwt_required
from models.measures import display, categories

# Endpoints for Categories
@api.route("/edit/categories", methods=["PUT", "GET"])
@jwt_required
def createCategory():
    if request.method == "PUT":
        # Erstellt eine Neue Kategorie
        # Achtung: Nutze diesen Endpoint mit vorsicht, das Löschen von Kategorien ist sehr aufwändig! TODO: Sqlquery zum Löschen einer Kategorie schreiben.
        #INPUTS:
        # name* (string) [DE]
        # name_english

        # Check for required values
        if "name" not in request.form:
            return "Error: Required values missing", 400
            
        c = categories.query.filter(categories.name == request.form.get("name")).first()
            # Prüfen, ob eine gleichnamige Kategorie schon existiert (Ausschlaggebend ist IMMER der Name in deutscher Sprache.)
        if not c:
            c = categories(request.form.get("name"), name_english=request.form.get("name_english"))
            db.session.add(c)
            db.session.flush()
                # Erzeuge neue Kategorie
            d = display("$_text_",None, category_id=c.id, is_default=True, varlist={"text":{"type":"str"}}) 
            db.session.add(d)
                # Erzeuge Default-Display für die neue Kategorie
            db.session.commit()
            return jsonify({"status": "Done", "category_id": c.id, "defaultDisplay_id": d.id}), 201
        else:
            return jsonify({"status": "Error", "Error":"Name already exists", "category_id": c.id}), 403
    elif request.method == "GET":
        #Listet alle categories auf
        cs = categories.query.all()
        result = []
        for c in cs:
            result.append({
                "id": c.id,
                "name": c.name,
                #"name_english": c.name_english
            })
        return jsonify(result), 200

@api.route("/edit/categories/<category_id>", methods=["PUT", "GET"])
@jwt_required
def modifyCategory(category_id):
    c = categories.query.get(category_id)
    if not c:
        return "Not found", 404
    if request.method == "PUT":
        # Kategorie bearbeiten
        #INPUTS:
        # name (string) [DE] (not recommended to use)
        # name_english 
        if "name" in request.form:
            c.name = request.form.get("name")
        if "name_english" in request.form:
            c.name_english = request.form.get("name_english")
        db.session.commit()
        return jsonify({"status": "Done"}), 200
    elif request.method == "GET":
        #List category-Details
        #Get default display of Category
        d = display.query.filter(display.is_default == True, display.category_id == c.id).first()
        if not d:
            return "Internal server error: Integrety error: category_id '"+str(c.id)+"' has no default display", 500
        result = {
            "id": c.id,
            "name": c.name,
            "name_english": c.name_english,
            "defaultDisplay_id": d.id
        }
        return jsonify(result), 200