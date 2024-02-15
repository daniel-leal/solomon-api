from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware

from app.solomon.infrastructure.config import DATABASE_URL
from app.solomon.infrastructure.database import CustomQuery
from app.solomon.routes.routes import init_routes

app = FastAPI(
    title="Solomon API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

init_routes(app)

app.add_middleware(
    DBSessionMiddleware,
    db_url=DATABASE_URL,
    session_args={"query_cls": CustomQuery},
)
