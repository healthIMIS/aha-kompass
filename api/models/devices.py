#!/usr/bin/env python3

# Corona-Info-App
# Landkreise
# © 2020 Tobias Höpp und Johannes Kreutz.

# Include dependencies
from main import db

class devices(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer,  primary_key=True)
    token = db.Column(db.Text, unique=True)
    provider = db.Column(db.Integer)
    # relationships
    districts = db.relationship("districts", secondary="deviceHasDistrict", back_populates="devices")
    def __init__(self, provider, token):
        self.provider = provider
        self.token = token
