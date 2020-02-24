from app.models import User, Sales, Items
from flask_login import current_user
from flask import render_template, redirect, url_for

import csv


def createCSV():

    with open("app/static/eBaySales.csv", "w", newline='', encoding='utf-8') as new_file:

        fieldnames = ["itemName", "date", "priceWithTax", "price", "quantity", "shipping",
                      "profit", "packaging", "payPalFees", "eBayFees", "refund"]

        csv_writer = csv.DictWriter(
            new_file, fieldnames=fieldnames, delimiter=",", extrasaction="raise")

        csv_writer.writeheader()

        sales = Sales.query.filter_by(username=current_user.username).all()

        for sale in sales:

            row = {fieldname: getattr(sale, fieldname)
                   for fieldname in fieldnames}

            row["date"] = row["date"].strftime('%m/%d/%Y')

            csv_writer.writerow(row)

        return
