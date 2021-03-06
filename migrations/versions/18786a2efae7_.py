"""empty message

Revision ID: 18786a2efae7
Revises: 
Create Date: 2020-04-20 20:21:34.315497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18786a2efae7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('payPalFixed', sa.String(length=64), nullable=True),
    sa.Column('payPalPercent', sa.String(length=64), nullable=True),
    sa.Column('eBayPercent', sa.String(length=64), nullable=True),
    sa.Column('saleDisplayInfo', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('items',
    sa.Column('itemName', sa.String(length=50), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('price', sa.String(length=64), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['username'], ['user.username'], ),
    sa.PrimaryKeyConstraint('itemName')
    )
    op.create_index(op.f('ix_items_date'), 'items', ['date'], unique=False)
    op.create_index(op.f('ix_items_itemName'), 'items', ['itemName'], unique=False)
    op.create_index(op.f('ix_items_username'), 'items', ['username'], unique=False)
    op.create_table('sales',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('itemName', sa.String(length=50), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('price', sa.String(length=64), nullable=False),
    sa.Column('priceWithTax', sa.String(length=64), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('shipping', sa.String(length=64), nullable=False),
    sa.Column('profit', sa.String(length=64), nullable=False),
    sa.Column('packaging', sa.String(length=64), nullable=True),
    sa.Column('payPalFees', sa.String(length=64), nullable=True),
    sa.Column('eBayFees', sa.String(length=64), nullable=True),
    sa.Column('refund', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['itemName'], ['items.itemName'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_date'), 'sales', ['date'], unique=False)
    op.create_index(op.f('ix_sales_itemName'), 'sales', ['itemName'], unique=False)
    op.create_index(op.f('ix_sales_username'), 'sales', ['username'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_sales_username'), table_name='sales')
    op.drop_index(op.f('ix_sales_itemName'), table_name='sales')
    op.drop_index(op.f('ix_sales_date'), table_name='sales')
    op.drop_table('sales')
    op.drop_index(op.f('ix_items_username'), table_name='items')
    op.drop_index(op.f('ix_items_itemName'), table_name='items')
    op.drop_index(op.f('ix_items_date'), table_name='items')
    op.drop_table('items')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
