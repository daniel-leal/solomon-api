from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware

from api.solomon.infrastructure.config import DATABASE_URL
from api.solomon.routes.routes import init_routes

app = FastAPI(
    title="Solomon API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

init_routes(app)

app.add_middleware(DBSessionMiddleware, db_url=DATABASE_URL)
