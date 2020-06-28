# Containers Used

The following is a list of containers used in the backend. They needs to be
composed together with the backend container.

1. `mysql`


# Useful Commands

## MySQL

Installation: `docker pull mysql:5.7`

Running `mysql` in detach mode: `docker run -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456789 -e MYSQL_DATABASE=BackendDB -d --name BackendDB mysql:5.7`

Viewing `mysql` logs: `docker logs BackendDB`


## Gunicorn

Running the app `gunicorn -w 2 --threads 2 -b 0.0.0.0:8080 wsgi:app`


## My App

Runnign the app `docker run -p 8000:8080 --detach --name backend backend:1.0`
