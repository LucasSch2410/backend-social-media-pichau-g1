from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class socialMedia(BaseModel):
    access_token: str
    product_name: str
    price: int
    installment: int
    typeSocial: str

class socialMediaOut(BaseModel):
    product_name: str
    typeSocial: str
    created_at: datetime
    image: str

    class Config:
        from_attributes = True


class requestSheet(BaseModel):
    sheet_url: str


class userData(BaseModel):
    username: str
    password: str

class userOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class downloadReq(BaseModel):
    username: str
    typeSocial: str

class imagesInfo(BaseModel):
    price: int
    installment: int
    typeSocial: str
    product_name: str
    image: str


class LoginResponse(BaseModel):
    access_token: str
    dropbox_token: str
    user: dict
    
class TokenData(BaseModel):
    id: Optional[int] = None