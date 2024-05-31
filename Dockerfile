FROM python:3.12-slim

RUN useradd containeruser

WORKDIR /home/containeruser

# Set environment variables
ENV FLASK_APP=govuk-frontend-flask.py \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY app app
COPY govuk-frontend-flask.py config.py requirements.txt ./
RUN pip install -r requirements.txt \
    && chown -R containeruser:containeruser ./

USER containeruser