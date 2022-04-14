from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SearchField
from wtforms.validators import DataRequired


class FriendsSearchForm(FlaskForm):
    search = SearchField('Write yor friends nickname', validators=[DataRequired()])
    submit = SubmitField('Search')