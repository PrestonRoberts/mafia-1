"""empty message

Revision ID: 15ea68a034c9
Revises: fde7190c77dc
Create Date: 2019-03-10 17:17:39.937468

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15ea68a034c9'
down_revision = 'fde7190c77dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game_room', sa.Column('gaTarget', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game_room', 'gaTarget')
    # ### end Alembic commands ###