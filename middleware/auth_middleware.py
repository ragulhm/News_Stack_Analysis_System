from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from security.jwt_handler import decode_access_token
from database.db import db_protocol
import logging

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """Matrix Identity verification per-request."""
        token = request.cookies.get("access_token")
        request.state.user = None
        
        if token and token.startswith("Bearer "):
            token = token.split(" ")[1]
            payload = decode_access_token(token)
            if payload and "sub" in payload:
                # Find user in database
                user_doc = await db_protocol.users.find_one({"username": payload["sub"]})
                if user_doc:
                    # Identity confirmed
                    request.state.user = user_doc
        
        response = await call_next(request)
        return response
