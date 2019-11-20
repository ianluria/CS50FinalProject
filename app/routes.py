from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import SaleForm, LoginForm, RegistrationForm, ItemForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Sales
from werkzeug.urls import url_parse

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
    if form.validate_on_submit():

        date = form.date.data
        price = form.price.data
        quantity = form.quantity.data
        postage = form.postage.data

        # calculate profit
        # populate_obj

        newSale = Sales(username=current_user, date=date,
                        price=price, quantity=quantity, shipping=postage)
        db.session.add(newSale)
        db.session.commit()

        flash("Sale Logged.")
        return redirect(url_for("index"))

    else:
        # create dynamic list of choice values
        return render_template("saleInput.html", form=form)


# Create a new item
@app.route("/addItem", methods=["GET", "POST"])
@login_required
def addItem():
    form = ItemForm()

    print("form data: ", form.data)

    if form.validate_on_submit():

        print("here.")

        itemFound = Items.query.filter_by(item=form.item.data).first()
        if not itemFound is None:
            flash("Item already being tracked.")
            return redirect(url_for("editItem"))

        flash("New Item Added.")
        # Need to add item info to db

        item = form.item.data
        price = form.pricePaid.data
        quantity = form.totalQuantity.data

        newItem = Items(username=current_user, item=item,
                        price=price, quantity=quantity)
        db.session.add(newItem)
        db.session.commit()

        return redirect(url_for("items"))

    return render_template("addItem.html", form=form)


# Edit an item
# If get return list of current items
# If post adjust the table
@app.route("editItem", methods=["GET", "POST"])
@login_required
def editItem():
    form = EditItemForm()
    if form.validate_on_submit():

        item = form.item.data
        price = form.pricePaid.data
        quantity = form.totalQuantity.data

        newItem = Items(username=current_user, item=item,
                        price=price, quantity=quantity)
        db.session.add(newItem)
        db.session.commit()

        return redirect(url_for("items"))

    items - Items.query.all()
    # Create a list of all itemNames
    items = [name["itemName"] for name in items]

    form.item.choices = items

    return render_template("_editItem.html", form=form)


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
