#!/usr/bin/env python3

# Corona-Info-App
# Landkreise
# © 2020 Tobias Höpp und Johannes Kreutz.

# Include dependencies
from main import db

#Association_Tables

#districtHasMeasures = db.Table('districtHasMeasures', db.Column('district_id', db.Integer, db.ForeignKey('districts.id')), db.Column('measures_id', db.Integer, db.ForeignKey('measures.id')))

# Class definition

# Links

class links(db.Model):
    __tablename__ = "links"
    id = db.Column(db.Integer, primary_key=True)
    href = db.Column(db.Text)
    title = db.Column(db.Text)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'))
    district = db.relationship("districts")
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'))
    source = db.relationship("sources") # TODO: Use N:M for Link deduplication and add this to the n:m-Table
    def __init__(self, title, href, district_id=None, source_id=None):
        self.title = title
        self.href = href
        self.district_id = district_id
        self.source_id = source_id
    
    

#Landkreise
class districts(db.Model):
    __tablename__ = "districts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    name_de = db.Column(db.String(100))
    incidence = db.Column(db.Integer)
    color = db.Column(db.String(10))
    #links = db.Column(db.JSON)
    geometry = db.Column(db.JSON)
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))
    category = db.Column(db.String(20))
    deactivate_region = db.Column(db.Boolean()) 
    lastModified = db.Column(db.String(40))
    mainLink = db.Column(db.Text)
    requestCounter = db.Column(db.BigInteger)
    # Relationships
    region = db.relationship("regions")
    links = db.relationship("links")
    groupLink = db.relationship("districtHasGroup")
    devices = db.relationship("devices", secondary="deviceHasDistrict", back_populates="districts")
    def __init__(self, id, name, incidence, color, geometry, category):
        self.id = id
        self.name = name
        self.incidence = incidence
        self.color = color
        self.geometry = geometry
        self.category = category
        self.name_de = name
        self.deactivate_region = False
        self.requestCounter = 0
        di = districts.query.filter(districts.name == name).all()
        # Kreisfreie Städte und Landkreise unterscheiden
        for d in di:
            # change existing name_de
            if d.name_de == name:
                if d.category == "Landkreis":
                    d.name_de += " (Kreis)"
                elif d.category == "Kreisfreie Stadt":
                    d.name_de += " (Stadt)"
                else:
                    d.name_de += " ("+d.category+")"
        if di:
            #set new name_de
            if category == "Landkreis":
                self.name_de += " (Kreis)"
            elif category == "Kreisfreie Stadt":
                self.name_de += " (Stadt)"
            else:
                self.name_de += " ("+category+")"
#Bundesländer
class regions(db.Model):
    __tablename__ = "regions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    districts = db.relationship("districts")
    groupLink = db.relationship("regionHasGroup")
    def __init__(self, name):
        self.name = name
#Bundesland erstellen oder id erhalten, wenn existiert.
def createRegionIfNotExists(name):
    r = regions.query.filter(regions.name == name).first()
    if not r:
        r = regions(name)
        db.session.add(r)
        db.session.flush()
    return r
def updateDistrictIncidence(district_id, incidence, color):
    d = districts.query.get(district_id)
    d.incidence = incidence
    d.color = color
    db.session.flush()
    return d
def addMeasure(district_id, measure):
    d = districts.query.get(district_id)
    d.measures.append(measure)
    db.session.add(d)
    db.session.flush()
    return d