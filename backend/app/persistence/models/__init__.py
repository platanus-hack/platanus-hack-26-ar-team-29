"""Eager imports so Alembic autogen sees every model."""

from app.persistence.models import chat, connections, ledger, plans, users  # noqa: F401
