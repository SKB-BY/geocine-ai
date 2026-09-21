from __future__ import annotations

KEYWORD_MAP: dict[str, list[str]] = {
    "desert": ["desert", "пустын", "dune", "песк", "сахара", "morocco", "марокк", "arizona"],
    "mountain": ["mountain", "гор", "peak", "вершин", "alps", "альп", "altai", "алтай"],
    "city": ["city", "город", "skyline", "столиц", "urban", "downtown"],
    "forest": ["forest", "лес", "taiga", "тайг", "беловеж", "pushcha"],
    "water": ["lake", "озер", "river", "рек", "sea", "мор", "coast", "берег"],
    "historic": ["fortress", "крепост", "castle", "замок", "ruins", "руин", "historic"],
    "industrial": ["warehouse", "склад", "factory", "завод", "industrial", "промышл"],
    "snow": ["snow", "снег", "winter", "зим", "ice", "лёд", "лед"],
    "village": ["village", "деревн", "rural", "село"],
}


def parse_scene(text: str) -> dict:
    q = text.lower()
    tags: list[str] = []
    for tag, words in KEYWORD_MAP.items():
        if any(word in q for word in words):
            tags.append(tag)
    kind = None
    if any(w in q for w in ("инвест", "invest", "недвиж", "девелоп", "roi", "доход")):
        kind = "investment"
    elif any(w in q for w in ("съём", "съем", "film", "кино", "сцен", "battle", "битв")):
        kind = "film"
    return {"tags": tags, "kind": kind, "raw": text, "engine": "rule-based-v1"}


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def match_score(parsed_tags: list[str], location_tags: list[str], distance_m: float | None) -> float:
    if not parsed_tags:
        tag_score = 0.55
    else:
        overlap = len(set(parsed_tags) & set(location_tags))
        tag_score = overlap / max(len(parsed_tags), 1)
    if distance_m is None:
        dist_score = 0.7
    else:
        dist_score = clamp01(1.0 - (distance_m / 5_000_000.0))
    return round(0.75 * tag_score + 0.25 * dist_score, 4)


def investment_score(growth: float, flood: float, permit: float, weather: float) -> float:
    risk = 0.45 * flood + 0.30 * weather + 0.25 * permit
    return round(clamp01(0.65 * growth + 0.35 * (1.0 - risk)), 4)


def final_scout_score(semantic: float, weather: float, flood: float, permit: float) -> float:
    readiness = 1.0 - (0.4 * weather + 0.35 * flood + 0.25 * permit)
    return round(clamp01(0.55 * semantic + 0.45 * readiness), 4)
