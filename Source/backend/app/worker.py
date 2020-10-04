import random
import string
import os
from settings import DB_ADDRESS, DB_USERNAME, DB_PASSWORD, PULSAR_ADDRESS
from database import Database
import pulsar

def push_event_worker(server_address, device_id, event_code, event_value):
    db = Database(DB_ADDRESS, DB_USERNAME, DB_PASSWORD)
    db.connect()

    if not db.device_exist(device_id):
        return 
    db.insert_event(device_id, event_code, event_value)

def add_telemetry_worker(server_address, device_id, current_in, voltage_in, current_out, voltage_out):
    db = Database(DB_ADDRESS, DB_USERNAME, DB_PASSWORD)
    db.connect()

    if not db.device_exist(device_id):
        return 
    
    mq = pulsar.Client(PULSAR_ADDRESS)
    producer = mq.create_producer('telemetry_update')
    
    db.insert_telemetry(device_id, current_in, voltage_in, current_out, voltage_out)
    producer.send((device_id).encode('utf-8'))
