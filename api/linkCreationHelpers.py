#!/usr/bin/env python3

# Corona-Info-App
# 
# © 2020 Tobias Höpp.

# Include utilities
import urllib
import json
from sqlalchemy import or_
import bs4
import visvalingamwyatt as vw
# Include db connection
from main import db, api

# Include models
from models.districts import districts, updateDistrictIncidence, createRegionIfNotExists
from models.measures import sources, regionHasGroup, display, createSource
from utils.measure_utils import createDefaultGroup

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import requests
#For multithreading
import multiprocessing
import threading
from queue import Queue

def part1():
    with open('landkreise.json') as f:
        data = json.load(f)
    result = {
        "ok" : [],
        "err" : []
    }
    for d in data:
        region_id = createRegionIfNotExists(d["Bundesland"]).id
        print(region_id)
        html_soup = bs4.BeautifulSoup(d["Regionale Einschränkungen"], 'html.parser')
        for l in html_soup.findAll('a'):
            category = None
            name = None
            if l.text[0:10] == "Landkreis ":
                category = "Landkreis"
                name = l.text[10:]
            elif l.text[-10:] == " Landkreis":
                category = "Landkreis"
                name = l.text[:-11]
            elif l.text[0:11] == "Stadtkreis ":
                category = "Stadtkreis"
                name = l.text[11:]
            elif l.text[0:17] == "Kreisfreie Stadt ":
                category = "Kreisfreie Stadt"
                name = l.text[17:]
            elif l.text[-17:] == " kreisfreie Stadt":
                category = "Kreisfreie Stadt"
                name = l.text[:-18]
            elif l.text[0:6] == "Stadt ":
                category = "Kreisfreie Stadt"
                name = l.text[6:]
            elif l.text[0:6] == "Kreis ":
                category = "Landkreis"
                name = l.text[6:]
            elif not "RKI" in l.text:
                name = l.text
            
            if name != None:
                try:
                    if category != None:
                        if category == "Landkreis":
                            d = districts.query.filter(districts.name.like("%{}%".format(name)), districts.region_id == region_id, or_(districts.category == "Landkreis", districts.category == "Kreis")).one()
                        else:    
                            d = districts.query.filter(districts.name.like("%{}%".format(name)), districts.region_id == region_id, districts.category == category).one()
                    else:
                        d = districts.query.filter(districts.name.like("%{}%".format(name)), districts.region_id == region_id).one()
                    result["ok"].append({"id": d.id, "link": l["href"], "comment": l.text})
                except NoResultFound:
                    result["err"].append({"id": None, "link": l["href"], "comment": l.text})
                except MultipleResultsFound:
                    result["err"].append({"id": None, "link": l["href"], "comment": l.text})

    with open('districtlinks.json', 'w') as json_file:
        json.dump(result, json_file)

def part2():
    with open('links.json') as f:
        data = json.load(f)
    
    abgedeckt = {}
    for d in data:
        abgedeckt[d["id"]] = d

    result = {
        "ok" : data,
        "missing" : []
    }

    for d in districts.query.all():
        if d.id not in abgedeckt:
            result["missing"].append({"id": d.id, "link": "", "comment": d.name_de})
            print(d.id)
    #with open('districtlinks2.json', 'w') as json_file:
     #   json.dump(result, json_file)


def part3():
    with open('links.json') as f:
        data = json.load(f)
    jobQueue = Queue()
    resultQueue = Queue()
    for d in data:
        jobQueue.put(d)
    for i in range(multiprocessing.cpu_count()):
        worker = threading.Thread(target=part3_helper, args=(jobQueue,resultQueue))
        worker.start()

    jobQueue.join()
    print("DONE")
    result = []
    for q_item in resultQueue.queue:
        result.append(q_item)
    with open('unsuccessfull.json', 'w') as json_file:
        json.dump(result, json_file)

def part3_helper(q, resultQueue):
    while not q.empty():
        job = q.get()
        try:
            headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:77.0) Gecko/20190101 Firefox/77.0"}
            r = requests.get(job["link"], timeout=(5, 10), headers=headers)
            if r.status_code != 200:
                res = job
                res["statusCode"] = r.status_code,
                print(res)
                resultQueue.put(res)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            res = job
            res["exception"] = str(e),
            print(res)
            resultQueue.put(res)

        q.task_done()

#part3()

import os
def tiles():
    from pathlib import Path
    jobQueue = Queue()
    files = list(Path("../app/src/static/tiles").rglob("*.png"))
    for f in files: 
        jobQueue.put(str(f))

    for i in range(multiprocessing.cpu_count()):
        worker = threading.Thread(target=tile_helper, args=(jobQueue,))
        worker.start()

    jobQueue.join()
    print("DONE")

def tile_helper(q):
    while not q.empty():
        job = q.get()
        try:
            os.system("convert "+job+" -quality 85 "+job[:-3]+"jpg")
            os.system("rm "+job)
        except:  # This is the correct syntax
            print("Something went wrong:", job)

        q.task_done()


tiles()