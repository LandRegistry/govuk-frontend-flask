FROM python:3.11-slim

RUN useradd containeruser

WORKDIR /home/containeruser

COPY requirements.txt requirements.txt
RUN python -m venv venv \
    && venv/bin/pip install -r requirements.txt

# Generate HTTPS Cert
RUN openssl req -new -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/C=GB/ST=Devon/L=Plymouth/O=HM Land Registry/OU=DDaT/CN=localhost"

COPY app app
COPY govuk-frontend-flask.py config.py docker-entrypoint.sh cert.pem key.pem ./
RUN chmod +x docker-entrypoint.sh \
    && chown -R containeruser:containeruser ./

# Set environment variables
ENV CONTACT_EMAIL="[contact email]" \
    CONTACT_PHONE="[contact phone]" \
    DEPARTMENT_NAME="[name of department]" \
    DEPARTMENT_URL="[url of department]" \
    FLASK_APP=govuk-frontend-flask.py \
    FLASK_DEBUG=True \
    FLASK_RUN_PORT=5000 \
    REDIS_URL=memory:// \
    SECRET_KEY=3e48b821144547db5f22c7357431a093489450fcc4aad992ab9e1dd1a9d3b40d \
    SERVICE_NAME="[name of service]" \
    SERVICE_PHASE="[phase]" \
    SERVICE_URL="[url of service]"

USER containeruser

EXPOSE 5000
ENTRYPOINT ["./docker-entrypoint.sh"]