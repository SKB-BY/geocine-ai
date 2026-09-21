from fastapi import APIRouter, HTTPException
from app.db import connect
from app.routers.billing import check_quota
from app.schemas import ScoutRequest
from app.services.scout import scout

router = APIRouter(prefix="/api/scout", tags=["scout"])

@router.post("")
async def post_scout(body: ScoutRequest):
    pool = await connect()
    quota = await check_quota(pool, body.plan_code, "scout", body.query)
    if not quota["allowed"]:
        raise HTTPException(status_code=402, detail={"quota": quota, "message": "Дневной лимит Free. Перейдите на Creator."})
    parsed, results = await scout(pool=pool, query=body.query, kind=body.kind, lon=body.lon, lat=body.lat, radius_km=body.radius_km, budget_usd=body.budget_usd, limit=body.limit)
    return {"query": body.query, "parsed": parsed, "results": results, "quota": quota}
