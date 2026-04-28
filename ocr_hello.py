"""
PROJE: Market Fisi OCR Sistemi (Full Pipeline)
ACIKLAMA: OpenCV -> PaddleOCR (predict) -> ReceiptParser (metadata)
"""

import sys
import cv2
from paddleocr import PaddleOCR
from receipt_parser import ReceiptParser

# ── YAPILANDIRMA ──────────────────────────────────────────────────────────
# enable_mkldnn=False: CPU optimizasyon hatasini kapatir.
_ocr_engine = PaddleOCR(use_textline_orientation=True, lang="tr", enable_mkldnn=False)
_parser = ReceiptParser()

def analyze_receipt(image_path: str):
    # 1. OpenCV ile goruntuyu oku
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Goruntu okunamadi: {image_path}")

    # 2. PaddleOCR ile tahmin yap (Yeni API: predict)
    # Bu metod dt_polys (koordinatlar) ve rec_texts (metinler) dondurur.
    prediction = _ocr_engine.predict(img)

    # 3. Parser ile anlamli verileri ayikla
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
        
        # BULUNAN VERI OZETI
        print(f"MAGAZA ADI   : {sonuc['store_name']}")
        print(f"TARIH        : {sonuc['date']}")
        print(f"TOPLAM TUTAR : {sonuc['total_amount']:.2f} TL")
        print("-" * 50)
        
        # TUM SATIRLAR (Siralanmis ve birlestirilmis)
        print("FIS ICERIGI (BIRLESTIRILMIS):")
        for i, satir in enumerate(sonuc['raw_lines'], 1):
            print(f" {i:02d} | {satir}")
        
        print("-" * 50)
        print("[OK] Analiz tamamlandi.")

    except Exception as e:
        print(f"\n[HATA] Bir sorun olustu: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
