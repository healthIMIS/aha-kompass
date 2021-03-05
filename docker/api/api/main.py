#!/usr/bin/env python3

# Corona-Info-App
# Main API server
# © 2020 Tobias Höpp und Johannes Kreutz.

# Include dependencies
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os

# Determine if we are running in production or development setup
production = True
if "PRODUCTION" in os.environ and os.environ["PRODUCTION"] == "true":
    print("Running in production setup.")
else:
    production = False
    print("Running in development setup.")

# Start flask instance
api = Flask(__name__)

if production:
    api.config['SQLALCHEMY_DATABASE_URI'] = "mysql://" + os.environ["MYSQL_USER"] + ":" + os.environ["MYSQL_PASSWORD"] + "@" + os.environ["MYSQL_HOST"] + "/" + os.environ["MYSQL_DATABASE"]
else:
    api.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(api)
if production:
    api.config['JWT_SECRET_KEY'] = os.environ["FLASK_SECRET_KEY"]
else:
    api.config['JWT_SECRET_KEY'] = "CoWhereIsSoSuperDuperSecretThatNoOneKnowsOrdoestheNSA?!"
api.config['JWT_BLACKLIST_ENABLED'] = True
api.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
api.config['JWT_TOKEN_LOCATION'] = ['headers','cookies']
#api.config['JWT_ACCESS_COOKIE_PATH'] = '/api/edit'
#api.config['JWT_REFRESH_COOKIE_PATH'] = '/api/auth/refresh'

api.config['JWT_COOKIE_CSRF_PROTECT'] = False #TODO: reenable this for PRODUCTION
#https://flask-jwt-extended.readthedocs.io/en/stable/options/
#http://www.redotheweb.com/2015/11/09/api-security.html
api.config['JWT_COOKIE_SECURE'] = False #TODO: reenable this for PRODUCTION
jwt = JWTManager(api)
# EASTER EGG
@api.route("/cow-here", methods=["GET"])
def cow():
    return "Muuuuuuuuuu", 418

if not production:
    @api.after_request
    def add_header(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

# Add other endpoints
from endpoints.measures import *
from endpoints.geo import *
from endpoints.edit_measures import *
from endpoints.edit_displays import *
from endpoints.edit_categories import *
from endpoints.edit_groups import *
from endpoints.edit_districts import *
from endpoints.login import *
from endpoints.flexstringpreview import *

# Initialisation
from update_data import *

# Create development server
if __name__ == "__main__":
    api.run(host="0.0.0.0", debug=True, port=8800, threaded=True)
