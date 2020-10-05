from settings import PULSAR_ADDRESS, SERVER_ADDRESS, SERVER_PORT
import pulsar
import socketio
from aiohttp import web
import json


sock_id = 0
socket_name = "SOCKET"+str(sock_id)
conntrack = {'AZDpXvKC':1}

mq = pulsar.Client(PULSAR_ADDRESS)
receiver = mq.subscribe(socket_name, subscription_name=socket_name)
sender = mq.create_producer('HUB0')
sender.send(json.dumps({"TYPE": "CONN", "SOCK_ID": sock_id}).encode('utf-8'))

sio = socketio.AsyncServer()
wa = web.Application()
sio.attach(wa)

@sio.event
def connect(sid, env):
    print("connection established.")
    if env["HTTP_CLIENT_TYPE"] == "HUB":
        sender.send(json.dumps({"TYPE": "CONNTRACK_UPDATE", "SOCK_ID": sock_id, "STATE":conntrack}).encode('utf-8'))

@sio.event
def force_update(sid, data):
    print('Force update received with ', data)

@sio.event
def update_available(sid, data):
    print('Update available received with ', data)
    print('Emit to room.')

@sio.event
def disconnect(sid):
    print('disconnected from server')

web.run_app(wa, host=SERVER_ADDRESS, port=SERVER_PORT+sock_id)
sender.send(json.dumps({"TYPE": "DISCONN", "SOCK_ID": sock_id}).encode('utf-8'))
