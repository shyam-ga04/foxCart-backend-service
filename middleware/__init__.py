import os
from typing import Optional

import jwt  # pyjwt
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from config import settings

# Load from env (supabase jwt secret)
SUPABASE_JWT_SECRET = settings.SUPABASE_JWT_SECRET
if not SUPABASE_JWT_SECRET:
    raise RuntimeError("SUPABASE_JWT_SECRET not set in environment variables.")

class SupabaseAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public routes (optional)
        public_paths = ["/health", "/docs", "/openapi.json", "/auth/signin", "/auth/signup"]
        if request.url.path in public_paths:
            return await call_next(request)

        token = self._get_token_from_headers(request)
        if not token:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header"
            )

        payload = self._decode_jwt(token)
        if not payload:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Invalid or expired token"
            )

        # Attach user to request
        request.state.user = payload
        return await call_next(request)

    def _get_token_from_headers(self, request: Request) -> Optional[str]:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        return auth_header.split(" ")[1]

    def _decode_jwt(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],  # Supabase uses HS256
                options={"verify_aud": False},  # Disable audience check if not using it
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
