FROM python:3

WORKDIR /usr/src/app

COPY ./aggregate.py . 
COPY ./liveness.py .
COPY ./settings.py .

COPY ./app/run.sh .

COPY ./requirements.txt .

RUN chmod +x ./run.sh
RUN pip install -r requirements.txt

CMD [ "./run.sh" ]
