from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from log import Log

async def log_request(request: Request, call_next):
    Log("backend", "info", "middleware", f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    Log("backend", "info", "middleware", f"Completed request: {request.method} {request.url.path} → {response.status_code}")
    return response