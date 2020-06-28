from flask import Flask, jsonify, request
from flask_cors import CORS
import pymongo
import datetime
import random
import string


# Backend App
app = Flask(__name__)
CORS(app)


# MongoDB Database
client = pymongo.MongoClient('mongodb://hyperlynk.zachaccino.me:27017/', username="hyperlynk", password="OnePurpleParrot")
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

    power_output = round(sum([d["telemetries"][-1]["current"] * d["telemetries"][-1]["voltage"] if d["telemetries"] else 0
                              for d in db.devices.find()]), 2)
    server_status = "Normal"
    region_counts = db.regions.count_documents({})

    overview = {
        "health": health,
        "operating_counts": operating_counts,
        "offline_counts": offline_counts,
        "failure_counts": failure_counts,
        "failure_percentage": str(failure_percentage) + "%",
        "power_output": power_output,
        "server_status": server_status,
        "region_counts": region_counts,
    }

    return response("Success", overview)


@app.route('/regions', methods=['GET'])
def regions():
    regions = []
    values = []
    for r in db.regions.find():
        pwr_output = round(sum([d["telemetries"][-1]["current"] * d["telemetries"][-1]["voltage"] if d["telemetries"] else 0
                                for d in db.devices.find({"region": r["name"]})]), 2)
        regions.append(r["name"])
        values.append(pwr_output)

    return response("Success", {"Regions": regions, "Values": values})


@app.route('/panels', methods=['POST'])
def panels():
    region_name = request.json['region_name']

    if not region_exists(region_name):
        return response("Region not found.", [])

    panels = []
    values = []
    for d in db.devices.find({"region": region_name}):
        pwr_output = 0
        if d["telemetries"]:
            pwr_output = d["telemetries"][-1]["current"] * \
                d["telemetries"][-1]["voltage"]

        panels.append(d["device_id"])
        values.append(round(pwr_output, 2))

    return response("Success", {"Panels": panels, "Values": values})


@app.route('/panel_detail', methods=['POST'])
def panel_detail():
    device_id = request.json['device_id']

    if not device_exists(device_id):
        return response("Device doest not exists.")

    device = db.devices.find_one({"device_id": device_id})
    current = [{"id": "Current", "data": []}]
    voltage = [{"id": "Voltage", "data": []}]
    power = [{"id": "Power", "data": []}]

    for t in device["telemetries"][-60:]:
        current[0]["data"].append(
            {"x": len(current[0]["data"]), "y": t["current"]})
        voltage[0]["data"].append(
            {"x": len(voltage[0]["data"]), "y": t["voltage"]})
        power[0]["data"].append(
            {"x": len(power[0]["data"]), "y": t["current"] * t["voltage"]})

    return response("", {
        "device_id": device["device_id"],
        "region": device["region"],
        "status": device["status"],
        "current_graph": current,
        "voltage_graph": voltage,
        "power_graph": power
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


@ app.route('/pull_event', methods=['POST'])
def pull_event():
    device_id = request.json['device_id']

    if not device_exists(device_id):
        return ""

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


# Telemetry
@ app.route('/add_telemetry', methods=['POST'])
def add_telemetry():
    device_id = request.json['device_id']
    current = float(request.json['current'])
    voltage = float(request.json['voltage'])

    if not device_exists(device_id):
        return "Failed. Device not exists."

    rec_time = datetime.datetime.utcnow()

    db.devices.update_one(
        {'device_id': device_id},
        {
            '$push': {
                'telemetries': {
                    'current': current,
                    'voltage': voltage,
                    'datetime': rec_time
                }
            },
            '$set': {
                'status': "Online",
                'last_modified': rec_time
            }
        }
    )

    return "Successfuly added."


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
