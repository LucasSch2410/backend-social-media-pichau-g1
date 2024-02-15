
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
    

def scrap_site(product_url):
    import cfscrape, bs4
    scraper = cfscrape.create_scraper()
    content = scraper.get(product_url.replace("https", "http")).content
    soup = bs4.BeautifulSoup(content, "html.parser") 

    print(soup)

    product_name_element = soup.find(attrs={"data-cy":"product-page-title"}).text.replace('/', '-')
    sku_element = soup.find('strong', string='SKU:')
    sku = sku_element.parent.text.split(':')[-1].strip().replace('/', '-')

    if sku in product_name_element:
        product_name = product_name_element.replace(f", {sku}", "")
    
    return product_name, sku

def download_templates(url):
    url = url[:-1] + "1"

    downloaded_file = requests.get(url)

    return downloaded_file.content

