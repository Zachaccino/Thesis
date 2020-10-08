from settings import PULSAR_ADDRESS, SERVER_ADDRESS, SERVER_PORT
import pulsar
import socketio
from aiohttp import web
import json


sock_id = 1
socket_name = "SOCKET"+str(sock_id)
conntrack = {}
sidtrack = {}

mq = pulsar.Client(PULSAR_ADDRESS)
receiver = mq.subscribe(socket_name, subscription_name=socket_name)
sender = mq.create_producer('HUB0')

sio = socketio.AsyncServer(engineio_logger=False, cors_allowed_origins="*")
wa = web.Application()
sio.attach(wa)


@sio.event
def connect(sid, env):
    print(conntrack)
    print('connected.')
    
@sio.event
async def frontend_connect(sid, data):
    print(conntrack)
    room = data["content"]
    if room not in conntrack:
        conntrack[room] = 1
    else:
        conntrack[room] += 1
    sio.enter_room(sid, room)
    print("ENTER ROOM", room)
    sender.send(json.dumps({"TYPE": "CONNTRACK_UPDATE", "SOCK_ID": sock_id, "STATE":conntrack}).encode('utf-8'))
    sidtrack[sid] = room

@sio.event
async def keep_alive(sid):
    print("keep alive>>>>>>>>>>>>>>>>>>>")

@sio.event
async def force_update(sid):
    print('Force update')

@sio.event
async def aggregate_update_available(sid, data):
    print("aggregate Update", data["content_id"])
    await sio.emit("aggregate_update", data=data["data"], room=data["content_id"])

@sio.event
async def realtime_update_available(sid, data):
    print("realtime Update", data["content_id"])
    await sio.emit("realtime_update", data=data["data"], room=data["content_id"])

@sio.event
def disconnect(sid):
    print(conntrack)
    print('disconnected from server')
    if sid in sidtrack:
        conntrack[sidtrack[sid]] -= 1
        del sidtrack[sid] 
        sender.send(json.dumps({"TYPE": "CONNTRACK_UPDATE", "SOCK_ID": sock_id, "STATE":conntrack}).encode('utf-8'))
    print(conntrack)

web.run_app(wa, host='0.0.0.0', port=SERVER_PORT+sock_id)
mq.close()
