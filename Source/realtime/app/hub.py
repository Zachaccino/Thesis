from settings import PULSAR_ADDRESS, SERVER_ADDRESS, SERVER_PORT, NUMBER_OF_SOCKETS
import pulsar
import socketio
import json 
import requests


# Message Queue
mq = pulsar.Client(PULSAR_ADDRESS)
receiver = mq.subscribe('HUB0', subscription_name='HUB0')

# Keeping a list of sockets
sockets = []

# Connection Tracking
# TYPE: {SocketID: {ContentID: Count}}
conntrack = {}


# Connect to socket clients
for i in range(NUMBER_OF_SOCKETS):
    sock = socketio.Client()
    sock.connect('http://' + SERVER_ADDRESS + ':' + str(SERVER_PORT + i), {"CLIENT_TYPE": "HUB"})
    sock.emit('force_update')
    sockets.append(sock)


# Synchronise connection tracker state
def conntrack_sync(sock_id, state):
    conntrack[sock_id] = state
    print("CONNTRACK sync.", conntrack)


# Received an aggregated update.
def aggregate_update_available(content_id, current_in, voltage_in, current_out, voltage_out, timestamp):
    print("HUB Aggregate Update Detected")
    if content_id == "overview":
        pass
    elif content_id == "regions":
        pass
    elif content_id == "panels":
        pass
    else:
        telemetry = None
        for sock_id in conntrack:
            if content_id in conntrack[sock_id] and conntrack[sock_id][content_id] > 0:
                if not telemetry:
                    telemetry = {"content_id": content_id, "data": {"CURRENT_IN": current_in, "VOLTAGE_IN": voltage_in, "CURRENT_OUT": current_out, "VOLTAGE_OUT": voltage_out, "TIME": timestamp}}
                print("HUB is sending aggregate update.", telemetry)
                sockets[sock_id].emit("aggregate_update_available", telemetry)


# Received a realtime update.
def realtime_update_available(content_id, current_in, voltage_in, current_out, voltage_out, timestamp):
    print("HUB Realtime Update Detected")
    if content_id == "overview":
        pass
    elif content_id == "regions":
        pass
    elif content_id == "panels":
        pass
    else:
        telemetry = None
        for sock_id in conntrack:
            if content_id in conntrack[sock_id] and conntrack[sock_id][content_id] > 0:
                if not telemetry:
                    telemetry = {"content_id": content_id, "data": {"CURRENT_IN": current_in, "VOLTAGE_IN": voltage_in, "CURRENT_OUT": current_out, "VOLTAGE_OUT": voltage_out, "TIME": timestamp}}
                print("HUB is sending realtime update.", telemetry)
                sockets[sock_id].emit("realtime_update_available", telemetry)


# Listening for Messages
while True:
    print("HUB LOOP")
    msg = receiver.receive()
    data = msg.data()
    receiver.acknowledge(msg)
    data = json.loads(data)
    print(data)
    
    if data["TYPE"] == "TELE_UPDATE_AGGREGATE":
        aggregate_update_available(data["CONTENT_ID"], data["CURRENT_IN"], data["VOLTAGE_IN"], data["CURRENT_OUT"], data["VOLTAGE_OUT"], data["TIME"])
    elif data["TYPE"] == "TELE_UPDATE_REALTIME":
        realtime_update_available(data["CONTENT_ID"], data["CURRENT_IN"], data["VOLTAGE_IN"], data["CURRENT_OUT"], data["VOLTAGE_OUT"], data["TIME"])
    elif data["TYPE"] == "CONNTRACK_UPDATE":
        conntrack_sync(data["SOCK_ID"], data["STATE"])


# Clean Up.
for sock in sockets:
    sock.disconnect()

mq.close()
