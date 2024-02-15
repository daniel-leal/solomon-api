from fastapi import APIRouter, Depends, HTTPException, status

from app.solomon.auth.application.dependencies import get_auth_service
from app.solomon.auth.application.security import get_current_user
from app.solomon.auth.application.services import AuthService
from app.solomon.auth.domain.exceptions import AuthenticationError
from app.solomon.auth.presentation.models import (
    LoginCreate,
    UserCreate,
    UserCreateResponse,
    UserLoggedResponse,
    UserTokenAuthenticated,
)
from app.solomon.users.application.dependencies import get_user_service
from app.solomon.users.application.services import UserService
from app.solomon.users.domain.exceptions import UserAlreadyExists

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate, user_service: UserService = Depends(get_user_service)
) -> UserCreateResponse:
    """
    Create a new user.

    This function receives a UserCreate object and a UserService instance,
    then tries to create a new user using the provided service.
    If the user already exists, it raises an HTTPException with status code 400.

    Parameters
    ----------
    user : UserCreate
        The user to be created.
    user_service : UserService, optional
        The service to be used to create the user, by default Depends(get_user_service)

    Returns
    -------
    JSONResponse
        The created user with a 201 status code.

    Raises
    ------
    HTTPException
        If the user already exists.
    """
    try:
        user_created = user_service.create_user(user)
        return user_created
    except UserAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(
    user: LoginCreate, auth_service: AuthService = Depends(get_auth_service)
) -> UserLoggedResponse:
    """
    Login a user.

    This function receives a UserLogin object and a UserService instance,
    then tries to login a user using the provided service.
    If the user already exists, it raises an HTTPException with status code 400.

    Parameters
    ----------
    user : UserLogin
        The user to be created.
    auth_service : AuthService
        The service to be used to authenticate the user

    Returns
    -------
    JSONResponse
        The created user with a 201 status code.

    Raises
    ------
    HTTPException
        If the username or password is invalid.
    """
    try:
        logged_user = auth_service.authenticate(user)
        return logged_user
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile")
async def profile(
    current_user: UserTokenAuthenticated = Depends(get_current_user),
) -> UserTokenAuthenticated:
    """
    Endpoint to get the profile of the currently authenticated user.

    Parameters
    ----------
    current_user : UserLoggedResponse
        The currently authenticated user, obtained from the `get_current_user`
        dependency.

    Returns
    -------
    UserLoggedResponse
        The profile of the currently authenticated user.
    """
    return current_user
