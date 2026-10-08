from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, budgets, categories, expenses, health, summary, users
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Application factory — keeps app construction testable and import-safe."""
    settings = get_settings()

    app = FastAPI(
        title="Ledgerly API",
        description="A clean, personal expense tracker API.",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/v1")
    app.include_router(auth.router, prefix="/v1")
    app.include_router(users.router, prefix="/v1")
    app.include_router(categories.router, prefix="/v1")
    app.include_router(expenses.router, prefix="/v1")
    app.include_router(budgets.router, prefix="/v1")
    app.include_router(summary.router, prefix="/v1")

    return app


app = create_app()
