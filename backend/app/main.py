from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_ask, routes_documents, routes_health, routes_search, routes_tickets, routes_tools
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import engine

configure_logging()
settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(routes_health.router)
app.include_router(routes_documents.router)
app.include_router(routes_search.router)
app.include_router(routes_ask.router)
app.include_router(routes_tools.router)
app.include_router(routes_tickets.router)
