-- Если 005 упал на строке Korda, этот файл добивает площадку отдельно.
INSERT INTO film_facilities (slug,name,city,country,facility_type,stages_count,largest_stage_sqm,power_kw,virtual_production,crew_max,day_rate_usd_from,permit_office,permit_notes,services,description,website,geom)
VALUES ('korda','Korda Studios','Этирд','HU','mixed',8,6000,3500,true,400,7000,'National Film Institute Hungary','Большие павильоны и бэклот-замок.',ARRAY['stage','backlot','vp'],'Удобно под период и фэнтези.','https://kordastudio.hu',ST_SetSRID(ST_MakePoint(18.6680,47.6150),4326))
ON CONFLICT (slug) DO NOTHING;
