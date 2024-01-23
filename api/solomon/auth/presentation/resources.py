from fastapi import APIRouter, Depends, HTTPException, Response, status

from api.solomon.auth.application.factories import get_auth_service
from api.solomon.auth.application.security import get_current_user
from api.solomon.auth.application.services import AuthService
from api.solomon.auth.domain.exceptions import AuthenticationError
from api.solomon.auth.presentation.models import (
    LoginCreate,
    UserCreate,
    UserCreateResponse,
    UserLoggedinResponse,
    UserTokenAuthenticated,
)
from api.solomon.users.application.factories import get_user_service
from api.solomon.users.application.services import UserService
from api.solomon.users.domain.exceptions import UserAlreadyExists

router = APIRouter()


@router.post(
    "/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user: UserCreate, user_service: UserService = Depends(get_user_service)
) -> Response:
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


@router.post("/login", response_model=UserLoggedinResponse)
async def login(
    user: LoginCreate, auth_service: AuthService = Depends(get_auth_service)
) -> Response:
    """
    Login a user.

    This function receives a UserLogin object and a UserService instance,
    then tries to login a user using the provided service.
    If the user already exists, it raises an HTTPException with status code 400.

    Parameters
    ----------
    user : UserLogin
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
        If the username or password is invalid.
    """
    try:
        user_loggedin = auth_service.authenticate(user)
        return user_loggedin
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", response_model=UserTokenAuthenticated)
async def profile(current_user: UserLoggedinResponse = Depends(get_current_user)):
    """
    Endpoint to get the profile of the currently authenticated user.

    Parameters
    ----------
    current_user : UserLoggedinResponse
        The currently authenticated user, obtained from the `get_current_user` dependency.

    Returns
    -------
    UserLoggedinResponse
        The profile of the currently authenticated user.
    """

    return current_user
