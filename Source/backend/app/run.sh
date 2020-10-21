#!/bin/sh

python init.py

python executor.py &
gunicorn -w 2 --threads 2 -b 0.0.0.0:8000 wsgi:app
