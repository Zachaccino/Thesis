#!/bin/sh
echo "10 seconds delay started..."

gunicorn -w 2 --threads 2 -b 0.0.0.0:8000 wsgi:app
