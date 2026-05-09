"""Error envelope per 02-3_api_surface.md §3.3."""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

log = structlog.get_logger(__name__)


# Stable machine-readable codes from 02-3 §3.3.
INVALID_REQUEST = "INVALID_REQUEST"
VALIDATION_FAILED = "VALIDATION_FAILED"
UNAUTHORIZED = "UNAUTHORIZED"
FORBIDDEN = "FORBIDDEN"
NOT_FOUND = "NOT_FOUND"
IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"
OPTIMISTIC_LOCK_CONFLICT = "OPTIMISTIC_LOCK_CONFLICT"
KYC_REQUIRED = "KYC_REQUIRED"
INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
PLAN_STALE = "PLAN_STALE"
RATE_LIMITED = "RATE_LIMITED"
PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
INTERNAL_ERROR = "INTERNAL_ERROR"


class APIError(Exception):
    def __init__(
        self,
        code: str,
        http_status: int,
        message_es: str,
        message_en: str | None = None,
        params: dict[str, Any] | None = None,
        details: Any | None = None,
    ) -> None:
        super().__init__(message_en or message_es)
        self.code = code
        self.http_status = http_status
        self.message_es = message_es
        self.message_en = message_en
        self.params = params or {}
        self.details = details


def _envelope(
    code: str,
    message_es: str,
    message_en: str | None,
    params: dict[str, Any],
    details: Any | None,
    trace_id: str,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message_es": message_es,
            "message_en": message_en,
            "params": params,
            "details": details,
            "trace_id": trace_id,
        }
    }


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def handle_api_error(request: Request, exc: APIError) -> JSONResponse:
        trace_id = uuid.uuid4().hex
        return JSONResponse(
            status_code=exc.http_status,
            content=_envelope(
                exc.code,
                exc.message_es,
                exc.message_en,
                exc.params,
                exc.details,
                trace_id,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        trace_id = uuid.uuid4().hex
        details = {".".join(str(p) for p in err["loc"]): err["msg"] for err in exc.errors()}
        return JSONResponse(
            status_code=422,
            content=_envelope(
                VALIDATION_FAILED,
                "Los datos enviados no son válidos.",
                "The submitted data is invalid.",
                {},
                details,
                trace_id,
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        trace_id = uuid.uuid4().hex
        log.exception("unhandled_exception", trace_id=trace_id, path=str(request.url))
        return JSONResponse(
            status_code=500,
            content=_envelope(
                INTERNAL_ERROR,
                "Ocurrió un error inesperado. Pasale este código a soporte.",
                "An unexpected error occurred. Share this trace id with support.",
                {},
                None,
                trace_id,
            ),
        )
