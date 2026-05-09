from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.base import Base

class CanonicalAsset(Base):
    __tablename__ = "canonical_assets"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    symbol: Mapped[str] = mapped_column(String, nullable=False)
    asset_class: Mapped[str] = mapped_column(String, nullable=False)
    network: Mapped[str | None] = mapped_column(String, nullable=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String, nullable=True)
    decimals: Mapped[int] = mapped_column(nullable=False, server_default=text("2"))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "asset_class IN ('fiat', 'stablecoin', 'crypto', 'equity', 'etf', 'bond', 'treasury', 'roboadvisor_share')",
            name="chk_canonical_assets_class",
        ),
        UniqueConstraint(
            "symbol", "asset_class", "network", name="uq_canonical_assets_symbol_class_network"
        ),
    )


class CanonicalAccount(Base):
    __tablename__ = "canonical_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    connection_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("provider_connections.id", ondelete="CASCADE"), nullable=False
    )
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    account_kind: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "account_kind IN ('checking', 'investment', 'roboadvisor', 'wallet_address', 'card', 'savings')",
            name="chk_canonical_accounts_kind",
        ),
        UniqueConstraint(
            "connection_id", "external_id", name="uq_canonical_accounts_connection_external"
        ),
    )


class CanonicalBalance(Base):
    __tablename__ = "canonical_balances"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("canonical_accounts.id", ondelete="CASCADE"), nullable=False
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("canonical_assets.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quantity: Mapped[float] = mapped_column(Numeric(28, 10), nullable=False)
    avg_cost_usd: Mapped[float | None] = mapped_column(Numeric(28, 10), nullable=True)
    cost_basis_usd: Mapped[float | None] = mapped_column(Numeric(28, 10), nullable=True)
    as_of: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="chk_canonical_balances_quantity_nonneg"),
        UniqueConstraint("account_id", "asset_id", name="uq_canonical_balances_account_asset"),
    )


class CanonicalTransaction(Base):
    __tablename__ = "canonical_transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    connection_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("provider_connections.id", ondelete="SET NULL"), nullable=True
    )
    external_id: Mapped[str | None] = mapped_column(String, nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    direction: Mapped[str | None] = mapped_column(String, nullable=True)
    
    source_account_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("canonical_accounts.id", ondelete="SET NULL"), nullable=True
    )
    dest_account_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("canonical_accounts.id", ondelete="SET NULL"), nullable=True
    )
    asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("canonical_assets.id", ondelete="SET NULL"), nullable=True
    )
    
    source_amount: Mapped[float | None] = mapped_column(Numeric(28, 10), nullable=True)
    source_currency: Mapped[str | None] = mapped_column(String, nullable=True)
    dest_amount: Mapped[float | None] = mapped_column(Numeric(28, 10), nullable=True)
    dest_unit: Mapped[str | None] = mapped_column(String, nullable=True)
    
    fee_amount: Mapped[float] = mapped_column(Numeric(28, 10), nullable=False, server_default=text("0"))
    fee_currency: Mapped[str | None] = mapped_column(String, nullable=True)
    
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'completed'"))
    
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    
    raw_provider_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    classifier: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    source_kind: Mapped[str] = mapped_column(String, nullable=False)
    
    source_plan_step_id: Mapped[uuid.UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    source_document_id: Mapped[uuid.UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True, index=True)
    
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    merchant: Mapped[str | None] = mapped_column(String, nullable=True)
    search_text: Mapped[str | None] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "type IN ('trade', 'transfer_internal', 'external_in', 'external_out', 'fee', 'dividend', 'classifier_change', 'onchain', 'other')",
            name="chk_canonical_transactions_type",
        ),
        CheckConstraint(
            "direction IS NULL OR direction IN ('in', 'out', 'internal')",
            name="chk_canonical_transactions_direction",
        ),
        CheckConstraint(
            "status IN ('completed', 'pending', 'failed', 'cancelled')",
            name="chk_canonical_transactions_status",
        ),
        CheckConstraint(
            "source_kind IN ('provider_pulled', 'document_ingested', 'agent_issued')",
            name="chk_canonical_transactions_source_kind",
        ),
        UniqueConstraint(
            "connection_id", "external_id", name="uq_canonical_transactions_connection_external"
        ),
    )
