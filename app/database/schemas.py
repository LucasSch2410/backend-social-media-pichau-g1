from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class socialMedia(BaseModel):
    datetime: str
    sku: str
    price: float
    installments: int
    installments_price: float
    product_url: str
    image_url: str
    bg_url: str
    discount: str
    product_name: Optional[str] = None
    
