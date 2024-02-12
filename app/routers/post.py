import os, shutil, zipfile, requests, tempfile, logging, zipfile, dropbox
from bs4 import BeautifulSoup
from fastapi import status, HTTPException, Depends, APIRouter, Response, FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from fastapi.params import Body
from typing import Annotated
from PIL import Image 
from io import BytesIO

from app.database import schemas, crud

# Auth and layouts
from app.oauth import dropbox_connect
from app.layouts.createLayout import createLayout


router = APIRouter(
    prefix="/images",
    tags=["Images"]
)


@router.post('/create', status_code=status.HTTP_201_CREATED)
def create_media(payLoad: schemas.socialMedia):
    """
    Create a social media post in the database.

    access_token: The Dropbox access token created by auth2 route.

    product: The name of the product with SKU.

    price: Price of the product without letters or commas.

    installment: Price of the installment without letters or commas.

    typeSocial: The type of the social media that the user want to create.

    user: Username from the user of the request.
    """
    web_product_name, web_sku = crud.scrap_site(payLoad.product_url)
    if web_sku != payLoad.sku:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'SKU não bate com o SKU do site.', headers={"Error": str(e)})

    typeSocial = ["stories"]
    payLoad.price = str(payLoad.price)
    payLoad.installments = str(payLoad.installments)
    payLoad.product_name = web_product_name

    try:
        with tempfile.TemporaryDirectory(dir=".") as tmp_dir:
            zip_data = crud.download_templates(payLoad.bg_url)  
            with zipfile.ZipFile(BytesIO(zip_data)) as zip:
                zip.extractall(tmp_dir)
                
                print(tmp_dir)
                access_token = crud.get_dropbox_token()
                dbx = dropbox_connect(access_token)

                for type in typeSocial:
                    layout = createLayout(type)
                    final_image = layout(payLoad, tmp_dir)()
                    # final_image = final_image.convert('RGB')   

                with tempfile.NamedTemporaryFile(suffix='.png') as tmp:

                    buffer = BytesIO()
                    final_image.save(buffer, format='PNG')
                    tmp.write(buffer.getvalue())

                    dbx.files_upload(tmp, f"/arquivos_criados/{payLoad.sku}.png", mode=dropbox.files.WriteMode("overwrite"))

                return {"message": "Imagem criada com sucesso."}
        
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Erro interno.', headers={"Error": str(e)})

