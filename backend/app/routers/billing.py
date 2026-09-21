from fastapi import APIRouter
from app.db import connect

router = APIRouter(prefix="/api/billing", tags=["billing"])

@router.get("/plans")
async def list_plans():
    pool = await connect()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT code, name, monthly_usd, daily_searches, can_export, can_api, can_unreal, audience FROM plans ORDER BY monthly_usd")
    return {"items": [dict(r) for r in rows]}

@router.get("/quote")
async def quote(plan: str = "creator", seats: int = 1):
    pool = await connect()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM plans WHERE code = $1", plan)
    if row is None:
        return {"error": "unknown plan"}
    monthly = float(row["monthly_usd"]) * max(seats, 1)
    return {"plan": row["code"], "seats": seats, "monthly_usd": monthly, "yearly_usd": round(monthly * 10, 2)}

async def check_quota(pool, plan_code: str, action: str, query: str) -> dict:
    async with pool.acquire() as conn:
        plan = await conn.fetchrow("SELECT * FROM plans WHERE code = $1", plan_code)
        if plan is None:
            plan = await conn.fetchrow("SELECT * FROM plans WHERE code = 'free'")
        used = await conn.fetchval("SELECT count(*) FROM usage_events WHERE plan_code = $1 AND action = $2 AND created_at >= date_trunc('day', now())", plan["code"], action)
        allowed = used < plan["daily_searches"]
        if allowed:
            await conn.execute("INSERT INTO usage_events (plan_code, action, query) VALUES ($1, $2, $3)", plan["code"], action, query)
        return {"plan": plan["code"], "limit": plan["daily_searches"], "used": int(used) + (1 if allowed else 0), "allowed": allowed, "upgrade": None if allowed else "creator"}
