CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS locations (
    id                  bigserial PRIMARY KEY,
    slug                text NOT NULL UNIQUE,
    name                text NOT NULL,
    country             text NOT NULL,
    region              text,
    kind                text NOT NULL CHECK (kind IN ('film', 'investment', 'both')),
    tags                text[] NOT NULL DEFAULT '{}',
    description         text NOT NULL,
    cost_estimate_usd   integer,
    shooting_cost_usd   integer,
    weather_risk        real NOT NULL CHECK (weather_risk BETWEEN 0 AND 1),
    flood_risk          real NOT NULL CHECK (flood_risk BETWEEN 0 AND 1),
    permit_difficulty   real NOT NULL CHECK (permit_difficulty BETWEEN 0 AND 1),
    growth_potential    real NOT NULL CHECK (growth_potential BETWEEN 0 AND 1),
    geom                geometry(Point, 4326) NOT NULL,
    created_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS locations_geom_gix ON locations USING GIST (geom);
CREATE INDEX IF NOT EXISTS locations_kind_idx ON locations (kind);
CREATE INDEX IF NOT EXISTS locations_tags_gin ON locations USING GIN (tags);

CREATE TABLE IF NOT EXISTS scout_jobs (
    id          bigserial PRIMARY KEY,
    query       text NOT NULL,
    parsed      jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at  timestamptz NOT NULL DEFAULT now()
);
