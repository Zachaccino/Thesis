FROM python:3

WORKDIR /usr/src/app

COPY ./mcu.py .
COPY ./mcu_ids .
COPY ./mcu_regions .

RUN pip install requests

CMD [ "python", "./mcu.py" ]
