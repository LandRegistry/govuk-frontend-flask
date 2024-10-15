from typing import Type

from flask import Flask
from flask_assets import Bundle, Environment
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config

assets = Environment()
csrf = CSRFProtect()
limiter = Limiter(
    get_remote_address,
    default_limits=["2 per second", "60 per minute"],
)


def create_app(config_class: Type[Config] = Config) -> Flask:
    app = Flask(__name__, static_url_path="/assets")
    app.config.from_object(config_class)
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True
    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PrefixLoader(
                {
                    "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                    "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
                }
            ),
        ]
    )
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    # Initialise app extensions
    assets.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    WTFormsHelpers(app)

    # Create static asset bundles
    css = Bundle(
        "src/css/*.css",
        filters="cssmin",
        output="dist/css/custom-%(version)s.min.css",
    )
    js = Bundle(
        "src/js/*.js",
        filters="jsmin",
        output="dist/js/custom-%(version)s.min.js",
    )
    if "css" not in assets:
        assets.register("css", css)
    if "js" not in assets:
        assets.register("js", js)

    # Register blueprints
    from app.demos import bp as demo_bp
    from app.main import bp as main_bp

    app.register_blueprint(demo_bp)
    app.register_blueprint(main_bp)

    return app
