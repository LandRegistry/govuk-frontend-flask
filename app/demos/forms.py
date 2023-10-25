from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import (
    GovCharacterCount,
    GovCheckboxesInput,
    GovCheckboxInput,
    GovDateInput,
    GovFileInput,
    GovPasswordInput,
    GovRadioInput,
    GovSelect,
    GovSubmitInput,
    GovTextArea,
    GovTextInput,
)
from wtforms.fields import (
    BooleanField,
    DateField,
    DateTimeField,
    DecimalField,
    FileField,
    FloatField,
    IntegerField,
    MultipleFileField,
    PasswordField,
    RadioField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import Email, EqualTo, InputRequired, Length, Optional, Regexp, ValidationError

from app.demos.custom_validators import RequiredIf


class BankDetailsForm(FlaskForm):
    name_on_the_account = StringField(
        "Name on the account",
        widget=GovTextInput(),
        validators=[InputRequired(message="Enter the name on the account")],
    )
    sort_code = StringField(
        "Sort code",
        widget=GovTextInput(),
        validators=[
            InputRequired(message="Enter a sort code"),
            Regexp(regex=r"\d{6}", message="Enter a valid sort code like 309430"),
        ],
        description="Must be 6 digits long",
    )
    account_number = StringField(
        "Account number",
        widget=GovTextInput(),
        validators=[
            InputRequired(message="Enter an account number"),
            Regexp(regex=r"\d{6,8}", message="Enter a valid account number like 00733445"),
            Length(min=6, max=8, message="Account number must be between 6 and 8 digits"),
        ],
        description="Must be between 6 and 8 digits long",
    )
    roll_number = StringField(
        "Building society roll number (if you have one)",
        widget=GovTextInput(),
        validators=[
            Optional(),
            Length(
                min=1,
                max=18,
                message="Building society roll number must be between 1 and 18 characters",
            ),
            Regexp(
                regex=r"[a-zA-Z0-9- /.]*$",
                message="Building society roll number must only include letters a to z, numbers, hyphens, spaces, forward slashes and full stops",
            ),
        ],
        description="You can find it on your card, statement or passbook",
    )
    submit = SubmitField("Continue", widget=GovSubmitInput())


class CreateAccountForm(FlaskForm):
    first_name = StringField(
        "First name",
        widget=GovTextInput(),
        validators=[InputRequired(message="Enter your first name")],
    )
    last_name = StringField(
        "Last name",
        widget=GovTextInput(),
        validators=[InputRequired(message="Enter your last name")],
    )
    date_of_birth = DateField(
        "Date of birth",
        widget=GovDateInput(),
        format="%d %m %Y",
        validators=[InputRequired(message="Enter your date of birth")],
        description="For example, 31 3 1980",
    )
    national_insurance_number = StringField(
        "National Insurance number",
        widget=GovTextInput(),
        validators=[
            InputRequired(message="Enter a National Insurance number"),
            Length(
                max=13,
                message="National Insurance number must be 13 characters or fewer",
            ),
            Regexp(
                regex=r"^[a-zA-Z]{2}\d{6}[aAbBcCdD]$",
                message="Enter a National Insurance number in the correct format",
            ),
        ],
        description="It’s on your National Insurance card, benefit letter, payslip or P60. For example, ‘QQ 12 34 56 C’.",
    )
    email_address = StringField(
        "Email address",
        widget=GovTextInput(),
        validators=[
            InputRequired(message="Enter an email address"),
            Length(max=256, message="Email address must be 256 characters or fewer"),
            Email(message="Enter an email address in the correct format, like name@example.com"),
        ],
        description="You'll need this email address to sign in to your account",
    )
    telephone_number = StringField(
        "UK telephone number",
        widget=GovTextInput(),
        validators=[
            InputRequired(message="Enter a UK telephone number"),
            Regexp(
                regex=r"[\d \+]",
                message="Enter a telephone number, like 01632 960 001, 07700 900 982 or +44 0808 157 0192",
            ),
        ],
    )
    password = PasswordField(
        "Create a password",
        widget=GovPasswordInput(),
        validators=[
            InputRequired(message="Enter a password"),
            Length(min=8, message="Password must be at least 8 characters"),
        ],
        description="Must be at least 8 characters",
    )
    confirm_password = PasswordField(
        "Confirm password",
        widget=GovPasswordInput(),
        validators=[
            InputRequired(message="Confirm your password"),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    terms_and_conditions = BooleanField(
        "I agree to the terms and conditions",
        widget=GovCheckboxInput(),
        validators=[InputRequired(message="Select to confirm you agree with the terms and conditions")],
    )
    submit = SubmitField("Create account", widget=GovSubmitInput())


class KitchenSinkForm(FlaskForm):
    string_field = StringField(
        "StringField",
        widget=GovTextInput(),
        validators=[InputRequired(message="StringField is required")],
        description="Hint text: WTForm StringField rendered using a GovTextInput widget.",
    )

    email_field = StringField(
        "EmailField",
        widget=GovTextInput(),
        validators=[InputRequired(message="EmailField is required"), Email()],
        description="Hint text: WTForm StringField rendered using a GovTextInput widget.",
    )

    float_field = FloatField(
        "FloatField",
        widget=GovTextInput(),
        validators=[InputRequired(message="FloatField is required")],
        description="Hint text: WTForm FloatField rendered using a GovTextInput widget.",
    )

    integer_field = IntegerField(
        "IntegerField",
        widget=GovTextInput(),
        validators=[InputRequired(message="IntegerField is required")],
        description="Hint text: WTForm IntegerField rendered using a GovTextInput widget.",
    )

    decimal_field = DecimalField(
        "DecimalField",
        widget=GovTextInput(),
        validators=[InputRequired(message="DecimalField is required")],
        description="Hint text: WTForm DecimalField rendered using a GovTextInput widget.",
    )

    textarea_field = TextAreaField(
        "TextAreaField",
        widget=GovTextArea(),
        validators=[InputRequired(message="TextAreaField is required")],
        description="Hint text: WTForm TextAreaField rendered using a GovTextArea widget.",
    )

    charactercount_field = TextAreaField(
        "CharacterCountField",
        widget=GovCharacterCount(),
        validators=[
            InputRequired(message="CharacterCountField is required"),
            Length(max=200, message="CharacterCountField must be 200 characters or fewer "),
        ],
        description="Hint text: WTForm TextAreaField rendered using a GovCharacterCount widget.",
    )

    boolean_field = BooleanField(
        "BooleanField",
        widget=GovCheckboxInput(),
        validators=[InputRequired(message="Please tick the box")],
        description="Hint text: WTForm BooleanField rendered using a GovCheckboxInput widget.",
    )

    select_field = SelectField(
        "SelectField",
        widget=GovSelect(),
        validators=[InputRequired(message="Please select an option")],
        choices=[
            ("", "Please select"),
            ("one", "One"),
            ("two", "Two"),
            ("three", "Three"),
        ],
        default="",
        description="Hint text: WTForm SelectField rendered using a GovSelect widget.",
    )

    select_multiple_field = SelectMultipleField(
        "SelectMultipleField",
        widget=GovCheckboxesInput(),
        validators=[InputRequired(message="Please select an option")],
        choices=[("one", "One"), ("two", "Two"), ("three", "Three")],
        description="Hint text: WTForm SelectMultipleField rendered using a GovCheckboxesInput widget.",
    )

    radio_field = RadioField(
        "RadioField",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Please select an option")],
        choices=[("one", "One"), ("two", "Two"), ("three", "Three")],
        description="Hint text: WTForm RadioField rendered using a GovRadioInput widget.",
    )

    file_field = FileField(
        "FileField",
        widget=GovFileInput(),
        validators=[InputRequired(message="Please upload a file")],
        description="Hint text: WTForm FileField rendered using a GovFileInput widget.",
    )

    multiple_file_field = MultipleFileField(
        "MultipleFileField",
        widget=GovFileInput(multiple=True),
        validators=[InputRequired(message="Please upload a file")],
        description="Hint text: WTForm MultipleFileField rendered using a MultipleFileField widget.",
    )

    password_field = PasswordField(
        "PasswordField",
        widget=GovPasswordInput(),
        validators=[
            InputRequired("Password is required"),
            EqualTo(
                "password_retype_field",
                message="Please ensure both password fields match",
            ),
        ],
        description="Hint text: WTForm PasswordField rendered using a GovPasswordInput widget.",
    )

    date_field = DateField(
        "DateField",
        widget=GovDateInput(),
        validators=[InputRequired(message="DateField is required")],
        description="Hint text: WTForm DateField rendered using a GovDateInput widget.",
    )

    date_time_field = DateTimeField(
        "DateTimeField",
        widget=GovDateInput(),
        validators=[InputRequired(message="DateTimeField is required")],
        description="Hint text: WTForm DateTimeField rendered using a GovDateInput widget.",
    )

    submit_button = SubmitField("SubmitField", widget=GovSubmitInput())


class ConditionalRevealForm(FlaskForm):
    contact = RadioField(
        "How would you prefer to be contacted?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select how you would prefer to be contacted")],
        choices=[
            ("email", "Email"),
            ("phone", "Phone"),
            ("text", "Text message"),
        ],
        description="Select one option.",
    )

    contact_by_email = StringField(
        "Email address",
        widget=GovTextInput(),
        # Set up the validation for each of the conditional fields with a custom RequiredIf validator
        # This will mark this field as required if the how_prefer_contacted is set to email
        validators=[
            RequiredIf(
                "contact",
                "email",
                message="Enter an email address in the correct format, like name@example.com",
            )
        ],
    )

    contact_by_phone = StringField(
        "Phone number",
        widget=GovTextInput(),
        validators=[
            RequiredIf(
                "contact",
                "phone",
                message="Enter a telephone number, like 01632 960 001 or +44 808 157 0192",
            )
        ],
    )

    contact_by_text = StringField(
        "Mobile phone number",
        widget=GovTextInput(),
        validators=[
            RequiredIf(
                "contact",
                "text",
                message="Enter a mobile phone number, like 07700 900 982",
            )
        ],
    )

    submit = SubmitField("Continue", widget=GovSubmitInput())


class AutocompleteForm(FlaskForm):
    # Manually added list here, but could be dynamically assigned in server route
    countries = [
        "Argentina",
        "Australia",
        "Brazil",
        "Canada",
        "China",
        "France",
        "Germany",
        "India",
        "Indonesia",
        "Italy",
        "Japan",
        "Mexico",
        "Russia",
        "Saudi Arabia",
        "South Africa",
        "South Korea",
        "Turkey",
        "United Kingdom",
        "United States",
    ]

    country = StringField(
        "G20 Countries",
        widget=GovTextInput(),
        validators=[InputRequired(message="Enter a country")],
        description="Start typing and select a suggestion",
    )

    submit = SubmitField("Continue", widget=GovSubmitInput())

    def validate_country(self, country):
        if country.data.title() not in self.countries:
            raise ValidationError(f"{country.data} is not a valid country")
