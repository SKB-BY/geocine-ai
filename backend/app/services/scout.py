from __future__ import annotations

import asyncpg

from app.services.scoring import (
    final_scout_score,
    investment_score,
    match_score,
    parse_scene,
)

LOCATION_SELECT = """
SELECT
    id, slug, name, country, region, kind, tags, description,
    cost_estimate_usd, weather_risk, flood_risk, permit_difficulty,
    growth_potential, shooting_cost_usd,
    ST_X(geom) AS lon,
    ST_Y(geom) AS lat,
    CASE
        WHEN $1::float8 IS NULL OR $2::float8 IS NULL THEN NULL
        ELSE ST_DistanceSphere(geom, ST_SetSRID(ST_MakePoint($1, $2), 4326))
    END AS distance_m
FROM locations
WHERE geom IS NOT NULL
"""


def row_to_dict(row: asyncpg.Record) -> dict:
    tags = list(row["tags"] or [])
    return {
        "id": row["id"],
        "slug": row["slug"],
        "name": row["name"],
        "country": row["country"],
        "region": row["region"],
        "kind": row["kind"],
        "tags": tags,
        "description": row["description"],
        "cost_estimate_usd": row["cost_estimate_usd"],
        "weather_risk": float(row["weather_risk"]),
        "flood_risk": float(row["flood_risk"]),
        "permit_difficulty": float(row["permit_difficulty"]),
        "growth_potential": float(row["growth_potential"]),
        "shooting_cost_usd": row["shooting_cost_usd"],
        "lon": float(row["lon"]),
        "lat": float(row["lat"]),
        "distance_m": float(row["distance_m"]) if row["distance_m"] is not None else None,
        "match_score": None,
        "investment_score": None,
    }


async def list_locations(pool, kind=None, lon=None, lat=None, radius_m=None):
    clauses = []
    args = [lon, lat]
    idx = 3
    if kind and kind != "both":
        clauses.append(f"(kind = ${idx} OR kind = 'both')")
        args.append(kind)
        idx += 1
    if lon is not None and lat is not None and radius_m:
        clauses.append(
            f"ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint($1,$2),4326)::geography, ${idx})"
        )
        args.append(radius_m)
        idx += 1
    sql = LOCATION_SELECT
    if clauses:
        sql += " AND " + " AND ".join(clauses)
    sql += " ORDER BY name"
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *args)
    items = [row_to_dict(r) for r in rows]
    for item in items:
        item["investment_score"] = investment_score(
            item["growth_potential"], item["flood_risk"], item["permit_difficulty"], item["weather_risk"]
        )
    return items


async def scout(pool, query, kind, lon, lat, radius_km, budget_usd, limit):
    parsed = parse_scene(query)
    items = await list_locations(
        pool,
        kind=kind or parsed["kind"],
        lon=lon,
        lat=lat,
        radius_m=radius_km * 1000 if lon is not None and lat is not None else None,
    )
    for item in items:
        semantic = match_score(parsed["tags"], item["tags"], item["distance_m"])
        item["match_score"] = final_scout_score(
            semantic, item["weather_risk"], item["flood_risk"], item["permit_difficulty"]
        )
        if budget_usd is not None and item["shooting_cost_usd"] and item["shooting_cost_usd"] > budget_usd:
            item["match_score"] = round(item["match_score"] * 0.65, 4)
    items.sort(key=lambda x: x["match_score"] or 0, reverse=True)
    return parsed, items[:limit]


async def investments(pool, query, lon, lat, radius_km, max_risk, limit):
    parsed = parse_scene(query)
    items = await list_locations(
        pool,
        kind="investment",
        lon=lon,
        lat=lat,
        radius_m=radius_km * 1000 if lon is not None and lat is not None else None,
    )
    filtered = []
    for item in items:
        risk = 0.45 * item["flood_risk"] + 0.30 * item["weather_risk"] + 0.25 * item["permit_difficulty"]
        if risk > max_risk:
            continue
        item["investment_score"] = investment_score(
            item["growth_potential"], item["flood_risk"], item["permit_difficulty"], item["weather_risk"]
        )
        item["match_score"] = match_score(parsed["tags"], item["tags"], item["distance_m"])
        filtered.append(item)
    filtered.sort(key=lambda x: (x["investment_score"] or 0), reverse=True)
    return parsed, filtered[:limit]
