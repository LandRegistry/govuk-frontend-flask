FROM python:3.13-slim

RUN addgroup --system app && adduser --system --group app

# Set environment variables
ENV FLASK_APP=govuk-frontend-flask.py \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /home/app

COPY govuk-frontend-flask.py config.py requirements.txt ./

RUN pip install -r requirements.txt \
    && chown -R app:app ./

COPY app app

USER app