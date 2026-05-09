"""ethereum custodial connection_type + auth_kind

Adds the new values that the custodial Ethereum surface requires:
* ``connection_type`` allows ``'ethereum_custodial'`` in addition to the
  existing ``'wallbit'`` and ``'ethereum'``.
* ``auth_kind`` allows ``'private_key'`` in addition to ``'api_key'``,
  ``'wallet_signature'``, ``'oauth'``.

Both columns are guarded by CHECK constraints introduced in
``0001_init_mvp.py``; we drop and recreate each constraint with the new IN
list. No data migration needed — there are no existing rows that would
violate the new lists.

Revision ID: 0002_ethereum_custodial_constraints
Revises: 0001_init_mvp
Create Date: 2026-05-09
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002_eth_custodial_constraints"
down_revision: str | None = "0001_init_mvp"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "provider_connections_type_check",
        "provider_connections",
        type_="check",
    )
    op.create_check_constraint(
        "provider_connections_type_check",
        "provider_connections",
        "connection_type IN ('wallbit','ethereum','ethereum_custodial')",
    )

    op.drop_constraint(
        "provider_connections_auth_kind_check",
        "provider_connections",
        type_="check",
    )
    op.create_check_constraint(
        "provider_connections_auth_kind_check",
        "provider_connections",
        "auth_kind IN ('api_key','wallet_signature','oauth','private_key')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "provider_connections_auth_kind_check",
        "provider_connections",
        type_="check",
    )
    op.create_check_constraint(
        "provider_connections_auth_kind_check",
        "provider_connections",
        "auth_kind IN ('api_key','wallet_signature','oauth')",
    )

    op.drop_constraint(
        "provider_connections_type_check",
        "provider_connections",
        type_="check",
    )
    op.create_check_constraint(
        "provider_connections_type_check",
        "provider_connections",
        "connection_type IN ('wallbit','ethereum')",
    )
