from __future__ import annotations

KEYWORD_MAP = {
    "desert": ["desert", "пустын", "dune", "песк", "morocco", "arizona"],
    "mountain": ["mountain", "горы", "горах", "горный", "вершин", "alps", "альп", "altai", "алтай"],
    "city": ["city", "город", "skyline", "столиц", "urban", "мурал", "mural"],
    "forest": ["forest", "лесу", "леса", "тайг", "беловеж"],
    "water": ["lake", "озер", "river", "река", "реки", "sea", "море", "набереж", "вода", "воды", "у воды"],
    "historic": ["крепост", "замок", "historic", "старый город"],
    "industrial": ["завод", "industrial", "сити"],
    "snow": ["snow", "снег", "зим"],
    "village": ["village", "деревн", "село"],
}
SELFIE_WORDS = ("селфи", "selfie", "фото", "рилс", "reels", "tiktok", "инста", "контент", "блог")
FILM_WORDS = ("съём", "съем", "film", "кино", "сцен", "клип")
INVEST_WORDS = ("инвест", "invest", "недвиж", "roi")

def parse_scene(text: str) -> dict:
    q = text.lower()
    tags = [tag for tag, words in KEYWORD_MAP.items() if any(word in q for word in words)]
    kind = "content"
    if any(w in q for w in INVEST_WORDS): kind = "investment"
    elif any(w in q for w in FILM_WORDS): kind = "film"
    elif any(w in q for w in SELFIE_WORDS): kind = "selfie"
    return {"tags": tags, "kind": kind, "raw": text, "engine": "rule-based-v2"}

def clamp01(v):
    return max(0.0, min(1.0, v))

def match_score(parsed_tags, location_tags, distance_m):
    tag_score = 0.55 if not parsed_tags else len(set(parsed_tags) & set(location_tags)) / max(len(parsed_tags), 1)
    dist_score = 0.7 if distance_m is None else clamp01(1.0 - (distance_m / 5_000_000.0))
    return round(0.75 * tag_score + 0.25 * dist_score, 4)

def investment_score(growth, flood, permit, weather):
    risk = 0.45 * flood + 0.30 * weather + 0.25 * permit
    return round(clamp01(0.65 * growth + 0.35 * (1.0 - risk)), 4)

def final_scout_score(semantic, weather, flood, permit):
    readiness = 1.0 - (0.4 * weather + 0.35 * flood + 0.25 * permit)
    return round(clamp01(0.55 * semantic + 0.45 * readiness), 4)

def consumer_score(item, kind):
    beauty = 0.5 * float(item.get("selfie_score") or 0.5) + 0.5 * float(item.get("content_score") or 0.5)
    quiet = 1.0 - float(item.get("crowd_level") or 0.4)
    safety = float(item.get("safety_score") or 0.7)
    access_bonus = 0.08 if item.get("price_tier") == "free" else 0.0
    base = 0.45 * beauty + 0.25 * quiet + 0.22 * safety + access_bonus
    if kind == "selfie":
        base = 0.7 * base + 0.3 * float(item.get("selfie_score") or 0.5)
    return round(clamp01(base), 4)
