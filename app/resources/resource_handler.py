import requests, os, logging, gdown
from PIL import Image, ImageFont
from io import BytesIO
from fastapi import HTTPException, status
from dropbox.exceptions import ApiError

def load_background(template_path, typeSocial):
    """Import the background template."""
    try:
        file_path = os.path.join(template_path, typeSocial + ".png")
        background = Image.open(file_path)
        return background

    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao importar o template da imagem.", headers={"Error": str(e)})


# Download the image from Dropbox
def load_product_image(image_url):
    """Download a file from Dropbox."""

    try:
        
        if "drive.google.com" and "view?usp=sharing" in image_url:
            file_id = image_url.split('/')[-2]
            prefix = 'https://drive.google.com/uc?/export=download&id='
            response = requests.get(prefix + file_id)
        elif "drive.google.com" in image_url:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Link do Google Drive inválido.', headers={"Error": str(e)})
        else:
            response = requests.get(image_url)

        data = BytesIO(response.content)

        if data is not None:
            image = Image.open(data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Link para Imagem do produto inválido.", headers={"Error": str(e)})
        return image
    except ApiError as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Erro ao baixar a imagem do produto.', headers={"Error": str(e)})
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno.", headers={"Error": str(e)})

def load_font(fontSize):
    """Import the BebasNeue Font"""
    try:
        font = ImageFont.truetype("data/input/fonts/BebasNeue-Bold.ttf", fontSize)
        return font
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao importar a fonte.", headers={"Error": str(e)})

