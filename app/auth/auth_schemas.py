from pydantic import BaseModel, ConfigDict, Field


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class UserCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=64)


class LoginSchema(BaseModel):
    name: str = Field(max_length=50)
    password: str = Field(max_length=64)