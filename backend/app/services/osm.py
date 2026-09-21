from __future__ import annotations
import hashlib, math, re
import httpx

PHOTON = "https://photon.komoot.io/api/"
UA = "GeoCineAI/0.3 (https://github.com/SKB-BY/geocine-ai)"

def _slug(osm_id: str, name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", f"{name}-{osm_id}".lower())[:70].strip("-")
    return base if len(base) >= 4 else "osm-" + hashlib.md5(osm_id.encode()).hexdigest()[:10]

def _tags_from_props(props: dict) -> list[str]:
    blob = " ".join(str(v).lower() for v in props.values())
    tags = []
    mapping = {
        "water": ("water", "river", "lake", "harbour", "beach", "набер"),
        "city": ("city", "town", "square", "street"),
        "historic": ("historic", "castle", "old", "heritage"),
        "mountain": ("peak", "mountain", "viewpoint"),
        "forest": ("forest", "wood", "park"),
    }
    for tag, words in mapping.items():
        if any(w in blob for w in words):
            tags.append(tag)
    return tags or ["city"]

async def search_places(queries, lat=None, lon=None, limit=30):
    items, seen = [], set()
    async with httpx.AsyncClient(timeout=20, headers={"User-Agent": UA}) as client:
        for q in (queries or [])[:6]:
            params = {"q": q, "limit": 12}
            if lat is not None and lon is not None:
                params["lat"] = lat; params["lon"] = lon
            try:
                res = await client.get(PHOTON, params=params)
                res.raise_for_status()
                feats = res.json().get("features") or []
            except Exception:
                continue
            for feat in feats:
                props = feat.get("properties") or {}
                coords = (feat.get("geometry") or {}).get("coordinates") or [None, None]
                lon_v, lat_v = coords[0], coords[1]
                if lon_v is None: continue
                osm_id = f"{props.get('osm_type','N')}{props.get('osm_id')}"
                if osm_id in seen: continue
                seen.add(osm_id)
                name = props.get("name") or q
                city = props.get("city") or props.get("county") or ""
                tags = _tags_from_props(props)
                selfie = 0.9 if "viewpoint" in str(props.get("osm_value")) else 0.7
                items.append({
                    "id": None, "slug": _slug(osm_id, name),
                    "name": f"{name}, {city}" if city else name,
                    "country": props.get("country") or props.get("countrycode") or "",
                    "region": city, "kind": "selfie", "tags": tags,
                    "description": props.get("osm_value") or "место с карты",
                    "access_type": "public", "price_tier": "free",
                    "crowd_level": 0.4, "selfie_score": selfie, "content_score": min(0.95, selfie+0.05),
                    "safety_score": 0.75, "golden_hour": True, "best_hours": "07:00-09:30,18:00-20:30",
                    "cost_estimate_usd": None, "weather_risk": 0.25,
                    "flood_risk": 0.15 if "water" in tags else 0.08,
                    "permit_difficulty": 0.12, "growth_potential": 0.4,
                    "shooting_cost_usd": None, "lon": float(lon_v), "lat": float(lat_v),
                    "distance_m": None, "match_score": None, "investment_score": None,
                    "source": "photon-osm", "osm_id": osm_id,
                })
            if len(items) >= limit:
                break
    if lat is not None and lon is not None:
        near = []
        for it in items:
            d = _haversine(lat, lon, it["lat"], it["lon"])
            it["distance_m"] = d
            if d <= 80000: near.append(it)
        items = near or items
    return items[:limit]

def _haversine(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(a))

async def cache_places(pool, items):
    if pool is None or not items: return
    sql = """INSERT INTO locations (slug,name,country,region,kind,tags,description,weather_risk,flood_risk,permit_difficulty,growth_potential,geom,access_type,price_tier,crowd_level,selfie_score,content_score,safety_score)
    VALUES ($1,$2,$3,$4,'selfie',$5,$6,$7,$8,$9,$10,ST_SetSRID(ST_MakePoint($11,$12),4326),$13,$14,$15,$16,$17,$18)
    ON CONFLICT (slug) DO NOTHING"""
    try:
        async with pool.acquire() as conn:
            for it in items:
                await conn.execute(sql, it["slug"], it["name"], it["country"] or "—", it.get("region"), it["tags"], it["description"], it["weather_risk"], it["flood_risk"], it["permit_difficulty"], it["growth_potential"], it["lon"], it["lat"], it["access_type"], it["price_tier"], it["crowd_level"], it["selfie_score"], it["content_score"], it["safety_score"])
    except Exception:
        return
