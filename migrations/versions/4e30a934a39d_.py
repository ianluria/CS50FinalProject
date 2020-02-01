"""empty message

Revision ID: 4e30a934a39d
Revises: 9ff389fdc4f6
Create Date: 2020-02-01 13:04:09.236099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e30a934a39d'
down_revision = '9ff389fdc4f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('eBayPercent', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('payPalFixed', sa.String(length=64), nullable=True))
    op.add_column('user', sa.Column('payPalPercent', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'payPalPercent')
    op.drop_column('user', 'payPalFixed')
    op.drop_column('user', 'eBayPercent')
    # ### end Alembic commands ###
