#!/usr/bin/env python3

# Corona-Info-App
# Update Measures from NINA-App
# © 2020 Tobias Höpp

# Include utilities
import json
import traceback
from sqlalchemy import and_
import bs4
from utils.markdownify import markdownify
# Include db connection
from main import db

# Include models
from models.districts import districts, links
from models.measures import sources, createSource, districtHasGroup, displayGroup
from models.association_tables import deviceHasDistrict

import requests
#For multithreading
import multiprocessing
import threading
from queue import Queue


# Include utils
from utils.measure_update_utils import getOrmakeCategory, makeMeasure
from utils.push_utils import push

def updateNINA(do_push=True):
    print("Lade Aktuelle Daten der NINA-App herunter")
    source_text = "NINA-API"
    so = sources.query.filter(sources.text == source_text).first()
    if not so: 
        so = createSource(source_text)
    #Neue verknüpfungen erstellen
    ds = districts.query.all()
    jobQueue = Queue()
    resultQueue = Queue()
    for d in ds:
        jobQueue.put({"region_id": d.region_id, "district_id": d.id, "source_id": so.id})
    #jobQueue.put({"region_id": 11, "district_id": 11012, "source_id": so.id})
    
    for i in range(multiprocessing.cpu_count()):
        worker = threading.Thread(target=NINArequestHelper, args=(jobQueue,resultQueue))
        worker.start()
    #NINArequestHelper(jobQueue,resultQueue)
    jobQueue.join()

    # Alte Verknüpfungen löschen
    #db.session.execute(districtHasGroup.__table__.update().where(and_(districtHasGroup.autolinked == True, districtHasGroup.source_id == so.id)).values(is_deleted=True))
    db.session.execute(districtHasGroup.__table__.delete().where(and_(districtHasGroup.autolinked == True, districtHasGroup.source_id == so.id)))
    db.session.execute(links.__table__.delete().where(links.source_id == so.id))
    db.session.flush()
    print("Schreibe Änderungen...")
    tourismusSourceID = createSource("https://tourismus-wegweiser.de/json").id
    for qi in resultQueue.queue:
        for measure in qi["measures"]:
            if measure["source"] in ["LAND", "BUND"]:
                #makeMeasure(measure["mkdown"], region_id=qi["region_id"], title=measure["title"], source=source_text, isOFP=True)
                # Maßnahmen werden für jeden District gespeichert, um den code zu vereinfachen.
                makeMeasure(measure["mkdown"], district_id=qi["district_id"], title=measure["title"], source=source_text, isOFP=True)
            elif measure["source"] == "KREIS":
                g = makeMeasure(measure["mkdown"], district_id=qi["district_id"], title=measure["title"], source=source_text, isOFP=True, subtitle="Kreisverordnung")
                # Bei Maßnahmen, die nur Kreisweit gelten, landesweite Tourismus-Wegweiser-Maßnahmen ersetzen.
                titles = []
                if measure["title"] == "Kontaktbestimmungen":
                    titles = ["Kontaktbeschränkungen"]
                elif measure["title"] == "Private Feiern":
                    titles = ["Private Hochzeits-, Geburtstags- oder sonstige Familienfeiern"]
                elif measure["title"] == "Öffentliche Veranstaltungen":
                    titles = ["Großveranstaltungen und Events (Kultur und Sport)", "Messen und Kongresse (öffentlich)"]
                elif measure["title"] == "Gaststätten":
                    titles = ["Restaurants, Cafés und Gaststätten (indoor)", "Biergärten und Außengastronomie", "Bars, Pubs und Kneipen", "Discotheken und Clubs"]
                elif measure["title"] == "Geschäfte":
                    titles = ["Einzelhandel"]
                if titles not in [[], None]:
                    values = {"region_id":qi["region_id"], "source_id": tourismusSourceID}
                    GroupCondition = "SELECT count(rhg.region_id) from regionHasGroup rhg where rhg.region_id=:region_id AND rhg.autolinked = 1 AND rhg.source_id=:source_id and rhg.is_deleted=0 AND rhg.displayGroup_id = dg.id"
                    TitleList = ""
                    # Workaround to use SQL-IN_Statement with prepared statements
                    for i in range(len(titles)):
                        TitleList += ":title"+str(i)+", "
                        values["title"+str(i)] = titles[i]
                    TitleList = TitleList[:-2]
                    TitleCondition = "SELECT count(dghd.display_id) from displayGroupHasDisplay dghd where dghd.displayGroup_id = dg.id and dghd.display_id in (SELECT d.id FROM display d WHERE d.title_de IN("+TitleList+"))"
                    ReplacementRequest = "SELECT dg.id FROM displayGroup dg WHERE dg.is_default = 1 AND ("+GroupCondition+") AND ("+TitleCondition+")"
                    rows = db.session.execute(ReplacementRequest, values)
                    for row in rows:
                        g.overwrites.append(displayGroup.query.get(row[0]))
            else:
                # Dieser Fall sollte garnicht erst eintreten...
                print("WARNING:", "Unknown NINA-Source occured", measure)      
                makeMeasure(measure["mkdown"], district_id=qi["district_id"], title=measure["title"], source=source_text, isOFP=True)
        for link in qi["links"]:
            l = links(link["title"], link["href"], qi["district_id"], so.id)
            db.session.add(l)
        # set last Modified
        if qi["lastModified"] != None:
            db.session.execute(districts.__table__.update().where(districts.id == qi["district_id"]).values(lastModified=qi["lastModified"]))
        # Prepare to send out push-Notifications
        #if qi["pushReasons"] != [] and do_push:
        #    push(qi["district_id"], qi["pushReasons"])
        #TODO: Do this in threads
    db.session.flush()

def NINArequestHelper(q, resultQueue):
    while not q.empty():
        job = q.get()
        rs = {"measures": [], "links": [], "lastModified": None, "district_id": job["district_id"], "region_id": job["region_id"], "pushReasons":[]}
        try:
            headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:77.0) Gecko/20190101 Firefox/77.0"}
            if len(str(job["district_id"])) == 4:
                url = "https://warnung.bund.de/api31/appdata/covid/covidrules/DE/0{:<011d}.json".format(job["district_id"])
            else:
                if 11001 <= job["district_id"] <= 11012:
                    url = "https://warnung.bund.de/api31/appdata/covid/covidrules/DE/110000000000.json"
                else:
                    url = "https://warnung.bund.de/api31/appdata/covid/covidrules/DE/{:<012d}.json".format(job["district_id"])
            r = requests.get(url, timeout=(5, 10), headers=headers)
            if r.status_code == 200:
                # Do lastModified:
                rs["lastModified"]=r.headers["last-modified"]
                result = r.json()
                for rule in result["rules"]:
                    text_de = markdownify(rule["text"])
                    # Ist diese Maßnahme neu? (Änderungen für Push-Benachrichtigungen feststellen)
                    checkUpdateRequest = "SELECT DISTINCT dg.id FROM displayGroup dg WHERE dg.is_default = 1 AND EXISTS(SELECT dhg.district_id from districtHasGroup dhg WHERE dhg.is_deleted = 0 AND dhg.autolinked = 1 AND dhg.displayGroup_id = dg.id AND dhg.source_id = :source_id AND dhg.district_id = :district_id) AND EXISTS (SELECT dghd.display_id from displayGroupHasDisplay dghd WHERE dghd.displayGroup_id = dg.id AND dghd.text_de = :text_de AND (SELECT d.title_de FROM display d WHERE d.id = dghd.display_id)= :title_de)"
                    rows = db.session.execute(checkUpdateRequest, {"source_id":job["source_id"],"district_id":job["district_id"],"text_de":text_de,"title_de":rule["caption"]}) # repr() seems not to be necessary
                    rf = rows.first()
                    if rf:
                        change = False
                    else:
                        change = True
                        rs["pushReasons"].append(rule["caption"])
                    rows.close()
                    rs["measures"].append({
                        "mkdown": text_de,
                        "title": rule["caption"],
                        "source": rule["source"],
                        "change": change,
                    })
                # Links ergänzen
                for regulation in result["regulations"]["sections"]:
                    rs["links"].append({
                        "title": "Zur "+result["regulations"]["sections"][regulation]["caption"],
                        "href": result["regulations"]["sections"][regulation]["url"]
                    })
                resultQueue.put(rs)

            else:
                print(job["district_id"], "konnte nicht geladen werden: StatusCode", r.status_code)
        except requests.exceptions.RequestException as e:
            print(job["district_id"], "konnte nicht geladen werden: RequestException", e)
        except ValueError:
            print(job["district_id"], "konnte nicht geladen werden: ValueError")
        except Exception as e:
            print (traceback.format_exc(), "\n", e, "\n", "Fehler-URL:", url)

        q.task_done()