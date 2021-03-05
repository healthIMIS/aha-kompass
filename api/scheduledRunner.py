#!/usr/bin/env python3

import schedule
import update_data
import datetime
import time


def update():
    print("Running data update at " + str(datetime.datetime.now()))
    try:
        update_data.update()
    except Exception:
        print("Update failed.")
        pass


schedule.every(15).minutes.do(update)


while True:
    schedule.run_pending()
    time.sleep(1)
