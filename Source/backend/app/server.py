from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import string
import os
from Database import Database


# Getting Environments.
server_address = os.environ.get("SERVER_ADDRESS")
if not server_address:
    exit(1)

app = Flask(__name__)
CORS(app)


# Setting up DB.
db_address = 'mongodb://' + server_address + ':27017/'
db = Database(db_address, "hyperlynk", "OnePurpleParrot")
db.connect()
db.init()


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
        "power_output_out": power_out,
        "power_output_in": power_in,
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

    if not db.device_exist(device_id):
        return response("Device doest not exists.")

    return response("", db.device_detail_graphs(device_id, 30))


# Event
@app.route('/push_event', methods=['POST'])
def push_event():
    device_id = request.json['device_id']
    event_code = request.json['event_code']
    event_value = float(request.json['event_value'])

    if not db.device_exist(device_id):
        return "Failed. Device not exists."

    db.insert_event(device_id, event_code, event_value)
    return "Successfuly added."


# Telemetry
@ app.route('/add_telemetry', methods=['POST'])
def add_telemetry():
    device_id = request.json['device_id']
    current_in = float(request.json['current_in'])
    voltage_in = float(request.json['voltage_in'])
    current_out = float(request.json['current_out'])
    voltage_out = float(request.json['voltage_out'])

    if not db.device_exist(device_id):
        return ""
    
    db.insert_telemetry(device_id, current_in, voltage_in, current_out, voltage_out)
    return db.serialise_events(device_id)


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
    print(region_name)

    if not db.region_exist(region_name):
        db.insert_region(region_name)
        return response('Region successfully added.')

    return response('Region name already exists.')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8002)
