from __future__ import annotations
import re
import httpx
from app.services.osm import search_places

UA = "GeoCineAI/0.3 (https://github.com/SKB-BY/geocine-ai)"

CITIES = [
    {"name": "Минск", "query": "Minsk", "country": "BY", "tier": "capital", "lat": 53.9023, "lon": 27.5619},
    {"name": "Брест", "query": "Brest Belarus", "country": "BY", "tier": "oblast", "lat": 52.0976, "lon": 23.6877},
    {"name": "Витебск", "query": "Vitebsk", "country": "BY", "tier": "oblast", "lat": 55.1904, "lon": 30.2049},
    {"name": "Гродно", "query": "Grodno", "country": "BY", "tier": "oblast", "lat": 53.6694, "lon": 23.8131},
    {"name": "Москва", "query": "Moscow", "country": "RU", "tier": "capital", "lat": 55.7558, "lon": 37.6173},
    {"name": "Санкт-Петербург", "query": "Saint Petersburg", "country": "RU", "tier": "capital", "lat": 59.9343, "lon": 30.3351},
    {"name": "Ярославль", "query": "Yaroslavl", "country": "RU", "tier": "oblast", "lat": 57.6261, "lon": 39.8845},
    {"name": "Смоленск", "query": "Smolensk", "country": "RU", "tier": "oblast", "lat": 54.7818, "lon": 32.0401},
    {"name": "Псков", "query": "Pskov", "country": "RU", "tier": "oblast", "lat": 57.8194, "lon": 28.3318},
    {"name": "Великий Новгород", "query": "Veliky Novgorod", "country": "RU", "tier": "oblast", "lat": 58.5213, "lon": 31.2755},
    {"name": "Владимир", "query": "Vladimir Russia", "country": "RU", "tier": "oblast", "lat": 56.1290, "lon": 40.4070},
    {"name": "Кострома", "query": "Kostroma", "country": "RU", "tier": "oblast", "lat": 57.7678, "lon": 40.9269},
    {"name": "Казань", "query": "Kazan", "country": "RU", "tier": "oblast", "lat": 55.7887, "lon": 49.1221},
    {"name": "Томск", "query": "Tomsk", "country": "RU", "tier": "oblast", "lat": 56.4846, "lon": 84.9476},
]

ANCHORS = {
    "Минск": ["Раковская улица Минск", "Троицкое предместье"],
    "Гродно": ["Советская улица Гродно", "Замковая улица Гродно"],
    "Брест": ["улица Советская Брест"],
    "Москва": ["Пятницкая улица", "Ивановская горка"],
    "Санкт-Петербург": ["Коломна Санкт-Петербург", "улица Рубинштейна"],
    "Смоленск": ["Блонье Смоленск"],
    "Псков": ["улица Советская Псков"],
    "Великий Новгород": ["Ярославово Дворище"],
    "Ярославль": ["Волжская набережная Ярославль"],
    "Кострома": ["Сусанинская площадь"],
    "Владимир": ["Большая Московская Владимир"],
    "Казань": ["улица Баумана Казань"],
    "Томск": ["улица Бакунина Томск"],
}

def parse_film_query(text):
    q = (text or "").lower()
    countries = []
    if any(w in q for w in ("беларус", "белорус", "рб", "гродн")): countries.append("BY")
    if any(w in q for w in ("росси", "рф", "москв", "петербург", "питер")): countries.append("RU")
    if not countries: countries = ["BY", "RU"]
    period = "18-19"
    if "18" in q and "19" in q: period = "18-19"
    elif "18" in q: period = "18"
    elif "19" in q: period = "19"
    named = [c for c in CITIES if c["name"].lower() in q]
    return {"raw": text, "countries": countries, "period": period, "settlement": "capital_oblast", "cities_named": [c["name"] for c in named], "kind": "film"}

def pick_cities(parsed, limit=8):
    pool = [c for c in CITIES if c["country"] in parsed["countries"]]
    if parsed["cities_named"]:
        named = [c for c in pool if c["name"] in parsed["cities_named"]]
        if named: return named[:limit]
    preferred = ["Гродно","Брест","Витебск","Минск","Санкт-Петербург","Москва","Смоленск","Псков","Великий Новгород","Ярославль","Кострома","Владимир","Казань","Томск"]
    return sorted(pool, key=lambda c: preferred.index(c["name"]) if c["name"] in preferred else 99)[:limit]

SKIP_PHOTO = re.compile(r"logo|герб|flag|карта|icon|svg|провайдер", re.I)

async def wiki_photos(client, lat, lon, need=4):
    photos = []
    try:
        geo = await client.get("https://ru.wikipedia.org/w/api.php", params={"action":"query","list":"geosearch","gscoord":f"{lat}|{lon}","gsradius":700,"gslimit":12,"format":"json"})
        geo.raise_for_status()
        hits = (geo.json().get("query") or {}).get("geosearch") or []
        pageids = [str(h["pageid"]) for h in hits if h.get("pageid")]
        if not pageids: return []
        pics = await client.get("https://ru.wikipedia.org/w/api.php", params={"action":"query","pageids":"|".join(pageids[:10]),"prop":"pageimages|info","pithumbsize":900,"inprop":"url","format":"json"})
        pics.raise_for_status()
        for page in ((pics.json().get("query") or {}).get("pages") or {}).values():
            title = page.get("title") or ""
            thumb = (page.get("thumbnail") or {}).get("source")
            if not thumb or SKIP_PHOTO.search(title) or SKIP_PHOTO.search(thumb): continue
            photos.append({"url": thumb, "title": title, "source": "wikipedia", "page": page.get("fullurl")})
            if len(photos) >= need: break
    except Exception:
        return photos
    return photos[:need]

async def search_film_locations(query, limit=12):
    parsed = parse_film_query(query)
    cities = pick_cities(parsed, 8)
    results, seen = [], set()
    async with httpx.AsyncClient(timeout=20, headers={"User-Agent": UA}) as client:
        for city in cities:
            phrases = list(ANCHORS.get(city["name"], [f"{city['name']} исторический центр"]))
            places = await search_places(phrases, lat=city["lat"], lon=city["lon"], limit=5)
            if not places:
                places = [{"name": f"Исторический центр, {city['name']}", "lat": city["lat"], "lon": city["lon"], "source": "city-core"}]
            for place in places:
                key = (round(place["lat"], 4), round(place["lon"], 4))
                if key in seen: continue
                seen.add(key)
                photos = await wiki_photos(client, place["lat"], place["lon"], 5)
                if len(photos) < 2:
                    photos += await wiki_photos(client, city["lat"], city["lon"], 5-len(photos))
                period = {"18": "XVIII век", "19": "XIX век"}.get(parsed["period"], "XVIII-XIX века")
                tier = "столица" if city["tier"]=="capital" else "областной центр"
                results.append({
                    "name": place.get("name") or city["name"], "city": city["name"], "country": city["country"],
                    "tier": city["tier"], "lat": place["lat"], "lon": place["lon"], "kind": "film",
                    "period": parsed["period"],
                    "why": f"Улочки и фасады, {period}. {city['name']} — {tier}, {city['country']}.",
                    "photos": photos[:5], "photo_count": min(len(photos), 5),
                    "source": place.get("source") or "photon-osm",
                    "match_score": 0.72 if photos else 0.5,
                })
                if len(results) >= limit: break
            if len(results) >= limit: break
    results.sort(key=lambda x: (x["photo_count"], x["match_score"]), reverse=True)
    return parsed, results[:limit]
