import requests
from PIL import Image, ImageFont
from io import BytesIO
from fastapi import HTTPException, status
from dropbox.exceptions import ApiError
from app.database.cloud_storage import verify_template

def load_background(path, user_id, typeSocial):
    """Import the background template."""
    try:
        template = verify_template(typeSocial, user_id)

        if template != False:
            background = Image.open(requests.get(template, stream = True).raw)
            return background
        
        background = Image.open(path)
        return background
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao importar o template da imagem.", headers={"Error": str(e)})


# Download the image from Dropbox
def load_product_image(sku, dropbox):
    """Download a file from Dropbox."""

    try:
        metadata, response = dropbox.files_download(f"/automacao_midia/{sku}.png")
        
        # Get the binary content of the file
        data = BytesIO(response.content)

        if data is not None:
            image = Image.open(data)
        else:
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno.", headers={"Error": str(e)})
        return image
    except ApiError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Erro ao baixar a imagem do produto no DropBox.', headers={"Error": str(e)})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno.", headers={"Error": str(e)})

def load_font(fontSize):
    """Import the BebasNeue Font"""
    try:
        font = ImageFont.truetype("data/input/fonts/BebasNeue-Bold.ttf", fontSize)
        return font
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao importar a fonte.", headers={"Error": str(e)})

