# Standard library imports
import re
import ast

# Third party imports
from datetime import date
from decimal import Decimal
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func
from werkzeug.urls import url_parse

# Local application imports
from app import app, db
from app.email import send_password_reset_email
from app.forms import LoginForm, RegistrationForm, ItemForm, ItemSelectForm, SaleForm, SaleActionForm, SaleHistoryAdjustForm, DeleteConfirmationForm, FeeForm, ResetPasswordRequestForm, ResetPasswordForm
from app.helpers import populateItemSelectField, calculateProfit, populateItemsObject, createSaleHistoryList, usd, populateFeeFields, createSaleActionForm
from app.models import User, Sales, Items
from app.createCSV import createCSV

# Dashboard of user sales
@app.route('/')
@app.route('/index')
@login_required
def index():

    t = current_user

    totalNumberOfSales = Sales.query.filter_by(
        username=current_user.username).count()
    totalProfit = db.session.query(func.sum(Sales.profit)).filter_by(
        username=current_user.username).scalar()

    totalProfit = 0 if totalProfit == None else totalProfit

    items = Items.query.filter_by(user=current_user).all()

    itemAndQuantityList = [(item.itemName, item.quantity -
                            sum([sale.quantity for sale in item.sales])) for item in items]

    totalSalesMessage = f"{current_user.username} is tracking {totalNumberOfSales} {'sale' if totalNumberOfSales == 1 else 'sales'} with total {'profit' if totalProfit >= 0 else 'loss'} of {usd(totalProfit or 0)}."

    return render_template("index.html", totalSalesMessage=totalSalesMessage, itemQuantityRemaining=itemAndQuantityList)

# Enter a new sale or edit and existing
@app.route("/newSale", methods=["GET", "POST"])
@login_required
def newSale():

    # Redirect user to addItem if no items have been added yet.
    if not Items.query.filter_by(user=current_user).first():
        flash("Please add an item before adding a new sale.", "error")
        return redirect(url_for("addItem"))

    form = SaleForm()

    populateItemSelectField(form)

    if form.validate_on_submit():

        # If the id hidden field has data, the sale is being edited.
        if form.hidden.data:

            # Create a dictionary from form hidden data.
            hiddenData = ast.literal_eval(form.hidden.data)

            # Get sale from database.
            usersSale = Sales.query.filter_by(username=current_user.username).filter_by(
                id=hiddenData["id"]).first_or_404()

            flash(
                f"{form.items.data}'s sale on {form.date.raw_data[0]} has been edited.", "success")
        else:
            flash(f"New Sale Logged for {form.items.data}.", "success")
            # Create a new instance of the Sales model.
            usersSale = Sales()
            usersSale.username = current_user.username

        # Link userSale object to an Item object if there is not one linked or user changed item during edit
        if not form.hidden.data or not hiddenData["originalItemName"] == form.items.data:

            usersSale.item = Items.query.filter_by(
                user=current_user).filter_by(itemName=form.items.data).first_or_404()

        usersSale.date = form.date.data
        usersSale.price = str(form.price.data)
        usersSale.priceWithTax = str(
            form.priceWithTax.data.quantize(Decimal("1.00")))
        usersSale.quantity = form.quantity.data
        usersSale.shipping = str(form.shipping.data)
        usersSale.packaging = str(form.packaging.data)
        # eBay fees never include sales taxes
        usersSale.eBayFees = str(
            Decimal(form.price.data*form.eBayPercent.data).quantize(Decimal("1.00")))
        # PayPal fees include sales taxes
        usersSale.payPalFees = str(Decimal(
            (form.priceWithTax.data if form.priceWithTax.data else form.price.data) * form.payPalPercent.data + form.payPalFixed.data).quantize(Decimal("1.00")))

        calculateProfit(usersSale)

        db.session.add(usersSale)
        db.session.commit()

        return redirect(url_for("sales"))

    else:
        # Prefill certain fields of the form
        form.date.data = date.today()
        populateFeeFields(form)
        return render_template("saleInput.html", form=form, action="add")

# Provide a list of items that user can select from to either edit/delete a sale or view a history of that item's sales.  Multiple items can be selected.
@app.route("/sales", methods=["GET", "POST"])
@login_required
def sales():

    form = createSaleActionForm()

    if form.validate_on_submit():

        # Store which items the user wants to view sales from, and the action.
        current_user.saleDisplayInfo = f"{{'userAction':'{form.action.data}', 'itemsList':{form.items.data}}}"

        db.session.add(current_user)
        db.session.commit()

        return redirect(url_for("displaySales", page=1))

    zeroSales = True if not Sales.query.filter_by(
        username=current_user.username).first() else False

    zeroItems = True if not Items.query.filter_by(
        user=current_user).first() else False

    return render_template("sales.html", form=form, zeroSales=zeroSales, zeroItems=zeroItems)


@app.route("/displaySales", methods=["GET"])
@login_required
def displaySales():

    page = int(request.args.get("page"))

    # Convert data with userAction and list of items to view sales into a dict
    try:
        requestItemsList = ast.literal_eval(current_user.saleDisplayInfo)
    except:
        flash("Error: User must have a saleDisplayInfo dict stored.", "error")
        return redirect(url_for("sales"))

    if page and requestItemsList:

        # createSaleHistory returns a dict {saleHistoryQuery object, saleHistoryList tuples(id, string)}
        saleHistory = createSaleHistoryList(
            page, requestItemsList["itemsList"], requestItemsList["userAction"])

        if requestItemsList["userAction"] in ["edit", "delete", "refund"]:
            adjustSaleHistoryForm = SaleHistoryAdjustForm(hidden=page)

            adjustSaleHistoryForm.sale.choices = saleHistory["saleHistoryList"]
            adjustSaleHistoryForm.submit.label.text = f"{requestItemsList['userAction'].capitalize()} Sale"

            history = None

        else:
            adjustSaleHistoryForm = None
            history = [sale[1] for sale in saleHistory["saleHistoryList"]]

        next_url = url_for(
            'displaySales', page=saleHistory["saleHistoryQuery"].next_num) if saleHistory["saleHistoryQuery"].has_next else None
        prev_url = url_for(
            'displaySales', page=saleHistory["saleHistoryQuery"].prev_num) if saleHistory["saleHistoryQuery"].has_prev else None

        return render_template("_saleHistory.html", userAction=requestItemsList["userAction"], adjustForm=adjustSaleHistoryForm, history=history, form=createSaleActionForm(), next_url=next_url, prev_url=prev_url)

    return redirect(url_for("sales"))


@app.route("/adjustSaleHistory", methods=["POST"])
@login_required
def adjustSaleHistory():

    form = SaleHistoryAdjustForm()

    try:
        requestItemsList = ast.literal_eval(current_user.saleDisplayInfo)
    except:
        flash("Error: User must have a saleDisplayInfo dict stored.", "error")
        return redirect(url_for("sales"))

    if requestItemsList:
        form.sale.choices = createSaleHistoryList(int(
            form.hidden.data), requestItemsList["itemsList"], requestItemsList["userAction"])["saleHistoryList"]

        if form.validate_on_submit():

            saleToAdjust = Sales.query.filter_by(username=current_user.username).filter_by(
                id=int(form.sale.data)).first_or_404()

            if requestItemsList["userAction"] == "delete":

                flash(
                    f"A sale from {saleToAdjust.itemName} made on {saleToAdjust.date.strftime('%m/%d/%Y')} has been deleted.", "success")

                db.session.delete(saleToAdjust)
                db.session.commit()

            elif requestItemsList["userAction"] == "edit":

                # Create a SaleForm that will be prepopulated with the sale-to-edit's information that the user can then adjust
                saleFormToEdit = SaleForm()

                populateItemSelectField(saleFormToEdit)
                saleFormToEdit.items.data = saleToAdjust.item.itemName

                # Store a dictionary with information used to process an edit on the newSale route
                saleFormToEdit.hidden.data = {
                    "id": saleToAdjust.id, "originalItemName": saleToAdjust.item.itemName}

                saleFormToEdit.date.data = saleToAdjust.date
                saleFormToEdit.price.data = Decimal(saleToAdjust.price)
                saleFormToEdit.priceWithTax.data = Decimal(
                    saleToAdjust.priceWithTax)
                saleFormToEdit.quantity.data = saleToAdjust.quantity
                saleFormToEdit.shipping.data = Decimal(saleToAdjust.shipping)
                saleFormToEdit.packaging.data = Decimal(saleToAdjust.packaging)
                populateFeeFields(saleFormToEdit)

                return render_template("saleInput.html", form=saleFormToEdit, action="edit")

            elif requestItemsList["userAction"] == "refund":

                saleToAdjust.refund = True
                calculateProfit(saleToAdjust, True)
                db.session.add(saleToAdjust)
                db.session.commit()
                flash(
                    f"Refund issued for {saleToAdjust.itemName} sold on {saleToAdjust.date.strftime('%m/%d/%Y')}. Loss is {saleToAdjust.profit}.", "success")

    return redirect(url_for("sales"))


@app.route("/items", methods=["GET"])
@login_required
def items():

    # Form that allows user to select an existing item to edit or delete
    form = ItemSelectForm()

    items = populateItemSelectField(form)

    return render_template("_adjustItem.html", items=items, form=form)


# Create a new item or edit an existing item's details
@app.route("/addItem", methods=["GET", "POST"])
@login_required
def addItem():

    form = ItemForm()

    if form.validate_on_submit():
        
        # Check if adding this item would bring total items being tracked to greater than 50
        if len(current_user.items.all()) > 50:
            flash("Error: cannot track more than 50 items.", "error")
            return redirect(url_for("addItem"))

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
            return redirect(url_for("items"))

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

        return redirect(url_for("items"))

    return render_template("_addItem.html", form=form, items=populateItemSelectField(), action="Add New")

# Route which processes a user's request to edit or delete an existing item.
@app.route("/adjustItem", methods=["POST"])
@login_required
def adjustItem():

    form = ItemSelectForm()

    populateItemSelectField(form)

    if form.validate_on_submit():

        if form.action.data == "delete":

            # deleteConfirmationForm = DeleteConfirmationForm(hidden=form.items.data)

            return render_template("deleteConfirmation.html", form=DeleteConfirmationForm(hidden=form.items.data))
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

            return render_template("_addItem.html", form=itemForm, items=populateItemSelectField(), action="Edit")

    return redirect(url_for("items"))


@app.route("/fees", methods=["GET", "POST"])
@login_required
def fees():

    form = FeeForm()

    if form.validate_on_submit():

        current_user.eBayPercent = str(form.eBayPercent.data)
        current_user.payPalPercent = str(form.payPalPercent.data)
        current_user.payPalFixed = str(form.payPalFixed.data)
        db.session.add(current_user)
        db.session.commit()
        flash("Selling fees sucessfully updated.", "success")
        return redirect(url_for("index"))

    form.eBayPercent.data = Decimal(current_user.eBayPercent)
    form.payPalPercent.data = Decimal(current_user.payPalPercent)
    form.payPalFixed.data = Decimal(current_user.payPalFixed)

    return render_template("fees.html", form=form)


@app.route("/deleteItem", methods=["POST"])
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

    return redirect(url_for("items"))


@app.route("/downloadCSV", methods=["GET"])
@login_required
def downloadCSV():

    createCSV()

    return redirect(url_for('static', filename='eBaySales.csv'))
