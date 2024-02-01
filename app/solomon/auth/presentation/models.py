from pydantic import BaseModel


class UserTokenAuthenticated(BaseModel):
    id: str
    username: str
    email: str
    token: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserCreateResponse(BaseModel):
    username: str
    email: str


class LoginCreate(BaseModel):
    username: str
    password: str


class UserLoggedinResponse(BaseModel):
    access_token: str
    token_type: str
