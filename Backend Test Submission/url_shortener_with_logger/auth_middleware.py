from fastapi import Request, HTTPException

API_TOKEN = "FXtjGHbhxPSKPXkt"

async def verify_token(request: Request):
    auth = request.headers.get("authorization")
    if not auth or auth != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")