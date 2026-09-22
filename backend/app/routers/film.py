from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.film_locations import search_film_locations

router = APIRouter(prefix="/api/film", tags=["film"])

class FilmSearchIn(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    limit: int = Field(default=12, ge=1, le=30)
    lon: float | None = None
    lat: float | None = None

@router.post("/locations")
async def post_film_locations(body: FilmSearchIn):
    parsed, results = await search_film_locations(body.query, limit=body.limit)
    return {
        "query": body.query,
        "parsed": parsed,
        "results": results,
        "filters": {
            "countries": parsed["countries"],
            "settlement": "столицы и областные центры",
            "period": parsed["period"],
        },
    }
