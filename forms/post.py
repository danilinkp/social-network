from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired


class PostsForm(FlaskForm):
    content = TextAreaField("Содержание")
    image = FileField(validators=[FileRequired()])
    submit = SubmitField('Применить')