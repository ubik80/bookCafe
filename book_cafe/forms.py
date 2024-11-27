from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import DecimalField, RadioField, SelectField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import InputRequired


class Login_Form(FlaskForm):
    username = StringField('Username', validators=[InputRequired('username required')])
    password = PasswordField('Password', validators=[InputRequired('password required')])
    submit = SubmitField('Submit')


class Register_Form(FlaskForm):
    username = StringField('Username', validators=[InputRequired('username required')])
    password = PasswordField('Password', validators=[InputRequired('password required')])
    submit = SubmitField('Submit')


class Add_Book_Form(FlaskForm):
    title = StringField('Title', validators=[InputRequired('title required')])
    author = StringField('Author', validators=[InputRequired('author required')])
    description = TextAreaField('Description')
    cover_picture = FileField('Cover Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')


class Find_Book_Form(FlaskForm):
    title = StringField('Title')
    author = StringField('Author')
    sort_by = RadioField('Sort by', choices=['title' ,'author'], default='title')
    submit = SubmitField('Submit')


if __name__ == "__main__":
    pass
