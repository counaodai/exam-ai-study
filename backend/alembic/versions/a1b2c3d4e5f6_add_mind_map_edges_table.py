"""add_mind_map_edges_table

Revision ID: a1b2c3d4e5f6
Revises: eda8b96ea2ad
Create Date: 2026-06-09 10:00:00.000000

新增思维导图独立连线表，支持任意节点间连接、箭头、样式编辑。
不影响其他模块。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'eda8b96ea2ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'mind_map_edges',
        sa.Column('mind_map_id', sa.Uuid(), nullable=False),
        sa.Column('source_id', sa.Uuid(), nullable=False),
        sa.Column('target_id', sa.Uuid(), nullable=False),
        sa.Column('edge_type', sa.String(length=20), nullable=False, server_default='default'),
        sa.Column('color', sa.String(length=20), nullable=False, server_default='#409EFF'),
        sa.Column('stroke_width', sa.SmallInteger(), nullable=False, server_default='2'),
        sa.Column('has_arrow', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('animated', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('label', sa.String(length=100), nullable=True),
        sa.Column('is_derived', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['mind_map_id'], ['mind_maps.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['mind_map_nodes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_id'], ['mind_map_nodes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_mind_map_edges_mind_map_id', 'mind_map_edges', ['mind_map_id'])
    op.create_index('ix_mind_map_edges_source_id', 'mind_map_edges', ['source_id'])
    op.create_index('ix_mind_map_edges_target_id', 'mind_map_edges', ['target_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_mind_map_edges_target_id', table_name='mind_map_edges')
    op.drop_index('ix_mind_map_edges_source_id', table_name='mind_map_edges')
    op.drop_index('ix_mind_map_edges_mind_map_id', table_name='mind_map_edges')
    op.drop_table('mind_map_edges')
