import pymongo
import datetime
import time
import os
import pulsar
from settings import PULSAR_ADDRESS
import json


# Setting Switch
deploy = False
development_address = "127.0.0.1"
deployment_address = "3.24.141.26"
server_address = deployment_address if deploy else development_address


# Aggregate telemetries every minute.
def aggregate_telemetry():
    # Period in Seconds
    period = 10

    # Database Conn
    client = pymongo.MongoClient(
        'mongodb://' + server_address + ':27017/', username="hyperlynk", password="OnePurpleParrot")
    db = client['hyperlynkdb']

    mq = pulsar.Client(PULSAR_ADDRESS)
    producer = mq.create_producer('HUB0')

    while(True):
        print("Aggregating")
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

            db.devices.update_one(
                {
                    "device_id": dev["device_id"]
                },
                {
                    "$push": {
                        "aggregate_telemetries": {
                            "current_in": 0 if count == 0 else total_current_in / count,
                            "voltage_in": 0 if count == 0 else total_voltage_in / count,
                            "current_out": 0 if count == 0 else total_current_out / count,
                            "voltage_out": 0 if count == 0 else total_voltage_out / count
                        }
                    },
                    "$set": {
                        "telemetries":[]
                    }
                }
            )

            aggr_msg = json.dumps({"TYPE": "TELE_UPDATE_AGGREGATE", "CONTENT_ID": dev["device_id"]})
            real_msg = json.dumps({"TYPE": "TELE_UPDATE_REALTIME", "CONTENT_ID": dev["device_id"]})
            producer.send(aggr_msg.encode('utf-8'))
            producer.send(real_msg.encode('utf-8'))

        time.sleep(period)

aggregate_telemetry()
