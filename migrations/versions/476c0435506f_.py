"""empty message

Revision ID: 476c0435506f
Revises: b0ee99709c72
Create Date: 2019-12-05 18:49:25.425388

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '476c0435506f'
down_revision = 'b0ee99709c72'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_items_username'), 'items', ['username'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_items_username'), table_name='items')
    # ### end Alembic commands ###
