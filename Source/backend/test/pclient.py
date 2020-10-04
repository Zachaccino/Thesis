import pulsar

client = pulsar.Client('pulsar://localhost:6650')
consumer = client.subscribe('telemetry_update', subscription_name='sock1')

while True:
    msg = consumer.receive()
    print("Received message: '%s'" % msg.data())
    consumer.acknowledge(msg)

client.close()