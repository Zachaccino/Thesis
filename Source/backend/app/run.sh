#!/bin/sh

python init.py

python executor.py &
python executor.py &
python executor.py &
python executor.py &
python executor2.py &
python executor2.py &
python executor2.py &
python executor2.py &

gunicorn -w 4 --threads 4 -b 0.0.0.0:8000 wsgi:app
