INSERT INTO locations (
    slug, name, country, region, kind, tags, description,
    cost_estimate_usd, shooting_cost_usd, weather_risk, flood_risk,
    permit_difficulty, growth_potential, geom
) VALUES
('minsk-center', 'Минск, центр и набережная Свислочи', 'BY', 'Минск', 'both', ARRAY['city','historic','water'], 'Городские панорамы, советский модернизм, набережная.', 420000, 85000, 0.28, 0.22, 0.35, 0.62, ST_SetSRID(ST_MakePoint(27.5615, 53.9023), 4326)),
('brest-fortress', 'Брестская крепость', 'BY', 'Брест', 'film', ARRAY['historic','city'], 'Монументальная историческая локация.', 180000, 62000, 0.30, 0.18, 0.72, 0.31, ST_SetSRID(ST_MakePoint(23.6550, 52.0830), 4326)),
('belovezhskaya-pushcha', 'Беловежская пуща', 'BY', 'Брестская область', 'both', ARRAY['forest','village'], 'Древний лес, экотуризм.', 210000, 54000, 0.34, 0.20, 0.68, 0.48, ST_SetSRID(ST_MakePoint(23.8800, 52.6300), 4326)),
('braslav-lakes', 'Браславские озёра', 'BY', 'Витебская область', 'both', ARRAY['water','forest','village'], 'Озёрный край, рассветы.', 160000, 41000, 0.36, 0.27, 0.40, 0.52, ST_SetSRID(ST_MakePoint(27.0500, 55.6400), 4326)),
('moscow-city', 'Москва-Сити', 'RU', 'Москва', 'both', ARRAY['city','industrial'], 'Небоскрёбы, ночные панорамы.', 2400000, 280000, 0.25, 0.16, 0.70, 0.58, ST_SetSRID(ST_MakePoint(37.5390, 55.7473), 4326)),
('altai-katun', 'Алтай, долина Катуни', 'RU', 'Алтай', 'film', ARRAY['mountain','water','village'], 'Горные долины, река, эпические планы.', 190000, 97000, 0.55, 0.33, 0.45, 0.44, ST_SetSRID(ST_MakePoint(85.9600, 51.7900), 4326)),
('kamchatka-volcano', 'Камчатка, вулканический район', 'RU', 'Камчатка', 'film', ARRAY['mountain','snow','desert'], 'Инопланетный рельеф.', 120000, 310000, 0.72, 0.15, 0.60, 0.29, ST_SetSRID(ST_MakePoint(158.6500, 53.0500), 4326)),
('morocco-erg-chebbi', 'Эрг-Шебби, Марокко', 'MA', 'Эр-Рашидия', 'film', ARRAY['desert'], 'Классические дюны для пустынных сцен.', 95000, 120000, 0.40, 0.05, 0.32, 0.37, ST_SetSRID(ST_MakePoint(-4.0000, 31.1700), 4326)),
('arizona-monument-valley', 'Monument Valley, США', 'US', 'Arizona / Utah', 'film', ARRAY['desert','mountain'], 'Иконический западный ландшафт.', 310000, 210000, 0.33, 0.06, 0.66, 0.41, ST_SetSRID(ST_MakePoint(-110.1667, 36.9833), 4326)),
('alps-grindelwald', 'Гриндельвальд, Альпы', 'CH', 'Bernese Oberland', 'both', ARRAY['mountain','snow','village'], 'Альпийские вершины.', 890000, 240000, 0.48, 0.14, 0.58, 0.46, ST_SetSRID(ST_MakePoint(8.0400, 46.6240), 4326)),
('istanbul-historic', 'Стамбул, исторический полуостров', 'TR', 'Стамбул', 'both', ARRAY['city','historic','water'], 'Стык континентов.', 670000, 130000, 0.27, 0.24, 0.50, 0.63, ST_SetSRID(ST_MakePoint(28.9784, 41.0082), 4326)),
('dubai-creek-harbour', 'Dubai Creek Harbour', 'AE', 'Dubai', 'investment', ARRAY['city','water'], 'Waterfront-девелопмент.', 1800000, 190000, 0.18, 0.12, 0.42, 0.71, ST_SetSRID(ST_MakePoint(55.3300, 25.2050), 4326)),
('lisbon-alfama', 'Лиссабон, Алфама', 'PT', 'Лиссабон', 'both', ARRAY['city','historic','water'], 'Узкие улицы, свет Атлантики.', 540000, 98000, 0.22, 0.19, 0.38, 0.57, ST_SetSRID(ST_MakePoint(-9.1300, 38.7130), 4326)),
('tbilisi-old-town', 'Тбилиси, старый город', 'GE', 'Тбилиси', 'both', ARRAY['city','historic','mountain'], 'Рельеф и текстура фасадов.', 280000, 47000, 0.29, 0.21, 0.33, 0.64, ST_SetSRID(ST_MakePoint(44.8070, 41.6930), 4326))
ON CONFLICT (slug) DO NOTHING;
