from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import datetime
import random
import string


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'
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

class Device(db.Model):
    __tablename__ = "device"
    __table_args__ = {'extend_existing': True}

    uid = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    telemetry = db.relationship(Telemetry)

def generate_id(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

@app.route('/overview')
def overview():
    devices = db.session.execute(Device.query)
    telemetries = {}

    for d in devices:
        res = db.session.execute(Telemetry.query
                                    .filter_by(device_uid=d[0])
                                    .order_by(Telemetry.time.desc())
                                    .limit(5))
        telemetries[d[0]] = [r for r in res]
    print(telemetries)
    return str(telemetries)


@app.route('/detail')
def detail():
    device_uid = request.json['device_uid']
    res = db.session.execute(Telemetry.query
                                .filter_by(device_uid=device_uid)
                                .order_by(Telemetry.time.desc())
                                .limit(5))
    print([d for d in res])
    return 'detail'


@app.route('/execute')
def execute():
    return 'execute'


@app.route('/add_telemetry', methods=['POST'])
def add_telemetry():
    data = request.json
    new_telemetry = Telemetry(device_uid=data["uid"],
                                voltage=float(data["voltage"]),
                                ampere=float(data["ampere"]))
    db.session.add(new_telemetry)
    db.session.commit()
    return 'add_telemetry'


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

    new_device = Device(uid=new_uid, name=data["device"])
    db.session.add(new_device)
    db.session.commit()

    return new_uid


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
