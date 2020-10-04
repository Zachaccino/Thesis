# Redis Worker

This is a redis worker. It connects to a redis instance and execute jobs from the worker.


# Dependencies

This program has the following python package dependencies:

1. `rq`

You can install it by doing:

```
pip3 install -r requirements.txt
```

# Structure

The program is inside the `./app` folder and supporting documents are under this directory.

```
workers
├── DockerFile
├── README.md
├── app
│   ├── run.py
│   └── settings.py
└── requirements.txt
```

# Settings

The configurable settings are placed in the `settings.py`.


# For Development

You can run this program by using.

```
cd app
python3 run.py
```

Please make sure your `DEVELOPMENT_ADDRESS` inside `settings.py` is configured properly and the `DEPLOY` is set to `False`.

# For Deployment to Docker

This program is designed to run inside the docker container. Please make sure your `SERVER_ADDRESS` inside `settings.py` is configured properly and the `DEPLOY` is set to `True`.

You need to build the image first.

`docker build --tag worker:1.0 .`

Then, you can run it inside Docker.

`docker run --detach --name worker0 worker:1.0`
