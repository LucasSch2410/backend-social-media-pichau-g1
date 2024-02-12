import os, shutil, zipfile, requests, tempfile, logging
from bs4 import BeautifulSoup
from fastapi import status, HTTPException, Depends, APIRouter, Response, FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from fastapi.params import Body
from typing import Annotated
from PIL import Image 
from io import BytesIO

from app.database.cloud_storage import upload_to_bucket, download_file_from_bucket, verify_template

from app.database import schemas, crud
from app.database.main import get_db

# Auth and layouts
from app.oauth import dropbox_connect
from app.layouts import createLayout
from .. import oauth2


router = APIRouter(
    prefix="/images",
    tags=["Images"]
)


@router.get("/")
def get_images(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    images = crud.get_all_images(db, current_user.id)

    return images

@router.get("/templates/{user_id}/{typeSocial}")
def get_templates(user_id: int, typeSocial: str):

    template = verify_template(typeSocial, user_id)

    if template != False:
        return template
    else:
        return None
        
@router.get("/static/templates/{typeSocial}")
def get_templates(typeSocial: str):

    path = f'data/input/templates/template-{typeSocial}.jpeg'
    if os.path.exists(path):
        return FileResponse(path)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Imagem não encontrada.')


@router.put("/templates/upload/{user_id}/{typeSocial}", status_code=status.HTTP_204_NO_CONTENT)
def set_templates(file: UploadFile, user_id: int, typeSocial: str, current_user: int = Depends(oauth2.get_current_user)):

    types = ['post', 'push', 'stories', 'wide']

    if typeSocial not in types:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não é possível acessar essa rota.')

    try:
        data = Image.open(file.file)

        if typeSocial == 'post':
            if data.width != 900 or data.height != 900:
                raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f'As medidas da imagem são inválidas.')
        elif typeSocial == 'push':
            if data.width != 720 or data.height != 360:
                raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f'As medidas da imagem são inválidas.')
        elif typeSocial == 'stories':
            if data.width != 1080 or data.height != 1920:
                raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f'As medidas da imagem são inválidas.')
        elif typeSocial == 'wide':
            if data.width != 1920 or data.height != 1080:
                raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=f'As medidas da imagem são inválidas.')
        
        file_path = f'data/output/temp/{user_id}'

        if not os.path.exists(file_path):
            os.mkdir(file_path)
        data.save(f'{file_path}/template-{typeSocial}.jpeg')

        upload_to_bucket(f'{user_id}/template-{typeSocial}', os.path.join(file_path, f'template-{typeSocial}.jpeg'))

        data.close()

    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Erro Interno', headers={"Error": str(e)})
    finally:
        if os.path.exists(file_path):
            shutil.rmtree(file_path)




@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=schemas.socialMediaOut)
def create_media(payLoad: schemas.socialMedia, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Create a social media post in the database.

    access_token: The Dropbox access token created by auth2 route.

    product: The name of the product with SKU.

    price: Price of the product without letters or commas.

    installment: Price of the installment without letters or commas.

    typeSocial: The type of the social media that the user want to create.

    user: Username from the user of the request.
    """

    payLoad.price = str(payLoad.price)
    payLoad.installment = str(payLoad.installment)

    try:
        # Verify if the user exists in database
        user_id = current_user.id
        name_file = payLoad.product_name.split(', ')[-1].replace('/', '-')

        dbx = dropbox_connect(payLoad.access_token)

        layout = createLayout(payLoad.typeSocial)
        final_image = layout(payLoad, dbx, user_id)()

        # Temporary creation
        with tempfile.NamedTemporaryFile(suffix='.jpeg') as tmp:

            buffer = BytesIO()
            final_image.save(buffer, format='JPEG')
            image_bytes = buffer.getvalue()
            tmp.write(image_bytes)

            upload_to_bucket(f'{user_id}/{payLoad.typeSocial}/{name_file}', tmp.name)


        # Creation of the image metadata in the database
        data = crud.upload_file_to_database(db, payLoad, user_id, name_file)

        return data
    except HTTPException as http_exception:
        logging.error(http_exception)
        raise http_exception
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Erro interno.', headers={"Error": str(e)})
    finally:
        if final_image:
            final_image.close()

@router.post('/sheet')
def scrap_sheet(payLoad: schemas.requestSheet, current_user: int = Depends(oauth2.get_current_user)):
    """
    Scrap the HTML of the Google Sheet in the URL from the request.

    sheet_url: URL of the Public Google Sheet to download with three columns (name, price, installment).
    """

    try:
        html = requests.get(payLoad.sheet_url)
        soup = BeautifulSoup(html.text, "html.parser")
        table = soup.find("tbody")
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='URL inválida.', headers={"Error": str(e)})
    
    products = []
    id = 1

    # Iterate across product lines
    for line in table:
        index = int(line.find('th').get_text())
        if index > 1:
            product = line.find_all('td')

            name = product[0].get_text()
            price = ''.join([char for char in product[1].get_text() if char.isnumeric()])
            installment = ''.join([char for char in product[2].get_text() if char.isnumeric()])

            if name != "":
                products.append({  # Adiciona o produto à lista
                    "product": name,
                    "price": price,
                    "installment": installment,
                    "key": id
                })
                id += 1

    return products



@router.post("/download")
def download_images(payLoad: schemas.downloadReq, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Create a zip file and deliver it to the user.

    user: Username to download the files.

    typeSocial: The type of the social media that the user want to download. [post, push, stories, wide]
    """

    user_id = current_user.id
    typeSocial = payLoad.typeSocial
    stored_images = crud.get_all_images(db, user_id, typeSocial)

    images_to_download = []
    for image in stored_images:
        images_to_download.append(image.product_name)

    local_path = f"data/output/temp/{user_id}/{typeSocial}"

    try:
        if not os.path.exists(local_path):
            os.makedirs(local_path)

        with zipfile.ZipFile(f'{local_path}/files.zip', 'w') as zip_file:
            for image in images_to_download:
                download_file_from_bucket(f'{user_id}/{typeSocial}/{image}', os.path.join(local_path, f'{image}.jpeg'))
                file_path = os.path.join(local_path, f'{image}.jpeg')
                zip_file.write(file_path, os.path.basename(file_path))

                
        upload_to_bucket(f'{user_id}/{typeSocial}/{typeSocial}', os.path.join(local_path, f'files.zip'))

        url = f"https://storage.googleapis.com/pichau_social_media/{user_id}/{typeSocial}/{typeSocial}"
    
        data = {"url": url}

        return JSONResponse(content=data)

    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Erro interno.', headers={"Error": str(e)})
    finally:
        if os.path.exists(f"{local_path}"):
            shutil.rmtree(f"data/output/temp/{user_id}")



@router.delete("/{id}")
def delete_image(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Delete the image with the id in the URL.

    id: ID of the image in the database.
    """

    crud.delete_image_database(db, id, current_user.id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/{id}/{typeSocial}")
def delete_all_images(id: int, typeSocial: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Delete all the images with the user id and the type social in the URL.

    id: ID of the user in the database.

    typeSocial: The type of social media to delete all the images.
    """
    try:
        images = crud.get_all_images(db, id, typeSocial)

        for image in images:
            crud.delete_image_database(db, id=image.id, user_id=id)

    except Exception as e:
        logging.error(e)
        return Response(status_code=status.HTTP_204_NO_CONTENT, headers={"Error": str(e)})

    return Response(status_code=status.HTTP_204_NO_CONTENT)
