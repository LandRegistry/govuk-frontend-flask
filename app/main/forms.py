from flask_wtf import FlaskForm  # type: ignore
from govuk_frontend_wtf.wtforms_widgets import GovRadioInput, GovSubmitInput  # type: ignore
from wtforms.fields import RadioField, SubmitField  # type: ignore
from wtforms.validators import InputRequired  # type: ignore


class CookiesForm(FlaskForm):
    """Form for managing cookie preferences."""

    functional: RadioField = RadioField(
        "Do you want to accept functional cookies?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select yes if you want to accept functional cookies")],
        choices=[("no", "No"), ("yes", "Yes")],
        default="no",
    )
    analytics: RadioField = RadioField(
        "Do you want to accept analytics cookies?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select yes if you want to accept analytics cookies")],
        choices=[("no", "No"), ("yes", "Yes")],
        default="no",
    )
    save: SubmitField = SubmitField("Save cookie settings", widget=GovSubmitInput())
