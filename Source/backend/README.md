# Backend

This is a backend server.


# Dependencies

Dependencies are specified in the `requirements.txt`. You can install the dependencies through the following command.

```
pip3 install -r requirements.txt
```


# Structure

The program is inside the `./app` folder and supporting documents are under this directory.


# Settings

The configurable settings are placed in the `settings.py`.


# For Development

You can run this program by using.

```
cd app
python3 server.py
```

Please make sure your `DEVELOPMENT_ADDRESS` inside `settings.py` is configured properly and the `DEPLOY` is set to `False`.


# For Deployment to Docker

This program is designed to run inside the docker container. Please make sure your `SERVER_ADDRESS` inside `settings.py` is configured properly and the `DEPLOY` is set to `True`.

You need to build the image first.

`PLACEHOLDER`

Then, you can run it inside Docker.

`PLACEHOLDER`
