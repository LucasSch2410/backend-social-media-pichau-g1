from fastapi import status, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.database import schemas, models, crud
from app.database.main import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=schemas.userOut)
def create_user(user: schemas.userData, db: Session = Depends(get_db)):

    new_user = crud.create_user(db, user)

    return new_user


@router.get('/{id}', response_model=schemas.userOut)
def get_user(id: int, db: Session = Depends(get_db)):

    username = db.query(models.User).filter(models.User.id == id).first()

    if not username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Usuário com o id: {id} não foi encontrado!")

    user = crud.get_user_data(db, username)

    return user


