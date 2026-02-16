"""Middleware package for FastAPI application."""

from app.middleware.auth_middleware import AuthMiddleware

__all__ = ["AuthMiddleware"]
