"""create roles table

Revision ID: 3d2fca7411f4
Revises: 0f3f9b49f1d9
Create Date: 2024-10-31 00:14:43.883520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d2fca7411f4'
down_revision: Union[str, None] = '0f3f9b49f1d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user_roles',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'is_worker')
    op.drop_column('users', 'is_user')
    op.drop_column('users', 'is_super_admin')
    op.drop_column('users', 'is_farmer')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_farmer', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('is_super_admin', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('is_user', sa.BOOLEAN(), server_default=sa.text('true'), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('is_worker', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('is_admin', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
    op.drop_table('user_roles')
    op.drop_table('roles')
    # ### end Alembic commands ###
