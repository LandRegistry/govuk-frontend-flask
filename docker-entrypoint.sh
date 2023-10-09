#!/bin/bash
source venv/bin/activate
exec gunicorn --certfile cert.pem --keyfile key.pem -b :5000 --access-logfile - --error-logfile - govuk-frontend-flask:app