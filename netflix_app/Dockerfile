## Alpine base image that contains python 3.7
#FROM python:3.7-alpine
#
#WORKDIR /srv/python-code-test
#COPY requirements.txt .
#
## Install system dependencies
## Install pip dependencies in the same layer
#RUN apk add --no-cache  \
#    bash build-base gcc && \
#    pip install --no-cache-dir pip-tools==5.2.1 && \
#    pip install --no-cache-dir -r requirements.txt
#
#gunicorn -w 4 -b 0.0.0.0:5000 run:create_app('dev')

FROM python:3.8

MAINTAINER Jerome <jkpaddick@gmail.com>

COPY . /usr/src/netflix_app
WORKDIR /usr/src/netflix_app

RUN pip install --no-cache-dir pip-tools==5.2.1 && \
    pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "/usr/src/netflix_app/wsgi.py"]