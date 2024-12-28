from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import DecimalField, RadioField, SelectField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import InputRequired, ValidationError
from configuration import ALLOWED_PICTURE_FILE_EXTENSIONS


class Login_Form(FlaskForm):
    username = StringField('Username', validators=[InputRequired('username required')])
    password = PasswordField('Password', validators=[InputRequired('password required')])
    submit = SubmitField('Submit')


class Register_Form(FlaskForm):
    username = StringField('Username', validators=[InputRequired('username required')])
    password = PasswordField('Password', validators=[InputRequired('password required')])
    submit = SubmitField('Submit')


class Add_Book_Form(FlaskForm):
    def validate_cover_picture(self, file):
        if not file or not file.data:
            return
        if not ('.' in file.data.filename and file.data.filename.rsplit('.', 1)[1].lower() in ALLOWED_PICTURE_FILE_EXTENSIONS):
            message = 'Wrong file format.'
            flash(message)
            raise ValidationError(message)

    title = StringField('Title', validators=[InputRequired('title required')])
    author = StringField('Author', validators=[InputRequired('author required')])
    description = TextAreaField('Description')
    cover_picture = FileField('Cover Picture')
    submit = SubmitField('Submit')


class Find_Book_Form(FlaskForm):
    title = StringField('Title')
    author = StringField('Author')
    sort_by = RadioField('Sort by', choices=[('title' ,'title') ,('author', 'author')], default='title')
    submit = SubmitField('Submit')


if __name__ == "__main__":
    pass
