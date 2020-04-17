from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import datetime


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
    status = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=False)

    telemetry = db.relationship(Telemetry)


@app.route('/overview')
def overview():
    devices = db.session.execute(Device.query)
    telemetries = {}

    for d in devices:
        res = db.session.execute(Telemetry.query
                                    .filter_by(device_uid=d[0])
                                    .order_by(Telemetry.time.desc())
                                    .limit(5))
        telemetries[d[0]] = [d for d in res]
    print(telemetries)
    return 'overview'


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
    new_telemetry = Telemetry(device_uid=data["device_uid"],
                                voltage=float(data["voltage"]),
                                ampere=float(data["ampere"]))
    db.session.add(new_telemetry)
    db.session.commit()
    return 'add_telemetry'


@app.route('/add_device', methods=['POST'])
def add_device():
    data = request.json
    new_device = Device(uid=data['uid'],
                            name=data["device"],
                            status=data["status"],
                            address=data['address'])
    db.session.add(new_device)
    db.session.commit()
    return 'add_device'


if __name__ == "__main__":
    app.run(debug=True)
