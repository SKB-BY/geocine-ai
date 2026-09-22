from __future__ import annotations
from app.services.llm import understand_query
from app.services.osm import search_places

SELECT = """SELECT id, slug, name, city, country, facility_type, stages_count, largest_stage_sqm,
 power_kw, virtual_production, crew_max, day_rate_usd_from, permit_office, permit_notes,
 services, description, website, ST_X(geom) AS lon, ST_Y(geom) AS lat FROM film_facilities"""

def row_to_dict(row):
    return {"id": row["id"], "slug": row["slug"], "name": row["name"], "city": row["city"],
        "country": row["country"], "facility_type": row["facility_type"], "stages_count": row["stages_count"],
        "largest_stage_sqm": row["largest_stage_sqm"], "power_kw": row["power_kw"],
        "virtual_production": bool(row["virtual_production"]), "crew_max": row["crew_max"],
        "day_rate_usd_from": row["day_rate_usd_from"], "permit_office": row["permit_office"],
        "permit_notes": row["permit_notes"], "services": list(row["services"] or []),
        "description": row["description"], "website": row["website"],
        "lon": float(row["lon"]), "lat": float(row["lat"]), "kind": "film", "source": "studio-catalog"}

async def list_studios(pool):
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(SELECT + " ORDER BY name")
        except Exception:
            return []
    return [row_to_dict(r) for r in rows]

async def search_studios(pool, query, lon=None, lat=None, limit=20):
    parsed = await understand_query(query)
    items = await list_studios(pool)
    q = query.lower()
    for it in items:
        blob = " ".join([it["name"], it["city"], it["country"], it["facility_type"], it["description"], "virtual" if it["virtual_production"] else ""]).lower()
        score = 0.4
        if parsed.get("city") and parsed["city"].lower() in blob: score += 0.25
        if any(w in q for w in ("led", "virtual", "unreal")) and it["virtual_production"]: score += 0.2
        if any(w in q for w in ("павил", "stage", "студ")): score += 0.1
        it["match_score"] = round(min(score, 0.99), 4)
    extra = list(parsed.get("search_queries") or []) + [f"{parsed.get('city') or ''} film studio", "sound stage backlot"]
    live = await search_places([x.strip() for x in extra if x.strip()], lat=lat, lon=lon, limit=12)
    for place in live:
        place.update({"kind": "film", "facility_type": "lot", "source": "photon-osm",
            "permit_notes": "Уточнить film office. Точка с карты, не карточка студии."})
        items.append(place)
    items.sort(key=lambda x: x.get("match_score") or 0.45, reverse=True)
    return parsed, items[:limit]

def callsheet(item):
    return {"title": item.get("name"), "unit": "main unit",
        "location": {"name": item.get("name"), "city": item.get("city"), "country": item.get("country"), "lon": item.get("lon"), "lat": item.get("lat")},
        "facility": item.get("facility_type"), "stages": item.get("stages_count"),
        "largest_stage_sqm": item.get("largest_stage_sqm"), "power_kw": item.get("power_kw"),
        "virtual_production": item.get("virtual_production"), "crew_max": item.get("crew_max"),
        "day_rate_usd_from": item.get("day_rate_usd_from"), "permit_office": item.get("permit_office"),
        "permit_notes": item.get("permit_notes"),
        "unreal_origin": {"crs": "EPSG:4326", "lon": item.get("lon"), "lat": item.get("lat"), "alt_m": 0}}
