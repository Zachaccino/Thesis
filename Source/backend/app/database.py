import pymongo
import datetime

# A class for interacting with database.
class Database:
    def __init__(self, addr, username, password):
        self.addr = addr
        self.username = username
        self.password = password
        self.client = None
        self.db = None

    # Database Lifecycles
    def connect(self):
        self.client = pymongo.MongoClient(
            self.addr, username=self.username, password=self.password)
        self.db = self.client['hyperlynkdb']

    def init(self):
        if not self.region_exist('Awaiting Allocation'):
            self.insert_region('Awaiting Allocation')

    def disconnect(self):
        return

    # Insertion
    def insert_region(self, name):
        self.db.regions.insert_one({'name': name})

    # Existance
    def device_exist(self, uid):
        return self.db.devices.count_documents({'device_id': uid}) != 0

    def region_exist(self, name):
        return self.db.regions.count_documents({'name': name}) != 0

    # Counter
    def count_operating(self):
        return self.db.devices.count_documents({'status': 'Online'})

    def count_offline(self):
        return self.db.devices.count_documents({'status': 'Offline'})

    def count_failure(self):
        return self.db.devices.count_documents({'status': 'Failure'})

    def count_region(self):
        return self.db.regions.count_documents({})

    def count_device(self):
        return self.db.devices.count_documents({})

    # Lenses and Simple Computations
    def current_out(self, device, time=-1):
        return device['aggregate_telemetries'][time]['current_out'] if device['aggregate_telemetries'] else 0

    def voltage_out(self, device, time=-1):
        return device['aggregate_telemetries'][time]['voltage_out'] if device['aggregate_telemetries'] else 0

    def current_in(self, device, time=-1):
        return device["aggregate_telemetries"][time]["current_in"] if device['aggregate_telemetries'] else 0

    def voltage_in(self, device, time=-1):
        return device['aggregate_telemetries'][time]['voltage_in'] if device['aggregate_telemetries'] else 0

    def power_out(self, device, time=-1):
        return self.current_out(device, time) * self.voltage_out(device, time)

    def power_in(self, device, time=-1):
        return self.current_in(device, time) * self.voltage_in(device, time)

    def regions(self):
        return self.db.regions.find()

    def devices(self, region_name=None, n_latest_records=1):
        if region_name:
            return self.db.devices.find(
                {'region': region_name},
                {'aggregate_telemetries': {'$slice': -n_latest_records}}
            )
        else:
            return self.db.devices.find(
                {},
                {'aggregate_telemetries': {'$slice': -n_latest_records}}
            )
    
    def find_device(self, device_id, aggregation=True, n_latest_records=1):
        tag = "aggregate_telemetries" if aggregation else "telemetries"
        return self.db.devices.find_one(
            {"device_id": device_id},
            {
                tag: {'$slice': -n_latest_records},
            }
        )

    # Power
    def total_power(self, region_name=None):
        pwr_in = 0
        pwr_out = 0
        for d in self.devices(region_name):
            pwr_in += self.power_in(d)
            pwr_out += self.power_out(d)
        return round(pwr_in, 2), round(pwr_out, 2)

    def total_power_by_region(self):
        region_names = []
        pwr_ins = []
        pwr_outs = []
        for r in self.regions():
            pwr_in, pwr_out = self.total_power(r['name'])
            region_names.append(r['name'])
            pwr_ins.append(round(pwr_in, 2))
            pwr_outs.append(round(pwr_out, 2))
        return region_names, pwr_ins, pwr_outs

    def total_power_by_device(self, region_name=None):
        device_ids = []
        pwr_ins = []
        pwr_outs = []
        for d in self.devices(region_name):
            device_ids.append(d['device_id'])
            pwr_ins.append(round(self.power_in(d), 2))
            pwr_outs.append(round(self.power_out(d), 2))
        return device_ids, pwr_ins, pwr_outs

    # Details
    def basic_graph(self, label, size, prefix="", postfix=""):
        graph = [{"id": label, "data": []}]
        for i in range(size):
            graph[0]["data"].append({"x": prefix + str(size - i) + postfix, "y": 0})
        return graph
    
    def stack_graph(self, graph1, graph2):
        return graph1 + graph2

    def set_point(self, graph, index, y, stack=0, x=None):
        graph[stack]["data"][index]["y"] = y
        if x:
            graph[stack]["data"][index]["x"] = x


    def device_detail_graphs(self, device_id, aggregation=False, n_latest_records=1):
        postfix = " min ago"
        if not aggregation:
            postfix = " sample"
            n_latest_records = 60
            

        current = self.stack_graph(self.basic_graph("Input", n_latest_records, postfix=postfix), self.basic_graph("Output", n_latest_records, postfix=postfix))
        pwr = self.stack_graph(self.basic_graph("Input", n_latest_records, postfix=postfix), self.basic_graph("Output", n_latest_records, postfix=postfix))
        voltage = self.stack_graph(self.basic_graph("Input", n_latest_records, postfix=postfix), self.basic_graph("Output", n_latest_records, postfix=postfix))
        efficiency = self.basic_graph("Efficiency", n_latest_records, postfix=postfix)


        dev = self.find_device(device_id, aggregation, n_latest_records)
        tag = "aggregate_telemetries" if aggregation else "telemetries"
        index = n_latest_records - len(dev[tag])
        
        for t in dev[tag]:
            self.set_point(current, index, round(t["current_in"], 2), 0)
            self.set_point(current, index, round(t["current_out"], 2), 1)
            self.set_point(voltage, index, round(t["voltage_in"], 2), 0)
            self.set_point(voltage, index, round(t["voltage_out"], 2), 1)
            self.set_point(pwr, index, round(t["current_in"] * t["voltage_in"], 2), 0)
            self.set_point(pwr, index, round(t["current_out"] * t["voltage_out"], 2), 1)
            self.set_point(efficiency, index, round((t["current_out"] * t["voltage_out"]) / (t["current_in"] * t["voltage_in"]+0.00001) * 100, 2))
            index += 1

        return {
            "device_id": dev["device_id"],
            "region": dev["region"],
            "status": dev["status"],
            "current_graph": current,
            "voltage_graph": voltage,
            "pwr_graph": pwr,
            "efficiency_graph": efficiency
        }
    
    def insert_event(self, device_id, event_code, event_value):
        self.db.devices.update_one(
            {'device_id': device_id},
            {
                '$push': {
                    'events': {
                        'event_code': event_code,
                        'event_value': event_value
                    }
                }
            }
        )
    
    def insert_telemetry(self, device_id, current_in, voltage_in, current_out, voltage_out):
        rec_time = datetime.datetime.utcnow()

        self.db.devices.update_one(
            {'device_id': device_id},
            {
                '$push': {
                    'telemetries': {
                        'current_in': current_in,
                        'voltage_in': voltage_in,
                        'current_out': current_out,
                        'voltage_out': voltage_out,
                        'datetime': rec_time
                    }
                },
                '$set': {
                    'status': "Online",
                    'last_modified': rec_time
                }
            }
        )
    
    def serialise_events(self, device_id):
        events = self.db.devices.find_one({'device_id': device_id})['events']

        self.db.devices.update_one(
            {'device_id': device_id},
            {
                '$set': {
                    'events': []
                }
            }
        )
        event_stream = ""
        for e in events:
            event_stream += e["event_code"] + ","
            event_stream += str(e["event_value"]) + ","

        return event_stream.rstrip(",")

    def set_device_online(self, device_id):
        self.db.devices.update_one(
            {'device_id': device_id},
            {
                '$set': {
                    'status': "Online"
                }
            }
        )
    
    def insert_device(self, new_id):
        self.db.devices.insert_one({
            'device_id': new_id,
            'status': "Online",
            'events': [],
            'aggregate_telemetries': [],
            'telemetries': [],
            'region': "Awaiting Allocation",
            'last_modified': datetime.datetime.utcnow()
        })

    def assign_device_to_region(self, device_id, region_name):
        self.db.devices.update(
            {'device_id': device_id},
            {
                '$set': {
                    'region': region_name
                }
            }
        )
    
    def to_csv(self, device_id):
        telemetries = self.db.devices.find_one({"device_id": device_id})["aggregate_telemetries"]
        lines = [["Time (Minute)", "CurrentIn", "VoltageIn", "CurrentOut", "VoltageOut"]]
        csv_string = ""

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
            csv_string += (",".join(l) + "<br>")
        
        return csv_string

    def server_status(self):
        return 'Normal'

    def system_health(self):
        return 'Normal'
