from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None