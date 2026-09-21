from __future__ import annotations
import asyncpg
from app.services.scoring import consumer_score, final_scout_score, investment_score, match_score, parse_scene

LOCATION_SELECT = """
SELECT id, slug, name, country, region, kind, tags, description,
    cost_estimate_usd, weather_risk, flood_risk, permit_difficulty,
    growth_potential, shooting_cost_usd,
    COALESCE(access_type, 'public') AS access_type,
    COALESCE(price_tier, 'free') AS price_tier,
    COALESCE(crowd_level, 0.4) AS crowd_level,
    COALESCE(selfie_score, 0.5) AS selfie_score,
    COALESCE(content_score, 0.5) AS content_score,
    COALESCE(safety_score, 0.7) AS safety_score,
    COALESCE(golden_hour, true) AS golden_hour,
    COALESCE(best_hours, '') AS best_hours,
    ST_X(geom) AS lon, ST_Y(geom) AS lat,
    CASE WHEN $1::float8 IS NULL OR $2::float8 IS NULL THEN NULL
    ELSE ST_DistanceSphere(geom, ST_SetSRID(ST_MakePoint($1, $2), 4326)) END AS distance_m
FROM locations WHERE geom IS NOT NULL
"""
CONSUMER = {"selfie", "content"}

def row_to_dict(row):
    return {
        "id": row["id"], "slug": row["slug"], "name": row["name"], "country": row["country"],
        "region": row["region"], "kind": row["kind"], "tags": list(row["tags"] or []),
        "description": row["description"], "access_type": row["access_type"], "price_tier": row["price_tier"],
        "crowd_level": float(row["crowd_level"]), "selfie_score": float(row["selfie_score"]),
        "content_score": float(row["content_score"]), "safety_score": float(row["safety_score"]),
        "golden_hour": bool(row["golden_hour"]), "best_hours": row["best_hours"],
        "cost_estimate_usd": row["cost_estimate_usd"], "weather_risk": float(row["weather_risk"]),
        "flood_risk": float(row["flood_risk"]), "permit_difficulty": float(row["permit_difficulty"]),
        "growth_potential": float(row["growth_potential"]), "shooting_cost_usd": row["shooting_cost_usd"],
        "lon": float(row["lon"]), "lat": float(row["lat"]),
        "distance_m": float(row["distance_m"]) if row["distance_m"] is not None else None,
        "match_score": None, "investment_score": None,
    }

async def list_locations(pool, kind=None, lon=None, lat=None, radius_m=None):
    clauses, args, idx = [], [lon, lat], 3
    if kind and kind not in CONSUMER and kind != "both":
        clauses.append(f"(kind = ${idx} OR kind = 'both')")
        args.append(kind); idx += 1
    if lon is not None and lat is not None and radius_m:
        clauses.append(f"ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint($1,$2),4326)::geography, ${idx})")
        args.append(radius_m); idx += 1
    sql = LOCATION_SELECT + (" AND " + " AND ".join(clauses) if clauses else "") + " ORDER BY name"
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *args)
    items = [row_to_dict(r) for r in rows]
    for item in items:
        item["investment_score"] = investment_score(item["growth_potential"], item["flood_risk"], item["permit_difficulty"], item["weather_risk"])
        item["consumer_score"] = consumer_score(item, kind)
    return items

async def scout(pool, query, kind, lon, lat, radius_km, budget_usd, limit):
    parsed = parse_scene(query)
    effective = kind or parsed["kind"]
    items = await list_locations(pool, kind=effective, lon=lon, lat=lat, radius_m=radius_km * 1000 if lon is not None and lat is not None else None)
    for item in items:
        semantic = match_score(parsed["tags"], item["tags"], item["distance_m"])
        film_score = final_scout_score(semantic, item["weather_risk"], item["flood_risk"], item["permit_difficulty"])
        if effective in CONSUMER:
            item["match_score"] = round(0.45 * film_score + 0.55 * consumer_score(item, effective), 4)
            if parsed["tags"]:
                item["match_score"] = round(0.6 * item["match_score"] + 0.4 * semantic, 4)
        else:
            item["match_score"] = film_score
        if budget_usd is not None and item["shooting_cost_usd"] and item["shooting_cost_usd"] > budget_usd:
            item["match_score"] = round(item["match_score"] * 0.65, 4)
    items.sort(key=lambda x: x["match_score"] or 0, reverse=True)
    return parsed, items[:limit]

async def investments(pool, query, lon, lat, radius_km, max_risk, limit):
    parsed = parse_scene(query)
    items = await list_locations(pool, kind=None, lon=lon, lat=lat, radius_m=radius_km * 1000 if lon is not None and lat is not None else None)
    out = []
    for item in items:
        risk = 0.45 * item["flood_risk"] + 0.30 * item["weather_risk"] + 0.25 * item["permit_difficulty"]
        if risk > max_risk:
            continue
        item["investment_score"] = investment_score(item["growth_potential"], item["flood_risk"], item["permit_difficulty"], item["weather_risk"])
        item["match_score"] = match_score(parsed["tags"], item["tags"], item["distance_m"])
        out.append(item)
    out.sort(key=lambda x: x["investment_score"] or 0, reverse=True)
    return parsed, out[:limit]
