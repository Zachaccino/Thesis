#!/bin/sh

python init.py

python executor.py &
python executor.py &
python executor2.py &
python executor2.py &
python executor.py &
python executor.py &
python executor2.py &
python executor2.py &



gunicorn -w 6 --threads 6 -b 0.0.0.0:8000 wsgi:app
