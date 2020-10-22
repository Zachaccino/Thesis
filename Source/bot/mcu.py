import requests
import random
import time
from threading import Thread
import os
from settings import BACKEND_ADDRESS, COUNT


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
    requests.post(BACKEND_ADDRESS + "/register_region", json={"region_name": region})


for r in region_pool:
    register_regions(r)


def id_to_region(id):
    return region_pool[sum([ord(c) for c in id]) % len(region_pool)]


def register_device(id):
    requests.post(BACKEND_ADDRESS + "/register_device",
                      json={"device_id": id})


def assign_device_to_region(id, region):
    requests.post(BACKEND_ADDRESS + "/assign_to_region",
                      json={"device_id": id, "region_name": region})


def deviation():
    return random.randint(-2, 2) + random.uniform(-0.5, 0.5)


def send_telemetries(id, current_in, voltage_in, current_out, voltage_out):
    r = requests.post(BACKEND_ADDRESS + "/add_telemetry",
                      json={"device_id": id, "current_in": current_in, "voltage_in": voltage_in, "current_out": current_out, "voltage_out": voltage_out})
    return r


# Worker
def worker(id):
    # Register Device
    register_device(id)
    assign_device_to_region(id, id_to_region(id))

    # States
    c_in = 5
    v_in = 30
    c_out = 4
    v_out = 26

    c_in_deviation = deviation()
    v_in_deviation = deviation()
    c_out_deviation = deviation()
    v_out_deviation = deviation()

    # Event Loop
    while True:
        events_csv = send_telemetries(id, c_in + c_in_deviation, v_in + v_in_deviation, c_out + c_out_deviation, v_out + v_out_deviation).content.decode("utf-8").split(",")
        events = []
        i = 0
        code = None
        value = None
        while i < len(events_csv):
            if i % 2 == 0:
                code = events_csv[i]
            else:
                value = float(events_csv[i])
                events.append((code, value))
            i += 1

        for e in events:
            if e[0] == "current":
                c_in = e[1]
                c_out = e[1] - 1
            if e[0] == "voltage":
                v_in = e[1]
                v_out = e[1] - 1
        
        c_in_deviation = deviation()
        v_in_deviation = deviation()
        c_out_deviation = deviation()
        v_out_deviation = deviation()
        time.sleep(1)

workers = []

for i in range(COUNT):
  t = Thread(target=worker, args=(id_pool[i],))
  t.start()
  workers.append(t)
  time.sleep(random.uniform(0, 0.5))
  print("Worker " + str(id_pool[i]) +  " spawned at location " + id_to_region(id_pool[i]))


for t in workers:
  t.join()

print("Workers finished.")
