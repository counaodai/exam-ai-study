"""add is_valid column to questions

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-09

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'questions',
        sa.Column('is_valid', sa.Boolean(), nullable=False, server_default=sa.text('1'),
                  comment='是否为有效提问，无效提问不计入统计')
    )


def downgrade() -> None:
    op.drop_column('questions', 'is_valid')
