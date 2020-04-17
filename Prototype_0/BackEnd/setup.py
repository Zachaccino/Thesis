from server import db

f = open("local.db", "w")
f.close()

db.create_all()
