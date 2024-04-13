FROM python:3.11.8

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y postgresql-client

WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt

COPY . /code/

COPY init_triggers.sql /code/
COPY run_sql_script.sh /code/run_sql_script.sh

EXPOSE 8000
