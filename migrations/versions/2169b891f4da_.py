"""empty message

Revision ID: 2169b891f4da
Revises: 
Create Date: 2018-11-10 12:05:51.752446

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2169b891f4da'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('player',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=16), nullable=True),
    sa.Column('role', sa.String(length=45), nullable=True),
    sa.Column('team', sa.String(length=45), nullable=True),
    sa.Column('roomID', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('room',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=4), nullable=True),
    sa.Column('playerCount', sa.Integer(), nullable=True),
    sa.Column('started', sa.Boolean(), nullable=True),
    sa.Column('ended', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.drop_table('Room')
    op.drop_table('Player')
    op.drop_table('sqlite_sequence')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sqlite_sequence',
    sa.Column('name', sa.NullType(), nullable=True),
    sa.Column('seq', sa.NullType(), nullable=True)
    )
    op.create_table('Player',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=16), nullable=False),
    sa.Column('role', sa.VARCHAR(length=16), nullable=True),
    sa.Column('team', sa.VARCHAR(length=128), nullable=True),
    sa.Column('roomID', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Room',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('code', sa.VARCHAR(length=4), nullable=True),
    sa.Column('playerCount', sa.INTEGER(), nullable=True),
    sa.Column('started', sa.BOOLEAN(), nullable=True),
    sa.Column('ended', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('room')
    op.drop_table('player')
    # ### end Alembic commands ###
