from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SubmitField, IntegerField, PasswordField, BooleanField
from wtforms.validators import DataRequired


class SaleForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()], format='%d-%m-%Y')
    price = DecimalField("Price", validators=[DataRequired()], places=2)
    # Must be greater than 0 and less than 1000
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    # Need a default value of 0.50
    postage = DecimalField("Postage", validators=[DataRequired()], places=2)
    submit = SubmitField("Log Sale")


class LoginForm:
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField("Sign In")
