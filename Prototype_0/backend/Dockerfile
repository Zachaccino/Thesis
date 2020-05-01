FROM python:3

WORKDIR /usr/src/app

COPY ./app/server.py .
COPY ./app/wsgi.py .
COPY ./app/setup.py .
COPY ./app/run.sh .


EXPOSE 8080

RUN chmod +x ./run.sh
RUN pip install flask
RUN pip install flask_cors
RUN pip install flask_sqlalchemy
RUN pip install mysqlclient
RUN pip install gunicorn

CMD [ "./run.sh" ]
