from fastapi import FastAPI
from middleware.logging import StructuredLoggingMiddleware
from middleware.rate_limiter import RateLimitMiddleware
from middleware.auth_middleware import AuthMiddleware
from cache.redis_cache import cache

def register_middlewares(app: FastAPI):
    """Register the Middleware Matrix. Must be called before the app starts."""
    
    # Register Middleware (Order: Last Added = First Executed)
    # Logging should be first in/last out to capture everything
    app.add_middleware(StructuredLoggingMiddleware)
    
    # Rate limiting should check before heavy auth/logic
    app.add_middleware(RateLimitMiddleware, limit=50, window=60)
    
    # Auth middleware for identity verification
    app.add_middleware(AuthMiddleware)
    
    print("MIDDLEWARE_MATRIX: Unified System registered.")

async def init_cache():
    """Initialize the Neural Buffer connection."""
    await cache.connect()
