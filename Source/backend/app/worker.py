import random
import string
import os
from database import Database
import pulsar

def push_event_worker(server_address, device_id, event_code, event_value):
    db_address = 'mongodb://' + server_address + ':27017/'
    db = Database(db_address, "hyperlynk", "OnePurpleParrot")
    db.connect()

    if not db.device_exist(device_id):
        return 
    db.insert_event(device_id, event_code, event_value)

def add_telemetry_worker(server_address, device_id, current_in, voltage_in, current_out, voltage_out):
    f = open("/Users/zachaccino/Repo/Thesis/Source/backend/app/test.txt", "w+")
    f.write("Hello\n")
    f.close()

    db_address = 'mongodb://' + server_address + ':27017/'
    db = Database(db_address, "hyperlynk", "OnePurpleParrot")
    db.connect()

    if not db.device_exist(device_id):
        return 
    
    mq = pulsar.Client('pulsar://localhost:6650')
    producer = mq.create_producer('telemetry_update')
    
    db.insert_telemetry(device_id, current_in, voltage_in, current_out, voltage_out)
    producer.send((device_id).encode('utf-8'))
