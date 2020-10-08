FROM python:3.8

WORKDIR /usr/src/app

COPY ./app/hub.py .
COPY ./app/settings.py .
COPY ./app/sock_0.py .
COPY ./app/sock_1.py .

COPY ./app/run.sh .

COPY ./requirements.txt .

EXPOSE 5000
EXPOSE 5001

RUN chmod +x ./run.sh
RUN pip install -r requirements.txt

CMD [ "./run.sh" ]
