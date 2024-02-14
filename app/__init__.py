from flask import Flask
from flask_assets import Bundle, Environment
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

from config import Config

assets = Environment()
compress = Compress()
csrf = CSRFProtect()
limiter = Limiter(get_remote_address, default_limits=["2 per second", "60 per minute"])
talisman = Talisman()


def create_app(config_class=Config):
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

    # Set content security policy
    csp = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
            "'sha256-GUQ5ad8JK5KmEWmROf3LZd9ge94daqNvd8xy9YS1iDw='",
            "'sha256-EOlYC7YurunqHZxQoZ/zL5TKc/rPajg45h85KVyb5So='",
        ],
    }

    # Set permissions policy
    permissions_policy = {
        "accelerometer": "()",
        "ambient-light-sensor": "()",
        "autoplay": "()",
        "battery": "()",
        "camera": "()",
        "cross-origin-isolated": "()",
        "display-capture": "()",
        "document-domain": "()",
        "encrypted-media": "()",
        "execution-while-not-rendered": "()",
        "execution-while-out-of-viewport": "()",
        "fullscreen": "()",
        "geolocation": "()",
        "gyroscope": "()",
        "keyboard-map": "()",
        "magnetometer": "()",
        "microphone": "()",
        "midi": "()",
        "navigation-override": "()",
        "payment": "()",
        "picture-in-picture": "()",
        "publickey-credentials-get": "()",
        "screen-wake-lock": "()",
        "sync-xhr": "()",
        "usb": "()",
        "web-share": "()",
        "xr-spatial-tracking": "()",
        "clipboard-read": "()",
        "clipboard-write": "()",
        "gamepad": "()",
        "speaker-selection": "()",
        "conversion-measurement": "()",
        "focus-without-user-activation": "()",
        "hid": "()",
        "idle-detection": "()",
        "interest-cohort": "()",
        "serial": "()",
        "sync-script": "()",
        "trust-token-redemption": "()",
        "unload": "()",
        "window-management": "()",
        "vertical-scroll": "()",
    }

    # Initialise app extensions
    assets.init_app(app)
    compress.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    talisman.init_app(app, content_security_policy=csp, permissions_policy=permissions_policy)
    WTFormsHelpers(app)

    # Create static asset bundles
    css = Bundle("src/css/*.css", filters="cssmin", output="dist/css/custom-%(version)s.min.css")
    js = Bundle("src/js/*.js", filters="jsmin", output="dist/js/custom-%(version)s.min.js")
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
