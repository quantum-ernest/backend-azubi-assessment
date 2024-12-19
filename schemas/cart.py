from pydantic import BaseModel
from schemas import ProductSchemaOut


class CartItemSchemaIn(BaseModel):
    quantity: int
    product_id: int


class CartItemSchemaOut(BaseModel):
    id: int
    quantity: int
    product_rel: ProductSchemaOut
