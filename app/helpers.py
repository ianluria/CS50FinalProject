from flask import render_template, redirect, url_for
from flask_login import current_user
from app.forms import ItemSelectForm, SaleForm
from app.models import Items

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


def calculateProfit(model):

    if isinstance(model, Sales):

        unitCost = model.item.price / model.item.quantity
        
        cost = model.quantity * unitCost + model.shipping

        return float(model.price - cost)
    else:
        raise TypeError("Model must be of Sales type.")