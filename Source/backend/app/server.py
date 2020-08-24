from flask import Flask, jsonify, request
from flask_cors import CORS
import pymongo
import datetime
import random
import string
import os


server_address = os.environ.get("SERVER_ADDRESS")

if not server_address:
    exit(1)

db_address = 'mongodb://' + server_address + ':27017/'


# Backend App
app = Flask(__name__)
CORS(app)


# MongoDB Database
client = pymongo.MongoClient(
    db_address, username="hyperlynk", password="OnePurpleParrot")
db = client['hyperlynkdb']

if db.regions.count_documents({'name': "Awaiting Allocation"}) == 0:
    db.regions.insert_one({
        'name': "Awaiting Allocation"
    })


# Generate a random device id.
def generate_device_id(length=16):
    return ''.join(random.choice(string.ascii_letters + "1234567890") for i in range(length))


# Generic Replies
def response(msg='', payload={}):
    return jsonify({'Message': str(msg), 'Payload': payload})


# Existence
def device_exists(device_id):
    return db.devices.count_documents({'device_id': device_id}) != 0


def region_exists(region_name):
    return db.regions.count_documents({'name': region_name}) != 0


# Viewing
@app.route('/overview', methods=['GET'])
def overview():
    health = "Normal"
    operating_counts = db.devices.count_documents({"status": "Online"})
    offline_counts = db.devices.count_documents({"status": "Offline"})
    failure_counts = db.devices.count_documents({"status": "Failure"})

    failure_percentage = 0.00
    if (operating_counts+offline_counts+failure_counts) != 0:
        failure_percentage = round(
            failure_counts/(operating_counts+offline_counts+failure_counts)*100, 2)

    power_output_out = round(sum([d["telemetries"][-1]["current_out"] * d["telemetries"][-1]["voltage_out"] if d["telemetries"] else 0
                              for d in db.devices.find()]), 2)
    
    power_output_in = round(sum([d["telemetries"][-1]["current_in"] * d["telemetries"][-1]["voltage_in"] if d["telemetries"] else 0
                              for d in db.devices.find()]), 2)

    server_status = "Normal"
    region_counts = db.regions.count_documents({})

    overview = {
        "health": health,
        "operating_counts": operating_counts,
        "offline_counts": offline_counts,
        "failure_counts": failure_counts,
        "failure_percentage": str(failure_percentage) + "%",
        "power_output_out": power_output_out,
        "power_output_in": power_output_in,
        "server_status": server_status,
        "region_counts": region_counts,
    }

    return response("Success", overview)


@app.route('/regions', methods=['GET'])
def regions():
    regions = []
    ins = []
    outs = []
    for r in db.regions.find():
        pwr_output_out = round(sum([d["telemetries"][-1]["current_out"] * d["telemetries"][-1]["voltage_out"] if d["telemetries"] else 0
                                for d in db.devices.find({"region": r["name"]})]), 2)
        pwr_output_in = round(sum([d["telemetries"][-1]["current_in"] * d["telemetries"][-1]["voltage_in"] if d["telemetries"] else 0
                                for d in db.devices.find({"region": r["name"]})]), 2)
        regions.append(r["name"])
        outs.append(pwr_output_out)
        ins.append(pwr_output_in)

    return response("Success", {"Regions": regions, "In": ins, "Out": outs})


@app.route('/panels', methods=['POST'])
def panels():
    region_name = request.json['region_name']

    if not region_exists(region_name):
        return response("Region not found.", [])

    panels = []
    ins = []
    outs = []
    for d in db.devices.find({"region": region_name}):
        pwr_output_out = 0
        pwr_output_in = 0
        if d["telemetries"]:
            pwr_output_out = d["telemetries"][-1]["current_out"] * \
                d["telemetries"][-1]["voltage_out"]
            pwr_output_in = d["telemetries"][-1]["current_in"] * \
                d["telemetries"][-1]["voltage_in"]

        panels.append(d["device_id"])
        outs.append(round(pwr_output_out, 2))
        ins.append(round(pwr_output_in, 2))

    return response("Success", {"Panels": panels, "In": ins, "Out": outs})


@app.route('/panel_detail', methods=['POST'])
def panel_detail():
    device_id = request.json['device_id']

    if not device_exists(device_id):
        return response("Device doest not exists.")

    device = db.devices.find_one({"device_id": device_id})
    current_in = [{"id": "current_in", "data": []}]
    voltage_in = [{"id": "voltage_in", "data": []}]
    current_out = [{"id": "current_out", "data": []}]
    voltage_out = [{"id": "voltage_out", "data": []}]
    power_in = [{"id": "power_in", "data": []}]
    power_out = [{"id": "power_out", "data": []}]

    for t in device["telemetries"][-60:]:
        current_in[0]["data"].append(
            {"x": len(current_in[0]["data"]), "y": t["current_in"]})
        voltage_in[0]["data"].append(
            {"x": len(voltage_in[0]["data"]), "y": t["voltage_in"]})
        current_out[0]["data"].append(
            {"x": len(current_out[0]["data"]), "y": t["current_out"]})
        voltage_out[0]["data"].append(
            {"x": len(voltage_out[0]["data"]), "y": t["voltage_out"]})
        power_in[0]["data"].append(
            {"x": len(power_in[0]["data"]), "y": t["current_in"] * t["voltage_in"]})
        power_out[0]["data"].append(
            {"x": len(power_out[0]["data"]), "y": t["current_out"] * t["voltage_out"]})

    return response("", {
        "device_id": device["device_id"],
        "region": device["region"],
        "status": device["status"],
        "current_in_graph": current_in,
        "voltage_in_graph": voltage_in,
        "power_in_graph": power_in,
        "current_out_graph": current_out,
        "voltage_out_graph": voltage_out,
        "power_out_graph": power_out
    })


# Event
@app.route('/push_event', methods=['POST'])
def push_event():
    device_id = request.json['device_id']
    event_code = request.json['event_code']
    event_value = float(request.json['event_value'])

    if not device_exists(device_id):
        return "Failed. Device not exists."

    db.devices.update_one(
        {'device_id': device_id},
        {
            '$push': {
                'events': {
                    'event_code': event_code,
                    'event_value': event_value
                }
            }
        }
    )

    return "Successfuly added."


# Telemetry
@ app.route('/add_telemetry', methods=['POST'])
def add_telemetry():
    device_id = request.json['device_id']
    current_in = float(request.json['current_in'])
    voltage_in = float(request.json['voltage_in'])
    current_out = float(request.json['current_out'])
    voltage_out = float(request.json['voltage_out'])

    if not device_exists(device_id):
        return ""

    rec_time = datetime.datetime.utcnow()

    db.devices.update_one(
        {'device_id': device_id},
        {
            '$push': {
                'telemetries': {
                    'current_in': current_in,
                    'voltage_in': voltage_in,
                    'current_out': current_out,
                    'voltage_out': voltage_out,
                    'datetime': rec_time
                }
            },
            '$set': {
                'status': "Online",
                'last_modified': rec_time
            }
        }
    )

    events = db.devices.find_one({'device_id': device_id})['events']

    db.devices.update_one(
        {'device_id': device_id},
        {
            '$set': {
                'events': []
            }
        }
    )

    event_stream = ""
    for e in events:
        event_stream += e["event_code"] + ","
        event_stream += str(e["event_value"]) + ","

    return event_stream.rstrip(",")


# Device Management
@ app.route('/register_device', methods=['POST'])
def register_device():
    device_id = request.json['device_id']

    # Device exists in database.
    if device_exists(device_id):
        db.devices.update_one(
            {'device_id': device_id},
            {
                '$set': {
                    'status': "Online"
                }
            }
        )
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

    db.devices.insert_one({
        'device_id': new_id,
        'status': "Online",
        'events': [],
        'telemetries': [],
        'region': "Awaiting Allocation",
        'last_modified': datetime.datetime.utcnow()
    })

    return new_id


@ app.route('/assign_to_region', methods=['POST'])
def assign_to_region():
    device_id = request.json['device_id']
    region_name = request.json['region_name']

    if not device_exists(device_id):
        return response("Device not found.")

    if not region_exists(region_name):
        return response("Region not found.")

    db.devices.update(
        {'device_id': device_id},
        {
            '$set': {
                'region': region_name
            }
        }
    )

    return response("Device assignment successful.")


# Region Management
@ app.route('/register_region', methods=['POST'])
def register_region():
    region_name = request.json['region_name']
    print(region_name)

    if not region_exists(region_name):
        db.regions.insert_one({
            'name': region_name
        })
        return response('Region successfully added.')

    return response('Region name already exists.')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8002)
