from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from cache.redis_cache import cache
import time
import logging

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Monolith Traffic Control: Prevent Denial of Identity attacks."""
    def __init__(self, app, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "Unknown"
        key = f"ratelimit:{client_ip}"
        
        # Identity Audit
        current_data = await cache.get(key)
        now = time.time()
        
        if current_data is None:
            # First request from this Node
            await cache.set(key, {"count": 1, "start": now}, expire=self.window)
        else:
            count = current_data.get("count", 0)
            start_time = current_data.get("start", now)
            
            if now - start_time > self.window:
                # Window reset
                await cache.set(key, {"count": 1, "start": now}, expire=self.window)
            elif count >= self.limit:
                # Limit exceeded
                logging.warning(f"RATE_LIMIT_ERROR: IP {client_ip} exceeded throttle threshold ({self.limit}/{self.window}s)")
                return Response(
                    content="Matrix Access Throttled: Too many requests.", 
                    status_code=429
                )
            else:
                # Increment count
                await cache.set(key, {"count": count + 1, "start": start_time}, expire=self.window)
        
        return await call_next(request)
