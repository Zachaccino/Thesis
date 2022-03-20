import pymongo
import datetime
import time
import os
import pulsar
from settings import DB_ADDRESS, DB_USERNAME, DB_PASSWORD
import json


# Monitor the status of the devices.
# Mark the device with extended downtime as failure.
def monitor_device_liveness():
    period = 10
    timeout = 60

    # MongoDB Database
    client = pymongo.MongoClient(DB_ADDRESS, username=DB_USERNAME, password=DB_PASSWORD)
    db = client['hyperlynkdb']

    while(True):
        # Find devices that are not offline but timeout for 1 mins already.
        db.devices.update_many(
            {
                "last_modified": {"$lt": datetime.datetime.utcnow() - datetime.timedelta(seconds=timeout)},
                "status": "Online"
            },
            {
                "$set": {
                    "status": "Failure"
                }
            }
        )
        time.sleep(period)


monitor_device_liveness()
