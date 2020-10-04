from redis import Redis
from rq import Worker, Queue, Connection


deploy = False
development_address = "127.0.0.1"
deployment_address = "3.24.141.26"
server_address = deployment_address if deploy else development_address


listen = ['high', 'default', 'low']
conn = Redis(server_address, 6379)


with Connection(conn):
    worker = Worker(map(Queue, listen))
    worker.work()