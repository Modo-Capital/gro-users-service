"""empty message

Revision ID: 1ebb58da7049
Revises: 5add1e65612b
Create Date: 2018-06-15 16:06:43.101545

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1ebb58da7049'
down_revision = '5add1e65612b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('inputs', sa.Column('annual_inc', sa.Integer(), nullable=True))
    op.add_column('inputs', sa.Column('collections_12_mths_zero', sa.Integer(), nullable=True))
    op.add_column('inputs', sa.Column('dti', sa.Float(), nullable=True))
    op.add_column('inputs', sa.Column('emp_length_num', sa.Integer(), nullable=True))
    op.add_column('inputs', sa.Column('home_ownership', sa.String(), nullable=True))
    op.add_column('inputs', sa.Column('mths_since_last_delinq', sa.Integer(), nullable=True))
    op.add_column('inputs', sa.Column('mths_since_last_major_derog', sa.Integer(), nullable=True))
    op.add_column('inputs', sa.Column('mths_since_last_record', sa.Integer(), nullable=True))
    op.add_column('inputs', sa.Column('open_acc', sa.Integer(), nullable=True))
    op.add_column('inputs', sa.Column('total_acc', sa.Integer(), nullable=True))
    op.drop_column('inputs', 'openAcc')
    op.drop_column('inputs', 'emp_length')
    op.drop_column('inputs', 'debt_to_income')
    op.drop_column('inputs', 'annual_income')
    op.drop_column('inputs', 'average_current_balance')
    op.drop_column('inputs', 'short_emp')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('inputs', sa.Column('short_emp', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('inputs', sa.Column('average_current_balance', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('inputs', sa.Column('annual_income', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('inputs', sa.Column('debt_to_income', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('inputs', sa.Column('emp_length', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('inputs', sa.Column('openAcc', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('inputs', 'total_acc')
    op.drop_column('inputs', 'open_acc')
    op.drop_column('inputs', 'mths_since_last_record')
    op.drop_column('inputs', 'mths_since_last_major_derog')
    op.drop_column('inputs', 'mths_since_last_delinq')
    op.drop_column('inputs', 'home_ownership')
    op.drop_column('inputs', 'emp_length_num')
    op.drop_column('inputs', 'dti')
    op.drop_column('inputs', 'collections_12_mths_zero')
    op.drop_column('inputs', 'annual_inc')
    # ### end Alembic commands ###