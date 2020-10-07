from settings import PULSAR_ADDRESS, SERVER_ADDRESS, SERVER_PORT
import pulsar
import socketio
from aiohttp import web
import json


sock_id = 1
socket_name = "SOCKET"+str(sock_id)
conntrack = {'AZDpXvKC':0}

mq = pulsar.Client(PULSAR_ADDRESS)
receiver = mq.subscribe(socket_name, subscription_name=socket_name)
sender = mq.create_producer('HUB0')

sio = socketio.AsyncServer()
wa = web.Application()
sio.attach(wa)

@sio.event
def connect(sid, env):
    sio.enter_room(sid, env["HTTP_CLIENT_TYPE"])
    if env["HTTP_CLIENT_TYPE"] == "HUB":
        sender.send(json.dumps({"TYPE": "CONNTRACK_UPDATE", "SOCK_ID": sock_id, "STATE":conntrack}).encode('utf-8'))
    print("Connected: ", env["HTTP_CLIENT_TYPE"])

@sio.event
def force_update(sid):
    print('Force update')

@sio.event
def aggregate_update_available(sid, data):
    print('Update available received with ', data)
    print('Emit to room.') 

@sio.event
def realtime_update_available(sid, data):
    print('Update available received with ', data)
    print('Emit to room.') 

@sio.event
def disconnect(sid):
    print('disconnected from server')

web.run_app(wa, host=SERVER_ADDRESS, port=SERVER_PORT+sock_id)
mq.close()
