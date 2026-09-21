from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.db import connect
from app.services.scout import list_locations

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("")
async def get_locations(
    kind: str | None = Query(default=None),
    lon: float | None = None,
    lat: float | None = None,
    radius_km: float | None = Query(default=None, ge=1, le=20000),
):
    pool = await connect()
    items = await list_locations(
        pool,
        kind=kind,
        lon=lon,
        lat=lat,
        radius_m=(radius_km * 1000) if radius_km and lon is not None and lat is not None else None,
    )
    return {"count": len(items), "items": items}


@router.get("/geojson")
async def get_locations_geojson(kind: str | None = Query(default=None)):
    pool = await connect()
    items = await list_locations(pool, kind=kind)
    features = []
    for item in items:
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [item["lon"], item["lat"]]},
                "properties": {k: v for k, v in item.items() if k not in ("lon", "lat")},
            }
        )
    return JSONResponse({"type": "FeatureCollection", "features": features})


@router.get("/{location_id}")
async def get_location(location_id: int):
    pool = await connect()
    items = await list_locations(pool)
    for item in items:
        if item["id"] == location_id:
            return item
    raise HTTPException(status_code=404, detail="location not found")


@router.get("/{location_id}/unreal")
async def export_unreal(location_id: int):
    pool = await connect()
    items = await list_locations(pool)
    item = next((x for x in items if x["id"] == location_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="location not found")
    return {
        "engine": "unreal",
        "crs": "EPSG:4326",
        "location_id": item["id"],
        "name": item["name"],
        "lon": item["lon"],
        "lat": item["lat"],
        "tags": item["tags"],
        "notes": item["description"],
        "world_origin": {"lon": item["lon"], "lat": item["lat"], "alt_m": 0},
        "cesium_georeference": True,
    }
