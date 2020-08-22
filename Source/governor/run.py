import pymongo
import datetime
import time
import os

server_address = os.environ.get("SERVER_ADDRESS")

if not server_address:
    exit(1)

def device_status_monitor():
    period = 10
    timeout = 60

    # MongoDB Database
    client = pymongo.MongoClient(
        'mongodb://' + server_address + ':27017/', username="hyperlynk", password="OnePurpleParrot")
    db = client['hyperlynkdb']

    while(True):
        # Find devices that are not offline but timeout for 1 mins already.
        db.devices.update_one(
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


device_status_monitor()
