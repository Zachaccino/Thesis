#!/bin/sh

python sock_0.py &
python sock_1.py &

echo "Sleeping 5 Seconds"
sleep 5

python hub.py
