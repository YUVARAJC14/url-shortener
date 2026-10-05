from urllib.parse import urlparse
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, URL, ValidationError
from urllib.parse import urlparse
from flask import request
from wtforms import StringField, SelectField, SubmitField


class LinkForm(FlaskForm):
    original_url = StringField("Long URL", validators=[
        DataRequired(),
        Length(max=2048),
        URL(message="Enter a full URL, like https://example.com/page"),
    ])
    expires_in = SelectField("Expires", choices=[
        ("0", "Never expires"), ("1", "Expires in 1 day"),
        ("7", "Expires in 7 days"), ("30", "Expires in 30 days"),
    ], default="0")
    submit = SubmitField("Shorten link")

    def validate_original_url(self, field):
        parsed = urlparse(field.data.strip())
        if parsed.scheme not in ("http", "https"):
            raise ValidationError("The URL must start with http:// or https://")
        if parsed.netloc.lower() == request.host.lower():
            raise ValidationError("You can't shorten a link to this site.")