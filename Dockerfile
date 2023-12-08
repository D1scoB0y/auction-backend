FROM python:3.10-slim-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY r.txt .

RUN pip install --no-cache-dir --upgrade -r r.txt

COPY . /app
