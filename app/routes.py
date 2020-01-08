from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import SaleForm, LoginForm, RegistrationForm, ItemForm, ItemSelectForm, SaleSelectForm, SaleHistoryAdjustForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Sales, Items
from werkzeug.urls import url_parse
from app.helpers import populateSelectField, calculateProfit, populateItemsObject, createSaleHistoryList
from datetime import date
import re

# Dashboard of user sales
@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html")

# Enter a new sale
@app.route("/sale", methods=["GET", "POST"])
@login_required
def sale():
    form = SaleForm()

    populateSelectField(form)

    if form.validate_on_submit():

        if form.id.data:

            # (id, item name)
            idData = tuple(re.findall(r'[\w]+', form.id.data))

            usersSale = Sales.query.filter_by(username=current_user.username).filter_by(
                id=idData[0]).first()

            if usersSale is None:
                flash("Sale doesn't exist.")
                return redirect(url_for("saleHistory"))

        else:
            usersSale = Sales()
            usersSale.username = current_user.username
            # Consider deleting this in favor of using the foreign key
            usersSale.itemName = form.items.data
            usersSale.item = Items.query.filter_by(
                username=current_user.username).filter_by(itemName=form.items.data).first()

        usersSale.date = form.date.data
        usersSale.price = str(form.price.data)
        usersSale.quantity = form.quantity.data
        usersSale.shipping = str(form.shipping.data)

        calculateProfit(usersSale)

        db.session.add(usersSale)
        db.session.commit()

        flash(f"Sale Logged for {usersSale.item.itemName}")
        return redirect(url_for("index"))

    else:
        form.date.data = date.today()
        # .strftime("%m/%d/%y")
        return render_template("saleInput.html", form=form)

# Returns a history of sales per item
@app.route("/saleHistory", methods=["GET", "POST"])
@login_required
def saleHistory():

    form = SaleSelectForm()

    items = Items.query.filter_by(username=current_user.username).all()

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
            adjustSaleHistoryForm.hidden.data = form.items.data
            adjustSaleHistoryForm.sale.choices = saleHistory
            return render_template("saleHistory.html", form=form, adjustForm=adjustSaleHistoryForm, userAction=userAction)
        else:
            return render_template("saleHistory.html", history=[sale[1] for sale in saleHistory], form=form)

    return render_template("saleHistory.html", form=form)


@app.route("/deleteSaleHistory", methods=["POST"])
@login_required
def deleteSaleHistory():

    form = SaleHistoryAdjustForm()

    userSelectionList = [sale.strip(
        "\' ") for sale in form.hidden.data.strip("[]").split(",")]

    form.sale.choices = createSaleHistoryList(userSelectionList)

    if form.validate_on_submit():

        print("form sale data", form.sale.data)

        saleToDelete = Sales.query.filter_by(username=current_user.username).filter_by(
            id=int(form.sale.data)).first()

        if saleToDelete is None:
            flash("Sale doesn't exist.")
            return redirect(url_for("saleHistory"))

        flash(f"Sale {saleToDelete.itemName} deleted.")

        print("delete", saleToDelete)

        db.session.delete(saleToDelete)
        db.session.commit()

    return redirect(url_for("saleHistory"))

    # print("In delete list", userSelectionList)

    # sale = Sales.query.filter_by(id=form.)

    # validation of submit may require validation to know which choices the user had to choose from
    # hidden field will contain the items the user choose to edit
    # populate a list of all sales for each item chosen

    #saleHistoryList = createSaleHistoryList(form.hidden.data)


@app.route("/editSaleHistory", methods=["POST"])
@login_required
def editSaleHistory():

    form = SaleHistoryAdjustForm()

    userSelectionList = [sale.strip(
        "\' ") for sale in form.hidden.data.strip("[]").split(",")]

    form.sale.choices = createSaleHistoryList(userSelectionList)

    if form.validate_on_submit():

        saleToEdit = Sales.query.filter_by(username=current_user.username).filter_by(
            id=int(form.sale.data)).first()

        if saleToEdit is None:
            flash("Sale doesn't exist.")
            return redirect(url_for("saleHistory"))

        saleFormToEdit = SaleForm()
        populateSelectField(saleFormToEdit)

        saleFormToEdit.items.data = saleToEdit.item.itemName
        saleFormToEdit.id.data = (saleToEdit.id, saleToEdit.item.itemName)
        saleFormToEdit.date.data = saleToEdit.date
        saleFormToEdit.price.data = saleToEdit.price
        saleFormToEdit.quantity.data = saleToEdit.quantity
        saleFormToEdit.shipping.data = saleToEdit.shipping

        return render_template("saleInput.html", form=saleFormToEdit, action="edit")

    return

# General purpose page with links which also displays the current items
@app.route("/items", methods=["GET"])
@login_required
def items():

    items = Items.query.filter_by(username=current_user.username).all()

    return render_template("items.html", items=items)


# Create a new item
@app.route("/addItem", methods=["GET", "POST"])
@login_required
def addItem():
    form = ItemForm()

    if form.validate_on_submit():

        itemFound = Items.query.filter_by(user=current_user).filter_by(
            itemName=form.itemName.data).first()

        if not itemFound is None:
            flash("Item already being tracked.")
            return redirect(url_for("addItem"))

        newItem = Items()

        populateItemsObject(newItem, form)

        db.session.add(newItem)
        db.session.commit()

        flash("New Item Added.")
        return redirect(url_for("addItem"))

    items = Items.query.filter_by(username=current_user.username).all()
    return render_template("_addItem.html", form=form, items=items)


@app.route("/selectItem", methods=["GET"])
@login_required
def selectItem():

    form = ItemSelectForm()

    items = populateSelectField(form)

    # items = Items.query.filter_by(username=current_user.username).all()

    # # Create a list of items for use in select field
    # names = [(item.itemName, item.itemName) for item in items]

    # form.items.choices = names

    return render_template("_itemSelect.html", form=form, items=items, destination="/" + request.args.get("destination"))


@app.route("/deleteItem", methods=["POST"])
@login_required
def deleteItem():

    form = ItemSelectForm()

    populateSelectField(form)

    if form.validate_on_submit():

        item = Items.query.filter_by(user=current_user).filter_by(
            itemName=form.items.data).first()

        if item is None:
            flash("Item doesn't exist.")
            return redirect(url_for("items"))

        db.session.delete(item)
        db.session.commit()

        flash(f"Item {item.itemName} deleted.")

    return redirect(url_for("items"))

# Allow user to select which item to edit
@app.route("/editItem", methods=["GET", "POST"])
@login_required
def editItem():

    form = ItemSelectForm()

    items = populateSelectField(form)

    if form.validate_on_submit():

        itemFound = Items.query.filter_by(user=current_user).filter_by(
            itemName=form.items.data).first()

        if itemFound is None:
            flash("Item doesn't exist.")
            return redirect(url_for("items"))

        # Populate an itemForm object with the itemFound data stored in the database.
        itemForm = ItemForm(obj=itemFound)
        itemForm.hidden.data = itemFound.itemName

        return render_template("_editItemDetails.html", form=itemForm, items=items)

    return redirect(url_for("items"))


@app.route("/editItemDetails", methods=["POST"])
@login_required
def editItemDetails():

    form = ItemForm()

    form.itemName.data = form.hidden.data

    if form.validate_on_submit():

        item = Items.query.filter_by(user=current_user).filter_by(
            itemName=form.hidden.data).first()

        if item is None:
            flash("Item doesn't exist.")
            return redirect(url_for("items"))

        populateItemsObject(item, form)

        db.session.add(item)
        db.session.commit()

        flash(f"Item {item.itemName} updated.")

        return redirect(url_for("items"))

    return redirect(url_for("items"))


# remove item
# get item to be removed from drop down menu
# get this user
# execute remove item on this user
# update database

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


# Display all items

# Show history of sales
