from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import SaleForm, LoginForm, RegistrationForm, ItemForm, ItemSelectForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Sales, Items
from werkzeug.urls import url_parse
from app.helpers import populateSelectField, calculateProfit
from datetime import date

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

        newSale = Sales()
        
        form.populate_obj(newSale)

        newSale.username = current_user.username
        newSale.profit = calculateProfit(newSale)
        
        db.session.add(newSale)
        db.session.commit()

        flash("Sale Logged.")
        return redirect(url_for("index"))

    else:
        form.date.data = date.today()
        # .strftime("%m/%d/%y")
        return render_template("saleInput.html", form=form)

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

        flash("New Item Added.")

        newItem = Items(username=current_user.username)

        form.populate_obj(newItem)

        db.session.add(newItem)
        db.session.commit()

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

        form.populate_obj(item)
        del item.hidden
        del item.submit

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
