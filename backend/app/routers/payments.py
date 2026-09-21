from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/payments", tags=["payments"])

class IntentIn(BaseModel):
    plan_code: str = Field(..., pattern="^(creator|studio)$")
    provider: str = Field(..., pattern="^(stripe|yookassa)$")
    seats: int = Field(default=1, ge=1, le=50)

@router.post("/intent")
async def create_intent(body: IntentIn):
    prices = {"creator": 9.9, "studio": 149.0}
    return {"status": "stub", "plan_code": body.plan_code, "provider": body.provider, "amount_usd": prices[body.plan_code] * body.seats}

@router.post("/webhook")
async def webhook(x_provider_signature: str | None = Header(default=None)):
    if not x_provider_signature:
        raise HTTPException(status_code=400, detail="missing signature")
    return {"status": "accepted_stub"}
