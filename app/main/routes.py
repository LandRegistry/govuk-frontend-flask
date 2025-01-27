import json
from typing import Optional, Tuple, Union

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
    # Initialize cookie policy. Defaults to rejecting all cookies.
    cookies_policy: dict[str, str] = {"functional": "no", "analytics": "no"}

    if form.validate_on_submit():
        # Update cookie policy based on form submission.
        cookies_policy["functional"] = form.functional.data
        cookies_policy["analytics"] = form.analytics.data
        # Create flash message confirmation before rendering template
        flash("You've set your cookie preferences.", "success")
        # Create the response so we can set the cookie before returning
        response: Response = make_response(render_template("cookies.html", form=form))
        # Set the cookies_policy cookie in the response
        response.set_cookie(
            "cookies_policy",
            json.dumps(cookies_policy),
            max_age=31557600,  # One year
            secure=True,
            samesite="Lax",
        )
        return response
    elif request.method == "GET":
        # Retrieve existing cookie policy if present.
        cookies_string: Optional[str] = request.cookies.get("cookies_policy")
        if cookies_string:
            try:
                # Set cookie consent radios to current consent
                cookies_policy = json.loads(cookies_string)
                form.functional.data = cookies_policy["functional"]
                form.analytics.data = cookies_policy["analytics"]
            except json.JSONDecodeError:
                # If conset not previously set, use default "no" policy
                form.functional.data = cookies_policy["functional"]
                form.analytics.data = cookies_policy["analytics"]

    return render_template("cookies.html", form=form)


@bp.route("/privacy", methods=["GET"])
def privacy() -> str:
    """Render the privacy policy page."""
    return render_template("privacy.html")


@bp.app_errorhandler(HTTPException)
def handle_http_exception(error: HTTPException) -> Tuple[str, int]:
    """Handle HTTP exceptions and render appropriate error template."""
    return render_template(f"{error.code}.html"), error.code


@bp.app_errorhandler(CSRFError)
def handle_csrf_error(error: CSRFError) -> Response:
    """Handle CSRF errors and display a flash message."""
    flash("The form you were submitting has expired. Please try again.")
    return redirect(request.url)
