FROM python:3.5.2

RUN apt-get update -y && \
    apt-get -y install python3-pip

WORKDIR /ml_blink_api

COPY . /ml_blink_api

RUN pip3 install -r requirements.txt
