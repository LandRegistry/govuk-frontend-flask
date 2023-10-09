#!/bin/bash
exec gunicorn --reload --certfile cert.pem --keyfile key.pem -b :5000 --access-logfile - --error-logfile - govuk-frontend-flask:app