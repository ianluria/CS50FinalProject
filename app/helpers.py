from flask import render_template, redirect, url_for
from flask_login import current_user
from app.forms import ItemSelectForm, SaleForm, ItemForm
from app.models import Items, Sales
from decimal import Decimal, getcontext

getcontext().prec = 2

# """Populates form select field and returns results from items query."""


def populateSelectField(form):

    if isinstance(form, ItemSelectForm) or isinstance(form, SaleForm):

        items = Items.query.filter_by(username=current_user.username).all()

        # Create a list of items for use in select field
        names = [(item.itemName, item.itemName) for item in items]

        form.items.choices = names

        return items
    else:
        raise TypeError("Form must be of ItemSelectForm or SaleForm type.")


def populateItemsObject(obj, form):

    if isinstance(obj, Items):
        if isinstance(form, ItemForm):
            newItem.username = username = current_user.username
            newItem.itemName = form.itemName
            newItem.price = str(form.price)
            newItem.quantity = form.quantity
            newItem.user = User.query.filter_by(
                username=current_user.username).first()
            return

    raise TypeError(
        "Obj must be of Items type and form must be of ItemForm type.")


def calculateProfit(model):

    if isinstance(model, Sales):

        unitCost = Decimal(model.item.price) / Decimal(model.item.quantity)

        cost = Decimal(model.quantity) * Decimal(unitCost) + \
            Decimal(model.shipping)

        profit = Decimal(model.price) - Decimal(cost)

        profit = Decimal(profit).quantize(Decimal("1.00"))

        model.profit = str(profit)

        return

    else:
        raise TypeError("Model must be of Sales type.")
