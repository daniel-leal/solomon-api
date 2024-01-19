from fastapi import APIRouter, FastAPI, Response

from api.solomon.auth.presentation.resources import router as auth_router

router = APIRouter()


@router.get("/health", status_code=200)
def health_check() -> Response:
    return {"status": "healthy"}


def init_routes(app: FastAPI) -> None:
    """
    Function to initialize all routes for the application.

    Parameters
    ----------
    app: FastAPI
        FastAPI application instance
    """
    app.include_router(router, tags=["health"])
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
