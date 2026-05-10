"""ProfilerService — analyzes user data via LLM to build a financial profile."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.anthropic import AnthropicClient
from app.ai.prompts.profiler import PROFILER_SYSTEM_PROMPT
from app.persistence.models.ledger import CanonicalTransaction
from app.persistence.models.users import UserProfile
from app.persistence.repositories.user_profile import UserProfileRepository
from app.services.portfolio import PortfolioService

log = structlog.get_logger(__name__)


class ProfilerService:
    def __init__(
        self,
        session: AsyncSession,
        portfolio_service: PortfolioService,
        anthropic_client: AnthropicClient,
    ) -> None:
        self.session = session
        self.repo = UserProfileRepository(session)
        self.portfolio_service = portfolio_service
        self.anthropic_client = anthropic_client

    async def get_profile(self, user_id: UUID) -> UserProfile | None:
        return await self.repo.get(user_id)

    async def generate_profile(self, user_id: UUID) -> UserProfile:
        log.info("Generating profile", user_id=str(user_id))

        # 1. Fetch current balances and positions
        balances = await self.portfolio_service.read_balances(user_id)
        positions = await self.portfolio_service.read_positions(user_id)

        # 2. Compute simple net worth & allocations directly in Python (to guide the LLM better)
        total_fiat_usd = sum(b.usd_value or 0.0 for b in balances)
        total_investments_usd = sum(p.usd_value or 0.0 for p in positions)
        total_usd = total_fiat_usd + total_investments_usd

        # 3. Aggregate transactions (last 30 days)
        thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
        stmt = (
            select(CanonicalTransaction)
            .where(CanonicalTransaction.user_id == user_id)
            .where(CanonicalTransaction.occurred_at >= thirty_days_ago)
        )
        result = await self.session.execute(stmt)
        txs = result.scalars().all()

        incoming_volume = 0.0
        outgoing_volume = 0.0
        merchants: dict[str, float] = {}
        trade_count = 0

        for tx in txs:
            amount = float(tx.source_amount or tx.dest_amount or 0.0)
            if tx.direction == "inbound":
                incoming_volume += amount
            elif tx.direction == "outbound":
                outgoing_volume += amount
                if tx.merchant:
                    merchants[tx.merchant] = merchants.get(tx.merchant, 0.0) + amount
            if tx.type == "trade":
                trade_count += 1

        context_data = {
            "balances": [b.model_dump() for b in balances],
            "positions": [p.model_dump() for p in positions],
            "aggregates": {
                "last_30_days": {
                    "incoming_volume_usd": incoming_volume,
                    "outgoing_volume_usd": outgoing_volume,
                    "top_merchants_by_spend": sorted(
                        merchants.items(), key=lambda x: x[1], reverse=True
                    )[:5],
                    "trade_count": trade_count,
                },
                "total_fiat_usd": total_fiat_usd,
                "total_investments_usd": total_investments_usd,
                "net_worth_usd": total_usd,
            },
        }

        # 4. Call Anthropic
        user_message = (
            f"User Data:\n{json.dumps(context_data, indent=2)}\n\nPlease output the JSON profile."
        )

        try:
            response = await self.anthropic_client.messages_create(
                system=PROFILER_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
                max_tokens=1000,
                temperature=0.2,
            )
            # Parse the response text
            # Depending on anthropic SDK, it returns a Message object with .content
            response_text = response.content[0].text

            # Remove any trailing/leading markdown if the model hallucinated it
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            profile_data = json.loads(response_text.strip())

        except Exception:
            log.error("Failed to generate profile with LLM", exc_info=True)
            # Fallback data if API fails
            profile_data = {
                "risk_profile": {
                    "level": "moderate",
                    "score_1_to_10": 5,
                    "reasoning": "Fallback due to LLM error",
                },
                "summaries": {"spending_behavior": "Unknown", "investment_style": "Unknown"},
                "portfolio_metrics": {
                    "estimated_net_worth_usd": total_usd,
                    "fiat_percentage": (total_fiat_usd / total_usd * 100) if total_usd > 0 else 0,
                    "investments_percentage": (total_investments_usd / total_usd * 100)
                    if total_usd > 0
                    else 0,
                },
            }

        # 5. Upsert
        profile = await self.repo.upsert(
            user_id=user_id,
            summaries=profile_data.get("summaries", {}),
            risk_profile=profile_data.get("risk_profile", {}),
            portfolio_metrics=profile_data.get("portfolio_metrics", {}),
            is_dirty=False,
        )

        await self.session.commit()
        return profile
