import pymongo
import datetime
import time
import os
from pyowm import OWM
from pprint import pprint
import pulsar
from settings import PULSAR_ADDRESS
import json


# Setting Switch
deploy = True
development_address = "127.0.0.1"
deployment_address = "3.24.141.26"
server_address = deployment_address if deploy else development_address


# Monitor the status of the devices.
# Mark the device with extended downtime as failure.
def monitor_device_liveness():
    period = 10
    timeout = 60

    # MongoDB Database
    client = pymongo.MongoClient(
        'mongodb://' + server_address + ':27017/', username="hyperlynk", password="OnePurpleParrot")
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


# Aggregate telemetries every minute.
def aggregate_telemetry():
    # Period in Seconds
    period = 60

    # Database Conn
    client = pymongo.MongoClient(
        'mongodb://' + server_address + ':27017/', username="hyperlynk", password="OnePurpleParrot")
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

            msg = json.dumps({"TYPE": "TELE_UPDATE_AGGREGATE", "CONTENT_ID": dev["device_id"]})
            producer.send(msg.encode('utf-8'))

        time.sleep(period)

# Cloud coverage is a pretty good predictor.
# More generalised.
def cloud_coverage_impact(percentage):
    if percentage < 30:
        return 0.75
    elif percentage < 50:
        return 0.5
    else:
        return 0.3

# TODO: CONSIDER 1 HR after sunrise and 1HR before sunset
def day_time(sunrise, sunset):
    current = int(datetime.datetime.utcnow().timestamp())
    if current < sunrise or current > sunset:
        return False
    return True


# Given time of day, sunrise, sunset, impact level, max power, and current power.
# TODO: TESTING NEEDED
def monitor_device_performance():
    period = 60

    # API Initialisation.
    owm = OWM('7ead5a3e5a333c0664faa13a659c5bc1')
    mgr = owm.weather_manager()

    # Database.
    client = pymongo.MongoClient(
        'mongodb://' + server_address + ':27017/', username="hyperlynk", password="OnePurpleParrot")
    db = client['hyperlynkdb']

    # Assume our pv panel produces 260 watts max.
    max_power = 260

    while(True):
        # Getting the weather observations.
        weather = {}
        for r in db.regions.find():
            if r["name"] == 'Awaiting Allocation':
                continue
            weather[r["name"]] = mgr.weather_at_place(r["name"] + ',AU').to_dict()
        
        # Checking the performances.
        for dev in db.devices.find({"status":"Online"}, {"device_id": 1, "region": 1, 'aggregate_telemetries': {'$slice': -1}}):
            if not day_time(weather[dev["region"]]["sunrise_time"], weather[dev["region"]]["sunset_time"]):
                continue

            if not dev["aggregate_telemetries"]:
                continue

            live_power = dev["aggregate_telemetries"][0]["current_in"] * dev["aggregate_telemetries"][0]["voltage_in"]
            threshold = max_power * cloud_coverage_impact(weather[dev['region']]["clouds"])

            if live_power <= threshold:
                db.devices.update_one(
                {
                    "device_id": dev['device_id']
                },
                {
                    "$set": {
                        "status": "Under Performing"
                    }
                }
            )
        time.sleep(period)

aggregate_telemetry()
