FROM python:3

WORKDIR /usr/src/app

COPY ./mcu.py .
COPY ./mcu_ids .
COPY ./mcu_regions .
COPY ./settings.py .

RUN pip install requests

CMD [ "python", "./mcu.py" ]
