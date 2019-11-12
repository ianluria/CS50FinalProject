"""items table

Revision ID: 0332ad9fcd9f
Revises: 0300b7f385dc
Create Date: 2019-11-07 16:17:10.726906

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0332ad9fcd9f'
down_revision = '0300b7f385dc'
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
    op.drop_index('ix_user_date', table_name='user')
    op.drop_index('ix_user_item', table_name='user')
    op.drop_index('ix_user_username', table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=64), nullable=True),
    sa.Column('item', sa.VARCHAR(length=255), nullable=True),
    sa.Column('date', sa.DATE(), nullable=True),
    sa.Column('price', sa.FLOAT(), nullable=True),
    sa.Column('quantity', sa.INTEGER(), nullable=True),
    sa.Column('shipping', sa.FLOAT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_username', 'user', ['username'], unique=False)
    op.create_index('ix_user_item', 'user', ['item'], unique=False)
    op.create_index('ix_user_date', 'user', ['date'], unique=False)
    op.drop_index(op.f('ix_sales_username'), table_name='sales')
    op.drop_index(op.f('ix_sales_item'), table_name='sales')
    op.drop_index(op.f('ix_sales_date'), table_name='sales')
    op.drop_table('sales')
    op.drop_index(op.f('ix_items_username'), table_name='items')
    op.drop_index(op.f('ix_items_item'), table_name='items')
    op.drop_index(op.f('ix_items_date'), table_name='items')
    op.drop_table('items')
    # ### end Alembic commands ###
