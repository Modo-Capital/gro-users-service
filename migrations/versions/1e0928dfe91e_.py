"""empty message

Revision ID: 1e0928dfe91e
Revises: c48cbff391b5
Create Date: 2018-06-06 18:56:24.078986

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1e0928dfe91e'
down_revision = 'c48cbff391b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('daily_balance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('balance', sa.Float(), nullable=False),
    sa.Column('bank_account_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('daily balance')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('daily balance',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"daily balance_id_seq"\'::regclass)'), nullable=False),
    sa.Column('date', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('balance', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('bank_account_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id'], name='daily balance_bank_account_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='daily balance_pkey')
    )
    op.drop_table('daily_balance')
    # ### end Alembic commands ###
