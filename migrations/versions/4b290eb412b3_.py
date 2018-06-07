"""empty message

Revision ID: 4b290eb412b3
Revises: 1e0928dfe91e
Create Date: 2018-06-06 19:07:29.432316

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b290eb412b3'
down_revision = '1e0928dfe91e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('daily_transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('bank_account_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('daily_transactions')
    # ### end Alembic commands ###