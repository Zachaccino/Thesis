FROM python:3.8

WORKDIR /usr/src/app

COPY ./app/conncount.py .
COPY ./app/database.py .
COPY ./app/executor.py .
COPY ./app/executor2.py .
COPY ./app/server.py .
COPY ./app/settings.py .
COPY ./app/worker.py .
COPY ./app/wsgi.py .
COPY ./app/init.py .

COPY ./app/run.sh .

COPY ./requirements.txt .

EXPOSE 8000

RUN chmod +x ./run.sh
RUN pip install -r requirements.txt

CMD [ "./run.sh" ]
