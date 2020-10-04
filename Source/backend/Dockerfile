FROM python:3

WORKDIR /usr/src/app

COPY ./app/server.py .
COPY ./app/wsgi.py .
COPY ./app/database.py .
COPY ./app/run.sh .
COPY ./requirements.txt .

EXPOSE 8000

RUN chmod +x ./run.sh
RUN pip install -r requirements.txt

CMD [ "./run.sh" ]
