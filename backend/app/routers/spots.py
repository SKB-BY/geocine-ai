from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.db import connect

router = APIRouter(prefix="/api/spots", tags=["spots"])

class SpotIn(BaseModel):
    title: str = Field(..., min_length=3, max_length=160)
    description: str = Field(..., min_length=3, max_length=2000)
    audience: str = "selfie"
    lon: float
    lat: float

@router.post("")
async def submit_spot(body: SpotIn):
    pool = await connect()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("INSERT INTO spot_submissions (title, description, audience, lon, lat) VALUES ($1,$2,$3,$4,$5) RETURNING id, status, created_at", body.title, body.description, body.audience, body.lon, body.lat)
    return {"ok": True, "spot": dict(row)}

@router.get("")
async def list_spots(status: str = "pending"):
    pool = await connect()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, title, description, audience, lon, lat, status, created_at FROM spot_submissions WHERE status = $1 ORDER BY created_at DESC LIMIT 50", status)
    return {"items": [dict(r) for r in rows]}
