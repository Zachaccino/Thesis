from settings import PULSAR_ADDRESS, SERVER_ADDRESS, SERVER_PORT, NUMBER_OF_SOCKETS
import pulsar
from aiohttp import web
import socketio
import json 


# Message Queue Setup
mq = pulsar.Client(PULSAR_ADDRESS)
receiver = mq.subscribe('HUB0', subscription_name='HUB0')
sockets = {}


# Connection Tracking
# TYPE: {SocketID: {ContentID: Count}}
conntrack = {}


def connect(sock_id):
    global sockets
    global conntrack
    if sock_id in sockets:
        return
    conntrack[sock_id] = {}
    sockets[sock_id] = socketio.Client()
    sockets[sock_id].connect('http://localhost:' + str(SERVER_PORT + sock_id), {"CLIENT_TYPE": "HUB"})
    conntrack = {0:{'AZDpXvKC':1}}
    print(conntrack)

def disconect(sock_id):
    if sock_id not in sockets:
        return
    conntrack[sock_id] = {}
    sockets[sock_id].disconnect()
    del sockets[sock_id]
    print(conntrack)

def conntrack_sync(sock_id, state):
    conntrack[sock_id] = state

def update_available(content_id):
    telemetry = {"content_id": content_id, "data": 10}
    for sock_id in conntrack:
        if content_id in conntrack[sock_id] and conntrack[sock_id][content_id] > 0:
            sockets[sock_id].emit("update_available", telemetry)


# Listening for Messages
while True:
    msg = receiver.receive()
    data = msg.data()
    receiver.acknowledge(msg)
    data = json.loads(data)
    print(data)
    
    if data["TYPE"] == "CONN":
        connect(data["SOCK_ID"])
    elif data["TYPE"] == "DISCONN":
        disconect(data["SOCK_ID"])
    elif data["TYPE"] == "TELE_UPDATE":
        update_available(data["CONTENT_ID"])
    elif data["TYPE"] == "CONNTRACK_UPDATE":
        conntrack_sync(data["SOCK_ID"], data["STATE"])
    else:
        print("No matching message type.")

mq.close()