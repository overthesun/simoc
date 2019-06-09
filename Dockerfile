FROM ubuntu:18.04

MAINTAINER Iurii Milovanov "duruku@gmail.com"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev python3-mysqldb libpq-dev

COPY . /app
WORKDIR /app

RUN python3 -m pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT [ "/bin/bash" ]

CMD [ "reset_and_run.sh" ]
