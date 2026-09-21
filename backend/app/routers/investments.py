from fastapi import APIRouter

from app.db import connect
from app.schemas import InvestmentRequest
from app.services.scout import investments

router = APIRouter(prefix="/api/investments", tags=["investments"])


@router.post("/analyze")
async def analyze_investments(body: InvestmentRequest):
    pool = await connect()
    parsed, results = await investments(
        pool=pool,
        query=body.query,
        lon=body.lon,
        lat=body.lat,
        radius_km=body.radius_km,
        max_risk=body.max_risk,
        limit=body.limit,
    )
    return {"query": body.query, "parsed": parsed, "results": results}
