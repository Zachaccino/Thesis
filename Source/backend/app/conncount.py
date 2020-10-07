from redis import Redis, WatchError
import json
import time

class ConnCount():
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.db = None
        self.top_level_key = 'conncount'

    # Connect to the database.
    def connect(self):
        self.db = Redis(self.addr, self.port)
    
    def reset(self):
        self.db.mset({self.top_level_key:json.dumps({})})

    # Get the value associated with the key.
    def get(self, sock_id):
        if not self.db:
            raise ConnectionError("RedisDict is not connected. Try `RedisDict.connect()`")
        value = None
        timestamp = None
        sock_id = str(sock_id)
        with self.db.pipeline() as p:
            while True:
                try:
                    p.watch(self.top_level_key)
                    if p.exists(self.top_level_key):
                        data = json.loads(p.get(self.top_level_key))[sock_id]
                        value = data["value"]
                        timestamp = data["timestamp"]
                    break
                except WatchError:
                    continue
                finally:
                    p.reset()
        return value, timestamp
    
    def get_all(self):
        if not self.db:
            raise ConnectionError("RedisDict is not connected. Try `RedisDict.connect()`")
        data = {}
        with self.db.pipeline() as p:
            while True:
                try:
                    p.watch(self.top_level_key)
                    if p.exists(self.top_level_key):
                        data = json.loads(p.get(self.top_level_key))
                    break
                except WatchError:
                    continue
                finally:
                    p.reset()
        return data

    # Update the value associated with the key.
    # Note, timestamp is in the format of unix time.
    def put(self, sock_id, count, timestamp=-1):
        if not self.db:
            raise ConnectionError("RedisDict is not connected. Try `RedisDict.connect()`")
        sock_id = str(sock_id)
        with self.db.pipeline() as p:
            while True:
                try:
                    p.watch(self.top_level_key)
                    last_update = -1
                    conncount = {}
                    if p.exists(self.top_level_key):
                        conncount = json.loads(p.get(self.top_level_key))
                        if sock_id in conncount:
                            last_update = conncount[sock_id]["timestamp"]
                    if last_update > timestamp:
                        break
                    if sock_id not in conncount:
                            conncount[sock_id] = {}
                    conncount[sock_id]["value"] = count
                    conncount[sock_id]["timestamp"] = timestamp
                    dump = json.dumps(conncount)
                    p.multi()
                    p.mset({self.top_level_key:dump})
                    p.execute()
                    break
                except WatchError:
                    continue
                finally:
                    p.reset()
                    
    # A convenient wrapper.
    def timestamp(self):
        return time.time()


from settings import REDIS_ADDRESS, REDIS_PORT

cc = ConnCount(REDIS_ADDRESS, REDIS_PORT)
cc.connect()
