import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

@sio.event
def realtime_update(data):
    print('message received with ', data)

@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://localhost:5000')

sio.emit('frontend_connect', )
sio.wait()