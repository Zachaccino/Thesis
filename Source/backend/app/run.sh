#!/bin/sh

python init.py

python executor.py &
python executor.py &
python executor2.py &
python executor2.py &


gunicorn -w 8 --threads 8 -b 0.0.0.0:8000 wsgi:app
