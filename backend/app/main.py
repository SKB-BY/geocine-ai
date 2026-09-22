from contextlib import asynccontextmanager
from pathlib import Path
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.db import close, connect
from app.routers import billing, film, investments, locations, payments, scout, spots, studios, tiles

FRONTEND_DIR = Path(os.environ.get("FRONTEND_DIR", str(Path(__file__).resolve().parents[2] / "frontend")))

@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect()
    yield
    await close()

app = FastAPI(title="GeoCine AI", version="0.3.1", description="Селфи, контент, натура для кино, студии.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list or ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
for r in (locations, scout, investments, tiles, billing, spots, payments, studios, film):
    app.include_router(r.router)

@app.get("/api/health")
async def health():
    pool = await connect()
    async with pool.acquire() as conn:
        ok = await conn.fetchval("SELECT postgis_version()")
    return {"status": "ok", "postgis": ok}

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
    @app.get("/")
    async def index():
        return FileResponse(FRONTEND_DIR / "index.html")
