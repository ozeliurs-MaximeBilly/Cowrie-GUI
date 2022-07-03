FROM python:latest

COPY ./www /app

RUN chmod -R 777 /app

RUN cd /app/data && wget "http://cf.ozeliurs.com/IP2LOCATION-LITE-DB11.IPV6.BIN"

RUN pip3 install -r /app/requirements.txt

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:8000/health || exit 1

WORKDIR /app

ENTRYPOINT ["bash", "/app/gunicorn_starter.sh"]
