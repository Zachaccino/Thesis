FROM python:3

ARG server_address
ENV SERVER_ADDRESS=server_address

WORKDIR /usr/src/app

COPY ./mcu.py .
COPY ./mcu_ids .
COPY ./mcu_regions .

RUN pip install requests

CMD [ "python", "./mcu.py" ]
