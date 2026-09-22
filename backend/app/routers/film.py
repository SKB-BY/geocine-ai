from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.film_locations import EPOCHS, search_film_locations

router = APIRouter(prefix="/api/film", tags=["film"])

class FilmSearchIn(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    limit: int = Field(default=12, ge=1, le=30)
    lon: float | None = None
    lat: float | None = None
    epochs: list[str] | None = None

@router.get("/epochs")
async def get_epochs():
    return {"items": [{"id": e["id"], "label": e["label"], "years": e["years"]} for e in EPOCHS]}

@router.post("/locations")
async def post_film_locations(body: FilmSearchIn):
    parsed, results = await search_film_locations(body.query, limit=body.limit, epochs=body.epochs)
    return {
        "query": body.query,
        "parsed": parsed,
        "results": results,
        "filters": {
            "countries": parsed["countries"],
            "settlement": "столицы и областные центры",
            "period": parsed["period"],
            "epochs": parsed.get("epochs"),
            "epoch_labels": parsed.get("epoch_labels"),
        },
    }
