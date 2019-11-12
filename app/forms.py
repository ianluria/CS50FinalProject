from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class SaleForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()], format='%d-%m-%Y')
    price = DecimalField("Price", validators=[DataRequired()], places=2)
    # Must be greater than 0 and less than 1000
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    # Need a default value of 0.50
    postage = DecimalField("Postage", validators=[DataRequired()], places=2)
    submit = SubmitField("Log Sale")