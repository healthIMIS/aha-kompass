#!/usr/bin/env python3

# Corona-Info-App
# Helpers for Measure Updates
# © 2020 Tobias Höpp

# Include db connection
from main import db

# Include models
from models.measures import regionHasGroup, display, createSource, districtHasGroup
from utils.measure_utils import createDefaultGroup


def getOrmakeCategory(title, is_OFP=False, weight=0, force=False):
    d = display.query.filter(display.title_de == title).first()
        # Prüfen, ob eine gleichnamige Kategorie schon existiert (Ausschlaggebend ist IMMER der Name in deutscher Sprache.)
    if not d:
        d = display(title)
        d.is_OFP = is_OFP
        d.weight = weight
        db.session.add(d)
        db.session.flush()
    if force:
        d.is_OFP = is_OFP
        d.weight = weight
    return d
# Definitions
def makeMeasure(text, region_id=None, district_id=None, display_id=None, title=None, source="", isOFP=None, subtitle=None):
    if district_id != None and region_id == None:
        is_district = True
    elif district_id == None and region_id != None:
        is_district = False
    else:
        quit("Fataler Fehler beim Aufruf von makeMeasure")

    if display_id == None:
        if title == None:
            raise ValueError("Neither display_id nor title given")
        d = getOrmakeCategory(title)
            # Entsprechende Kategorie anlegen
    else:
        d = display.query.get(display_id)
    if isOFP != None: #TODO: Solve this more effectively!
        d.is_OFP = isOFP
    rr = createDefaultGroup(d.id,text,subtitle=subtitle)
    if not rr.ok:
        raise Exception("Error: createDefaultGroup: "+rr.etxt)
    g = rr.val

    if not is_district:
        dhg = regionHasGroup.query.filter(regionHasGroup.region_id == region_id, regionHasGroup.displayGroup_id == g.id).first()
        if not dhg:
            # Check if link between region and Group already exists
            dhg = regionHasGroup(region_id, g.id)
            db.session.add(dhg)
            db.session.flush()
                # Create new Link
    else:
        dhg = districtHasGroup.query.filter(districtHasGroup.district_id == district_id, districtHasGroup.displayGroup_id == g.id).first()
        if not dhg:
            # Check if link between region and Group already exists
            dhg = districtHasGroup(district_id, g.id)
            db.session.add(dhg)
            db.session.flush()
                # Create new Link
    dhg.source_id = createSource(source).id
    dhg.autolinked = True
    dhg.is_deleted = False
    return g
