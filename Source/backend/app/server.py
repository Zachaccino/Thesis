from settings import DB_ADDRESS, DB_USERNAME, DB_PASSWORD, REDIS_ADDRESS, REDIS_PORT
from conncount import ConnCount
from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import string
import os
from database import Database
from redis import Redis
from rq import Queue
from worker import push_event_worker, add_telemetry_worker, add_telemetry_worker_batch
import time
import pulsar
from random import randrange
import threading


app = Flask(__name__)
CORS(app)


# Setting up Mongo DB.
db = Database(DB_ADDRESS, DB_USERNAME, DB_PASSWORD)
db.connect()

# Setting up Redis Async Job Queue.
q = Queue(connection=Redis(REDIS_ADDRESS, REDIS_PORT))
q1 = Queue(connection=Redis(REDIS_ADDRESS, REDIS_PORT+1))

# Setting up ConnCount.
cc = ConnCount(REDIS_ADDRESS, REDIS_PORT)
cc.connect()

# Periodic Subroutine
buffer = [[], []]
buffer_selector = 0

buffer_lock = threading.Lock()

def batch_processor():
    global buffer_selector
    while True:
        time.sleep(1)
        with buffer_lock:
            buffer_selector = 0 if buffer_selector else 1
        if not buffer[buffer_selector]:
            continue
        if randrange(2) == 0:
            q.enqueue(add_telemetry_worker_batch, args=(buffer[buffer_selector],))
        else:
            q1.enqueue(add_telemetry_worker_batch, args=(buffer[buffer_selector],))
        buffer[buffer_selector] = []
        

processor_thread = threading.Thread(target=batch_processor)
processor_thread.start()


# Generate a random device id.
def generate_device_id(length=16):
    return ''.join(random.choice(string.ascii_letters + "1234567890") for i in range(length))


# Generic Replies
def response(msg='', payload={}):
    return jsonify({'Message': str(msg), 'Payload': payload})


# Viewing
@app.route('/overview', methods=['GET'])
def overview():
    health = db.system_health()
    operating_counts = db.count_operating()
    offline_counts = db.count_offline()
    failure_counts = db.count_failure()
    total_counts = operating_counts + offline_counts + failure_counts
    failure_percentage = 0 if total_counts == 0 else round(failure_counts/total_counts*100, 2)
    power_in, power_out= db.total_power()
    server_status = db.server_status()
    region_counts = db.count_region()
    return response("Success", {
        "health": health,
        "operating_counts": operating_counts,
        "offline_counts": offline_counts,
        "failure_counts": failure_counts,
        "failure_percentage": str(failure_percentage) + "%",
        "power_out": power_out,
        "power_in": power_in,
        "server_status": server_status,
        "region_counts": region_counts,
    })


@app.route('/regions', methods=['GET'])
def regions():
    regions, ins, outs = db.total_power_by_region()
    return response("Success", {"Regions": regions, "In": ins, "Out": outs})


@app.route('/panels', methods=['POST'])
def panels():
    region_name = request.json['region_name']

    if not db.region_exist(region_name):
        return response("Region not found.", [])

    panels, ins, outs = db.total_power_by_device(region_name)
    return response("Success", {"Panels": panels, "In": ins, "Out": outs})


@app.route('/panel_detail', methods=['POST'])
def panel_detail():
    device_id = request.json['device_id']
    aggregation = request.json['aggregation']
    if not db.device_exist(device_id):
        return response("Device doest not exists.")

    return response("", db.device_detail_graphs(device_id, aggregation, 240))


# Event
@app.route('/push_event', methods=['POST'])
def push_event():
    device_id = request.json['device_id']
    event_code = request.json['event_code']
    event_value = float(request.json['event_value'])
    q.enqueue(push_event_worker, args=(device_id, event_code, event_value))
    return "OK"


# Telemetry
@ app.route('/add_telemetry', methods=['POST'])
def add_telemetry():
    device_id = request.json['device_id']
    current_in = float(request.json['current_in'])
    voltage_in = float(request.json['voltage_in'])
    current_out = float(request.json['current_out'])
    voltage_out = float(request.json['voltage_out'])
    sample = [device_id, current_in, voltage_in, current_out, voltage_out]
    with buffer_lock:
        buffer[buffer_selector].append(sample)
    events = db.serialise_events(device_id)
    return events


# Device Management
@ app.route('/register_device', methods=['POST'])
def register_device():
    device_id = request.json['device_id']

    # Device exists in database.
    if db.device_exist(device_id):
        db.set_device_online(device_id)
        return device_id

    # Verify the id is legal.
    new_id = device_id

    if len(device_id) != 8:
        new_id = generate_device_id(8)
    else:
        for c in device_id:
            if c not in string.ascii_letters + "1234567890":
                new_id = generate_device_id(8)
                break

    db.insert_device(new_id)
    return new_id


@ app.route('/assign_to_region', methods=['POST'])
def assign_to_region():
    device_id = request.json['device_id']
    region_name = request.json['region_name']

    if not db.device_exist(device_id):
        return response("Device not found.")

    if not db.region_exist(region_name):
        return response("Region not found.")

    db.assign_device_to_region(device_id, region_name)
    return response("Device assignment successful.")


# Region Management
@ app.route('/register_region', methods=['POST'])
def register_region():
    region_name = request.json['region_name']
    if not db.region_exist(region_name):
        db.insert_region(region_name)
        return response('Region successfully added.')

    return response('Region name already exists.')


@ app.route('/sync_conncount', methods=['POST'])
def sync_conncount():
    # Sock_ID should be an integer.
    sock_id = request.json['sock_id']
    # Count is also an integer.
    count = request.json['count']
    print("SOCKID ", sock_id)
    print("COUNT ", count)
    # However, json key must be string, so we must convert it from int to str.
    cc.put(str(sock_id), count)
    return "OK"


@ app.route('/request_port', methods=['GET'])
def request_port():
    best_sock = None
    conncount = cc.get_all()
    print(conncount)
    for sock_id in conncount:
        if not best_sock:
            best_sock = sock_id
        elif conncount[sock_id]["value"] < conncount[best_sock]["value"]:
            best_sock = sock_id
    
    # Hardcoding, Since Redis seems to evict the key on low memory.
    if not best_sock:
        cc.put("0", 0)
        cc.put("1", 0)
        return {"sock_id": 0, "DEBUG": conncount}

    return {"sock_id": int(best_sock), "DEBUG": conncount}


@ app.route('/csv/<device_id>', methods=['GET'])
def csv(device_id):
    return db.to_csv(device_id)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
