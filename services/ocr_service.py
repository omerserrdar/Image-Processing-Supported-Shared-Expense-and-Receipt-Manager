"""
TR: Gemini Vision API servisi — fiş görselinden veri ve barkod çıkarımı.
EN: Gemini Vision API service — data and barcode extraction from receipt images.
"""

import asyncio
import base64
import json
import os
from datetime import datetime, timedelta

from config import settings
from models.schemas import ReceiptExtraction

# TR: OCR/AI servisinin amaci, goruntuyu yapilandirilmis veriye cevirmektir
# EN: The OCR/AI service converts images into structured receipt data

# TR: Gemini API istemcisi | EN: Gemini API client
_client = None


def _get_client():
    """TR: Gemini istemcisini lazy initialization ile döndürür | EN: Returns Gemini client with lazy init"""
    global _client
    if _client is None:
        # TR: Gemini istemcisini ilk kullanmada olustur
        # EN: Create the Gemini client on first use
        from google import genai
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


# TR: Fiş analiz prompt'u | EN: Receipt analysis prompt
RECEIPT_PROMPT = """Analyze this document carefully. It may be a shopping receipt, an invoice, or a warranty certificate ("Garanti Belgesi"). Extract the following information and return it as JSON:

1. store_name: The store, merchant, or brand name (look at the top or logo)
2. date: The date in YYYY-MM-DD format. If the format is DD.MM.YYYY, convert it. If missing, use today's date.
3. total_amount: The total amount as a number (in Turkish Lira / TRY). If it's a warranty certificate without a price, use 0.
4. category: Classify into exactly one of these categories: Market, Food, Electronics, Travel, Health, Clothing, Education, Bills, Other. If it's a warranty certificate, it is likely Electronics or Other.
5. items: List of purchased items, each with name, quantity (default 1.0), and price. If it's a warranty certificate, list the product name as the item.
6. barcodes: ALL barcode numbers, serial numbers (S/N), or IMEI numbers visible on the document. Warranty certificates ALWAYS have serial numbers or barcodes. Look extremely carefully! Extract the exact alphanumeric text under or near the barcode.
7. has_warranty: MUST be true if the document is a warranty certificate ("Garanti Belgesi"), warranty card, or if any item might have a warranty.

IMPORTANT:
- For amounts, use the numeric value only (e.g., 154.00 not "154,00 TL")
- If you cannot find a field, use reasonable defaults.
- Extract ALL visible barcodes, IMEI, and serial numbers as strings (including alphanumeric ones). Do not miss them!
- Be thorough with item extraction.
"""


def _analyze_receipt_sync(image_path: str) -> dict:
    """
    TR: Fiş görselini Gemini Vision API ile senkron analiz eder (thread içinde çalışır).
    EN: Synchronously analyzes a receipt image using Gemini Vision API (runs inside thread).
    """
    # TR: API istemcisini hazirla
    # EN: Initialize API client
    client = _get_client()

    # TR: Gorsel dosyasini belleğe al
    # EN: Load image bytes into memory
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # TR: Dosya uzantisindan MIME turunu belirle
    # EN: Resolve MIME type from file extension
    ext = os.path.splitext(image_path)[1].lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
    mime_type = mime_map.get(ext, "image/jpeg")

    from google.genai import types

    # TR: Gemini'den JSON schema'ya uygun yapi bekle
    # EN: Request structured JSON output based on schema
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            RECEIPT_PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ReceiptExtraction,
            temperature=0.1,  # TR: Düşük sıcaklık = deterministik | EN: Low temp = deterministic
        ),
    )

    # TR: JSON yanitini parse et, hata olursa varsayilanlari kullan
    # EN: Parse JSON response, fall back to defaults on error
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError:
        data = {
            "store_name": "Unknown",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_amount": 0.0,
            "category": "Other",
            "items": [],
            "barcodes": [],
            "has_warranty": False,
        }

    # TR: Garanti varsa kategoriye gore varsayilan sureyi ekle
    # EN: If warranty exists, enrich with category defaults
    if data.get("has_warranty"):
        cat = data.get("category", "Other")
        default_months = settings.WARRANTY_DEFAULTS.get(cat, 0)
        if default_months > 0:
            try:
                # TR: Fis tarihinden garanti bitis tarihini hesapla
                # EN: Compute warranty expiry date from receipt date
                receipt_date = datetime.strptime(data["date"], "%Y-%m-%d")
                expiry = receipt_date + timedelta(days=default_months * 30)
                data["warranty_months"] = default_months
                data["warranty_expiry"] = expiry.strftime("%Y-%m-%d")
            except ValueError:
                # TR: Tarih formati bozuksa sadece sureyi ayarla
                # EN: If date parsing fails, keep duration without expiry
                data["warranty_months"] = default_months
                data["warranty_expiry"] = None

    return data


async def analyze_receipt(image_path: str) -> dict:
    """
    TR: Fiş görselini Gemini Vision API ile asenkron analiz eder.
        Ağır API çağrısını ayrı thread'e taşır, event loop bloke olmaz.
    EN: Asynchronously analyzes a receipt image using Gemini Vision API.
        Offloads heavy API call to a thread pool so the event loop stays responsive.
    """
    # TR: Agir API cagrisi icin thread pool'a tasima
    # EN: Offload heavy API call to a background thread
    return await asyncio.to_thread(_analyze_receipt_sync, image_path)


def generate_barcode_image(barcode_number: str, barcode_format: str = "code128") -> str | None:
    """
    TR: Barkod numarasından taratılabilir barkod görseli oluşturur.
    EN: Generates a scannable barcode image from a barcode number.

    Args:
        barcode_number: Barkod numarası | Barcode number string
        barcode_format: Barkod formatı (code128, ean13, vb.) | Barcode format

    Returns:
        Oluşturulan dosyanın yolu | Path to the generated file
    """
    try:
        import barcode
        from barcode.writer import ImageWriter

        # TR: Barkod gorseli kayit klasorunu garanti altina al
        # EN: Ensure barcode output directory exists
        os.makedirs(settings.BARCODE_DIR, exist_ok=True)

        # TR: Barkod numarasini normalize et
        # EN: Normalize barcode number input
        clean_number = barcode_number.strip()

        # TR: EAN-13 formatı için kontrol (13 haneli sayısal)
        # EN: Check for EAN-13 format (13-digit numeric)
        if clean_number.isdigit() and len(clean_number) == 13:
            barcode_class = barcode.get_barcode_class("ean13")
        elif clean_number.isdigit() and len(clean_number) == 8:
            barcode_class = barcode.get_barcode_class("ean8")
        else:
            barcode_class = barcode.get_barcode_class("code128")

        # TR: Barkodu olustur ve dosyaya kaydet
        # EN: Generate barcode and persist to file
        bc = barcode_class(clean_number, writer=ImageWriter())
        filename = f"barcode_{clean_number}"
        filepath = os.path.join(settings.BARCODE_DIR, filename)
        saved_path = bc.save(filepath)

        return saved_path

    except Exception as e:
        # TR: Barkod uretimi hatasini logla ve None dondur
        # EN: Log barcode generation error and return None
        print(f"Barcode generation error: {e}")
        return None
