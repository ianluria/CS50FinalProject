"""empty message

Revision ID: 42abcdc3afc2
Revises: 8765ea64752f
Create Date: 2020-01-23 20:39:19.610865

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42abcdc3afc2'
down_revision = '8765ea64752f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('items', 'id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('id', sa.INTEGER(), nullable=False))
    # ### end Alembic commands ###
