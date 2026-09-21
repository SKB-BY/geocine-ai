from __future__ import annotations

import json
import httpx
from app.config import settings
from app.services.scoring import parse_scene

SYSTEM = """Ты помощник поиска локаций для селфи, роликов и кино.
Верни ТОЛЬКО JSON:
{\"kind\": \"selfie|content|film|investment\", \"tags\": [], \"city\": \"\", \"search_queries\": []}
search_queries — фразы для карты: waterfront, viewpoint, old town, mural.
"""

CITIES = {"минск": "Minsk", "minsk": "Minsk", "гродно": "Hrodna", "москва": "Moscow", "тбилиси": "Tbilisi", "лиссабон": "Lisbon", "стамбул": "Istanbul", "дубай": "Dubai", "рига": "Riga", "вильнюс": "Vilnius", "прага": "Prague", "краков": "Krakow", "барселона": "Barcelona", "париж": "Paris", "рим": "Rome"}

def _guess_city(text: str) -> str:
    q = text.lower()
    for key, name in CITIES.items():
        if key in q:
            return name
    return ""

def _default_queries(text, tags, city):
    city = city or ""
    bits = []
    if "water" in tags: bits += ["waterfront promenade", "river embankment"]
    if "city" in tags or "historic" in tags: bits += ["old town", "historic street"]
    if not bits: bits = ["scenic viewpoint", "city park"]
    out = [f"{city} {b}".strip() for b in bits]
    if city:
        out += [f"{city} viewpoint", f"{city} old town"]
    out.append(text)
    seen, uniq = set(), []
    for item in out:
        if item.lower() not in seen:
            seen.add(item.lower()); uniq.append(item)
    return uniq[:6]

async def understand_query(text: str) -> dict:
    fallback = parse_scene(text)
    parsed = {
        "kind": fallback.get("kind") or "content",
        "tags": fallback.get("tags") or [],
        "city": _guess_city(text),
        "country": "",
        "must": [],
        "avoid": [],
        "search_queries": _default_queries(text, fallback.get("tags") or [], _guess_city(text)),
        "engine": "rules",
        "raw": text,
    }
    key = (settings.openai_api_key or "").strip()
    if not key:
        return parsed
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            res = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": settings.llm_model or "gpt-4o-mini",
                    "temperature": 0.2,
                    "response_format": {"type": "json_object"},
                    "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
                },
            )
        res.raise_for_status()
        data = json.loads(res.json()["choices"][0]["message"]["content"])
        parsed.update({k: data[k] for k in data if k in parsed or k in ("kind", "tags", "city", "search_queries")})
        parsed["engine"] = "openai+" + (settings.llm_model or "gpt-4o-mini")
        if not parsed.get("search_queries"):
            parsed["search_queries"] = _default_queries(text, parsed.get("tags") or [], parsed.get("city") or "")
    except Exception as exc:
        parsed["engine"] = f"rules-fallback:{type(exc).__name__}"
    return parsed
