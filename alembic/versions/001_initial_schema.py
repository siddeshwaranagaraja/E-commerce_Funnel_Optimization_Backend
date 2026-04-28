"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-04-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('user_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('product_id', sa.String(), nullable=True),
        sa.Column('device_type', sa.String(), nullable=True),
        sa.Column('source_channel', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('metadata_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_events_id'), 'user_events', ['id'], unique=False)
    op.create_index(op.f('ix_user_events_user_id'), 'user_events', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_events_session_id'), 'user_events', ['session_id'], unique=False)
    op.create_index(op.f('ix_user_events_timestamp'), 'user_events', ['timestamp'], unique=False)

    op.create_table('funnel_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date_key', sa.DateTime(), nullable=False),
        sa.Column('stage_name', sa.String(), nullable=False),
        sa.Column('users_count', sa.Integer(), nullable=False),
        sa.Column('sessions_count', sa.Integer(), nullable=False),
        sa.Column('conversion_rate', sa.Float(), nullable=True),
        sa.Column('dropoff_rate', sa.Float(), nullable=True),
        sa.Column('segment_key', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_funnel_snapshots_id'), 'funnel_snapshots', ['id'], unique=False)
    op.create_index(op.f('ix_funnel_snapshots_date_key'), 'funnel_snapshots', ['date_key'], unique=False)

    op.create_table('behavior_insights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('insight_type', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_behavior_insights_id'), 'behavior_insights', ['id'], unique=False)

    op.create_table('experiment_suggestions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('experiment_name', sa.String(), nullable=False),
        sa.Column('hypothesis', sa.Text(), nullable=False),
        sa.Column('variants', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_experiment_suggestions_id'), 'experiment_suggestions', ['id'], unique=False)

    op.create_table('recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recommendation_type', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recommendations_id'), 'recommendations', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_recommendations_id'), table_name='recommendations')
    op.drop_table('recommendations')
    op.drop_index(op.f('ix_experiment_suggestions_id'), table_name='experiment_suggestions')
    op.drop_table('experiment_suggestions')
    op.drop_index(op.f('ix_behavior_insights_id'), table_name='behavior_insights')
    op.drop_table('behavior_insights')
    op.drop_index(op.f('ix_funnel_snapshots_date_key'), table_name='funnel_snapshots')
    op.drop_index(op.f('ix_funnel_snapshots_id'), table_name='funnel_snapshots')
    op.drop_table('funnel_snapshots')
    op.drop_index(op.f('ix_user_events_timestamp'), table_name='user_events')
    op.drop_index(op.f('ix_user_events_session_id'), table_name='user_events')
    op.drop_index(op.f('ix_user_events_user_id'), table_name='user_events')
    op.drop_index(op.f('ix_user_events_id'), table_name='user_events')
    op.drop_table('user_events')