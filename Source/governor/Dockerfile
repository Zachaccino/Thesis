FROM python:3

ARG server_address
ENV SERVER_ADDRESS=server_address

WORKDIR /usr/src/app

COPY ./run.py .

RUN pip install pymongo

CMD [ "python", "./run.py" ]
