FROM python:3.8

WORKDIR /usr/src/app

COPY ./aggregate.py . 
COPY ./liveness.py .
COPY ./settings.py .

COPY ./run.sh .

COPY ./requirements.txt .

RUN chmod +x ./run.sh
RUN pip install -r requirements.txt

CMD [ "./run.sh" ]
