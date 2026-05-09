from fastapi import APIRouter

from app.api.rest import chat, connections, onchain, plans, portfolio
from app.api.ws import chat as ws_chat

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(connections.router, prefix="/connections", tags=["connections"])
# /connections/{id}/onchain/* routes — separate file for clarity, mounted under
# the same /connections prefix so URL paths match the artifact (02-3 §5.13.2).
api_router.include_router(onchain.router, prefix="/connections", tags=["onchain"])
api_router.include_router(portfolio.router, tags=["portfolio"])
api_router.include_router(ws_chat.router, tags=["ws"])
