from pydantic import BaseModel
from typing import Optional


class ProductImageSchemaOut(BaseModel):
    id: int
    thumbnail: Optional[str] = None
    mobile: Optional[str] = None
    tablet: Optional[str] = None
    desktop: Optional[str] = None


class ProductSchemaOut(BaseModel):
    id: int
    name: str
    price: float
    category: str
    description: Optional[str] = None
    image: Optional[ProductImageSchemaOut] = None
