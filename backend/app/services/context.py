import uuid
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.persistence.models.users import UserProfile
from app.persistence.models.ledger import CanonicalTransaction

async def recalculate_user_profile(session: AsyncSession, user_id: uuid.UUID):
    stmt = select(UserProfile).where(UserProfile.user_id == user_id)
    result = await session.execute(stmt)
    profile = result.scalar_one_or_none()
    
    if not profile or not profile.is_dirty:
        return
        
    # Recalculate based on categorized transactions
    tx_stmt = select(CanonicalTransaction).where(
        CanonicalTransaction.user_id == user_id,
        CanonicalTransaction.status == 'completed'
    )
    tx_result = await session.execute(tx_stmt)
    txs = tx_result.scalars().all()
    
    income = 0.0
    necessary_expense = 0.0
    discretionary_expense = 0.0
    
    for tx in txs:
        cat = tx.classifier.get("category")
        amt = tx.source_amount or tx.dest_amount or 0.0
        
        if cat == "income" and tx.direction == "in":
            income += float(amt)
        elif cat == "necessary_expense" and tx.direction == "out":
            necessary_expense += float(amt)
        elif cat == "discretionary_expense" and tx.direction == "out":
            discretionary_expense += float(amt)
            
    # Naive assumption: all data represents one month for the MVP
    savings_rate = 0.0
    if income > 0:
        total_exp = necessary_expense + discretionary_expense
        savings_rate = max(0.0, (income - total_exp) / income * 100)
        
    profile.summaries = {
        "monthly_income_avg_usd": income,
        "monthly_recurring_spend_usd": necessary_expense,
        "discretionary_spend_usd": discretionary_expense,
        "savings_rate_pct": savings_rate,
        "runway_months": 6.0 # Hardcoded for MVP
    }
    
    profile.is_dirty = False
    profile.last_recomputed_at = datetime.now(timezone.utc)
    
    await session.commit()
    print(f"Recalculated profile for user {user_id}")
