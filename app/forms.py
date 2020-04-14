# Standard library imports
import ast

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SubmitField, IntegerField, PasswordField, BooleanField, SelectField, HiddenField, SelectMultipleField, RadioField
from wtforms.validators import ValidationError, InputRequired, Email, EqualTo, Length, NumberRange
from app.models import User, Items, Sales
from app import db
from sqlalchemy import func
from flask_login import current_user
import datetime
from decimal import Decimal


class FeeForm(FlaskForm):

    eBayPercent = DecimalField("eBay Fee Percent", validators=[
                               InputRequired(), NumberRange(min=0, max=1)], places=2)
    payPalFixed = DecimalField("PayPal Base Fee $", validators=[
                               InputRequired(), NumberRange(min=0)], places=2)
    payPalPercent = DecimalField("PayPal Fee Percent", validators=[
                                 InputRequired(), NumberRange(min=0, max=1)], places=2)
    submit = SubmitField("Adjust Fees")


class SaleForm(FeeForm):
    items = SelectField("Item", validators=[InputRequired()])
    date = DateField("Date", validators=[InputRequired()], format='%m-%d-%Y')
    price = DecimalField("Sale Price", validators=[
                         InputRequired(), NumberRange(min=0)], places=2)
    priceWithTax = DecimalField("Price With Tax", validators=[
                                NumberRange(min=0)], places=2)
    quantity = IntegerField("Quantity", validators=[
                            InputRequired(), NumberRange(min=1)])
    shipping = DecimalField("Postage", validators=[
                            InputRequired(), NumberRange(min=0)], places=2)
    packaging = DecimalField("Packaging", validators=[
                             InputRequired(), NumberRange(min=0)], places=2)
    hidden = HiddenField()
    submit = SubmitField("Log Sale")

    def validate_priceWithTax(form, field):

        if not isinstance(form.price.data, Decimal):
            raise ValidationError()

        if field.data:
            if field.data < form.price.data:
                raise ValidationError(
                    "Price with tax cannot be less than price.")

            if field.data < 0:
                raise ValidationError("Price cannot be less than zero.")

    def validate_date(form, field):

        if not type(field.data) == datetime.date:
            raise ValidationError("Date must be 'MM-DD-YYYY'")

        if field.data > datetime.date.today():
            raise ValidationError("Date cannot be in the future.")

    def validate_quantity(form, field):

        if not isinstance(field.data, int):
            raise ValidationError()

        item = Items.query.filter_by(user=current_user).filter_by(
            itemName=form.items.data).first_or_404()

        unitsRemaining = item.quantity - \
            sum([sale.quantity for sale in item.sales])

        # For validation, return units sold from sale to unitsRemaining if the sale is being edited
        if form.hidden.data:
            hiddenData = ast.literal_eval(form.hidden.data)

            originalSale = Sales.query.filter_by(username=current_user.username).filter_by(
                id=hiddenData["id"]).first_or_404()

            unitsRemaining += originalSale.quantity

        if field.data > unitsRemaining:
            raise ValidationError(
                f"{unitsRemaining} of quantity remaining for {form.items.data}.")


class SaleActionForm(FlaskForm):
    items = SelectMultipleField("Item(s)", validators=[InputRequired()])
    action = RadioField("Action", validators=[InputRequired()], choices=[("history", "View History"), (
        "delete", "Delete Sale"), ("edit", "Edit Sale"), ("refund", "Refund Sale")], render_kw={"class": "form-check-input"})
    submit = SubmitField("Get Sales")


class SaleHistoryAdjustForm(FlaskForm):
    sale = RadioField("Select Sale", validators=[InputRequired()], render_kw={
                      "class": "form-check-input"})
    hidden = HiddenField()
    submit = SubmitField("Action")


class ItemForm(FlaskForm):
    itemName = StringField("Item Name", validators=[
                           InputRequired(), Length(max=40)])
    price = DecimalField("Total Price", validators=[
                         InputRequired(), NumberRange(min=0)], places=2)
    quantity = IntegerField("Total Quantity", validators=[
                            InputRequired(), NumberRange(min=1)])
    hidden = HiddenField()
    submit = SubmitField('Add')

    def validate_quantity(form, field):

        # Only validate quantity if item is being edited
        if form.hidden.data:
            itemBeingEdited = Items.query.filter_by(user=current_user).filter_by(
                itemName=form.hidden.data).first_or_404()

            quantitySold = sum(
                [sale.quantity for sale in itemBeingEdited.sales])

            # Can't adjust quantity below amount that has already been sold
            if field.data < quantitySold:
                raise ValidationError(f"Can't have less than {quantitySold}.")

    # Check if itemName will be a duplicate
    def validate_itemName(form, field):

        thisItem = field.data.strip()

        items = Items.query.filter_by(user=current_user).all()

        items = [item.itemName.lower() for item in items]

        if thisItem.lower() in items:

            # If editing, ignore error for repeating item name being edited.
            if form.hidden.data.lower() == thisItem.lower():
                return

            else:
                raise ValidationError(f"{thisItem} is already being tracked.")


class ItemSelectForm(FlaskForm):
    items = RadioField("Items", validators=[InputRequired()], render_kw={
                       "class": "form-check-input"})
    action = RadioField("Action", validators=[InputRequired()], choices=[(
        'edit', 'Edit'), ('delete', 'Delete')], render_kw={"class": "form-check-input"})
    submit = SubmitField('Select')


class DeleteConfirmationForm(FlaskForm):
    hidden = HiddenField(validators=[InputRequired()])
    confirm = SubmitField("Confirm Deletion")