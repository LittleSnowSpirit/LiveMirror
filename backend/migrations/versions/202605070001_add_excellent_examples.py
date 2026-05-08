"""add excellent_examples table

Revision ID: 202605070001
Revises: 202604210001
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa


revision = "202605070001"
down_revision = "202604210001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "excellent_examples",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("speech_type", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("emotion_impact", sa.Float(), nullable=False),
        sa.Column("engagement_rate", sa.Float(), nullable=False),
        sa.Column("session_id", sa.String(length=100), nullable=True),
        sa.Column("timestamp", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index(op.f("ix_excellent_examples_id"), "excellent_examples", ["id"], unique=False)
    op.create_index(op.f("ix_excellent_examples_speech_type"), "excellent_examples", ["speech_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_excellent_examples_speech_type"), table_name="excellent_examples")
    op.drop_index(op.f("ix_excellent_examples_id"), table_name="excellent_examples")
    op.drop_table("excellent_examples")
