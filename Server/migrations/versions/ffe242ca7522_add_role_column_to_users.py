"""Add role column to users

Revision ID: ffe242ca7522
Revises: ed0908a1cc6f
Create Date: 2025-09-26 17:36:33.300710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffe242ca7522'
down_revision = 'ed0908a1cc6f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('role', sa.String(), nullable=False, server_default='user')
        )
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_email'))
        batch_op.drop_column('role')
