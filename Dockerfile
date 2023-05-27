# pull official base image
FROM python:3.10.7-slim-buster

# install redis
RUN apt-get update && apt-get install -y redis-server

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /app 

CMD ["bash", "-c", "redis-server --daemonize yes && nohup celery -A make_celery worker --concurrency=2 & gunicorn --bind 0.0.0.0:5000 run:app"]