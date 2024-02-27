
from ..config import settings
import requests
from fastapi import HTTPException, status

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

def download_templates(url):
    if not "dropbox" in url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'O link dos templates não é um link Dropbox válido.'
            )
    try:
        url = url[:-1] + "1"

        downloaded_file = requests.get(url)

        return downloaded_file.content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Falha interna ao fazer o download das imagens. Verifique se a pasta e o nome dos arquivos estão corretos.',
            headers={"Error": str(e)}
        )

