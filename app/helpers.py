# Standard library imports
from decimal import Decimal
# Related third party imports
from flask_login import current_user
# Local application/library specific imports
from app.forms import ItemSelectForm, SaleForm, ItemForm, SaleActionForm
from app.models import Items, Sales


# Poplates the choices field of a given form
def populateItemSelectField(form):

    if isinstance(form, ItemSelectForm) or isinstance(form, SaleForm) or isinstance(form, SaleActionForm):

        # Create a list of items for use in select field
        names = [(item.itemName, item.itemName) for item in current_user.items]

        form.items.choices = names


# Transfers information from ItemForm's user input to an Item object
def populateItemsObject(obj, form, edit=False):

    if isinstance(obj, Items) and isinstance(form, ItemForm):

        obj.itemName = form.itemName.data.strip()
        obj.price = str(form.price.data)
        obj.quantity = form.quantity.data

        # Only fill these values if a new instance of Items is being created.
        if not edit:
            obj.username = current_user.username
            obj.user = current_user

        return

    raise TypeError(
        "Obj must be of Items type and form must be of ItemForm type.")


def calculateProfit(model, refund=False):

    if isinstance(model, Sales):

        unitCost = Decimal(model.item.price) / Decimal(model.item.quantity)

        cost = Decimal(model.quantity) * Decimal(unitCost) + \
            Decimal(model.shipping) + Decimal(model.packaging) + \
            Decimal(model.eBayFees) + Decimal(model.payPalFees)

        if refund:
            # Refund assumes that items, shipping, packaging, and PP fees are lost
            model.profit = str(
                Decimal(0-cost+Decimal(model.eBayFees)).quantize(Decimal("1.00")))
            return

        profit = Decimal(model.price) - Decimal(cost)

        profit = Decimal(profit).quantize(Decimal("1.00"))

        model.profit = str(profit)

        return

    else:
        raise TypeError("Model must be of Sales type.")


def usd(value):
    """Format value as USD."""
    return f"${Decimal(value):,.2f}"


def populateFeeFields(form):
    if isinstance(form, SaleForm):
        form.eBayPercent.data = Decimal(current_user.eBayPercent)
        form.payPalPercent.data = Decimal(current_user.payPalPercent)
        form.payPalFixed.data = Decimal(current_user.payPalFixed)
        return
    else:
        raise TypeError("form must be of SaleForm type.")


def createSaleActionForm():
    form = SaleActionForm()

    populateItemSelectField(form)

    form.items.size = len(form.items.choices)

    return form
