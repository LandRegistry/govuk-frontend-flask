import os

import redis


class Config(object):
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE")
    DEPARTMENT_NAME = os.environ.get("DEPARTMENT_NAME")
    DEPARTMENT_URL = os.environ.get("DEPARTMENT_URL")
    ONE_LOGIN_ACCESS_TOKEN_URL = os.environ.get("ONE_LOGIN_ACCESS_TOKEN_URL")
    ONE_LOGIN_AUTHORIZE_URL = os.environ.get("ONE_LOGIN_AUTHORIZE_URL")
    ONE_LOGIN_CLIENT_ID = os.environ.get("ONE_LOGIN_CLIENT_ID")
    ONE_LOGIN_JWKS_URL = os.environ.get("ONE_LOGIN_JWKS_URL")
    ONE_LOGIN_PRIVATE_KEY_PATH = os.environ.get("ONE_LOGIN_PRIVATE_KEY_PATH")
    ONE_LOGIN_PUBLIC_TOKEN_URL = os.environ.get("ONE_LOGIN_PUBLIC_TOKEN_URL")
    ONE_LOGIN_USERINFO_URL = os.environ.get("ONE_LOGIN_USERINFO_URL")
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STORAGE_URI = os.environ.get("VALKEY_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SERVICE_NAME = os.environ.get("SERVICE_NAME")
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE")
    SERVICE_URL = os.environ.get("SERVICE_URL")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    SESSION_REDIS = redis.from_url(os.environ.get("VALKEY_URL"))
    SESSION_TYPE = "redis"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


class TestConfig(Config):
    CONTACT_EMAIL = "test@example.com"
    CONTACT_PHONE = "08081570000"
    DEBUG = True
    DEPARTMENT_NAME = "Department of Magical Law Enforcement"
    DEPARTMENT_URL = "https://www.example.com/"
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STORAGE_URI = "memory://"
    SECRET_KEY = "4f378500459bb58fecf903ea3c113069f11f150b33388f56fc89f7edce0e6a84"  # nosec B105
    SERVICE_NAME = "Apply for a wand licence"
    SERVICE_PHASE = "Beta"
    SERVICE_URL = "https://wand-licence.service.gov.uk"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
