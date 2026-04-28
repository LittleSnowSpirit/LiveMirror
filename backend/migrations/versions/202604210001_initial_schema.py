"""initial schema

Revision ID: 202604210001
Revises:
Create Date: 2026-04-21
"""

from alembic import op
import sqlalchemy as sa


revision = "202604210001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token", sa.String(length=500), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index(op.f("ix_tokens_id"), "tokens", ["id"], unique=False)
    op.create_index(op.f("ix_tokens_token"), "tokens", ["token"], unique=True)

    op.create_table(
        "danmus",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.Float(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("user_level", sa.Integer(), nullable=True),
        sa.Column("sentiment", sa.String(length=20), nullable=True),
        sa.Column("sentiment_score", sa.Float(), nullable=True),
        sa.Column("danmu_type", sa.String(length=50), nullable=True),
        sa.Column("like_count", sa.Integer(), nullable=True),
        sa.Column("reply_count", sa.Integer(), nullable=True),
        sa.Column("speech_segment_id", sa.Integer(), nullable=True),
        sa.Column("is_key_danmu", sa.Boolean(), nullable=True),
        sa.Column("key_type", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index(op.f("ix_danmus_id"), "danmus", ["id"], unique=False)
    op.create_index(op.f("ix_danmus_user_id"), "danmus", ["user_id"], unique=False)
    op.create_index(op.f("ix_danmus_timestamp"), "danmus", ["timestamp"], unique=False)
    op.create_index(op.f("ix_danmus_username"), "danmus", ["username"], unique=False)
    op.create_index(op.f("ix_danmus_speech_segment_id"), "danmus", ["speech_segment_id"], unique=False)
    op.create_index(op.f("ix_danmus_created_at"), "danmus", ["created_at"], unique=False)
    op.create_index("idx_danmu_timestamp_type", "danmus", ["timestamp", "danmu_type"], unique=False)
    op.create_index("idx_danmu_sentiment", "danmus", ["sentiment", "sentiment_score"], unique=False)
    op.create_index("idx_danmu_key", "danmus", ["is_key_danmu", "key_type"], unique=False)

    op.create_table(
        "danmu_batches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("batch_id", sa.String(length=100), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=True),
        sa.Column("file_format", sa.String(length=20), nullable=True),
        sa.Column("total_count", sa.Integer(), nullable=True),
        sa.Column("success_count", sa.Integer(), nullable=True),
        sa.Column("failed_count", sa.Integer(), nullable=True),
        sa.Column("start_timestamp", sa.Float(), nullable=True),
        sa.Column("end_timestamp", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index(op.f("ix_danmu_batches_id"), "danmu_batches", ["id"], unique=False)
    op.create_index(op.f("ix_danmu_batches_batch_id"), "danmu_batches", ["batch_id"], unique=True)

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.String(length=100), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("duration", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("current_step", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("transcription", sa.Text(), nullable=True),
        sa.Column("transcription_segments", sa.JSON(), nullable=True),
        sa.Column("language", sa.String(length=20), nullable=True),
        sa.Column("analysis_result", sa.JSON(), nullable=True),
        sa.Column("report_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index(op.f("ix_tasks_id"), "tasks", ["id"], unique=False)
    op.create_index(op.f("ix_tasks_task_id"), "tasks", ["task_id"], unique=True)
    op.create_index(op.f("ix_tasks_status"), "tasks", ["status"], unique=False)
    op.create_index(op.f("ix_tasks_created_at"), "tasks", ["created_at"], unique=False)

    op.create_table(
        "analysis_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.String(length=100), sa.ForeignKey("tasks.task_id"), nullable=False),
        sa.Column("report_data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index(op.f("ix_analysis_reports_id"), "analysis_reports", ["id"], unique=False)
    op.create_index(op.f("ix_analysis_reports_task_id"), "analysis_reports", ["task_id"], unique=False)
    op.create_index(op.f("ix_analysis_reports_created_at"), "analysis_reports", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("analysis_reports")
    op.drop_table("tasks")
    op.drop_table("danmu_batches")
    op.drop_table("danmus")
    op.drop_table("tokens")
    op.drop_table("users")
