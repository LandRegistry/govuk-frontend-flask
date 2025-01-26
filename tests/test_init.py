from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app
from config import Config


def test_create_app():
    app = create_app()
    assert isinstance(app, Flask)


def test_config_loaded_with_context():
    app = create_app()
    with app.app_context():
        assert app.config["DEBUG"] == Config.DEBUG


def test_config_loaded():
    app = create_app()
    assert app.config["DEBUG"] == Config.DEBUG


def test_jinja_env_config():
    app = create_app()
    assert app.jinja_env.lstrip_blocks is True
    assert app.jinja_env.trim_blocks is True


def test_middleware_applied():
    app = create_app()
    assert isinstance(app.wsgi_app, ProxyFix)


def test_extensions_initialized():
    app = create_app()
    # assert "assets" in app.extensions
    assert "csrf" in app.extensions
    assert "limiter" in app.extensions


def test_asset_bundles_registered():
    app = create_app()
    assert "css" in app.jinja_env.assets_environment._named_bundles
    assert "js" in app.jinja_env.assets_environment._named_bundles


def test_blueprints_registered():
    app = create_app()
    assert "demos" in app.blueprints
    assert "main" in app.blueprints
