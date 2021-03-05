#!/usr/bin/env python3

# Corona-Info-App
# Cron-Script for LK Marburg-Bidenkopf
# © 2020 Johannes Kreutz.

# Include utilities

# Include db connection
from main import db
from models.cron import cron

for job in cron.query.all():
    if job.run() == False:
            print ("A Job was unsuccessful:", job.id)
"""
#For multithreading
import multiprocessing
import threading
from queue import Queue

def processJobQueue(q):
    while not q.empty():
        job_id = q.get()
        try:
            if cron.query.get(job_id).run() == False:
                print ("A Job was unsuccessful:", job_id)
        except:
            cron.query.get(job_id).add_error_log("Thread failed!")
        q.task_done()
jobQueue = Queue()
for job in cron.query.all():
    jobQueue.put(job.id)

for i in range(multiprocessing.cpu_count()):
    worker = threading.Thread(target=processJobQueue, args=(jobQueue,))
    worker.start()

print("waiting for Cronjobs to complete:", jobQueue.qsize())
jobQueue.join()
"""