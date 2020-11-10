#!/bin/sh

python init.py

python executor.py &
python executor.py &
python executor.py &
python executor.py &
python executor.py &
python executor.py &
python executor.py &
python executor.py &
python executor.py &
python executor.py &
python executor.py &
python executor.py &

gunicorn -w 12 --threads 12 -b 0.0.0.0:8000 wsgi:app
