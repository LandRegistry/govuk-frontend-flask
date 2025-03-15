FROM python:3.13-slim

RUN addgroup --system appgroup && adduser --system --group appuser

# Set environment variables
ENV FLASK_APP=govuk-frontend-flask.py \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /home/app

COPY --chown=appuser:appgroup govuk-frontend-flask.py config.py requirements.txt ./

RUN pip install -r requirements.txt

COPY --chown=appuser:appgroup app app

USER appuser

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-w", "4", "--access-logfile", "-", "govuk-frontend-flask:app"]