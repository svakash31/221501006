from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timedelta
import secrets
from typing import Optional
from auth_middleware import verify_token
from logger_middleware import log_request
from log import Log

app = FastAPI()
app.middleware("http")(log_request)

db = {}

class URLRequest(BaseModel):
    url: HttpUrl
    validity: Optional[int] = 30
    shortcode: Optional[str] = None

@app.post("/shorturls", status_code=201)
async def create_short_url(data: URLRequest, request: Request, token=Depends(verify_token)):
    shortcode = data.shortcode or secrets.token_urlsafe(4)
    if shortcode in db:
        Log("backend", "error", "handler", f"Shortcode '{shortcode}' already exists")
        raise HTTPException(status_code=400, detail="Shortcode already exists")
    expiry_time = datetime.utcnow() + timedelta(minutes=data.validity)
    db[shortcode] = {
        "original_url": str(data.url),
        "created_at": datetime.utcnow().isoformat(),
        "expiry": expiry_time.isoformat(),
        "hits": 0,
        "clicks": []
    }
    Log("backend", "info", "service", f"Created shortcode '{shortcode}' for URL {data.url}")
    return {
        "shortLink": f"{request.url.scheme}://{request.client.host}:{request.url.port}/{shortcode}",
        "expiry": expiry_time.isoformat()
    }

@app.get("/{shortcode}")
async def redirect_to_url(shortcode: str, request: Request):
    if shortcode not in db:
        Log("backend", "warn", "handler", f"Shortcode '{shortcode}' not found")
        raise HTTPException(status_code=404, detail="Shortcode not found")
    entry = db[shortcode]
    if datetime.utcnow() > datetime.fromisoformat(entry["expiry"]):
        Log("backend", "warn", "handler", f"Shortcode '{shortcode}' expired")
        raise HTTPException(status_code=410, detail="Link expired")
    entry["hits"] += 1
    entry["clicks"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "referrer": request.headers.get("referer", "direct"),
        "location": "IN"
    })
    Log("backend", "info", "service", f"Redirected shortcode '{shortcode}'")
    return RedirectResponse(entry["original_url"])

@app.get("/shorturls/{shortcode}")
async def get_url_stats(shortcode: str, token=Depends(verify_token)):
    if shortcode not in db:
        Log("backend", "warn", "handler", f"Stats requested for nonexistent shortcode '{shortcode}'")
        raise HTTPException(status_code=404, detail="Shortcode not found")
    Log("backend", "info", "service", f"Stats returned for shortcode '{shortcode}'")
    return db[shortcode]