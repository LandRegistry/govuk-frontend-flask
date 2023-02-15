from wtforms.validators import InputRequired


class RequiredIf(InputRequired):
    def __init__(self, other_field_name, other_field_value, *args, **kwargs):
        self.other_field_name = other_field_name
        self.other_field_value = other_field_value

        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)

        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)

        if other_field.data == self.other_field_value:
            super(RequiredIf, self).__call__(form, field)
