"""FastAPI application entry point."""

from collections.abc import Sequence
from os import environ

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app(*, cors_origins: Sequence[str] | None = None) -> FastAPI:
    if cors_origins is None:
        configured_origins = environ.get(
            "PLAYGROUND_CORS_ORIGINS",
            "http://localhost:5173",
        )
        cors_origins = [
            origin.strip() for origin in configured_origins.split(",") if origin.strip()
        ]

    app = FastAPI(title="Playground API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(cors_origins),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
