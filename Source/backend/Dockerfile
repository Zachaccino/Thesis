FROM python:3

WORKDIR /usr/src/app

COPY ./app/server.py .
COPY ./app/wsgi.py .
COPY ./app/database.py .
COPY ./app/run.sh .

EXPOSE 8000

RUN chmod +x ./run.sh
RUN pip install flask
RUN pip install flask_cors
RUN pip install flask_sqlalchemy
RUN pip install pymongo
RUN pip install gunicorn

CMD [ "./run.sh" ]
