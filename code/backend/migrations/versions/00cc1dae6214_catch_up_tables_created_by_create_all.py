"""Catch-up: tables created by create_all() without a migration (plan 7.8, D14)

Revision ID: 00cc1dae6214
Revises: f7fcbdcef3ba
Create Date: 2026-11-02 11:28:11.535589

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00cc1dae6214'
down_revision: Union[str, None] = 'f7fcbdcef3ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tables that create_all() made at startup before this migration existed (2026-11-02):
    # create only what is missing, so an existing database upgrades without errors.
    existing = set(sa.inspect(op.get_bind()).get_table_names())

    if 'assistant_messages' not in existing:
        op.create_table('assistant_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=16), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('actions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'assistant_messages' not in existing:
        with op.batch_alter_table('assistant_messages', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_assistant_messages_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_assistant_messages_user_id'), ['user_id'], unique=False)

    if 'directive_states' not in existing:
        op.create_table('directive_states',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('survival_mode', sa.Boolean(), nullable=True),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('quiet_hours_from', sa.String(), nullable=True),
        sa.Column('quiet_hours_to', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'directive_states' not in existing:
        with op.batch_alter_table('directive_states', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_directive_states_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_directive_states_user_id'), ['user_id'], unique=True)

    if 'ecosystem_snapshots' not in existing:
        op.create_table('ecosystem_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('data', sa.Text(), nullable=False),
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'ecosystem_snapshots' not in existing:
        with op.batch_alter_table('ecosystem_snapshots', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_ecosystem_snapshots_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_ecosystem_snapshots_user_id'), ['user_id'], unique=True)

    if 'ingredient_usage' not in existing:
        op.create_table('ingredient_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ingredient', sa.String(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'ingredient_usage' not in existing:
        with op.batch_alter_table('ingredient_usage', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_ingredient_usage_date'), ['date'], unique=False)
            batch_op.create_index(batch_op.f('ix_ingredient_usage_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_ingredient_usage_ingredient'), ['ingredient'], unique=False)
            batch_op.create_index(batch_op.f('ix_ingredient_usage_user_id'), ['user_id'], unique=False)

    if 'outbox_events' not in existing:
        op.create_table('outbox_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('data', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('next_attempt_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('hub_response', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'outbox_events' not in existing:
        with op.batch_alter_table('outbox_events', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_outbox_events_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_outbox_events_status'), ['status'], unique=False)
            batch_op.create_index(batch_op.f('ix_outbox_events_user_id'), ['user_id'], unique=False)

    if 'push_subscriptions' not in existing:
        op.create_table('push_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('endpoint', sa.Text(), nullable=False),
        sa.Column('p256dh', sa.String(length=200), nullable=False),
        sa.Column('auth', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('endpoint')
        )
    if 'push_subscriptions' not in existing:
        with op.batch_alter_table('push_subscriptions', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_push_subscriptions_user_id'), ['user_id'], unique=False)

    if 'reminder_logs' not in existing:
        op.create_table('reminder_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.String(length=30), nullable=False),
        sa.Column('day', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'kind', 'day')
        )
    if 'reminder_logs' not in existing:
        with op.batch_alter_table('reminder_logs', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_reminder_logs_user_id'), ['user_id'], unique=False)

    if 'reminder_settings' not in existing:
        op.create_table('reminder_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('morning_time', sa.String(length=5), nullable=False),
        sa.Column('evening_time', sa.String(length=5), nullable=False),
        sa.Column('photo_reminders', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )
    if 'reminder_settings' not in existing:
        with op.batch_alter_table('reminder_settings', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_reminder_settings_user_id'), ['user_id'], unique=True)

    if 'skin_reactions' not in existing:
        op.create_table('skin_reactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ingredient', sa.String(), nullable=False),
        sa.Column('reaction', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'skin_reactions' not in existing:
        with op.batch_alter_table('skin_reactions', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_skin_reactions_date'), ['date'], unique=False)
            batch_op.create_index(batch_op.f('ix_skin_reactions_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_skin_reactions_ingredient'), ['ingredient'], unique=False)
            batch_op.create_index(batch_op.f('ix_skin_reactions_user_id'), ['user_id'], unique=False)

    if 'skincare_products' not in existing:
        op.create_table('skincare_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('ingredients_json', sa.Text(), nullable=False),
        sa.Column('actives_json', sa.Text(), nullable=False),
        sa.Column('slot', sa.String(), nullable=True),
        sa.Column('in_routine', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'skincare_products' not in existing:
        with op.batch_alter_table('skincare_products', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_skincare_products_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_skincare_products_user_id'), ['user_id'], unique=False)

    if 'style_preview_logs' not in existing:
        op.create_table('style_preview_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.String(length=20), nullable=False),
        sa.Column('option', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
    if 'style_preview_logs' not in existing:
        with op.batch_alter_table('style_preview_logs', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_style_preview_logs_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_style_preview_logs_user_id'), ['user_id'], unique=False)

    if 'adherence_logs' not in existing:
        op.create_table('adherence_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('protocol_type', sa.Enum('SKINCARE_MORNING', 'SKINCARE_EVENING', 'TRAINING', 'SLEEP', 'NUTRITION', 'STRESS', name='protocoltypeenum'), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('difficulty_level', sa.Enum('FULL', 'REDUCED', 'MINIMUM', 'SURVIVAL', name='difficultylevelenum'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    if 'adherence_logs' not in existing:
        with op.batch_alter_table('adherence_logs', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_adherence_logs_date'), ['date'], unique=False)
            batch_op.create_index(batch_op.f('ix_adherence_logs_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_adherence_logs_protocol_type'), ['protocol_type'], unique=False)

    if 'consistency_metrics' not in existing:
        op.create_table('consistency_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_days', sa.Integer(), nullable=False),
        sa.Column('overall_consistency_score', sa.Float(), nullable=False),
        sa.Column('system_status', sa.String(length=50), nullable=False),
        sa.Column('protocols_tracked', sa.Integer(), nullable=False),
        sa.Column('protocols_needing_reduction', sa.Integer(), nullable=False),
        sa.Column('average_adherence', sa.Float(), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    if 'consistency_metrics' not in existing:
        with op.batch_alter_table('consistency_metrics', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_consistency_metrics_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_consistency_metrics_period_start'), ['period_start'], unique=False)

    if 'protocol_adherence' not in existing:
        op.create_table('protocol_adherence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('protocol_type', sa.Enum('SKINCARE_MORNING', 'SKINCARE_EVENING', 'TRAINING', 'SLEEP', 'NUTRITION', 'STRESS', name='protocoltypeenum'), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_days', sa.Integer(), nullable=False),
        sa.Column('total_scheduled', sa.Integer(), nullable=False),
        sa.Column('total_completed', sa.Integer(), nullable=False),
        sa.Column('adherence_rate', sa.Float(), nullable=False),
        sa.Column('adherence_level', sa.Enum('EXCELLENT', 'GOOD', 'MODERATE', 'LOW', 'CRITICAL', name='adherencelevelenum'), nullable=False),
        sa.Column('current_difficulty', sa.Enum('FULL', 'REDUCED', 'MINIMUM', 'SURVIVAL', name='difficultylevelenum'), nullable=False),
        sa.Column('recommended_difficulty', sa.Enum('FULL', 'REDUCED', 'MINIMUM', 'SURVIVAL', name='difficultylevelenum'), nullable=False),
        sa.Column('consecutive_misses', sa.Integer(), nullable=False),
        sa.Column('longest_streak', sa.Integer(), nullable=False),
        sa.Column('current_streak', sa.Integer(), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
    if 'protocol_adherence' not in existing:
        with op.batch_alter_table('protocol_adherence', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_protocol_adherence_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_protocol_adherence_period_start'), ['period_start'], unique=False)
            batch_op.create_index(batch_op.f('ix_protocol_adherence_protocol_type'), ['protocol_type'], unique=False)

        # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('protocol_adherence', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_protocol_adherence_protocol_type'))
        batch_op.drop_index(batch_op.f('ix_protocol_adherence_period_start'))
        batch_op.drop_index(batch_op.f('ix_protocol_adherence_id'))

    op.drop_table('protocol_adherence')
    with op.batch_alter_table('consistency_metrics', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_consistency_metrics_period_start'))
        batch_op.drop_index(batch_op.f('ix_consistency_metrics_id'))

    op.drop_table('consistency_metrics')
    with op.batch_alter_table('adherence_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_adherence_logs_protocol_type'))
        batch_op.drop_index(batch_op.f('ix_adherence_logs_id'))
        batch_op.drop_index(batch_op.f('ix_adherence_logs_date'))

    op.drop_table('adherence_logs')
    with op.batch_alter_table('style_preview_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_style_preview_logs_user_id'))
        batch_op.drop_index(batch_op.f('ix_style_preview_logs_id'))

    op.drop_table('style_preview_logs')
    with op.batch_alter_table('skincare_products', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_skincare_products_user_id'))
        batch_op.drop_index(batch_op.f('ix_skincare_products_id'))

    op.drop_table('skincare_products')
    with op.batch_alter_table('skin_reactions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_skin_reactions_user_id'))
        batch_op.drop_index(batch_op.f('ix_skin_reactions_ingredient'))
        batch_op.drop_index(batch_op.f('ix_skin_reactions_id'))
        batch_op.drop_index(batch_op.f('ix_skin_reactions_date'))

    op.drop_table('skin_reactions')
    with op.batch_alter_table('reminder_settings', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_reminder_settings_user_id'))

    op.drop_table('reminder_settings')
    with op.batch_alter_table('reminder_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_reminder_logs_user_id'))

    op.drop_table('reminder_logs')
    with op.batch_alter_table('push_subscriptions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_push_subscriptions_user_id'))

    op.drop_table('push_subscriptions')
    with op.batch_alter_table('outbox_events', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_outbox_events_user_id'))
        batch_op.drop_index(batch_op.f('ix_outbox_events_status'))
        batch_op.drop_index(batch_op.f('ix_outbox_events_id'))

    op.drop_table('outbox_events')
    with op.batch_alter_table('ingredient_usage', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_ingredient_usage_user_id'))
        batch_op.drop_index(batch_op.f('ix_ingredient_usage_ingredient'))
        batch_op.drop_index(batch_op.f('ix_ingredient_usage_id'))
        batch_op.drop_index(batch_op.f('ix_ingredient_usage_date'))

    op.drop_table('ingredient_usage')
    with op.batch_alter_table('ecosystem_snapshots', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_ecosystem_snapshots_user_id'))
        batch_op.drop_index(batch_op.f('ix_ecosystem_snapshots_id'))

    op.drop_table('ecosystem_snapshots')
    with op.batch_alter_table('directive_states', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_directive_states_user_id'))
        batch_op.drop_index(batch_op.f('ix_directive_states_id'))

    op.drop_table('directive_states')
    with op.batch_alter_table('assistant_messages', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_assistant_messages_user_id'))
        batch_op.drop_index(batch_op.f('ix_assistant_messages_id'))

    op.drop_table('assistant_messages')
    # ### end Alembic commands ###
