from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CSVProduct(BaseModel):
    product_id: int
    name: str
    category: str
    price: float

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: str) -> str:
        return v.lower()

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be positive")
        return v

