FROM python:3

WORKDIR /usr/src/app

COPY ./app/settings.py .
COPY ./app/run.py .
COPY ./requirements.txt .

RUN pip install -r requirements.txt

CMD [ "python", "run.py" ]
