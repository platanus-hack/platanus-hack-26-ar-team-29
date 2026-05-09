"""Eager imports so Alembic autogen sees every model."""

from app.persistence.models import chat, connections, plans, users, ledger  # noqa: F401
