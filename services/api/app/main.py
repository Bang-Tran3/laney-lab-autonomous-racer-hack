from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.database import connect, init_schema
from app.routers.models import router as models_router
from app.routers.runs import router as runs_router
from app.routers.training import router as training_router
from app.storage import LocalArtifactStorage


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = cfg
        app.state.db = connect(cfg.database_path)
        init_schema(app.state.db)
        app.state.storage = LocalArtifactStorage(cfg.storage_root)
        try:
            yield
        finally:
            app.state.db.close()

    app = FastAPI(title=cfg.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(cfg.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(runs_router)
    app.include_router(models_router)
    app.include_router(training_router)
    return app


app = create_app()
