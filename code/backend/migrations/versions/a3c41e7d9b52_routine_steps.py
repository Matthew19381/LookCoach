"""routine_steps (own skincare routine)

Revision ID: a3c41e7d9b52
Revises: 75de7bceaf5d
Create Date: 2026-11-04 23:40:00

The own routine and the "Dziś" view (2026-10-15) created routine_steps through
create_all; master's Alembic history never had it. "Add if missing": the PC's
looks_optimizer.db already has the table (since 2026-10-18) and only gets this
revision stamped. downgrade drops only what this revision would have added.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3c41e7d9b52'
down_revision: Union[str, None] = '75de7bceaf5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Own skincare routine steps (models/routine_step.py)."""
    if "routine_steps" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        'routine_steps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('slot', sa.String(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('weekdays', sa.String(), nullable=False),
        sa.Column('essential', sa.Boolean(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('evidence_key', sa.String(), nullable=True),
        sa.Column('note', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_routine_steps_id', 'routine_steps', ['id'])
    op.create_index('ix_routine_steps_user_id', 'routine_steps', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_routine_steps_user_id', table_name='routine_steps')
    op.drop_index('ix_routine_steps_id', table_name='routine_steps')
    op.drop_table('routine_steps')
