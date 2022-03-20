from settings import REDIS_ADDRESS, REDIS_PORT, TARGET_JOB_PRIORITIES
from redis import Redis
from rq import Worker, Queue, Connection


while True:
    redis_conn = Redis(REDIS_ADDRESS, REDIS_PORT+1)
    try:
        with Connection(redis_conn):
            worker = Worker(map(Queue, TARGET_JOB_PRIORITIES))
            worker.work()
    except:
        print("Exception Occur in Worker")

    redis_conn.close()
