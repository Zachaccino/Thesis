import requests
import random
import time
from threading import Thread
import os

server_address = os.environ.get("SERVER_ADDRESS")

if not server_address:
    exit(1)

# Configuration
counts = 10
server = 'http://' + server_address + ':8000'
debug = False

# Read IDs
f = open("mcu_ids", "r")
id_pool = f.readline().split(",")
f.close()

# Read Regions
f = open("mcu_regions", "r")
region_pool = f.readline().split(",")
f.close()


# Register All Regions
def register_regions(region):
    requests.post(server + "register_region", json={"region_name": region})


for r in region_pool:
    register_regions(r)


# Helpers
def dprint(msg):
    if debug:
        print(msg)


def id_to_region(id):
    return region_pool[sum([ord(c) for c in id]) % len(region_pool)]


def register_device(id):
    r = requests.post(server + "register_device",
                      json={"device_id": id})
    dprint(r.content)


def assign_device_to_region(id, region):
    r = requests.post(server + "assign_to_region",
                      json={"device_id": id, "region_name": region})
    dprint(r.content)


def deviation():
    return random.randint(-2, 2) + random.uniform(-0.5, 0.5)


def send_telemetries(id, current, voltage):
    r = requests.post(server + "add_telemetry",
                      json={"device_id": id, "current": current, "voltage": voltage})
    dprint(r.content)


def pull_events(id):
    r = requests.post(server + "pull_event",
                      json={"device_id": id})
    dprint(r.content.decode("utf-8"))

    events = r.content.decode("utf-8").split(",")
    res = []
    i = 0
    code = None
    value = None
    while i < len(events):
        if i % 2 == 0:
            code = events[i]
        else:
            value = float(events[i])
            res.append((code, value))
        i += 1
    dprint(res)
    return res


def push_events(id, code, value):
    r = requests.post(server + "push_event",
                      json={"device_id": id, "event_code": code, "event_value": value})
    dprint(r.content)


# Worker
def worker(id):
    # Register Device
    register_device(id)
    assign_device_to_region(id, id_to_region(id))

    # States
    current = 5
    voltage = 5 

    c_deviation = deviation()
    v_deviation = deviation()

    # Event Loop
    while True:
        send_telemetries(id, current + c_deviation, voltage + v_deviation)
        events = pull_events(id)

        for e in events:
            if e[0] == "current":
                current = e[1]
            if e[0] == "voltage":
                voltage = e[1]
        
        c_deviation = deviation()
        v_deviation = deviation()



        time.sleep(1)

workers = []

for i in range(counts):
  t = Thread(target=worker, args=(id_pool[i],))
  t.start()
  workers.append(t)
  time.sleep(random.uniform(0, 0.5))
  print("Worker " + str(i) + " spawned.")


for t in workers:
  t.join()

print("Workers finished.")
