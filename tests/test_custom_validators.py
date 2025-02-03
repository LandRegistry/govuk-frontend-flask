import pytest
from wtforms import Form, StringField, ValidationError
from wtforms.validators import DataRequired

from app.demos.custom_validators import RequiredIf


def required_if(form, field):
    if form.dependency.data == "yes" and not field.data:
        raise ValidationError("This field is required.")


class TestForm(Form):
    dependency = StringField("Dependency", [DataRequired()])
    dependent = StringField("Dependent", [required_if])


@pytest.fixture
def form():
    """Create a new form instance for each test."""
    return TestForm()


def test_required_if_dependency_matches():
    """Test validation when dependency field matches target value."""
    form = TestForm(data={"dependency": "yes", "dependent": ""})
    assert not form.validate()
    assert "This field is required." in form.dependent.errors


def test_required_if_dependency_differs():
    """Test validation when dependency field differs from target value."""
    form = TestForm(data={"dependency": "no", "dependent": ""})
    assert form.validate()


def test_required_if_dependency_missing():
    """Test validation when dependency field doesn't exist."""

    class InvalidForm(Form):
        dependent = StringField(validators=[RequiredIf("missing_field", "yes")])

    form = InvalidForm()
    with pytest.raises(Exception) as exc:
        form.validate()
    assert 'no field named "missing_field" in form' in str(exc.value)


def test_required_if_with_valid_input():
    """Test validation with valid input for both fields."""
    form = TestForm(data={"dependency": "yes", "dependent": "valid input"})
    assert form.validate()
