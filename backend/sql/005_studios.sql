CREATE TABLE IF NOT EXISTS film_facilities (
    id bigserial PRIMARY KEY,
    slug text NOT NULL UNIQUE,
    name text NOT NULL,
    city text NOT NULL,
    country text NOT NULL,
    facility_type text NOT NULL CHECK (facility_type IN ('sound_stage','backlot','water_tank','vp_volume','mixed','lot')),
    stages_count integer NOT NULL DEFAULT 1,
    largest_stage_sqm integer,
    power_kw integer,
    virtual_production boolean NOT NULL DEFAULT false,
    crew_max integer,
    day_rate_usd_from integer,
    permit_office text,
    permit_notes text,
    services text[] NOT NULL DEFAULT '{}',
    description text NOT NULL,
    website text,
    geom geometry(Point, 4326) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS film_facilities_gix ON film_facilities USING GIST (geom);

INSERT INTO film_facilities (slug,name,city,country,facility_type,stages_count,largest_stage_sqm,power_kw,virtual_production,crew_max,day_rate_usd_from,permit_office,permit_notes,services,description,website,geom) VALUES
('belarusfilm','Беларусьфильм','Минск','BY','mixed',8,1200,800,false,180,2500,'Мингорисполком','Павильоны по заявке.',ARRAY['stage','workshops'],'Национальная студия. Павильоны и цеха.','https://belarusfilm.by',ST_SetSRID(ST_MakePoint(27.5344,53.8616),4326)),
('mosfilm','Мосфильм','Москва','RU','mixed',16,2400,2000,true,400,8000,'Департамент СМИ Москвы','Лот и улицы-декорации.',ARRAY['stage','backlot','vp'],'Павильоны, декорации, техника.','https://www.mosfilm.ru',ST_SetSRID(ST_MakePoint(37.5316,55.7260),4326)),
('lenfilm','Ленфильм','Санкт-Петербург','RU','sound_stage',6,900,700,false,150,4500,'Комитет по культуре СПб','На улицу города — отдельный пермит.',ARRAY['stage','archive'],'Павильоны рядом с северной натурой.','https://www.lenfilm.ru',ST_SetSRID(ST_MakePoint(30.3400,59.9560),4326)),
('barrandov','Barrandov Studios','Прага','CZ','mixed',14,4000,2500,true,500,9000,'Prague Film Office','Сильный rebate Чехии.',ARRAY['stage','backlot','vp','water'],'Европейский хаб: павильоны и бэклот.','https://www.barrandov.cz',ST_SetSRID(ST_MakePoint(14.3880,50.0310),4326)),
('cinecitta','Cinecittà','Рим','IT','mixed',18,3500,2200,true,450,10000,'Roma Film Commission','Город — отдельная комиссия.',ARRAY['stage','backlot','vp'],'Классика европейского производства.','https://www.cinecitta.com',ST_SetSRID(ST_MakePoint(12.5690,41.8490),4326)),
('pinewood','Pinewood Studios','Iver Heath','GB','mixed',20,5500,4000,true,700,18000,'Film London','007 Stage, бронировать рано.',ARRAY['stage','backlot','vp','water'],'Крупные павильоны и вода.','https://pinewoodgroup.com',ST_SetSRID(ST_MakePoint(-0.5320,51.5480),4326)),
('leavesden','Warner Bros. Studios Leavesden','Leavesden','GB','mixed',12,4200,3000,true,500,16000,'Film London','Часть лота — тур, часть — съёмка.',ARRAY['stage','backlot','vp'],'Долгие сезоны и улицы-декорации.','https://www.wbslleavesden.com',ST_SetSRID(ST_MakePoint(-0.4180,51.6930),4326)),
('babelsberg','Studio Babelsberg','Потсдам','DE','mixed',16,3800,2800,true,480,11000,'Medienboard Berlin-Brandenburg','Рядом Берлин.',ARRAY['stage','backlot','vp'],'Старая студия, современные павильоны.','https://www.studiobabelsberg.com',ST_SetSRID(ST_MakePoint(13.0900,52.3870),4326)),
('korda','Korda Studios','Этирд','HU','mixed',8,6000,3500,true,400,7000,'National Film Institute Hungary','Большие павильоны и бэклот-замок.',ARRAY['stage','backlot','vp'],'Удобно под период и фэнтези.',ARRAY['https://kordastudio.hu']::text[],ST_SetSRID(ST_MakePoint(18.6680,47.6150),4326)),
('trilith','Trilith / Atlanta studio belt','Фейетвилл','US','mixed',20,5000,4000,true,800,14000,'Georgia Film Office','Сильный tax credit Джорджии.',ARRAY['stage','backlot','vp'],'Пояс студий у Атланты, LED-сцены.','https://trilith.com',ST_SetSRID(ST_MakePoint(-84.4780,33.4470),4326)),
('dubai-studio-city','Dubai Studio City','Дубай','AE','mixed',10,3000,2500,true,350,9000,'Dubai Media City','Павильоны закрытые, рядом пустыня.',ARRAY['stage','vp','backlot'],'Студийный кластер и VP.','https://www.dubaistudiocity.ae',ST_SetSRID(ST_MakePoint(55.2150,25.0370),4326)),
('istanbul-beykoz','Beykoz Kundura','Стамбул','TR','mixed',7,1800,1100,false,220,3200,'Istanbul Film Office','На улицу — обязательный пермит.',ARRAY['stage','historic'],'Индустриал на Босфоре.','https://www.beykozkundura.com',ST_SetSRID(ST_MakePoint(29.0880,41.0860),4326)),
('tbilisi-qartuli','Грузинская киностудия','Тбилиси','GE','sound_stage',4,800,500,false,120,1800,'Tbilisi City Hall','Павильонов мало, натура сильная.',ARRAY['stage'],'Небольшой лот и старый город.','https://www.geocinema.ge',ST_SetSRID(ST_MakePoint(44.7830,41.7050),4326)),
('prague-vp','Prague LED / VP stages','Прага','CZ','vp_volume',3,800,1500,true,180,12000,'Prague Film Office','Virtual production рядом с Barrandov.',ARRAY['vp','led'],'LED-volume под интерьеры и авто.','https://www.praguerocks.com',ST_SetSRID(ST_MakePoint(14.4378,50.0755),4326))
ON CONFLICT (slug) DO NOTHING;
