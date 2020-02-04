from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SubmitField, IntegerField, PasswordField, BooleanField, SelectField, HiddenField, SelectMultipleField, RadioField
from wtforms.validators import ValidationError, InputRequired, Email, EqualTo, Length, NumberRange
from app.models import User, Items
from app import db
from sqlalchemy import func
from flask_login import current_user
import datetime

class FeeForm(FlaskForm):

    eBayPercent = DecimalField("eBay Fee Percent", validators=[InputRequired(), NumberRange(min=0,max=1)], places=2)
    payPalFixed = DecimalField("PayPal Base Fee", validators=[InputRequired(), NumberRange(min=0)], places=2)
    payPalPercent = DecimalField("PayPal Fee Percent", validators=[InputRequired(), NumberRange(min=0,max=1)], places=2)
    submit = SubmitField("Adjust Fees")

class SaleForm(FeeForm):
    items = SelectField("Item", validators=[InputRequired()])
    date = DateField("Date", validators=[InputRequired()], format='%m-%d-%Y')
    price = DecimalField("Price", validators=[InputRequired(), NumberRange(min=0)], places=2)
    quantity = IntegerField("Quantity", validators=[InputRequired(), NumberRange(min=0)])
    shipping = DecimalField("Postage", validators=[InputRequired(), NumberRange(min=0)], places=2)
    packaging = DecimalField("Packaging", validators=[InputRequired(), NumberRange(min=0)], places=2)
    hidden = HiddenField()
    submit = SubmitField("Log Sale")

    def validate_date(form,field):

        if not type(field.data) == datetime.date:
            raise ValidationError("Date must be 'MM-DD-YYYY'")

        if field.data > datetime.date.today():
            raise ValidationError("Date cannot be in the future.")


    def validate_quantity(form,field):

        item = Items.query.filter_by(user=current_user).filter_by(itemName=form.items.data).first_or_404()

        totalNumberOfItemsSold = item.quantity - sum([sale.quantity for sale in item.sales])

        # totalNumberOfItemSales = db.session.query(func.sum(Sales.quantity)).filter_by(username=current_user.username).filter_by(itemName=)

        if field.data > totalNumberOfItemsSold:
            raise ValidationError(f"{totalNumberOfItemsSold} of quantity remaining for {form.items.data}.")

class SaleActionForm(FlaskForm):
    items = SelectMultipleField("Item(s)", validators=[InputRequired()])
    action = RadioField("Action", validators=[InputRequired()], choices=[("history","View History"), ("delete","Delete Sale"), ("edit","Edit Sale"), ("refund", "Refund Sale")])
    submit = SubmitField("Get Sales")

class SaleHistoryAdjustForm(FlaskForm):
    sale = RadioField("Select Sale", validators=[InputRequired()])
    hidden = HiddenField(validators=[InputRequired()])
    submit = SubmitField("Action")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=64)])
    password = PasswordField("Password", validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(max=64)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[InputRequired(), EqualTo('password')])
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
    itemName = StringField("Item Name", validators=[InputRequired(), Length(max=255)])
    # date = DateField("Date", validators=[InputRequired()], format='%d-%m-%Y')
    price = DecimalField("Total Price", validators=[InputRequired(), NumberRange(min=0)], places=2)
    # Must be greater than 0 and less than 1000
    quantity = IntegerField("Total Quantity", validators=[InputRequired(), NumberRange(min=1)])
    hidden = HiddenField()
    submit = SubmitField('Add')

    def validate_itemName(form, field):
        itemName = field.data.strip()
        item = Items.query.filter_by(user=current_user).filter_by(itemName=itemName).first()
        if item:   
            raise ValidationError(f"{itemName} is already being tracked.")

class ItemSelectForm(FlaskForm):
    items = RadioField("Items", validators=[InputRequired()])
    action = RadioField("Action", validators=[InputRequired()], choices=[('edit','Edit'),('delete','Delete')])
    submit = SubmitField('Select')

class DeleteConfirmationForm(FlaskForm):
    hidden = HiddenField(validators=[InputRequired()])
    confirm = SubmitField("Confirm Deletion")


