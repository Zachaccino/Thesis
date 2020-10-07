FROM python:3

WORKDIR /usr/src/app

COPY ./run1.py .
COPY ./run2.py .
COPY ./run.sh .

RUN chmod +x ./run.sh

CMD [ "./run.sh" ]
