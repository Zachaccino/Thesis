import pymongo

client = pymongo.MongoClient('mongodb://hyperlynk.zachaccino.me:27017/', username="hyperlynk", password="OnePurpleParrot")
db = client['hyperlynkdb']

device_id = "IOfaSZKA"

telemetries = db.devices.find_one({"device_id": device_id})["aggregate_telemetries"]

lines = [["Time (Minute)", "CurrentIn", "VoltageIn", "CurrentOut", "VoltageOut"]]


for i, t in enumerate(telemetries):
    line = []
    line.append(str(i))
    line.append(str(t["current_in"]))
    line.append(str(t["voltage_in"]))
    line.append(str(t["current_out"]))
    line.append(str(t["voltage_out"]))
    lines.append(line)

out = open("telemetries.csv", "w+")

for l in lines:
    out.write(",".join(l) + "\n")

out.close()