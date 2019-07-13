"""empty message

Revision ID: bcd7013d2964
Revises: 15ea68a034c9
Create Date: 2019-03-10 20:20:01.197502

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcd7013d2964'
down_revision = '15ea68a034c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player', sa.Column('selfHeal', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('player', 'selfHeal')
    # ### end Alembic commands ###