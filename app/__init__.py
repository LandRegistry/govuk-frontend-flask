from typing import Type

from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect  # type: ignore[import]
from govuk_frontend_wtf.main import WTFormsHelpers  # type: ignore[import]
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config

# Initialize Flask extensions. These are initialized here for easier access.
csrf: CSRFProtect = CSRFProtect()
db: SQLAlchemy = SQLAlchemy()
limiter: Limiter = Limiter(get_remote_address, default_limits=["2 per second", "60 per minute"])
migrate: Migrate = Migrate()
oauth = OAuth()
sess = Session()


def create_app(config_class: Type[Config] = Config) -> Flask:
    """Create and configure the Flask application.

    Args:
        config_class: The configuration class to use (defaults to `Config`).

    Returns:
        A configured Flask application instance.
    """
    app: Flask = Flask(__name__)  # type: ignore[assignment]
    app.config.from_object(config_class)
    app.jinja_env.globals["govukRebrand"] = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True

    # Configure Jinja2 template loader to search in multiple locations.
    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),  # Load templates from the 'app' package.
            PrefixLoader(
                {
                    "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                    "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
                }
            ),
        ]
    )

    # Use ProxyFix middleware to handle proxies correctly.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)  # type: ignore[method-assign]

    # Initialize Flask extensions
    csrf.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)
    oauth.init_app(app)
    sess.init_app(app)
    WTFormsHelpers(app)

    oauth.register(
        name="one_login",
        client_id="HGIOgho9HIRhgoepdIOPFdIUWgewi0jw",
        authorize_url="http://localhost:3000/authorize",  # browser uses localhost
        access_token_url="http://govuk-one-login:3000/token",  # container uses Docker DNS
        jwks_uri="http://govuk-one-login:3000/.well-known/jwks.json",
        client_kwargs={"scope": "openid email phone"},
    )

    # Register blueprints. These define different sections of the application.
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app


from app import models  # noqa: E402,F401
