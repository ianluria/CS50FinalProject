from flask_login import current_user
from app.forms import ItemSelectForm, SaleForm, ItemForm, SaleActionForm
from app.models import Items, Sales, User
from decimal import Decimal


# Can also be used to return a preformatted list of strings with item details
def populateItemSelectField(form=False):

    items = Items.query.filter_by(username=current_user.username).all()

    if isinstance(form, ItemSelectForm) or isinstance(form, SaleForm) or isinstance(form, SaleActionForm):

        # Create a list of items for use in select field
        names = [(item.itemName, item.itemName) for item in items]

        form.items.choices = names

    return

    # items = [
    #     f"{item.itemName} cost {usd(item.price)} for quantity of {item.quantity} and added on {item.date.strftime('%m/%d/%Y')}." for item in items]

    # return items


def populateItemsObject(obj, form, edit=False):

    if isinstance(obj, Items):
        if isinstance(form, ItemForm):

            obj.itemName = form.itemName.data.strip()
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


def createSaleHistoryList(page, listOfItemNames, userAction=False):

    historyQuery = Sales.query.filter(
        Sales.username == current_user.username, Sales.itemName.in_(listOfItemNames)).order_by(Sales.date.desc()).paginate(page, 30, False)

    historyList = historyQuery.items

    # Remove any already refunded sales if userAction is editing or refunding
    if userAction in ["edit", "refund"]:
        historyList = [sale for sale in historyList if not sale.refund]

    historyList = [
        (str(sale.id), f"{'Refunded' if sale.refund else ''} {sale.quantity} {sale.itemName} sold at {usd(Decimal(sale.price))} on {sale.date.strftime('%m/%d/%Y')} with shipping of {usd(Decimal(sale.shipping))} and packaging of {usd(Decimal(sale.packaging))} for a {'profit' if Decimal(sale.profit) >= 0 else 'loss'} of {usd(Decimal(sale.profit))}.") for sale in historyList]

    return {"saleHistoryQuery": historyQuery, "saleHistoryList": historyList}


def usd(value):
    """Format value as USD."""
    # return f"${value:,.2f}"
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

    names = populateItemSelectField(form)

    form.items.size = len(names)

    return form
