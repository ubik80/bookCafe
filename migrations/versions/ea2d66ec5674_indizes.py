"""indizes

Revision ID: ea2d66ec5674
Revises: 03c7950c4aae
Create Date: 2024-11-14 22:11:47.988993

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea2d66ec5674'
down_revision = '03c7950c4aae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.create_index('title_author_index', ['title', 'author'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.drop_index('title_author_index')

    # ### end Alembic commands ###