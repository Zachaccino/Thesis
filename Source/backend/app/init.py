from database import Database
from conncount import ConnCount
from settings import DB_ADDRESS, DB_USERNAME, DB_PASSWORD, REDIS_ADDRESS, REDIS_PORT


# Setting up Mongo DB.
db = Database(DB_ADDRESS, DB_USERNAME, DB_PASSWORD)
db.connect()
db.init()

# Setting up ConnCount.
cc = ConnCount(REDIS_ADDRESS, REDIS_PORT)
cc.connect()
cc.reset()
