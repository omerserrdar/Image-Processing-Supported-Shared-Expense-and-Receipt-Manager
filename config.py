"""
TR: Uygulama yapılandırma modülü. .env dosyasından tüm ayarları yükler.
EN: Application configuration module. Loads all settings from .env file.
"""

import os
from dotenv import load_dotenv

# TR: Ortam degiskenlerini .env dosyasindan yukle
# EN: Load environment variables from .env
load_dotenv()


class Settings:
    """
    TR: Merkezi yapılandırma sınıfı — tek kaynak noktası (single source of truth).
    EN: Central configuration class — single source of truth for all settings.
    """

    # --- Application ---
    # TR: Uygulama kimligi ve temel parametreler
    # EN: App identity and core runtime parameters
    APP_NAME: str = "ReceiptShare"
    APP_VERSION: str = "2.0.0"
    APP_PORT: int = int(os.getenv("APP_PORT", "8080"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")

    # --- Gemini API ---
    # TR: Gemini Vision API baglantisi
    # EN: Gemini Vision API configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # --- MongoDB Atlas ---
    # TR: Veritabani baglanti ayarlari
    # EN: Database connection settings
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "receiptshare")

    # --- File Upload ---
    # TR: Dosya sistemi yollarini tek merkezde tanimla
    # EN: Centralized filesystem paths
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    BARCODE_DIR: str = os.path.join(BASE_DIR, "generated_barcodes")
    MAX_UPLOAD_SIZE_MB: int = 10

    # --- Warranty Defaults (months by category) ---
    # TR: Kategoriye gore varsayilan garanti sureleri (ay)
    # EN: Default warranty durations by category (months)
    WARRANTY_DEFAULTS: dict = {
        "Electronics": 24,
        "Clothing": 6,
        "Health": 12,
        "Market": 0,
        "Food": 0,
        "Travel": 0,
        "Education": 0,
        "Bills": 0,
        "Other": 0,
    }

    # --- Categories (with colors and icons) ---
    # TR: UI'da kullanilacak kategori tanimlari
    # EN: Category definitions used by the UI
    CATEGORIES: list = [
        {"key": "Market",      "color": "#10b981", "icon": "shopping_cart"},
        {"key": "Food",        "color": "#f43f5e", "icon": "restaurant"},
        {"key": "Electronics", "color": "#6366f1", "icon": "devices"},
        {"key": "Travel",      "color": "#f59e0b", "icon": "flight"},
        {"key": "Health",      "color": "#06b6d4", "icon": "local_hospital"},
        {"key": "Clothing",    "color": "#ec4899", "icon": "checkroom"},
        {"key": "Education",   "color": "#8b5cf6", "icon": "school"},
        {"key": "Bills",       "color": "#ef4444", "icon": "receipt"},
        {"key": "Other",       "color": "#94a3b8", "icon": "category"},
    ]


settings = Settings()

# TR: Uygulama dizinleri yoksa olustur
# EN: Create application directories if missing
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.BARCODE_DIR, exist_ok=True)
