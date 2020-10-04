from settings import SERVER_ADDRESS, SERVER_PORT, TARGET_JOB_PRIORITIES
from redis import Redis
from rq import Worker, Queue, Connection

redis_conn = Redis(SERVER_ADDRESS, SERVER_PORT)

with Connection(redis_conn):
    worker = Worker(map(Queue, TARGET_JOB_PRIORITIES))
    worker.work()