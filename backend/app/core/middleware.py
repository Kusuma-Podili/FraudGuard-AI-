"""Custom HTTP Middlewares: Request Correlation IDs, Latency Budget Timing, and Error Handlers."""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from backend.app.core.exceptions import FraudGuardException
from backend.app.core.logging import get_logger

logger = get_logger("fraudguard.middleware")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Injects and propagates unique X-Correlation-ID across all requests."""

    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", f"corr_{uuid.uuid4().hex[:12]}")
        request.state.correlation_id = correlation_id

        response: Response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Measures request execution duration and attaches latency headers."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"

        # Log inference latency warnings if above 25ms SLO
        if "/transactions/score" in request.url.path and elapsed_ms > 25.0:
            logger.warning(
                f"Inference latency threshold breached: {elapsed_ms:.2f}ms on {request.url.path}",
                extra={"latency_ms": elapsed_ms, "correlation_id": getattr(request.state, "correlation_id", "N/A")}
            )

        return response


async def fraudguard_exception_handler(request: Request, exc: FraudGuardException) -> JSONResponse:
    """Standardized RFC 7807 error payload."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": f"https://api.fraudguard.ai/errors/{exc.error_code.lower()}",
            "title": exc.error_code,
            "status": exc.status_code,
            "detail": exc.message,
            "instance": request.url.path,
            "details": exc.details,
            "correlation_id": getattr(request.state, "correlation_id", "N/A"),
        }
    )
