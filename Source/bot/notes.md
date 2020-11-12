# Address Changes
Backend -> settings.py
Frontend -> RemoteServer.js
Frontend -> RemoteSocket.js
Governor -> settings.py
Realtime -> settings.py

# Launch Sequence
MongoDB
Redis
Pulsar

Frontend
Backend
Socket
Governor

Bot


# Config

4 Backend
12 Worker
500 Requests

## 100 Devices
Done
Monitoring - OK

## 200 Devices
Done
Monitoring - Delayed for 5 Mins from bots terminated to async finishes.


# Config

4 Backend
4 Worker
500 Requests

## 50 Devices
Done
Monitoring - OK

## 100 Devices
Done
Monitoring - Delayed for 4 mins from bots terminated to async finishes.

## 200 Devices
Done
Monitoring - Delayed for 16 mins from bots terminated to async finishes.


# Config

8 Backend
24 Worker
500 Requests

## 200 Devices
Done
Monitoring - Ok.


## 500 Devices
Done
Monitoring - Delayed for 10 mins from bots terminated to async finishes.
Simulators terminated 1 mins later than expected.


# Config

4 Backend
6 + 8 + 8 = 26 Worker
2 Thread for other services
500 Requests

## 500 Devices

