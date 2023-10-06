#!/bin/bash
source venv/bin/activate
source build.sh
exec gunicorn --certfile cert.pem --keyfile key.pem -b :5000 --access-logfile - --error-logfile - govuk-frontend-flask:app