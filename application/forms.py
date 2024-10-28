from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,IntegerField
from wtforms.validators import Email,Length,EqualTo,DataRequired


class RegistrationForm(FlaskForm):
    first_name = StringField(label='',validators=[Length(min=2,max=50),DataRequired()])
    last_name = StringField(label='',validators=[Length(min=1,max=50),DataRequired()])
    phone_number = StringField(label='',validators=[Length(min=10,max=10),DataRequired()])
    email_address = StringField(label='', validators=[Email(),DataRequired()])
    pan_number = StringField(label='',validators=[Length(min=8,max=8),DataRequired()])
    password1 = PasswordField(label='',validators=[Length(min=6,max=60),DataRequired()])
    password2 = PasswordField(label='',validators=[EqualTo('password1'),DataRequired()]) 
    submit = SubmitField(label='REGISTER HERE')

    


class LoginForm(FlaskForm):
    email_address = StringField(label='',validators=[Email(),DataRequired()])
    password = PasswordField(label='',validators=[DataRequired()])
    submit = SubmitField(label='SIGN IN')


