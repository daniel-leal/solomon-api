from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware

from app.solomon.infrastructure.config import DATABASE_URL
from app.solomon.routes.routes import init_routes

app = FastAPI(
    title="Solomon API",
    version="0.1.0",
    docs_url="/app/docs",
    redoc_url="/app/redoc",
)

init_routes(app)

app.add_middleware(DBSessionMiddleware, db_url=DATABASE_URL)
