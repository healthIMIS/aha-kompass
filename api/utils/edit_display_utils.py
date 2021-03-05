#!/usr/bin/env python3

# Corona-Info-App
# edit_display_utils
# © 2020 Tobias Höpp.

from utils.measure_utils import dR_
from models.measures import displayGroup, displayGroupHasDisplay, display
from main import db

# Utils for display

#TODO: group the following functions into one per add/remove/modify
def addDefaultGroups(groups, dg):
#Add default_groups to displayGroup
    #INPUT:
    # groups: Array von displayGroup-IDs
    # dg: displayGroup-Objekt

    if not isinstance(groups, list):
        #check if groups is actually an array:
        return dR_(0, "groups is not a list")
    for group in groups:
        d_g = displayGroup.query.get(group)
        if not d_g:
            return dR_(0, "Invalid ID in groups: '"+str(group)+"'") 
        if not d_g.is_default:
            # Check if the group is actually a default-group to prevent errors
            return dR_(0, "Invalid ID in groups: '"+str(group)+"' is not a default-group")
        dg.default.append(d_g)
    return dR_(1)

def removeDefaultGroups(groups, dg):
#Remove default_groups from displayGroup
# NOT allowed for default_groups!!! TODO
    #INPUT:
    # groups: Array von displayGroup-IDs
    # dg: displayGroup-Objekt

    if not isinstance(groups, list):
        #check if groups is actually an array:
        return dR_(0, "groups is not a list")
    for group in groups:
        d_g = displayGroup.query.get(group)
        if not d_g:
            return dR_(0, "Invalid ID in groups: '"+str(group)+"'") 
        #No check if the group to remove is actually a default-Group
        try:
            dg.default.remove(d_g)
        except ValueError:
            pass
    return dR_(1)

def addOverwriteGroups(groups, dg): 
# Add overwrite_groups to displayGroup
# NOT allowed for default_groups!!!       TODO
    if not isinstance(groups, list):
        return dR_(0, "groups is not a list")
    for group in groups:
        o_g = displayGroup.query.get(group)
        if not o_g:
            return dR_(0, "Invalid ID in groups: '"+str(group)+"'") 
        dg.overwrites.append(o_g) 
    return dR_(1) 

def removeOverwriteGroups(groups, dg): 
# Remove overwrite_groups from displayGroup 
# NOT allowed for default_groups!!!      TODO
    if not isinstance(groups, list):
        return dR_(0, "groups is not a list")
    for group in groups:
        o_g = displayGroup.query.get(group)
        if not o_g:
            return dR_(0, "Invalid ID in groups: '"+str(group)+"'") 
        try:
            dg.overwrites.remove(o_g) 
        except ValueError:
            pass
    return dR_(1) 
"""
def addDisplayConfigs(displayConfigs, dg):         
#Add displayConfigs (and Display) to displayGroup
# NOT allowed for default_groups!!!TODO
    if not isinstance(displayConfigs, list):
        return dR_(0, "displayConfigs is not a list")
    for displayConfig in displayConfigs:
        if not(isinstance(displayConfig, dict) and all(e in displayConfig for e in ("display_id", "configuration"))):
            return dR_(0, "Invalid JSON-Contents in displayConfig")
        d = display.query.get(displayConfig["display_id"])
        if not d:
            return dR_(0, "Invalid display_id in displayConfig: '"+str(displayConfig["display_id"])+"'") 
        if displayGroupHasDisplay.query.get({"displayGroup_id": dg.id, "display_id": displayConfig["display_id"]}) != None:
            return dR_(0, "Invalid display_id in displayConfig: This group is already connected to display_id '"+str(displayConfig["display_id"])+"'. Use Modify instead.") 
        
        # checking configuration to have all required parameters
        ok, err = validateConfig(displayConfig["configuration"],d.varlist)
        if not ok:
            return dR_(0,etxt="Invalid configuration for display '"+str(displayConfig["display_id"])+"': "+err) 
        dghd = displayGroupHasDisplay(dg.id, displayConfig["display_id"], displayConfig["configuration"])
        db.session.add(dghd)
    return dR_(1) 

def modifyDisplayConfigs(displayConfigs, dg):         
# modify displayConfigs of displayGroup's Display
# NOT allowed for default_groups!!!TODO
    if not isinstance(displayConfigs, list):
        return dR_(0, "displayConfigs is not a list")
    for displayConfig in displayConfigs:
        if not(isinstance(displayConfig, dict) and all(e in displayConfig for e in ("display_id", "configuration"))):
            return dR_(0, "Invalid JSON-Contents in displayConfig")

        dghd = displayGroupHasDisplay.query.get({"displayGroup_id": dg.id, "display_id": displayConfig["display_id"]})
        if dghd ==None:
            return dR_(0, "Invalid display_id in displayConfig: This group is not connected to display_id '"+str(displayConfig["display_id"])+"'") 
        ok, err = validateConfig(displayConfig["configuration"],dghd.display.varlist)
        if not ok:
            return dR_(0,etxt="Invalid configuration for display '"+str(displayConfig["display_id"])+"': "+err)
        dghd.configuration = displayConfig["configuration"]
    return dR_(1) 
"""
def removeDisplayConfigs(displayConfigs, dg):         
#Remove displayConfigs (and Display) from displayGroup
# NOT allowed for default_groups!!!TODO
    if not isinstance(displayConfigs, list):
        return dR_(0, "displayConfigs is not a list")
    for displayConfig in displayConfigs:
        if not(isinstance(displayConfig, dict) and "display_id" in displayConfig):
            return dR_(0, "Invalid JSON-Contents in displayConfig")
        #if display.query.get(displayConfig["display_id"]) == None:
        #    return dR_(0, "Invalid display_id in displayConfig: '"+str(displayConfig["display_id"])+"'") 
        dghd = displayGroupHasDisplay.query.get({"displayGroup_id": dg.id, "display_id": displayConfig["display_id"]})
        if dghd:
            db.session.delete(dghd)
    return dR_(1) 