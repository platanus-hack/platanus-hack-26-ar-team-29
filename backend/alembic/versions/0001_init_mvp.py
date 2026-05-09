"""init mvp

Revision ID: 0001_init_mvp
Revises:
Create Date: 2026-05-09

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_init_mvp"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


_TABLES_WITH_UPDATED_AT = (
    "users",
    "chat_sessions",
    "provider_connections",
    "trade_plans",
    "trade_plan_steps",
)


def upgrade() -> None:
    # Required for gen_random_uuid() server defaults.
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # Auto-bump updated_at trigger function (per 02-4 §3).
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at := now();
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column(
            "primary_currency",
            sa.String(),
            server_default=sa.text("'USD'"),
            nullable=False,
        ),
        sa.Column(
            "locale",
            sa.String(),
            server_default=sa.text("'es-AR'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "primary_currency IN ('USD','ARS')",
            name="users_primary_currency_check",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "chat_sessions",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column(
            "pinned",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "last_activity_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_chat_sessions_user_active",
        "chat_sessions",
        ["user_id", "last_activity_at"],
        unique=False,
        postgresql_where=sa.text("archived_at IS NULL"),
        postgresql_using="btree",
    )

    op.create_table(
        "provider_connections",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("connection_type", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=True),
        sa.Column("auth_kind", sa.String(), nullable=False),
        sa.Column("credentials_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column(
            "credentials_kid",
            sa.String(),
            server_default=sa.text("'v1'"),
            nullable=False,
        ),
        sa.Column(
            "capabilities",
            postgresql.ARRAY(sa.String()),
            server_default=sa.text("'{}'::text[]"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(),
            server_default=sa.text("'healthy'"),
            nullable=False,
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("disconnected_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "auth_kind IN ('api_key','wallet_signature','oauth')",
            name="provider_connections_auth_kind_check",
        ),
        sa.CheckConstraint(
            "connection_type IN ('wallbit','ethereum')",
            name="provider_connections_type_check",
        ),
        sa.CheckConstraint(
            "status IN ('healthy','degraded','error','revoked','pending')",
            name="provider_connections_status_check",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_provider_connections_user_active",
        "provider_connections",
        ["user_id"],
        unique=False,
        postgresql_where=sa.text("disconnected_at IS NULL"),
    )

    op.create_table(
        "chat_messages",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("turn_id", sa.UUID(), nullable=True),
        sa.Column("author", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column(
            "content_blocks",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "tool_call",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("plan_id", sa.UUID(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "author IN ('user','agent','system','tool')",
            name="chat_messages_author_check",
        ),
        sa.CheckConstraint(
            "kind IN ('text','tool_call','plan_proposal','plan_step_update','navigation')",
            name="chat_messages_kind_check",
        ),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_chat_messages_plan",
        "chat_messages",
        ["plan_id"],
        unique=False,
        postgresql_where=sa.text("plan_id IS NOT NULL"),
    )
    op.create_index(
        "ix_chat_messages_session_created",
        "chat_messages",
        ["session_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "trade_plans",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "state",
            sa.String(),
            server_default=sa.text("'pending_approval'"),
            nullable=False,
        ),
        sa.Column(
            "origin_kind",
            sa.String(),
            server_default=sa.text("'chat'"),
            nullable=False,
        ),
        sa.Column("origin_session_id", sa.UUID(), nullable=True),
        sa.Column("origin_message_id", sa.UUID(), nullable=True),
        sa.Column("total_estimated_usd", sa.Numeric(precision=28, scale=10), nullable=True),
        sa.Column(
            "failure_policy",
            sa.String(),
            server_default=sa.text("'stop_on_first_error'"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_reason", sa.String(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "state IN ('pending_approval','approved','executing','completed',"
            "'partially_failed','rejected','expired')",
            name="trade_plans_state_check",
        ),
        sa.ForeignKeyConstraint(["origin_message_id"], ["chat_messages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["origin_session_id"], ["chat_sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_trade_plans_user_state_created",
        "trade_plans",
        ["user_id", "state", "created_at"],
        unique=False,
    )

    op.create_table(
        "trade_plan_steps",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("plan_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("tool_name", sa.String(), nullable=False),
        sa.Column(
            "args",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("human_description_es", sa.String(), nullable=False),
        sa.Column("human_description_en", sa.String(), nullable=True),
        sa.Column(
            "category",
            sa.String(),
            server_default=sa.text("'write'"),
            nullable=False,
        ),
        sa.Column("provider_capability", sa.String(), nullable=True),
        sa.Column("connection_id", sa.UUID(), nullable=True),
        sa.Column("estimated_usd", sa.Numeric(precision=28, scale=10), nullable=True),
        sa.Column(
            "state",
            sa.String(),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column("result_summary", sa.String(), nullable=True),
        sa.Column(
            "result_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("category IN ('read','write')", name="trade_plan_steps_category_check"),
        sa.CheckConstraint(
            "state IN ('pending','executing','ok','failed','skipped')",
            name="trade_plan_steps_state_check",
        ),
        sa.ForeignKeyConstraint(
            ["connection_id"], ["provider_connections.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["plan_id"], ["trade_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plan_id", "ordinal", name="uq_trade_plan_steps_plan_ordinal"),
    )
    op.create_index(
        "ix_trade_plan_steps_plan_state",
        "trade_plan_steps",
        ["plan_id", "state"],
        unique=False,
    )

    # Attach the auto-bump trigger to every table with updated_at.
    for table in _TABLES_WITH_UPDATED_AT:
        op.execute(
            f"""
            CREATE TRIGGER trg_{table}_set_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            """
        )

    # Seed the hardcoded dev user (idempotent).
    op.execute(
        """
        INSERT INTO users (id, display_name, primary_currency, locale)
        VALUES ('00000000-0000-0000-0000-000000000001'::uuid,
                'Tomás Demo', 'USD', 'es-AR')
        ON CONFLICT (id) DO NOTHING;
        """
    )


def downgrade() -> None:
    for table in _TABLES_WITH_UPDATED_AT:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_set_updated_at ON {table}")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at()")

    op.drop_index("ix_trade_plan_steps_plan_state", table_name="trade_plan_steps")
    op.drop_table("trade_plan_steps")
    op.drop_index("ix_trade_plans_user_state_created", table_name="trade_plans")
    op.drop_table("trade_plans")
    op.drop_index("ix_chat_messages_session_created", table_name="chat_messages")
    op.drop_index(
        "ix_chat_messages_plan",
        table_name="chat_messages",
        postgresql_where=sa.text("plan_id IS NOT NULL"),
    )
    op.drop_table("chat_messages")
    op.drop_index(
        "ix_provider_connections_user_active",
        table_name="provider_connections",
        postgresql_where=sa.text("disconnected_at IS NULL"),
    )
    op.drop_table("provider_connections")
    op.drop_index(
        "ix_chat_sessions_user_active",
        table_name="chat_sessions",
        postgresql_where=sa.text("archived_at IS NULL"),
        postgresql_using="btree",
    )
    op.drop_table("chat_sessions")
    op.drop_table("users")
