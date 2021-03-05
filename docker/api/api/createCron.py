# Include utilities
import json
# Include db connection
from main import db
import os
# Include models
from models.cron import cron, CreateCron
from models.districts import addCron

#Erzeugung von Cron-Jobs
f = open("cron_jobs.json", "r")
cron_jobs = json.loads(f.read())
f.close()
for job in cron_jobs:
    
    if "commands" not in job or job["commands"] == None:
        job["commands"] = {}
    c = CreateCron(job["type"], job["url"], commands=job["commands"])
    if "district_id" in job:
        addCron(job["district_id"], c)
    
    ### The following lines are for debug and testing only. Remove them in Production! #TODO
    if job["type"] == 1:
        # Check the complete document for changes (Debug only!)
        cmd = job["commands"]["search"]
        commands = {}
        while True:
            if cmd["type"] == "remove_attributes":
                commands = {
                    "search": {
                        "type":"remove_attributes",
                        "to_remove": cmd["to_remove"]
                    }
                }
                break
            if "next" in cmd:
                cmd = cmd["next"]
            else:
                break
        c = CreateCron(job["type"], job["url"], commands=commands)
        #if "district_id" in job:
            #addCron(job["district_id"], c)
print("Führe Cronjobs initial aus.")
os.system("/usr/bin/python3 /home/tobias/Corona-Info/api/cron.py")
print("Setze alles als gelesen.")
for job in cron.query.all():
    job.referenceHtml_lastRead = job.referenceHtml_lastCron
    job.unread_change = False
db.session.commit()