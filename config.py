import os


class Config(object):
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE")
    DEPARTMENT_NAME = os.environ.get("DEPARTMENT_NAME")
    DEPARTMENT_URL = os.environ.get("DEPARTMENT_URL")
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SERVICE_NAME = os.environ.get("SERVICE_NAME")
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE")
    SERVICE_URL = os.environ.get("SERVICE_URL")
    DEBUG = os.environ.get("DEBUG", False)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
