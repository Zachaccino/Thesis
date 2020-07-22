FROM python:3

WORKDIR /usr/src/app

COPY ./run.py .

RUN pip install pymongo

CMD [ "python", "./run.py" ]
