## **eBaySalt** *The eBay Sales Tracker*

A simple application built with Flask to store and track eBay sales.

The user can create a unique, password protected account.

Once logged in, the user can add up to 40 unique items for sale, and set specific eBay fee information.

Each item can have an unlimited number of associated unique sales.

Each sale contains information such as the date, price, sales tax, and shipping costs.

After the sale is entered, based on the sale information, a profit calcuation is stored for it.

The user is able to edit, delete, and refund each sale, as well as edit or delete items themselves.

The complete sale history for each item is available for view and can also be downloaded in csv format.

All data is stored in a SQLite database and queries are made using Flask SQLAlchemy.

Created by Ian Luria 2020
https://github.com/ianluria 
