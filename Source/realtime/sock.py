from aiohttp import web
import socketio

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


@sio.event
def connect(sid, environ):
    sio.enter_room(sid, environ["HTTP_CONTENT_KEY"])

@sio.event
async def new_telemetry(sid, data):
    print("New Telemetry", data)
    # If room exists.

    await sio.emit('refresh_telemetry', room=data["id"])

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    web.run_app(app)