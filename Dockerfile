FROM python:3.11-slim

RUN useradd containeruser

WORKDIR /home/containeruser

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt

# Generate HTTPS Cert
RUN openssl req -new -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/C=GB/ST=Devon/L=Plymouth/O=HM Land Registry/OU=DDaT/CN=localhost"

COPY app app
COPY govuk-frontend-flask.py config.py run.sh cert.pem key.pem ./
RUN chmod +x run.sh

ENV FLASK_APP govuk-frontend-flask.py

RUN chown -R containeruser:containeruser ./
USER containeruser

EXPOSE 5000
ENTRYPOINT ["./run.sh"]