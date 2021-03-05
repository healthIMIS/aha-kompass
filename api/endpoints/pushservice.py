# Include dependencies
from flask import request, jsonify
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import IntegrityError
# Include modules
from main import api, db
from models.devices import devices
from models.districts import districts
import json
# registrieren + lk hinzufügen, deregistrieren, landkreise hinzufügen, landkreise löschen

@api.route("/pushservice/<provider_id>/<token>", methods=["PUT", "GET", "POST", "DELETE"])
def pushservicefunction(provider_id,token):
    # Deactivate this endpoint
    return "Not found", 404

    
    if not provider_id.isnumeric() or int(provider_id) not in [1,2]:
        return "Not found", 404
    if request.json:
        inputs = request.json
    else:
        inputs = request.form.to_dict()
    if request.method == "PUT":
        if devices.query.filter(devices.token == token).first():
            return "Existing", 403
        d = devices(provider_id, token)
        db.session.add(d)

        if isinstance(inputs.get("dist_add"), str):
            try:
                dist_add = json.loads(inputs.get("dist_add"))
            except json.JSONDecodeError:
                return "invalid JSON delivered in dist_add", 400
        else:
            dist_add = inputs.get("dist_add")
        if isinstance(dist_add, list):
            for dist in dist_add:
                di = districts.query.get(dist)
                if not di:
                    return "DistrictID "+str(dist)+" not found", 400
                d.districts.append(di)
        try:
            db.session.commit()
        except IntegrityError:
            return "Existing", 403
        return "Success", 200
    else:
        try:
            d = devices.query.filter(devices.token == token).one()
        except NoResultFound:
            return "Not found", 404
        except MultipleResultsFound:
            return "Internal Server Error: Data integrety", 500
        if request.method == "GET":
            dists = []
            for dist in d.districts:
                dists.append(dist.id)
            return jsonify(districts=dists), 200
        elif request.method == "DELETE":
            db.session.delete(d)
            db.session.commit()
            return "Success", 200
        elif request.method == "POST":
            if isinstance(inputs.get("dist_add"), str):
                try:
                    dist_add = json.loads(inputs.get("dist_add"))
                except json.JSONDecodeError:
                    return "invalid JSON delivered in dist_add", 400
            else:
                dist_add = inputs.get("dist_add")
            if isinstance(dist_add, list):
                for dist in dist_add:
                    di = districts.query.get(dist)
                    if not di:
                        return "DistrictID "+str(dist)+" not found", 400
                    d.districts.append(di)
            if isinstance(inputs.get("dist_remove"), str):
                try:
                    dist_remove = json.loads(inputs.get("dist_remove"))
                except json.JSONDecodeError:
                    return "invalid JSON delivered in dist_remove", 400
            else:
                dist_remove = inputs.get("dist_remove")
            if isinstance(dist_remove, list):
                for dist in dist_remove:
                    di = districts.query.get(dist)
                    if not di:
                        return "DistrictID "+str(dist)+" not found", 400
                    try:
                        d.districts.remove(di)
                    except ValueError:
                        pass
            db.session.commit()
            return "Success", 200