#!/usr/bin/env python3

# Corona-Info-App
# Measures
# © 2020 Tobias Höpp und Johannes Kreutz.

# Include dependencies
import enum
from main import db
import json

class sources(db.Model):
#Datenquellen für Maßnahmen
    __tablename__ = "sources"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    def __init__(self, text):
        self.text = text

class regionHasGroup(db.Model):
#Verknüpft Gruppen und regionen miteinander
    __tablename__ = "regionHasGroup"
    region = db.relationship("regions")
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), primary_key=True)
    displayGroup = db.relationship("displayGroup")
    displayGroup_id = db.Column(db.Integer, db.ForeignKey('displayGroup.id'), primary_key=True)
    autolinked = db.Column(db.Boolean)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'))
    source = db.relationship("sources")
    is_deleted = db.Column(db.Boolean)
        #Als gelöscht markieren, ohne entgültig zu löschen um besser arbeiten zu können.
    def __init__(self, region_id, displayGroup_id, autolinked=False, source_id=None):
        self.region_id = region_id
        self.displayGroup_id = displayGroup_id
        self.autolinked = autolinked
        self.source_id = source_id
        self.is_deleted = False
class districtHasGroup(db.Model): #Ehemals BaseDataHasDistrict
    __tablename__ = "districtHasGroup"
    district = db.relationship("districts")
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), primary_key=True)
    displayGroup = db.relationship("displayGroup")
    displayGroup_id = db.Column(db.Integer, db.ForeignKey('displayGroup.id'), primary_key=True)
    autolinked = db.Column(db.Boolean)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'))
    source = db.relationship("sources")
    is_deleted = db.Column(db.Boolean)
        #Als gelöscht markieren, ohne entgültig zu löschen um besser arbeiten zu können.
    def __init__(self, district_id, displayGroup_id, autolinked=False, source_id=None):
        self.district_id = district_id
        self.displayGroup_id = displayGroup_id
        self.autolinked = autolinked
        self.source_id = source_id
        self.is_deleted = False

class categories(db.Model):
#Kategorien für Maßnahmen und Anzeigen
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)
        #Deutscher Name
    name_english = db.Column(db.Text)
    display = db.relationship("display")
    def __init__(self, name, name_english=None):
        self.name = name
        self.name_english = name_english

class display(db.Model):
# Anzeigen: Definieren mittels ihrer Konfiguration, wie eine DisplayGroup angezeigt wird. 
    __tablename__ = "display"

    # Daten
    id = db.Column(db.Integer, primary_key=True)
    flexstring_german = db.Column(db.Text)
    flexstring_english = db.Column(db.Text)
    subtitle_german = db.Column(db.Text)
    subtitle_english = db.Column(db.Text)
    name = db.Column(db.Text)
        # Name of display. It is only for internal use and not displayed for the end-user
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_default = db.Column(db.Boolean())
        # Handelt es ich um das Default-Display einer Kategorie? Dieses zeigt die Konfiguration direkt als Freitext an. Text und Untertitel sind nicht zugelassen. 
    is_deprecated = db.Column(db.Boolean())
        # Handelt es sich um ein Display, das nicht mehr verwendet werden soll?
    deprecated_by_id = db.Column(db.Integer, db.ForeignKey('display.id'))
    is_OFP = db.Column(db.Boolean()) 
        # Wird dieses Display auf der ersten Seite angezeigt?
    varlist = db.Column(db.JSON)
        # Liste der Variablen
    is_mergable = db.Column(db.Boolean())
        # Kann dieses display gemerged werden (hängt von varlist ab)
    weight = db.Column(db.Integer)
        # Determines how far up top an item is in list
    # Relationships
    category = db.relationship("categories")
    groupLink = db.relationship("displayGroupHasDisplay")
    #deprecated_by = db.relationship("display")
    
    # Constructor
    def __init__(self, flexstring_german, subtitle_german, category_id=None, is_default=False, varlist={}):
        self.flexstring_german = flexstring_german
        self.subtitle_german = subtitle_german
        self.category_id = category_id
        self.is_default = is_default
        self.is_deprecated = False
        self.is_OFP = False
        self.is_Mergable = False
        self.weight = 0
        self.varlist = varlist

class displayGroup(db.Model):
# Displaygruppen stellen als Default-Gruppen (is_default = 1 oder 2) Maßnahmen da oder gruppieren sonst solche
    __tablename__ = "displayGroup"
    
    # Data
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    is_default = db.Column(db.Integer)
        # Handelt es sich um eine default-gruppe? = Direkte Maßnahme eines Landkreises/Landes und nicht eine Zusammenfassung solcher 
        # (default_groups sind mit genau einer Anzeige+ Config verbunden und dürfen nicht geändert werden.)
        # NUR defaultgroups können mit einem district / einer region verknüpft sein!
        # 0: Nein, 1: Ja, 2: Ja - keine Deduplizierung anwenden!
    # Relationships
    replicats_into = db.relationship("displayGroup", secondary="displayGroupReplicates", back_populates="replicats_into", primaryjoin="displayGroupReplicates.c.replicats_of_id==displayGroup.id", secondaryjoin="displayGroupReplicates.c.displayGroup_id==displayGroup.id")
    replication_of = db.relationship("displayGroup", secondary="displayGroupReplicates", back_populates="replication_of", primaryjoin="displayGroupReplicates.c.displayGroup_id==displayGroup.id", secondaryjoin="displayGroupReplicates.c.replicats_of_id==displayGroup.id")
        # Zuordnung zu Gruppe, durch dessen "änderung" diese entstanden ist bzw. die durch Änderung dieser Gruppe entstanden sind
        # Nur wirklich relevant für defaultGroups.
    default_of = db.relationship("displayGroup", secondary="displayGroupHasDefault", back_populates="default", primaryjoin="displayGroupHasDefault.c.default_id==displayGroup.id", secondaryjoin="displayGroupHasDefault.c.displayGroup_id==displayGroup.id")
    default = db.relationship("displayGroup", secondary="displayGroupHasDefault", back_populates="default_of", primaryjoin="displayGroupHasDefault.c.displayGroup_id==displayGroup.id", secondaryjoin="displayGroupHasDefault.c.default_id==displayGroup.id")
        # Zuordnung zur Default-Gruppe bzw. für Default-Gruppen zu den resultierenden Gruppen
    displayLink = db.relationship("displayGroupHasDisplay")
        # Zugehöriges Display
    overwrites = db.relationship("displayGroup", secondary="displayGroupOverwrites", back_populates="overwritten_by", primaryjoin="displayGroupOverwrites.c.displayGroup_id==displayGroup.id", secondaryjoin="displayGroupOverwrites.c.overwrite_id==displayGroup.id")
    overwritten_by = db.relationship("displayGroup", secondary="displayGroupOverwrites", back_populates="overwrites", primaryjoin="displayGroupOverwrites.c.overwrite_id==displayGroup.id", secondaryjoin="displayGroupOverwrites.c.displayGroup_id==displayGroup.id")
        # Gruppen, die diese überschreibt / diese überschreiben. Wird eine Gruppe von einer anderen Gruppe überschrieben, die ausgewählt wurde (anhand des Landkreises), wird diese NICHT angezeigt. 
        # Insbesondere sollten sich gruppen NIE gegenseitig / im Zirkel überschreiben. Eine Gruppe sollte eine andere also nur dann überschreiben, wenn diese strengere Maßnahmen darstellt. 
    regionLink = db.relationship("regionHasGroup")
    districtLink = db.relationship("districtHasGroup")
        # Zugehörige Verlinkungen der Districte (Landkreise) und Regionen (Länder). 
        # Nur relevant für defaultGruops. (diese können aber aufgrund von Änderungen detatched sein)

    #Constructor
    def __init__(self, name=None, is_default=0):
        self.name = name
        self.is_default = is_default

class displayGroupHasDisplay(db.Model):
# "Config-Tabelle"
# Zuordnung von Gruppen zu Displays und Konfiguration dieser
    __tablename__ = "displayGroupHasDisplay"
    
    # Data
    displayGroup_id = db.Column(db.Integer, db.ForeignKey('displayGroup.id'), primary_key=True)
    display_id = db.Column(db.Integer, db.ForeignKey('display.id'), primary_key=True)
        # Essential n:m
    configuration = db.Column(db.JSON())
        #Konfiguration der Anzeige bzw. des Displays

    # Relationships
    displayGroup = db.relationship("displayGroup")
    display = db.relationship("display")
        # Essential n:m
    
    #Constructor
    def __init__(self, displayGroup_id, display_id, configuration):
        self.displayGroup_id = displayGroup_id
        self.display_id = display_id
        self.configuration = configuration

def createSource(text):
    d = sources.query.filter(sources.text == text).first()
    if not d:
        d = sources(text)
        db.session.add(d)
        db.session.flush()
    return d