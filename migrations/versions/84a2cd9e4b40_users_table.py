"""users table

Revision ID: 84a2cd9e4b40
Revises: 
Create Date: 2019-11-12 11:51:58.763749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84a2cd9e4b40'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('item', sa.String(length=255), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('price', sa.Float(precision=2), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_date'), 'items', ['date'], unique=False)
    op.create_index(op.f('ix_items_item'), 'items', ['item'], unique=True)
    op.create_index(op.f('ix_items_username'), 'items', ['username'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('sales',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('item', sa.String(length=255), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('price', sa.Float(precision=2), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('shipping', sa.Float(precision=2), nullable=True),
    sa.ForeignKeyConstraint(['item'], ['items.item'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_date'), 'sales', ['date'], unique=False)
    op.create_index(op.f('ix_sales_item'), 'sales', ['item'], unique=False)
    op.create_index(op.f('ix_sales_username'), 'sales', ['username'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_sales_username'), table_name='sales')
    op.drop_index(op.f('ix_sales_item'), table_name='sales')
    op.drop_index(op.f('ix_sales_date'), table_name='sales')
    op.drop_table('sales')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_items_username'), table_name='items')
    op.drop_index(op.f('ix_items_item'), table_name='items')
    op.drop_index(op.f('ix_items_date'), table_name='items')
    op.drop_table('items')
    # ### end Alembic commands ###