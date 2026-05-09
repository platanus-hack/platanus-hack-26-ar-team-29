from fastapi import APIRouter

from app.api.rest import chat, connections, plans, portfolio
from app.api.ws import chat as ws_chat

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(connections.router, prefix="/connections", tags=["connections"])
api_router.include_router(portfolio.router, tags=["portfolio"])
api_router.include_router(ws_chat.router, tags=["ws"])
