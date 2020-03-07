
# Third party imports
from decimal import Decimal
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

# Local application imports
from app import db
from app.items import bp
from app.forms import ItemForm, ItemSelectForm, DeleteConfirmationForm
from app.helpers import populateItemSelectField, calculateProfit, populateItemsObject
from app.models import User, Sales, Items


@bp.route("/items", methods=["GET"])
@login_required
def items():

    # Form that allows user to select an existing item to edit or delete
    form = ItemSelectForm()

    items = populateItemSelectField(form)

    return render_template("items/_adjustItem.html", items=items, form=form)


# Create a new item or edit an existing item's details
@bp.route("/addItem", methods=["GET", "POST"])
@login_required
def addItem():

    form = ItemForm()

    if form.validate_on_submit():

        # Check if adding this item would bring total items being tracked to greater than 50
        if len(current_user.items.all()) > 50:
            flash("Error: cannot track more than 50 items.", "error")
            return redirect(url_for("items.addItem"))

        # The user has altered the item name.
        if form.hidden.data and not form.hidden.data == form.itemName.data:

            # Use the unmodified item name to query the database
            itemName = form.hidden.data

            # Go through all the sales for the item and update the foreign key due to name change.
            updateForeignKey = True

        else:
            itemName = form.itemName.data
            updateForeignKey = False

        item = Items.query.filter_by(user=current_user).filter_by(
            itemName=itemName).first()

        edit = True

        # User has entered an item name that is in database, but did not arrive through the editing route.
        if item and not form.hidden.data:
            flash(
                f"Item '{itemName}' is already in database.  Use editing option to adjust it.", "error")
            return redirect(url_for("items.items"))

        # Create a new Items object if the user is entering a new item
        if item is None:
            item = Items()
            edit = False

        if edit:
            sales = item.sales.all()

        # Update item with new data from form.
        populateItemsObject(item, form, edit=edit)

        # The profit for each sale will be updated given the new item information from user
        if edit:
            for sale in sales:
                if updateForeignKey:
                    # Update each sale's itemName to the new itemName from form
                    sale.itemName = item.itemName
                calculateProfit(sale)

            flash(f"Item {item.itemName} updated.", "success")
        else:
            flash(f"{item.itemName} added.", "success")

        db.session.add(item)
        db.session.commit()

        return redirect(url_for("items.items"))

    return render_template("items/_addItem.html", form=form, items=populateItemSelectField(), action="Add New")

# Route which processes a user's request to edit or delete an existing item.
@bp.route("/adjustItem", methods=["POST"])
@login_required
def adjustItem():

    form = ItemSelectForm()

    populateItemSelectField(form)

    if form.validate_on_submit():

        if form.action.data == "delete":

            # deleteConfirmationForm = DeleteConfirmationForm(hidden=form.items.data)

            return render_template("items/deleteConfirmation.html", form=DeleteConfirmationForm(hidden=form.items.data))
            # Forward user to a warning page

            # # Delete all sales history for item
            # salesToDelete = Sales.query.filter_by(username=current_user.username).filter_by(
            #     item=item).all()

            # for sale in salesToDelete:
            #     db.session.delete(sale)

            # db.session.delete(item)
            # db.session.commit()

            # flash(f"Item {item.itemName} deleted.")

        elif form.action.data == "edit":

            item = Items.query.filter_by(user=current_user).filter_by(
                itemName=form.items.data).first_or_404()

            # Populate an itemForm object with the "item" data stored in the database to show user.
            itemForm = ItemForm(price=Decimal(item.price),
                                quantity=item.quantity, itemName=item.itemName)
            # Store the current name of the item in a hidden field to track if the user makes changes to the itemName.
            itemForm.hidden.data = item.itemName

            itemForm.submit.label.text = form.action.data.capitalize()

            return render_template("items/_addItem.html", form=itemForm, items=populateItemSelectField(), action="Edit")

    return redirect(url_for("items.items"))


@bp.route("/deleteItem", methods=["POST"])
@login_required
def deleteItem():

    form = DeleteConfirmationForm()

    if form.validate_on_submit():

        item = Items.query.filter_by(user=current_user).filter_by(
            itemName=form.hidden.data).first_or_404()

        # Delete all sales history for item
        salesToDelete = Sales.query.filter_by(username=current_user.username).filter_by(
            item=item).all()

        for sale in salesToDelete:
            db.session.delete(sale)

        db.session.delete(item)
        db.session.commit()

        flash(f"Item {item.itemName} deleted.", "success")

    return redirect(url_for("items.items"))
