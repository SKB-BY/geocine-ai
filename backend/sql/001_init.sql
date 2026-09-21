CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS locations (
    id bigserial PRIMARY KEY,
    slug text NOT NULL UNIQUE,
    name text NOT NULL,
    country text NOT NULL,
    region text,
    kind text NOT NULL CHECK (kind IN ('selfie', 'content', 'film', 'investment', 'both')),
    audiences text[] NOT NULL DEFAULT ARRAY['content'],
    tags text[] NOT NULL DEFAULT '{}',
    description text NOT NULL,
    cost_estimate_usd integer,
    shooting_cost_usd integer,
    weather_risk real NOT NULL CHECK (weather_risk BETWEEN 0 AND 1),
    flood_risk real NOT NULL CHECK (flood_risk BETWEEN 0 AND 1),
    permit_difficulty real NOT NULL CHECK (permit_difficulty BETWEEN 0 AND 1),
    growth_potential real NOT NULL CHECK (growth_potential BETWEEN 0 AND 1),
    access_type text NOT NULL DEFAULT 'public',
    price_tier text NOT NULL DEFAULT 'free',
    crowd_level real NOT NULL DEFAULT 0.4,
    selfie_score real NOT NULL DEFAULT 0.5,
    content_score real NOT NULL DEFAULT 0.5,
    safety_score real NOT NULL DEFAULT 0.7,
    golden_hour boolean NOT NULL DEFAULT true,
    best_hours text NOT NULL DEFAULT '07:00-09:00,18:00-20:00',
    geom geometry(Point, 4326) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS locations_geom_gix ON locations USING GIST (geom);
CREATE INDEX IF NOT EXISTS locations_kind_idx ON locations (kind);
CREATE INDEX IF NOT EXISTS locations_tags_gin ON locations USING GIN (tags);

CREATE TABLE IF NOT EXISTS scout_jobs (
    id bigserial PRIMARY KEY,
    query text NOT NULL,
    parsed jsonb NOT NULL DEFAULT '{}'::jsonb,
    plan_code text NOT NULL DEFAULT 'free',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS plans (
    code text PRIMARY KEY,
    name text NOT NULL,
    monthly_usd numeric(10,2) NOT NULL,
    daily_searches integer NOT NULL,
    can_export boolean NOT NULL DEFAULT false,
    can_api boolean NOT NULL DEFAULT false,
    can_unreal boolean NOT NULL DEFAULT false,
    audience text NOT NULL
);
INSERT INTO plans (code, name, monthly_usd, daily_searches, can_export, can_api, can_unreal, audience) VALUES
('free','Free',0,20,false,false,false,'selfie'),
('creator','Creator',9.90,80,true,false,false,'content'),
('studio','Studio',149,2000,true,true,true,'film'),
('enterprise','Enterprise',0,100000,true,true,true,'investment')
ON CONFLICT (code) DO NOTHING;

CREATE TABLE IF NOT EXISTS usage_events (
    id bigserial PRIMARY KEY,
    plan_code text NOT NULL DEFAULT 'free',
    action text NOT NULL,
    query text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS spot_submissions (
    id bigserial PRIMARY KEY,
    title text NOT NULL,
    description text NOT NULL,
    audience text NOT NULL DEFAULT 'selfie',
    lon float8 NOT NULL,
    lat float8 NOT NULL,
    geom geometry(Point, 4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(lon, lat), 4326)) STORED,
    status text NOT NULL DEFAULT 'pending',
    created_at timestamptz NOT NULL DEFAULT now()
);
