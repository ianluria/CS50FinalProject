# Standard library imports
import re
import ast

# Third party imports
from datetime import date
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func
from werkzeug.urls import url_parse

# Local application imports
from app import app, db
from app.forms import SaleForm, LoginForm, RegistrationForm, ItemForm, ItemSelectForm, SaleSelectForm, SaleHistoryAdjustForm
from app.helpers import populateSelectField, calculateProfit, populateItemsObject, createSaleHistoryList
from app.models import User, Sales, Items

# Dashboard of user sales
@app.route('/')
@app.route('/index')
@login_required
def index():

    totalNumberOfSales = Sales.query.filter_by(
        username=current_user.username).count()
    totalSales = db.session.query(func.sum(Sales.price)).filter_by(
        username=current_user.username).scalar()

    message = f"{current_user.username} is tracking {totalNumberOfSales} sales worth ${totalSales}."

    return render_template("index.html", message=message)

# Enter a new sale or edit and existing
@app.route("/newSale", methods=["GET", "POST"])
@login_required
def newSale():
    form = SaleForm()

    populateSelectField(form)

    if form.validate_on_submit():

        # If the id hidden field has data, the sale is being edited.
        if form.id.data:

            hiddenData = ast.literal_eval(form.id.data)
            # Create a tuple as (orginial sale id, orignial item name)
            # idData = tuple(re.findall(r'[\w]+', form.id.data))

            # first or 404 ???
            # Get sale from database.
            usersSale = Sales.query.filter_by(username=current_user.username).filter_by(
                id=hiddenData["id"]).first()

            if usersSale is None:
                flash("Sale doesn't exist.")
                return redirect(url_for("sales"))

            # Get the new item from the database

            # Update the sale's item and itemName

        # If there is not form.id.data, create a new instance of the Sales model.
        if not form.id.data:
            usersSale = Sales()
            usersSale.username = current_user.username

        # Link userSale object to an Item object if there is not one linked or user changed item during edit
        if not form.id.data or not hiddenData["originalItemName"] == form.items.data:

            # Consider deleting this in favor of using the foreign key
            usersSale.itemName = form.items.data
            # first or 404????
            usersSale.item = Items.query.filter_by(
                user=current_user).filter_by(itemName=form.items.data).first()

        usersSale.date = form.date.data
        usersSale.price = str(form.price.data)
        usersSale.quantity = form.quantity.data
        usersSale.shipping = str(form.shipping.data)

        calculateProfit(usersSale)

        db.session.add(usersSale)
        db.session.commit()

        flash(f"Sale Logged for {usersSale.item.itemName}")
        return redirect(url_for("sales"))

    else:
        form.date.data = date.today()
        # .strftime("%m/%d/%Y")
        return render_template("saleInput.html", form=form)


@app.route("/sales", methods=["GET", "POST"])
@login_required
def sales():

    form = SaleSelectForm()

    items = Items.query.filter_by(user=current_user).all()

    names = [(item.itemName, item.itemName) for item in items]

    form.items.choices = names
    form.items.size = len(names)

    if form.validate_on_submit():

        # List of tuples (sale.id, string of sale information)
        saleHistory = createSaleHistoryList(form.items.data)

        # Determine how template will be structured depending on which action choice user has made.
        userAction = form.action.data

        if userAction == "edit" or userAction == "delete":
            adjustSaleHistoryForm = SaleHistoryAdjustForm()
            adjustSaleHistoryForm.hidden.data = {
                'action': userAction, 'itemsSelected': form.items.data}
            adjustSaleHistoryForm.sale.choices = saleHistory
            return render_template("_saleAdjust.html", form=form, adjustForm=adjustSaleHistoryForm, userAction=userAction)
        else:
            return render_template("_saleHistory.html", history=[sale[1] for sale in saleHistory], form=form)

    return render_template("sales.html", form=form)


@app.route("/adjustSaleHistory", methods=["POST"])
@login_required
def adjustSaleHistory():

    form = SaleHistoryAdjustForm()

    # Convert string data from form into a dict
    hiddenData = ast.literal_eval(form.hidden.data)

    # Get list of all relevant sales to pass validation check
    # userSelectionList = [sale.strip(
    #     "\' ") for sale in form.hidden.data.strip("[]").split(",")]

    form.sale.choices = createSaleHistoryList(hiddenData["itemsSelected"])

    if form.validate_on_submit():

        # first or 404?
        saleToAdjust = Sales.query.filter_by(username=current_user.username).filter_by(
            id=int(form.sale.data)).first()

        if hiddenData["action"] == "delete":

            flash(f"Sale {saleToAdjust.itemName} deleted.")

            db.session.delete(saleToAdjust)
            db.session.commit()

        elif hiddenData["action"] == "edit":

            saleFormToEdit = SaleForm()

            populateSelectField(saleFormToEdit)
            saleFormToEdit.items.data = saleToAdjust.item.itemName

            saleFormToEdit.id.data = {
                "id": saleToAdjust.id, "originalItemName": saleToAdjust.item.itemName}
            saleFormToEdit.date.data = saleToAdjust.date
            saleFormToEdit.price.data = saleToAdjust.price
            saleFormToEdit.quantity.data = saleToAdjust.quantity
            saleFormToEdit.shipping.data = saleToAdjust.shipping

            return render_template("saleInput.html", form=saleFormToEdit, action="edit")

    return redirect(url_for("sales"))


@app.route("/items", methods=["GET"])
@login_required
def items():

    # Form that allows user to select an existing item to edit or delete
    form = ItemSelectForm()

    items = populateSelectField(form)

    return render_template("items.html", items=items, form=form)


# Create a new item
@app.route("/addItem", methods=["GET", "POST"])
@login_required
def addItem():

    form = ItemForm()

    if form.validate_on_submit():

        # Establish an itemName to query database
        if form.hidden.data and not form.hidden.data == form.itemName.data:

            itemName = form.hidden.data

        else:
            itemName = form.itemName.data

        item = Items.query.filter_by(user=current_user).filter_by(
            itemName=itemName).first()

        edit = True

        # User has entered an item name that is in database, but did not arrive through the editing route.
        if item and not form.hidden.data:
            flash(
                f"Item '{itemName}' is already in database.  Use editing option to adjust it.")
            return redirect(url_for("items"))

        # Create a new Items object if the user is entering a new item
        if item is None:

            item = Items()
            edit = False

        # Update item with new data from form.
        populateItemsObject(item, form, edit=edit)

        if edit:
            # Update every relevant sale in the history to reflect the changes the user made to item.
            sales = Sales.query.filter_by(username=current_user.username).filter_by(
                item=item).all()

            for sale in sales:
                sale.itemName = item.itemName
                calculateProfit(sale)
                db.session.add(sale)

            flash(f"Item {item.itemName} updated.")
        else:
            flash(f"{item.itemName} added.")

        db.session.add(item)
        db.session.commit()

        return redirect(url_for("items"))

    # Return a list of the items already in database
    return render_template("_addItem.html", form=form)

# Route which processes a user's request to edit or delete an existing item.
@app.route("/adjustItem", methods=["POST"])
@login_required
def adjustItem():

    form = ItemSelectForm()

    items = populateSelectField(form)

    if form.validate_on_submit():

        # First or 404?
        item = Items.query.filter_by(user=current_user).filter_by(
            itemName=form.items.data).first()

        if item is None:
            flash("Item doesn't exist.")
            return redirect(url_for("items"))

        if form.action.data == "delete":

            db.session.delete(item)
            db.session.commit()

            # Also delete sales history for item??

            flash(f"Item {item.itemName} deleted.")

        elif form.action.data == "edit":

            # Populate an itemForm object with the "item" data stored in the database to show user.
            itemForm = ItemForm(obj=item)
            # Store the current name of the item in a hidden field to track if the user makes changes to the itemName.
            itemForm.hidden.data = item.itemName

            flash(f"Editing {item.itemName}.")

            return render_template("_addItem.html", form=itemForm)

    return redirect(url_for("items"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password.")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

# Create a new user account
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
