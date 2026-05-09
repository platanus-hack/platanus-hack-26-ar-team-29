from fastapi import APIRouter

from app.api.rest import chat, connections, defi, onchain, plans, portfolio
from app.api.ws import chat as ws_chat

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(connections.router, prefix="/connections", tags=["connections"])
# /connections/{id}/onchain/* routes — separate file for clarity, mounted under
# the same /connections prefix so URL paths match the artifact (02-3 §5.13.2).
api_router.include_router(onchain.router, prefix="/connections", tags=["onchain"])
# DeFi: /defi/markets sits under /defi; supply/withdraw/positions are
# connection-scoped. Mounting two routers from defi.py keeps URLs aligned with
# 02-3 §5.13.3 without rewriting prefixes inline.
api_router.include_router(defi.markets_router, prefix="/defi", tags=["defi"])
api_router.include_router(defi.connection_scoped_router, prefix="/connections", tags=["defi"])
api_router.include_router(portfolio.router, tags=["portfolio"])
api_router.include_router(ws_chat.router, tags=["ws"])
