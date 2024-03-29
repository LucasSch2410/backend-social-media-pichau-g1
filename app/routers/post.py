import zipfile, tempfile, logging, zipfile, dropbox
from fastapi import status, HTTPException, APIRouter
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
    if payLoad.sku in payLoad.product_name:
        payLoad.product_name = payLoad.product_name.replace(payLoad.sku, "")

    typeSocial = ["stories", "post", "push", "wide"]

    try:
        with tempfile.TemporaryDirectory(dir=".") as tmp_dir:
            zip_data = crud.download_templates(payLoad.bg_url)  
            with zipfile.ZipFile(BytesIO(zip_data)) as zip:
                zip.extractall(tmp_dir)
                
                access_token = crud.get_dropbox_token()
                dbx = dropbox_connect(access_token)

                for type in typeSocial:
                    layout = createLayout(type)
                    final_image = layout(payLoad, tmp_dir)()

                    with tempfile.NamedTemporaryFile(suffix='.png') as tmp:

                        buffer = BytesIO()
                        final_image.save(buffer, format='PNG')
                        tmp.write(buffer.getvalue())
                        tmp.seek(0)

                        dbx.files_upload(tmp.read(), f"/arquivos_criados/{payLoad.sku}-{type}.png", mode=dropbox.files.WriteMode("overwrite"))

                return {"message": "Imagem criada com sucesso."}
        
    except HTTPException as http_exception:
        logging.error(http_exception, exc_info=True)
        raise http_exception
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Erro interno.', headers={"Error": str(e)})

