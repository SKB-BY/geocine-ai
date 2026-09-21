# Architecture

```
browser (Leaflet) -> FastAPI -> asyncpg -> PostGIS 16
```

Defaults: EPSG:4326, GIST on geom, distances via geography / ST_DistanceSphere, tiles via ST_AsMVT.
