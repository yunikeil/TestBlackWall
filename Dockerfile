FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /binanceapp

WORKDIR /binanceapp

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY conf /binanceapp/conf
COPY src /binanceapp/src
COPY alembic.ini /binanceapp
COPY .env /binanceapp
