FROM node:jod-alpine as build

COPY package*.json ./

RUN npm install

FROM python:3.13-slim

RUN useradd appuser

WORKDIR /home/appuser

# Set environment variables
ENV FLASK_APP=govuk-frontend-flask.py \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY app app
COPY govuk-frontend-flask.py config.py requirements.txt ./
RUN pip install -r requirements.txt \
    && chown -R appuser:appuser ./

USER appuser