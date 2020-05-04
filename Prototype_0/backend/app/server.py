from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import datetime
import random
import string
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456789@db:3306/BackendDB'
db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)


class Telemetry(db.Model):
    __tablename__ = "telemetry"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    device_uid = db.Column(db.String(80), db.ForeignKey('device.uid'), nullable=False)
    voltage = db.Column(db.Float, nullable=False)
    ampere = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime(80), default=datetime.datetime.utcnow, nullable=False)

class Event(db.Model):
    __tablename__ = "event"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    device_uid = db.Column(db.String(80), db.ForeignKey('device.uid'), nullable=False)
    code = db.Column(db.String(80), nullable=False)
    value = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime(80), default=datetime.datetime.utcnow, nullable=False)

class Device(db.Model):
    __tablename__ = "device"
    __table_args__ = {'extend_existing': True}

    uid = db.Column(db.String(80), primary_key=True)

    telemetry = db.relationship(Telemetry)




def generate_id(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

@app.route('/overview')
def overview():
    devices = db.session.execute(Device.query)
    telemetries = {}

    for device in devices:
        res = db.session.execute(Telemetry.query
                                    .filter_by(device_uid=device[0])
                                    .order_by(Telemetry.time.desc())
                                    .limit(15))
        telemetries[device[0]] = [{"voltage":t[2], "ampere":t[3], "time":t[4]} for t in res]

    nivo_data = {}
    for device in telemetries:
        device_data = [{"id":"voltage", "data":[]}, {"id":"Ampere", "data":[]}]
        for measurement in telemetries[device]:
            time = str(measurement["time"]).split(" ")[1][:12]
            voltage_point = {"x":time, "y":measurement["voltage"]}
            ampere_point = {"x":time, "y":measurement["ampere"]}

            device_data[0]["data"].append(voltage_point)
            device_data[1]["data"].append(ampere_point)
        nivo_data[device] = device_data

    return jsonify(nivo_data)


@app.route('/detail')
def detail():
    device_uid = request.json['device_uid']
    res = db.session.execute(Telemetry.query
                                .filter_by(device_uid=device_uid)
                                .order_by(Telemetry.time.desc())
                                .limit(5))
    print([d for d in res])
    return 'detail'


@app.route('/add_event', methods=['POST'])
def add_event():
    data = request.json
    uid = data["uid"]
    event_code = data["event"]
    event_value = float(data["value"])

    device_exist = db.session.execute(Device.query.filter(Device.uid == uid)).scalar()

    if not device_exist:
        new_device = Device(uid=uid)
        db.session.add(new_device)
        db.session.commit()

    new_event = Event(device_uid=uid,
                        code=event_code,
                        value=event_value)
    db.session.add(new_event)
    db.session.commit()

    return "add_event"

# HERERERERERE
@app.route('/pull_events', methods=['POST'])
def pull_events():
    data = request.json
    uid = data["uid"]

    res = db.session.execute(Event.query
                                .filter_by(device_uid=uid)
                                .order_by(Event.time.asc())
                                .limit(1))

    deserialised = [(str(e[2]) + "," + str(e[3]), e[0]) for e in res]

    if not deserialised:
        return "NA,0"
    else:
        db.session.execute(Event.query.filter_by(id=deserialised[0][1]).delete())
        db.session.commit()
        return deserialised[0][0]


@app.route('/add_telemetry', methods=['POST'])
def add_telemetry():
    data = request.json

    device_exist = db.session.execute(Device.query.filter(Device.uid == data['uid'])).scalar()

    if not device_exist:
        new_device = Device(uid=data['uid'])
        db.session.add(new_device)
        db.session.commit()

    new_telemetry = Telemetry(device_uid=data["uid"],
                                voltage=float(data["voltage"]),
                                ampere=float(data["ampere"]))
    db.session.add(new_telemetry)
    db.session.commit()

    event_exist = db.session.execute(Event.query.filter(Device.uid == data['uid'])).scalar()

    if event_exist:
        return 'true'
    else:
        return 'false'


@app.route('/add_device', methods=['POST'])
def add_device():
    data = request.json
    device_exist = db.session.execute(Device.query.filter(Device.uid == data['uid'])).scalar()

    if device_exist:
        return data['uid'];

    new_uid = data['uid']

    for c in data['uid']:
        if c not in string.ascii_letters:
            new_uid = generate_id(16)
            break

    if len(data['uid']) != 16:
        new_uid = generate_id(16)

    new_device = Device(uid=new_uid)
    db.session.add(new_device)
    db.session.commit()

    return new_uid


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
