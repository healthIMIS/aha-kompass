FROM debian:buster-slim

MAINTAINER Johannes Kreutz <ahaatlas@jkm-marburg.de>

ENV DEBIAN_FRONTEND noninteractive

ENV VERSION "1"

USER root

RUN apt-get update && apt-get install -y --no-install-recommends nginx mariadb-client python3 python3-pip python3-setuptools python3-flask python3-requests python3-flask-sqlalchemy python3-numpy python3-feedparser python3-bs4 python3-mysqldb python3-schedule uwsgi uwsgi-plugin-python3
RUN pip3 install wheel
RUN pip3 install visvalingamwyatt flask-jwt-extended
RUN apt-get purge -y python3-pip python3-setuptools
RUN apt-get autoremove -y

RUN mkdir /usr/local/bin/api
ADD api /usr/local/bin/api

COPY default /etc/nginx/sites-enabled/

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

CMD ["./entrypoint.sh"]
