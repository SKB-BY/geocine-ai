from __future__ import annotations
import re
import httpx
from app.services.osm import search_places

UA = "GeoCineAI/0.3 (https://github.com/SKB-BY/geocine-ai)"
CITIES = [
    {"name": "Минск", "query": "Minsk", "country": "BY", "tier": "capital", "lat": 53.9023, "lon": 27.5619},
    {"name": "Гродно", "query": "Grodno", "country": "BY", "tier": "oblast", "lat": 53.6694, "lon": 23.8131},
    {"name": "Витебск", "query": "Vitebsk", "country": "BY", "tier": "oblast", "lat": 55.1904, "lon": 30.2049},
    {"name": "Брест", "query": "Brest Belarus", "country": "BY", "tier": "oblast", "lat": 52.0976, "lon": 23.6877},
    {"name": "Гомель", "query": "Gomel", "country": "BY", "tier": "oblast", "lat": 52.4345, "lon": 30.9754},
    {"name": "Москва", "query": "Moscow", "country": "RU", "tier": "capital", "lat": 55.7558, "lon": 37.6173},
    {"name": "Санкт-Петербург", "query": "Saint Petersburg", "country": "RU", "tier": "capital", "lat": 59.9343, "lon": 30.3351},
    {"name": "Ярославль", "query": "Yaroslavl", "country": "RU", "tier": "oblast", "lat": 57.6261, "lon": 39.8845},
    {"name": "Псков", "query": "Pskov", "country": "RU", "tier": "oblast", "lat": 57.8194, "lon": 28.3318},
    {"name": "Великий Новгород", "query": "Veliky Novgorod", "country": "RU", "tier": "oblast", "lat": 58.5213, "lon": 31.2755},
    {"name": "Владимир", "query": "Vladimir Russia", "country": "RU", "tier": "oblast", "lat": 56.1290, "lon": 40.4070},
    {"name": "Кострома", "query": "Kostroma", "country": "RU", "tier": "oblast", "lat": 57.7678, "lon": 40.9269},
    {"name": "Томск", "query": "Tomsk", "country": "RU", "tier": "oblast", "lat": 56.4846, "lon": 84.9476},
    {"name": "Екатеринбург", "query": "Yekaterinburg", "country": "RU", "tier": "oblast", "lat": 56.8389, "lon": 60.6057},
    {"name": "Самара", "query": "Samara", "country": "RU", "tier": "oblast", "lat": 53.1959, "lon": 50.1002},
    {"name": "Иркутск", "query": "Irkutsk", "country": "RU", "tier": "oblast", "lat": 52.2869, "lon": 104.3050},
    {"name": "Вологда", "query": "Vologda", "country": "RU", "tier": "oblast", "lat": 59.2205, "lon": 39.8915},
]
EPOCHS = [
    {"id": "medieval", "label": "Средневековье / крепость", "years": "XII–XVII", "words": ("средневек", "готик", "кремл", "крепост", "замок"), "cities": ("Псков", "Великий Новгород", "Владимир", "Гродно")},
    {"id": "baroque", "label": "Барокко", "years": "XVII–XVIII", "words": ("барокко", "барочн"), "cities": ("Санкт-Петербург", "Гродно", "Витебск")},
    {"id": "classicism", "label": "Классицизм", "years": "1760–1830", "words": ("классици", "екатеринин"), "cities": ("Санкт-Петербург", "Москва", "Кострома", "Ярославль", "Гомель")},
    {"id": "empire", "label": "Ампир", "years": "1810–1840", "words": ("ампир",), "cities": ("Москва", "Санкт-Петербург")},
    {"id": "eclectic", "label": "Эклектика / XIX век", "years": "1840–1900", "words": ("эклект", "доходн", "19 век", "xix"), "cities": ("Санкт-Петербург", "Москва", "Минск", "Гродно", "Самара")},
    {"id": "art_nouveau", "label": "Модерн", "years": "1890–1914", "words": ("модерн", "art nouveau", "югенд"), "cities": ("Санкт-Петербург", "Москва", "Самара", "Гродно", "Томск")},
    {"id": "wooden", "label": "Деревянный город", "years": "XVIII–XX", "words": ("деревян", "резной"), "cities": ("Томск", "Вологда", "Иркутск", "Кострома")},
    {"id": "constructivism", "label": "Конструктивизм", "years": "1920–1935", "words": ("конструктив", "авангард"), "cities": ("Москва", "Екатеринбург", "Минск", "Самара")},
    {"id": "stalinist", "label": "Сталинский ампир", "years": "1935–1955", "words": ("сталинк", "сталинск", "высотк"), "cities": ("Минск", "Москва", "Санкт-Петербург")},
]
EPOCH_BY_ID = {e["id"]: e for e in EPOCHS}

def detect_epochs(q):
    return [e["id"] for e in EPOCHS if any(w in q for w in e["words"])]

def parse_film_query(text):
    q = (text or "").lower()
    countries = []
    if any(w in q for w in ("беларус", "рб", "гродн")): countries.append("BY")
    if any(w in q for w in ("росси", "рф", "москв", "петербург")): countries.append("RU")
    if not countries: countries = ["BY", "RU"]
    epochs = detect_epochs(q) or ["eclectic"]
    return {"raw": text, "countries": countries, "period": "18-19", "epochs": epochs,
            "epoch_labels": [EPOCH_BY_ID[e]["label"] for e in epochs], "kind": "film", "cities_named": [c["name"] for c in CITIES if c["name"].lower() in q]}

def apply_epoch_filter(parsed, requested):
    clean = [e for e in (requested or []) if e in EPOCH_BY_ID]
    if clean:
        parsed["epochs"] = clean
        parsed["epoch_labels"] = [EPOCH_BY_ID[e]["label"] for e in clean]
    return parsed

def pick_cities(parsed, limit=8):
    pool = [c for c in CITIES if c["country"] in parsed["countries"]]
    preferred = []
    for eid in parsed.get("epochs") or []:
        preferred.extend(list(EPOCH_BY_ID.get(eid, {}).get("cities") or ()))
    return sorted(pool, key=lambda c: preferred.index(c["name"]) if c["name"] in preferred else 99)[:limit]

async def wiki_photos(client, lat, lon, need=4):
    photos = []
    try:
        geo = await client.get("https://ru.wikipedia.org/w/api.php", params={"action":"query","list":"geosearch","gscoord":f"{lat}|{lon}","gsradius":700,"gslimit":12,"format":"json"})
        hits = (geo.json().get("query") or {}).get("geosearch") or []
        ids = [str(h["pageid"]) for h in hits if h.get("pageid")]
        if not ids: return []
        pics = await client.get("https://ru.wikipedia.org/w/api.php", params={"action":"query","pageids":"|".join(ids[:10]),"prop":"pageimages","pithumbsize":900,"format":"json"})
        for page in ((pics.json().get("query") or {}).get("pages") or {}).values():
            thumb = (page.get("thumbnail") or {}).get("source")
            if thumb: photos.append({"url": thumb, "title": page.get("title"), "source": "wikipedia"})
            if len(photos) >= need: break
    except Exception:
        return photos
    return photos[:need]

async def search_film_locations(query, limit=12, epochs=None):
    parsed = apply_epoch_filter(parse_film_query(query), epochs)
    results, seen = [], set()
    async with httpx.AsyncClient(timeout=20, headers={"User-Agent": UA}) as client:
        for city in pick_cities(parsed, 8):
            phrases = [f"{city['name']} исторический центр"]
            places = await search_places(phrases, lat=city["lat"], lon=city["lon"], limit=4) or [{"name": f"Исторический центр, {city['name']}", "lat": city["lat"], "lon": city["lon"]}]
            for place in places:
                key = (round(place["lat"],4), round(place["lon"],4))
                if key in seen: continue
                seen.add(key)
                photos = await wiki_photos(client, place["lat"], place["lon"], 5)
                styles = ", ".join(parsed.get("epoch_labels") or [])
                results.append({"name": place.get("name") or city["name"], "city": city["name"], "country": city["country"],
                    "lat": place["lat"], "lon": place["lon"], "kind": "film", "epochs": parsed["epochs"],
                    "epoch_labels": parsed.get("epoch_labels"), "why": f"{styles}. {city['name']}.",
                    "photos": photos[:5], "photo_count": len(photos[:5]), "match_score": 0.7 if photos else 0.5})
                if len(results) >= limit: break
            if len(results) >= limit: break
    return parsed, results[:limit]
