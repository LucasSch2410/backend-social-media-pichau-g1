import requests, os
from fastapi import status, Depends, APIRouter, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import schemas 
from app.database import crud
from app.database.main import get_db

from ..config import settings
from ..database.schemas import LoginResponse
from .. import oauth2

router = APIRouter(
    tags=["Authentication"]
)

def get_dropbox_token():
    client_id = settings.client_id
    client_secret = settings.client_secret
    refresh_token = settings.refresh_token
    token_url = "https://api.dropboxapi.com/oauth2/token"

    params = {
        "grant_type": 'refresh_token',
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }

    try:
        r = requests.post(token_url, data=params)
        r.raise_for_status()
        dropbox_response = r.json()
        return dropbox_response['access_token']
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Falha interna na geração de token: {str(e)}',
            headers={"Error": str(e)}
        )


@router.post('/login', response_model=schemas.LoginResponse)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Creates a new Access Token for Dropbox.
    """
    user = crud.get_user_data(db, user_credentials)

    dropbox_token = get_dropbox_token()
    access_token = oauth2.create_access_token(data = {"user_id": user.id})

    response = LoginResponse(
        user={"username": user.username, "id": user.id},
        dropbox_token=dropbox_token,
        access_token=access_token
    )

    return response