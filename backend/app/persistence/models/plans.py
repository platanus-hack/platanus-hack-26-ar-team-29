"""Trade plan ORM models — see 02-4_database_schema.md."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.base import Base


class TradePlan(Base):
    __tablename__ = "trade_plans"
    __table_args__ = (
        CheckConstraint(
            "state IN ('pending_approval','approved','executing','completed',"
            "'partially_failed','rejected','expired')",
            name="trade_plans_state_check",
        ),
        Index("ix_trade_plans_user_state_created", "user_id", "state", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    state: Mapped[str] = mapped_column(
        String, nullable=False, server_default=text("'pending_approval'")
    )
    origin_kind: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'chat'"))
    origin_session_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    origin_message_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("chat_messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    total_estimated_usd: Mapped[Decimal | None] = mapped_column(Numeric(28, 10), nullable=True)
    failure_policy: Mapped[str] = mapped_column(
        String, nullable=False, server_default=text("'stop_on_first_error'")
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    plan_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    steps: Mapped[list[TradePlanStep]] = relationship(
        "TradePlanStep",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="TradePlanStep.ordinal",
    )


class TradePlanStep(Base):
    __tablename__ = "trade_plan_steps"
    __table_args__ = (
        CheckConstraint("category IN ('read','write')", name="trade_plan_steps_category_check"),
        CheckConstraint(
            "state IN ('pending','executing','ok','failed','skipped')",
            name="trade_plan_steps_state_check",
        ),
        UniqueConstraint("plan_id", "ordinal", name="uq_trade_plan_steps_plan_ordinal"),
        Index("ix_trade_plan_steps_plan_state", "plan_id", "state"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("trade_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    tool_name: Mapped[str] = mapped_column(String, nullable=False)
    args: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    human_description_es: Mapped[str] = mapped_column(String, nullable=False)
    human_description_en: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'write'"))
    provider_capability: Mapped[str | None] = mapped_column(String, nullable=True)
    connection_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("provider_connections.id", ondelete="SET NULL"),
        nullable=True,
    )
    estimated_usd: Mapped[Decimal | None] = mapped_column(Numeric(28, 10), nullable=True)
    state: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'pending'"))
    result_summary: Mapped[str | None] = mapped_column(String, nullable=True)
    result_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    plan: Mapped[TradePlan] = relationship("TradePlan", back_populates="steps")
