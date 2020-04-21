"""empty message

Revision ID: fddd86a7ede3
Revises: 9e51ff09e17d
Create Date: 2020-04-21 01:58:26.432048

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fddd86a7ede3'
down_revision = '9e51ff09e17d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('num_upcoming_shows', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'num_upcoming_shows')
    # ### end Alembic commands ###
