from fastapi import APIRouter

from app.db import connect
from app.schemas import ScoutRequest, ScoutResponse
from app.services.scout import scout

router = APIRouter(prefix="/api/scout", tags=["scout"])


@router.post("", response_model=ScoutResponse)
async def post_scout(body: ScoutRequest):
    pool = await connect()
    parsed, results = await scout(
        pool=pool,
        query=body.query,
        kind=body.kind,
        lon=body.lon,
        lat=body.lat,
        radius_km=body.radius_km,
        budget_usd=body.budget_usd,
        limit=body.limit,
    )
    return {"query": body.query, "parsed": parsed, "results": results}
