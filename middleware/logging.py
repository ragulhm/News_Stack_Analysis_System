import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Monolith Neural Pulse Monitor: Log all request/response telemetry."""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Capture Request Metadata
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "Unknown"
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        status_code = response.status_code
        
        # Log structured pulse
        log_message = (
            f"NEURAL_PULSE: {method} {path} | "
            f"STATUS: {status_code} | IP: {client_ip} | "
            f"LATENCY: {process_time:.4f}s"
        )
        
        if status_code >= 400:
            logging.error(log_message)
        else:
            logging.info(log_message)
            
        return response
