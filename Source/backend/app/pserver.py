import pulsar

client = pulsar.Client('pulsar://localhost:6650')
producer = client.create_producer('telemetry_update')

for i in range(10):
    producer.send(('hello-pulsar-%d' % i).encode('utf-8'))

client.close()