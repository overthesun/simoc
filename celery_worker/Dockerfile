FROM ubuntu:18.04

MAINTAINER Iurii Milovanov "duruku@gmail.com"

ARG DB_TYPE
ARG DB_HOST
ARG DB_PORT
ARG DB_NAME
ARG DB_USER
ARG DB_PASSWORD
ENV DB_TYPE ${DB_TYPE}
ENV DB_HOST ${DB_HOST}
ENV DB_PORT ${DB_PORT}
ENV DB_NAME ${DB_NAME}
ENV DB_USER ${DB_USER}
ENV DB_PASSWORD ${DB_PASSWORD}

ARG REDIS_HOST
ARG REDIS_PORT
ARG REDIS_PASSWORD
ENV REDIS_HOST ${REDIS_HOST}
ENV REDIS_PORT ${REDIS_PORT}
ENV REDIS_PASSWORD ${REDIS_PASSWORD}

ARG CELERY_THREADS
ENV CELERY_THREADS ${CELERY_THREADS}

ENV NO_FLASK 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    python3-setuptools \
    python3-mysqldb

COPY ./celery_worker/requirements.txt /simoc/celery_worker/requirements.txt
RUN python3 -m pip install -r /simoc/celery_worker/requirements.txt

COPY . /simoc

WORKDIR /simoc

ENTRYPOINT [ "/bin/bash" ]
CMD ["start_worker.sh"]
