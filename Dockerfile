FROM ubuntu:18.04

MAINTAINER Iurii Milovanov "duruku@gmail.com"

ARG DB_TYPE
ARG PORT
ARG WORKERS

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev python3-setuptools python3-mysqldb \
    libssl-dev libffi-dev libpq-dev

COPY . /simoc
WORKDIR /simoc

RUN python3 -m pip install -r requirements.txt

ENV DB_TYPE ${DB_TYPE}
ENV PORT ${PORT}
ENV WORKERS ${WORKERS}

EXPOSE ${PORT}

ENTRYPOINT [ "/bin/bash" ]
CMD ["reset_and_run.sh"]
