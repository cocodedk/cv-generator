"""Middleware configuration for FastAPI application."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


def setup_rate_limiting(app: FastAPI) -> Limiter:
    """Configure rate limiting middleware."""
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    return limiter


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware.

    **Production Configuration Required:**
    The CORS_ORIGINS environment variable must be set in production to a
    comma-separated list of trusted origins. Example:
    CORS_ORIGINS="https://example.com,https://www.example.com"

    **Security Note:**
    Currently, allow_methods and allow_headers are wildcarded (["*"]).
    In production, these should be restricted to only the required methods
    and headers, or reviewed alongside the origins configuration to ensure
    appropriate security boundaries.
    """
    cors_origins = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://localhost:8000"
        ).split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
