import pymongo
import datetime
import time
import os
import pulsar
from settings import PULSAR_ADDRESS, DB_ADDRESS, DB_USERNAME, DB_PASSWORD
import json


# Aggregate telemetries every minute.
def aggregate_telemetry():
    # Period in Seconds
    period = 60

    # Database Conn
    client = pymongo.MongoClient(DB_ADDRESS, username=DB_USERNAME, password=DB_PASSWORD)
    db = client['hyperlynkdb']
    mq = pulsar.Client(PULSAR_ADDRESS)
    producer = mq.create_producer('HUB0')

    while(True):
        # Aggregation Loop
        for dev in db.devices.find({}, {"device_id": 1, "telemetries": 1}):
            total_current_in = 0
            total_voltage_in = 0
            total_current_out = 0
            total_voltage_out = 0
            count = 0

            for t in dev["telemetries"]:
                total_current_in += t["current_in"]
                total_voltage_in += t["voltage_in"]
                total_current_out += t["current_out"]
                total_voltage_out += t["voltage_out"]
                count += 1
            
            c_in = 0 if count == 0 else total_current_in / count
            v_in = 0 if count == 0 else total_voltage_in / count
            c_out = 0 if count == 0 else total_current_out / count
            v_out = 0 if count == 0 else total_voltage_out / count

            db.devices.update_one(
                {
                    "device_id": dev["device_id"]
                },
                {
                    "$push": {
                        "aggregate_telemetries": {
                            "current_in": c_in,
                            "voltage_in": v_in,
                            "current_out": c_out,
                            "voltage_out": v_out
                        }
                    },
                    "$set": {
                        "telemetries":[]
                    }
                }
            )

            aggr_msg = json.dumps({"TYPE": "TELE_UPDATE_AGGREGATE", "CONTENT_ID": dev["device_id"], "CURRENT_IN": c_in, "VOLTAGE_IN": v_in, "CURRENT_OUT": c_out, "VOLTAGE_OUT": v_out, "TIME": time.time()})
            producer.send(aggr_msg.encode('utf-8'))

        time.sleep(period)

aggregate_telemetry()
