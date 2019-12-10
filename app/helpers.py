from flask import render_template, redirect, url_for
from flask_login import current_user
from app.forms import ItemSelectForm
from app.models import Items

# """Populates form select field and returns results from items query."""
def populateSelectField(form):

    if isinstance(form, ItemSelectForm):
    
        items = Items.query.filter_by(username=current_user.username).all()

        # Create a list of items for use in select field
        names = [(item.itemName, item.itemName) for item in items]

        form.items.choices = names

        return items
    else:
        raise TypeError("Form must be of ItemSelectForm type.")
