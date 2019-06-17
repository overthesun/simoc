FROM ubuntu:18.04

MAINTAINER Iurii Milovanov "duruku@gmail.com"

ARG APP_PORT
ARG DB_TYPE
ARG DB_HOST
ARG DB_PORT
ARG DB_NAME
ARG DB_USER
ARG DB_PASSWORD

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev python3-setuptools python3-mysqldb

COPY . /simoc
WORKDIR /simoc

RUN python3 -m pip install -r requirements.txt

ENV APP_PORT ${APP_PORT}
ENV DB_TYPE ${DB_TYPE}
ENV DB_HOST ${DB_HOST}
ENV DB_PORT ${DB_PORT}
ENV DB_NAME ${DB_NAME}
ENV DB_USER ${DB_USER}
ENV DB_PASSWORD ${DB_PASSWORD}

EXPOSE ${APP_PORT}

ENTRYPOINT [ "/bin/bash" ]
CMD ["run.sh"]
