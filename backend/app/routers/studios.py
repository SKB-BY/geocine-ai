from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.db import connect
from app.services.studios import callsheet, list_studios, search_studios

router = APIRouter(prefix="/api/studios", tags=["studios"])

class StudioSearchIn(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    lon: float | None = None
    lat: float | None = None
    limit: int = Field(default=20, ge=1, le=50)

@router.get("")
async def get_studios():
    pool = await connect()
    items = await list_studios(pool)
    return {"count": len(items), "items": items}

@router.post("/search")
async def post_search(body: StudioSearchIn):
    pool = await connect()
    parsed, items = await search_studios(pool, body.query, body.lon, body.lat, body.limit)
    return {"query": body.query, "parsed": parsed, "results": items}

@router.get("/{studio_id}/callsheet")
async def get_callsheet(studio_id: int):
    pool = await connect()
    items = await list_studios(pool)
    item = next((x for x in items if x["id"] == studio_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="studio not found")
    return callsheet(item)

@router.get("/{studio_id}/unreal")
async def get_unreal(studio_id: int):
    pool = await connect()
    items = await list_studios(pool)
    item = next((x for x in items if x["id"] == studio_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="studio not found")
    sheet = callsheet(item)
    sheet["engine"] = "unreal"
    sheet["cesium_georeference"] = True
    return sheet
