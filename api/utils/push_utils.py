#!/usr/bin/env python3

# Corona-Info-App
# Update Measures from NINA-App
# © 2020 Tobias Höpp

from main import db

def push(district_id, reasons):
    DevicesRequest = "SELECT dv.token FROM devices dv WHERE dv.provider = :provider AND dv.id IN (SELECT dhd.device_id FROM deviceHasDistrict dhd WHERE dhd.district_id = :district_id)"
    rows = db.session.execute(DevicesRequest, {"provider":1,"district_id":district_id})
    deviceIDs = []
    for row in rows:
        deviceIDs.append(row[0])
    if deviceIDs != []:
        print("PUSH", district_id, reasons, deviceIDs)
    else:
        print("PUSH", district_id, reasons)