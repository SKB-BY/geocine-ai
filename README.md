# GeoCine AI

GIS + AI платформа для поиска киносъёмочных локаций и анализа инвестиций в недвижимость.

Репозиторий: https://github.com/SKB-BY/geocine-ai

## Что внутри (MVP 0.1)

- PostGIS 16: точки `geometry(Point,4326)`, GIST, GIN по тегам
- FastAPI + asyncpg: scout, investments, GeoJSON, MVT, экспорт в Unreal
- Leaflet UI: тёмная карта, карточки локаций, rule-based matcher
- Docker Compose: `db` + `api` одной командой

Демо-каталог: Беларусь, Россия, Марокко, США, Альпы, Стамбул, Дубай, Лиссабон, Тбилиси.

## Запуск

```bash
cp .env.example .env
docker compose up --build
```

Открыть: http://localhost:8000

## Стек

| Слой | Технология |
|------|------------|
| API | Python 3.12, FastAPI, asyncpg |
| GIS | PostGIS 16, EPSG:4326, ST_DWithin / ST_DistanceSphere / ST_AsMVT |
| UI | Leaflet 1.9, vanilla JS |
| Ops | Docker Compose, GitHub Actions compile check |

Это исследовательский MVP, не инвестиционная рекомендация.

MIT
