# Production connection 
import dropbox
from fastapi import status, HTTPException
from dropbox.exceptions import AuthError

def dropbox_connect(access_token):
    """Create a connection to Dropbox."""

    try:
        dbx = dropbox.Dropbox(access_token)
        dbx.users_get_current_account()
        return dbx
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Error with invalid token', headers={"Error": str(e)})
