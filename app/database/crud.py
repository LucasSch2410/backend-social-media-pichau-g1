from sqlalchemy.orm import Session
from fastapi import  HTTPException, status
from app.database.cloud_storage import delete_from_bucket

from . import models


def create_user(db: Session, user_data):

    verifyIfUserExists = db.query(models.User).filter(models.User.username == user_data.username).first()

    if verifyIfUserExists:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Usuário com o nome: {user_data.username} já existe.")

    new_user = models.User(**user_data.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_user_data(db: Session, user_data):
    
    data = db.query(models.User).filter(models.User.username == user_data.username).first()

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Usuário com o nome {user_data.username} não foi encontrado!")

    if data.password != user_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Senha incorreta!")

    return data


def upload_file_to_database(db: Session, payLoad, user_id, name_file):
    verify_product_database = db.query(models.Images).filter(models.Images.product_name == name_file, 
        models.Images.typeSocial == payLoad.typeSocial, models.Images.owner_id == user_id)

    if verify_product_database:
        verify_product_database.delete(synchronize_session=False)

    data = models.Images(
            product_name=payLoad.product_name.split(', ')[-1],
            price=payLoad.price,
            installment=payLoad.installment,
            image=f"https://storage.googleapis.com/pichau_social_media/{user_id}/{payLoad.typeSocial}/{name_file}",
            typeSocial = payLoad.typeSocial,
            owner_id=user_id
    )
            
    db.add(data)
    db.commit()
    db.refresh(data)

    return data


def get_all_images(db: Session, user_id, typeSocial=None):

    if typeSocial != None:
        images = db.query(models.Images).filter(models.Images.owner_id == user_id, models.Images.typeSocial == typeSocial).all()
    else:
        images = db.query(models.Images).filter(models.Images.owner_id == user_id).all()

    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrada imagens no banco de dados.')

    return images


def delete_image_database(db: Session, id, user_id):

    image = db.query(models.Images).filter(models.Images.id == id, models.Images.owner_id == user_id)

    if image.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Essa imagem não existe.")
    
    try:
        delete_from_bucket(image.first().product_name, user_id, image.first().typeSocial)

        image.delete(synchronize_session=False)
        db.commit()

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error", headers={"Error": str(e)})

