# GeoCine AI

Ищем места, где можно снять селфи, ролик или сцену. Рядом тот же каталог смотрит инвестор: что за район и какие там риски.

Репозиторий: https://github.com/SKB-BY/geocine-ai

Картинки в `docs/screens/`

## Как запустить

```bash
git clone https://github.com/SKB-BY/geocine-ai.git
cd geocine-ai
cp .env.example .env
docker compose down -v
docker compose up --build
```

Открыть http://localhost:8000

Если база поднималась на старой схеме, `down -v` обязателен.

В каталоге больше двадцати точек.

```bash
python3 tests/test_query.py
```
