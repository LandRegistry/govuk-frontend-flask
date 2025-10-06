from typing import Tuple, Union

from flask import Response, flash, make_response, redirect, render_template, request
from flask_wtf.csrf import CSRFError  # type: ignore
from werkzeug.exceptions import HTTPException

from app.main import bp
from app.main.forms import CookiesForm


@bp.route("/", methods=["GET"])
def index() -> str:
    """Render the index page."""
    return render_template("index.html")


@bp.route("/accessibility", methods=["GET"])
def accessibility() -> str:
    """Render the accessibility statement page."""
    return render_template("accessibility.html")


@bp.route("/cookies", methods=["GET", "POST"])
def cookies() -> Union[str, Response]:
    """Handle GET and POST requests for managing cookie preferences."""
    form: CookiesForm = CookiesForm()
    # Initialize cookie settings. Defaults to rejecting all cookies.
    functional: str = "no"
    analytics: str = "no"

    if form.validate_on_submit():
        # Update cookie settings based on form submission
        functional = form.functional.data
        analytics = form.analytics.data
        # Create flash message confirmation before rendering template
        flash("You've set your cookie preferences.", "success")
        # Create the response so we can set cookies before returning
        response: Response = make_response(render_template("cookies.html", form=form))

        # Set individual cookies in the response
        response.set_cookie("functional", functional, max_age=31557600, secure=True, samesite="Lax")
        response.set_cookie("analytics", analytics, max_age=31557600, secure=True, samesite="Lax")

        return response
    elif request.method == "GET":
        # Retrieve existing cookie settings if present
        functional = request.cookies.get("functional", "no")
        analytics = request.cookies.get("analytics", "no")

        # Pre-populate form with existing settings
        form.functional.data = functional
        form.analytics.data = analytics

    return render_template("cookies.html", form=form)


@bp.route("/privacy", methods=["GET"])
def privacy() -> str:
    """Render the privacy policy page."""
    return render_template("privacy.html")


@bp.route("/health", methods=["GET"])
def health() -> Response:
    """Route for healthchecks"""
    return make_response("OK", 200)


@bp.app_errorhandler(HTTPException)
def handle_http_exception(error: HTTPException) -> Response:
    """Handle HTTP exceptions and render appropriate error template."""
    return make_response(render_template(f"{error.code}.html"), error.code)


@bp.app_errorhandler(CSRFError)
def handle_csrf_error(error: CSRFError) -> Response:
    """Handle CSRF errors and display a flash message."""
    flash("The form you were submitting has expired. Please try again.")
    return make_response(redirect(request.path))
