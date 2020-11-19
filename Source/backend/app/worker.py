import random
import string
import os
from settings import DB_ADDRESS, DB_USERNAME, DB_PASSWORD, PULSAR_ADDRESS
from database import Database
import pulsar
import json
import time

def push_event_worker(device_id, event_code, event_value):
    db = Database(DB_ADDRESS, DB_USERNAME, DB_PASSWORD)
    db.connect()
    if not db.device_exist(device_id):
        return 
    db.insert_event(device_id, event_code, event_value)

def add_telemetry_worker(device_id, current_in, voltage_in, current_out, voltage_out):
    db = Database(DB_ADDRESS, DB_USERNAME, DB_PASSWORD)
    db.connect()
    if not db.device_exist(device_id):
        return 
    mq = pulsar.Client(PULSAR_ADDRESS)
    producer = mq.create_producer('HUB0')
    db.insert_telemetry(device_id, current_in, voltage_in, current_out, voltage_out)
    msg = json.dumps({"TYPE": "TELE_UPDATE_REALTIME", "CONTENT_ID": device_id, "CURRENT_IN": current_in, "VOLTAGE_IN": voltage_in, "CURRENT_OUT": current_out, "VOLTAGE_OUT": voltage_out, "TIME": time.time()})
    producer.send(msg.encode('utf-8'))

# device_id, current_in, voltage_in, current_out, voltage_out

def add_telemetry_worker_batch(telemetries):
    db = Database(DB_ADDRESS, DB_USERNAME, DB_PASSWORD)
    db.connect()
    mq = pulsar.Client(PULSAR_ADDRESS)

    for t in telemetries:
        if not db.device_exist(t[0]):
            continue 
        producer = mq.create_producer('HUB0')
        db.insert_telemetry(t[0], t[1], t[2], t[3], t[4])
        msg = json.dumps({"TYPE": "TELE_UPDATE_REALTIME", "CONTENT_ID": t[0], "CURRENT_IN": t[1], "VOLTAGE_IN": t[2], "CURRENT_OUT": t[3], "VOLTAGE_OUT": t[4], "TIME": time.time()})
        producer.send(msg.encode('utf-8'))
