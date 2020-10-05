import random
import string
import os
from settings import DB_ADDRESS, DB_USERNAME, DB_PASSWORD, PULSAR_ADDRESS
from database import Database
import pulsar
import json

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

    msg = json.dumps({"TYPE": "TELE_UPDATE", "CONTENT_ID": device_id})
    producer.send(msg.encode('utf-8'))
