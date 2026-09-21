from typing import Any, Literal
from pydantic import BaseModel, Field

LocationKind = Literal["selfie", "content", "film", "investment", "both"]

class LocationOut(BaseModel):
    id: int
    slug: str
    name: str
    country: str
    region: str | None = None
    kind: LocationKind
    tags: list[str] = Field(default_factory=list)
    description: str
    cost_estimate_usd: int | None = None
    weather_risk: float
    flood_risk: float
    permit_difficulty: float
    growth_potential: float
    shooting_cost_usd: int | None = None
    lon: float
    lat: float
    distance_m: float | None = None
    match_score: float | None = None
    investment_score: float | None = None

class ScoutRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    kind: LocationKind | None = None
    lon: float | None = None
    lat: float | None = None
    radius_km: float = Field(default=5000, ge=1, le=20000)
    budget_usd: int | None = Field(default=None, ge=0)
    plan_code: str = "free"
    limit: int = Field(default=20, ge=1, le=50)

class ScoutResponse(BaseModel):
    query: str
    parsed: dict[str, Any]
    results: list[LocationOut]

class InvestmentRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    lon: float | None = None
    lat: float | None = None
    radius_km: float = Field(default=500, ge=1, le=20000)
    max_risk: float = Field(default=0.6, ge=0, le=1)
    limit: int = Field(default=20, ge=1, le=50)
