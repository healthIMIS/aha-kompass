#!/usr/bin/env python3

# Corona-Info-App
# Cron-Jobs
# © 2020 Tobias Höpp und Johannes Kreutz.

# Include dependencies
from main import db
import enum
from datetime import datetime
import difflib
from bs4 import BeautifulSoup
from utils.cron_utils import runJob
from models.association_tables import districtHasCron

# Class definition
class cron(db.Model):
    __tablename__ = "cron"
    id = db.Column(db.Integer, primary_key=True)
    class types(enum.IntEnum):
        RSS_feeed = 0
        HTML = 1
    type = db.Column(db.Enum(types))
    districts = db.relationship("districts", secondary=districtHasCron, back_populates="cron")
    #district_id = db.Column(db.Integer, db.ForeignKey('districts.id'))
    #district = db.relationship("districts")
    url = db.Column(db.String(100))
    last_change_time = db.Column(db.DateTime)
    last_cron_time = db.Column(db.DateTime)
    unread_change = db.Column(db.Boolean)
    referenceHtml_lastCron = db.Column(db.Text)
    referenceHtml_lastRead = db.Column(db.Text)
    commands = db.Column(db.JSON)
    cron_error_log = db.Column(db.Text) 
    def __init__(self, type, url, commands={}):
        self.type = type
        self.url = url
        self.unread_change = False
        self.last_change_time = datetime.fromtimestamp(0)
        self.last_cron_time = datetime.fromtimestamp(0)
        self.commands = commands
        self.referenceHtml_lastCron = ""
        self.referenceHtml_lastRead = ""
    def run(self):
        res = runJob(self)
        if res == None:
            return False
        else:
            db.session.flush()
            return True
    def difference(self):
        return(list(difflib.Differ().compare(BeautifulSoup(self.referenceHtml_lastRead, 'html.parser').prettify().split("\n"),BeautifulSoup(self.referenceHtml_lastCron, 'html.parser').prettify().split("\n"))))
        #TODO: Test this method!
        #TODO: This method might not work because of different inclines
    def set_as_read(self):
        self.referenceHtml_lastRead = self.referenceHtml_lastCron
        self.unread_change = False
        #TODO: Test this method!
    def cron_error(self):
        if self.cron_error_log == None:
            return False
        else:
            return True
        #TODO: Test this method!
    def add_error_log(self, report):
        if self.cron_error_log == None:
            self.cron_error_log = report
        else:
            self.cron_error_log += "\n"+report
        db.session.flush()
def CreateCron(type, url, commands={}):
    c = cron(type, url, commands=commands)
    db.session.add(c)
    db.session.flush()
    return c

