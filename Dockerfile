FROM python:3.11-slim

RUN useradd containeruser

WORKDIR /home/containeruser

COPY app app
COPY govuk-frontend-flask.py config.py docker-entrypoint.sh requirements.txt ./
RUN pip install -r requirements.txt \
    && chmod +x docker-entrypoint.sh \
    && chown -R containeruser:containeruser ./

# Set environment variables
ENV CONTACT_EMAIL="[contact email]" \
    CONTACT_PHONE="[contact phone]" \
    DEPARTMENT_NAME="[name of department]" \
    DEPARTMENT_URL="[url of department]" \
    REDIS_URL="redis://redis:6379" \
    SECRET_KEY=3e48b821144547db5f22c7357431a093489450fcc4aad992ab9e1dd1a9d3b40d \
    SERVICE_NAME="[name of service]" \
    SERVICE_PHASE="[phase]" \
    SERVICE_URL="[url of service]"

USER containeruser

EXPOSE 5000
ENTRYPOINT ["./docker-entrypoint.sh"]