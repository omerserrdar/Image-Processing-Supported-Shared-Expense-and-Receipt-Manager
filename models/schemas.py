"""
TR: Pydantic veri modelleri — tüm veri yapıları burada tanımlanır.
EN: Pydantic data models — all data structures are defined here.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# TR: Pydantic modelleri API/servisler arasi veri sozlesmesini tanimlar
# EN: Pydantic models define data contracts across API/services


# ──────────────────────────────────────────────
#  AUTH MODELS
# ──────────────────────────────────────────────

class UserRegister(BaseModel):
    """TR: Kayıt formu modeli | EN: Registration form model"""
    # TR: Kullanici kayit formu alanlari
    # EN: Registration form fields
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=150)
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    """TR: Giriş formu modeli | EN: Login form model"""
    # TR: Login form alanlari
    # EN: Login form fields
    email: str
    password: str


# ──────────────────────────────────────────────
#  RECEIPT MODELS (Gemini Structured Output)
# ──────────────────────────────────────────────

class ReceiptItem(BaseModel):
    """TR: Fiş üzerindeki tek bir ürün satırı | EN: A single item line on the receipt"""
    # TR: Urun satiri alanlari
    # EN: Item line fields
    name: str = Field(description="Product name")
    quantity: float = Field(default=1.0, description="Quantity purchased")
    price: float = Field(description="Line total price in TRY")


class ReceiptExtraction(BaseModel):
    """
    TR: Gemini Vision API'den dönen yapılandırılmış fiş verisi.
    EN: Structured receipt data returned from Gemini Vision API.
    """
    # TR: Gemini structured output alanlari
    # EN: Gemini structured output fields
    store_name: str = Field(description="Store or merchant name")
    date: str = Field(description="Receipt date in YYYY-MM-DD format")
    total_amount: float = Field(description="Total amount in TRY")
    category: str = Field(
        default="Other",
        description="One of: Market, Food, Electronics, Travel, Health, Clothing, Education, Bills, Other"
    )
    items: list[ReceiptItem] = Field(
        default_factory=list,
        description="List of purchased items"
    )
    barcodes: list[str] = Field(
        default_factory=list,
        description="All barcode numbers found on the receipt"
    )
    has_warranty: bool = Field(
        default=False,
        description="Whether any item on the receipt might have a warranty"
    )


# ──────────────────────────────────────────────
#  FAMILY MODELS
# ──────────────────────────────────────────────

class FamilyCreate(BaseModel):
    """TR: Yeni aile grubu oluşturma modeli | EN: New family group creation model"""
    # TR: Aile olusturma formu alanlari
    # EN: Family creation form fields
    name: str = Field(..., min_length=2, max_length=100)


class FamilyMember(BaseModel):
    """TR: Aile üye bilgisi | EN: Family member info"""
    # TR: Uye bilgisi alanlari
    # EN: Member fields
    user_id: str
    name: str
    role: str = "member"  # "admin" or "member"
    joined_at: datetime = Field(default_factory=datetime.utcnow)


# ──────────────────────────────────────────────
#  WARRANTY MODEL
# ──────────────────────────────────────────────

class WarrantyInfo(BaseModel):
    """TR: Garanti bilgisi | EN: Warranty information"""
    # TR: Garanti alanlari
    # EN: Warranty fields
    has_warranty: bool = False
    warranty_months: int = 0
    expiry_date: Optional[str] = None
    product_name: Optional[str] = None
