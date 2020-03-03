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


