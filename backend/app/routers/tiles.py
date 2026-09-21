from fastapi import APIRouter, Response

from app.db import connect

router = APIRouter(prefix="/api/tiles", tags=["tiles"])


@router.get("/{z}/{x}/{y}.mvt")
async def vector_tile(z: int, x: int, y: int):
    sql = """
    SELECT ST_AsMVT(q, 'locations', 4096, 'geom') AS tile
    FROM (
        SELECT
            ST_AsMVTGeom(geom, ST_TileEnvelope($1, $2, $3), 4096, 64, true) AS geom,
            id, name, kind, slug
        FROM locations
        WHERE geom && ST_TileEnvelope($1, $2, $3)
    ) q;
    """
    pool = await connect()
    async with pool.acquire() as conn:
        tile = await conn.fetchval(sql, z, x, y)
    return Response(content=bytes(tile or b""), media_type="application/vnd.mapbox-vector-tile")
