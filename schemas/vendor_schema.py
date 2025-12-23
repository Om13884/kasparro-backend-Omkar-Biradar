from pydantic import BaseModel, Field, field_validator


class VendorProduct(BaseModel):
    vendor_id: str
    product_name: str
    group: str
    amount: float

    @field_validator("product_name")
    @classmethod
    def name_required(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("product_name required")
        return v

    @field_validator("group")
    @classmethod
    def normalize_group(cls, v: str) -> str:
        return v.lower()

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("amount must be positive")
        return v
