from database import Database
import time
from redis import Redis
from rq import Queue
from workers import *

before = 0
after = 0

def start():
    global before
    before = time.time()

def stop():
    after = time.time()
    print((after-before)*1000)


# Connection establishment is quick.
start()
deploy = False
development_address = "127.0.0.1"
deployment_address = "3.24.141.26"
server_address = deployment_address if deploy else development_address
db_address = 'mongodb://' + server_address + ':27017/'
db = Database(db_address, "hyperlynk", "OnePurpleParrot")
db.connect()
q = Queue(connection=Redis(server_address, 6379))
stop()

# Insert data is really slow.
start()
db.insert_telemetry("AZDpXvKC", 10, 10, 10, 10)
#q.enqueue(add_telemetry_worker, server_address, "AZDpXvKC", 10, 10, 10, 10)
stop()
