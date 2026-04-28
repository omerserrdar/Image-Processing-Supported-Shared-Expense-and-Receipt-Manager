"""
TR: PROJE: Market Fişi OCR Sistemi (Full Pipeline)
    AÇIKLAMA: OpenCV -> PaddleOCR (predict) -> ReceiptParser (metadata)
EN: PROJECT: Grocery Receipt OCR System (Full Pipeline)
    DESCRIPTION: OpenCV -> PaddleOCR (predict) -> ReceiptParser (metadata)
"""

import sys
import cv2
from paddleocr import PaddleOCR
from receipt_parser import ReceiptParser

# ── YAPILANDIRMA | CONFIGURATION ─────────────────────────────────────────
# TR: enable_mkldnn=False: CPU optimizasyon hatasını kapatır.
# EN: enable_mkldnn=False: Disables CPU optimization to prevent potential errors.
_ocr_engine = PaddleOCR(use_textline_orientation=True, lang="tr", enable_mkldnn=False)
_parser = ReceiptParser()

def analyze_receipt(image_path: str):
    # TR: 1. OpenCV ile görüntüyü oku
    # EN: 1. Read the image using OpenCV
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Goruntu okunamadi: {image_path}")

    # TR: 2. PaddleOCR ile tahmin yap (Yeni API: predict)
    # TR: Bu metod dt_polys (koordinatlar) ve rec_texts (metinler) döndürür.
    # EN: 2. Make prediction using PaddleOCR (New API: predict)
    # EN: This method returns dt_polys (coordinates) and rec_texts (texts).
    prediction = _ocr_engine.predict(img)

    # TR: 3. Parser (Ayrıştırıcı) ile anlamlı verileri (tarih, toplam vb.) ayıkla
    # EN: 3. Extract meaningful data (date, total etc.) using the Parser
    data = _parser.parse(prediction)
    return data

def main():
    if len(sys.argv) < 2:
        print("\n[!] Kullanım: python ocr_hello.py <dosya_adi>")
        sys.exit(1)

    dosya = sys.argv[1]
    
    try:
        print(f"\n[*] Fiş Analiz Ediliyor: {dosya}")
        print("-" * 50)
        
        sonuc = analyze_receipt(dosya)
        
        # TR: BULUNAN VERİ ÖZETİ
        # EN: FOUND DATA SUMMARY
        print(f"MAGAZA ADI   : {sonuc['store_name']}")
        print(f"TARIH        : {sonuc['date']}")
        print(f"TOPLAM TUTAR : {sonuc['total_amount']:.2f} TL")
        print("-" * 50)
        
        # TR: TÜM SATIRLAR (Sıralanmış ve birleştirilmiş orijinal içerik)
        # EN: ALL LINES (Sorted and merged original content)
        print("FIS ICERIGI (BIRLESTIRILMIS) | RECEIPT CONTENT (MERGED):")
        for i, satir in enumerate(sonuc['raw_lines'], 1):
            print(f" {i:02d} | {satir}")
        
        print("-" * 50)
        print("[OK] Analiz tamamlandi.")

    except Exception as e:
        print(f"\n[HATA] Bir sorun olustu: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
