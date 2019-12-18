from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SubmitField, IntegerField, PasswordField, BooleanField, SelectField, HiddenField, SelectMultipleField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User


class SaleForm(FlaskForm):
    items = SelectField("Item", validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()], format='%d-%m-%Y')
    price = DecimalField("Price", validators=[DataRequired()], places=2)
    # Must be greater than 0 and less than 1000
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    # Need a default value of 0.50
    shipping = DecimalField("Postage", validators=[DataRequired()], places=2)
    submit = SubmitField("Log Sale")

class SaleSelectForm(FlaskForm):
    items = SelectMultipleField("Item(s)", validators=[DataRequired()])
    action = RadioField("Action", validators=[DataRequired()], choices=[("history","View History"), ("delete","Delete Sale"), ("edit","Edit Sale")])
    submit = SubmitField("Get History")

class SaleHistoryAdjustForm(FlaskForm):
    sale = RadioField("Select Sale", validators=[DataRequired()])
    hidden = HiddenField(validators=[DataRequired()])
    submit = SubmitField("Action")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ItemForm(FlaskForm):
    itemName = StringField("Item", validators=[DataRequired()])
    # date = DateField("Date", validators=[DataRequired()], format='%d-%m-%Y')
    price = DecimalField("Total Price", validators=[DataRequired()], places=2)
    # Must be greater than 0 and less than 1000
    quantity = IntegerField("Total Quantity", validators=[DataRequired()])
    hidden = HiddenField()
    submit = SubmitField('Add')

class ItemSelectForm(FlaskForm):
    items = SelectField("Items", validators=[DataRequired()])
    submit = SubmitField('Select')
