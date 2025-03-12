FROM python:3.13-slim

RUN addgroup --system app && adduser --system --group app

# Set environment variables
ENV FLASK_APP=govuk-frontend-flask.py \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /home/app

COPY --chown=app:app govuk-frontend-flask.py config.py requirements.txt ./

RUN pip install -r requirements.txt

COPY --chown=app:app app app

USER app