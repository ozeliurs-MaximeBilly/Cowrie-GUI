FROM python:latest

COPY ./www /app

RUN chmod -R 777 /app

RUN cd /app/data && wget "http://cf.ozeliurs.com/IP2LOCATION-LITE-DB11.IPV6.BIN"

RUN pip3 install -r /app/requirements.txt

WORKDIR /app

ENTRYPOINT ["bash", "/app/gunicorn_starter.sh"]
