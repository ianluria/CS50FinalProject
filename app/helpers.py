from flask import render_template, redirect, url_for
from flask_login import current_user
from app.forms import ItemSelectForm, SaleForm, ItemForm, SaleActionForm
from app.models import Items, Sales, User
from decimal import Decimal, getcontext

getcontext().prec = 2

# """Populates form select field and returns results from items query."""


def populateItemSelectField(form):

    if isinstance(form, ItemSelectForm) or isinstance(form, SaleForm) or isinstance(form, SaleActionForm):

        items = Items.query.filter_by(username=current_user.username).all()

        # Create a list of items for use in select field
        names = [(item.itemName, item.itemName) for item in items]

        form.items.choices = names

        return items
    else:
        raise TypeError(
            "Form must be of ItemSelectForm, SaleActionForm, or SaleForm type.")


def populateItemsObject(obj, form, edit=False):

    if isinstance(obj, Items):
        if isinstance(form, ItemForm):

            obj.itemName = form.itemName.data
            obj.price = str(form.price.data)
            obj.quantity = form.quantity.data

            # Only fill these values if a new instance of Items is being created.
            if not edit:
                obj.username = current_user.username
                obj.user = User.query.filter_by(
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


def createSaleHistoryList(listOfItemNames):

    historyList = Sales.query.filter(
        Sales.username == current_user.username, Sales.itemName.in_(listOfItemNames)).all()

    adjustSaleChoices = [
        (str(sale.id), f"{sale.itemName} quantity {sale.quantity} at ${sale.price} on {sale.date.strftime('%m/%d/%Y')} shipping ${sale.shipping} for a profit of ${sale.profit}") for sale in historyList]

    return adjustSaleChoices
