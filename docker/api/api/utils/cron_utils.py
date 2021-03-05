#!/usr/bin/env python3

# Corona-Info-App
# Cron-Script for LK Marburg-Bidenkopf
# © 2020 Johannes Kreutz.

# Include utilities
import feedparser
from datetime import datetime
import time
from bs4 import BeautifulSoup, element as bs4element
import requests
import re
import difflib

#definitions
keywords =["corona", "covid", "sars", "virus", "verordnung", "allgemeinverfügung", "allgemeinverfuegung", "infektion", "quarant"] #only lower-case!!!
def spaceless_prettify(soup):
    r = []
    for s in soup.prettify().split("\n"):
        r.append(s.strip())
        #TODO: Care about all kinds of whitespaces!
    return r

# The following function is there to search for the right parts of the html document
def parse_search(html_soup, search, job):
    #find element
    while True:
        if search["type"] == "search":
            if search["category"] == "general":
                if "text" in search:
                    text = re.compile(search["text"])
                else:
                    text = None
                if "class" in search:
                    attrs={"class": re.compile(search["class"])}
                else:
                    attrs = {}
                html_soup = html_soup.find(re.compile(search["regex"]), text=text, attrs=attrs)
                if html_soup == None:
                    job.add_error_log(str(datetime.now())+" FATAL: No item found for tag "+search["regex"]+", text "+str(text)+" class: "+search["class"])
                    return None
            elif search["category"] == "multi":
                if "text" in search:
                    text = re.compile(search["text"])
                else:
                    text = None
                if "class" in search:
                    attrs={"class": re.compile(search["class"])}
                else:
                    attrs = {}
                res = ""
                soups = html_soup.find_all(re.compile(search["regex"]), text=text, attrs=attrs)
                if not soups:
                    job.add_error_log(str(datetime.now())+" FATAL: No item found for tag "+search["regex"]+", text "+str(text)+" class: "+search["class"])
                    return None
                for s in soups:
                    if "next" in search:
                        s = parse_search(s, search["next"], job)
                        if s == None:
                            #Job is not skipped to be able to still work with the rest of it
                            continue
                    res += str(s)
                return BeautifulSoup(res, 'html.parser')
            elif search["category"] == "text":
                tmp = html_soup.findAll(text=re.compile(search["regex"]))
                if len(tmp) == 0:
                    job.add_error_log(str(datetime.now())+" FATAL: No item found for text "+str(search["regex"]))
                    return None
                if len(tmp) > 1:
                    job.add_error_log(str(datetime.now())+" Warning: More than one item found for text "+str(search["regex"]))
                html_soup = tmp[0]
                #TODO: add option to only search for one
            elif search["category"] == "id":
                html_soup = html_soup.find(id=search["id"])
                if html_soup == None:
                    job.add_error_log(str(datetime.now())+" FATAL: No item found for id "+search["id"])
                    return None
            elif search["category"] == "class":
                tmp = html_soup.findAll(attrs={"class": re.compile(search["regex"])})
                if len(tmp) == 0:
                    job.add_error_log(str(datetime.now())+" FATAL: No item of class "+search["regex"]+" found.")
                    return None
                if len(tmp) > 1:
                    job.add_error_log(str(datetime.now())+" Warning: More than one item of class "+search["regex"]+" found.")
                html_soup = tmp[0]
                #TODO: add option to only search for one
        elif search["type"] == "get":
            if search["category"] == "parent":
                html_soup = html_soup.parent
        elif search["type"] == "remove_attributes":
            for attribute in search["to_remove"]:
                for tag in html_soup.descendants:
                    regex = re.compile(attribute)
                    to_remove = []
                    try:
                        for attr in tag.attrs:
                            if re.match(regex, attr):
                                to_remove.append(attr)
                        for attr in to_remove: 
                            del tag[attr]                         
                    except AttributeError:
                        pass
        elif search["type"] == "multiple":
                res = ""
                for se in search["array"]:
                    res += str(parse_search(html_soup, se, job))
                    #errors are not forwarded so that parts of the search can still be executed
                return BeautifulSoup(res, 'html.parser')
        if "next" not in search:
            return html_soup
        else:
            search = search["next"]

def runJob(job):
    if job.type == job.types.RSS_feeed:
        try:
            request = requests.get(job.url, timeout=5)
        except requests.Timeout:
            job.add_error_log(str(datetime.now())+" FATAL: connection timeout (more than 5s) "+job.url)
            return None
        except requests.exceptions.ConnectionError:
            job.add_error_log(str(datetime.now())+" FATAL: ConnectionError. Is your computer connected to the internet?")
            return None
        if request.status_code != 200:
            job.add_error_log(str(datetime.now())+" FATAL: connection response code "+str(request.status_code))
            return None
        try:
            feed = feedparser.parse(request.text)
        except e:
            job.add_error_log(str(datetime.now())+" FATAL: feed could not be parsed "+str(e))
            return None
        last_change_time = job.last_change_time.timetuple()
        newest =last_change_time
        for e in feed.entries:
            if e.published_parsed > newest:
                newest = e.published_parsed
        newest = datetime.fromtimestamp(time.mktime(newest))
        if newest > job.last_change_time:
            job.last_change_time = newest
            for e in feed.entries:
                if e.published_parsed > last_change_time:
                    if "title_detail" in e and "value" in e.title_detail and any(kw in e.title_detail.value.lower() for kw in keywords) or "summary" in e and any(kw in e.summary.lower() for kw in keywords):
                        job.unread_change = True
                        break
            #Safe the current feed-XML
            job.referenceHtml_lastCron = request.text
    elif job.type == job.types.HTML:
        try:
            request = requests.get(job.url, timeout=5)
        except requests.Timeout:
            job.add_error_log(str(datetime.now())+" FATAL: connection timeout (more than 5s) "+job.url)
            return None
        except requests.exceptions.ConnectionError:
            job.add_error_log(str(datetime.now())+" FATAL: ConnectionError. Is your computer connected to the internet?")
            return None
        if request.status_code != 200:
            job.add_error_log(str(datetime.now())+" FATAL: connection response code "+str(request.status_code))
            return None
        html_soup = BeautifulSoup(request.text, 'html.parser')
        if "search" in job.commands:
            html_soup = parse_search(html_soup, job.commands["search"], job)
        if html_soup == None:
            return None
        soup = BeautifulSoup(str(html_soup), 'html.parser') #This is due to a bug in bs4 that 
        if str(soup) != job.referenceHtml_lastCron:
            last_change = list(difflib.Differ().compare(spaceless_prettify(BeautifulSoup(job.referenceHtml_lastCron, 'html.parser')),spaceless_prettify(soup)))
            #TODO: Change back the next line. This is for debug only!! Do not use this in production cause it just costs performance!
            if True:#job.unread_change == False:
                if "checkkeywords" in job.commands and job.commands["checkkeywords"] == True:
                    if any(kw in ht.lower() for kw in keywords for ht in last_change if(ht.startswith("- ") or ht.startswith("+ "))):
                        job.unread_change = True
                        job.last_change_time = datetime.now()
                    else:
                        print("Unrecognized changes were detected.")
                else:
                    job.unread_change = True
                    job.last_change_time = datetime.now()
            #TODO: remove this debug-output
            print("-----------------------------------------------")
            print(job.id)
            print(job.url)
            for ht in last_change:
                print(job.id, ": ", ht)
            job.referenceHtml_lastCron = str(soup)
    job.last_cron_time = datetime.now()
    return job