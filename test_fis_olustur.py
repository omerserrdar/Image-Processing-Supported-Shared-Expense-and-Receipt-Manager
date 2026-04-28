"""
TR: PROJE: OCR Çoklu Test Görseli Oluşturucu
    AÇIKLAMA: Sistemin farklı mağaza adı, tarih formatı ve tutar yapılarını 
              doğru ayıklayıp ayıklamadığını test etmek için 3 farklı fiş üretir.
EN: PROJECT: OCR Multiple Test Image Generator
    DESCRIPTION: Generates 3 different receipts to test if the system correctly 
                 extracts different store names, date formats, and amount structures.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def fis_uret(dosya_adi, magaza, detaylar, islemler, toplam_bilgi):
    """Genel bir fis tasarimi olusturur."""
    genislik, yukseklik = 450, 600
    resim = Image.new("RGB", (genislik, yukseklik), "white")
    cizici = ImageDraw.Draw(resim)
    
    # Fontlari bul (Hata almamak icin yalin fonta donuslu)
    try:
        f_baslik = ImageFont.truetype("arialbd.ttf", 26)
        f_normal = ImageFont.truetype("arial.ttf", 20)
        f_kucuk = ImageFont.truetype("arial.ttf", 16)
    except:
        f_baslik = f_normal = f_kucuk = ImageFont.load_default()

    y = 40
    # 1. Magaza Adi
    cizici.text((100, y), magaza, fill="black", font=f_baslik)
    y += 40
    
    # 2. Detaylar (Tarih, Fis No vb.)
    for d in detaylar:
        cizici.text((20, y), d, fill="black", font=f_kucuk)
        y += 22
    
    y += 10
    cizici.text((20, y), "-" * 40, fill="black", font=f_kucuk)
    y += 30
    
    # 3. Urunler
    for urun in islemler:
        cizici.text((20, y), urun, fill="black", font=f_normal)
        y += 30
    
    y += 10
    cizici.text((20, y), "-" * 40, fill="black", font=f_kucuk)
    y += 30
    
    # 4. Toplam Bilgisi
    for t in toplam_bilgi:
        cizici.text((20, y), t, fill="black", font=f_baslik if "TOPLAM" in t else f_normal)
        y += 35

    resim.save(dosya_adi)
    print(f"[OK] Fis olusturuldu: {dosya_adi}")

# --- TEST SENARYOLARI ---

def testleri_olustur():
    # 1. Senaryo: Standart Buyuk Market (Noktali Tarih)
    fis_uret(
        "fis_migros.png",
        "MIGROS JET",
        ["Tarih: 25.04.2026", "Saat: 10:20", "Fis No: 4455"],
        ["ELMA KG        1.5   45.50", "EKMEK          3     13.50", "PEYNIR         1     95.00"],
        ["TOPLAM:        154.00 TL", "KREDI KARTI    154.00 TL"]
    )

    # 2. Senaryo: Yerel Bakkal (Slasli Tarih ve Farkli Layout)
    fis_uret(
        "fis_bakkal.png",
        "OZCAN KARDESLER",
        ["Tarih: 12/05/2026", "Fis: 0098"],
        ["YUMURTA 10LU   1     40.00", "SUT 1L         2     50.00", "GAZETE         1     10.00"],
        ["ARA TOPLAM:    100.00", "KDV %1:          1.00", "TOPLAM:        101.00 TL"]
    )

    # 3. Senaryo: Cafe/Restoran (Tireli Tarih ve Semboller)
    fis_uret(
        "fis_cafe.png",
        "MOC CAFE",
        ["20-06-2026", "Sira No: 12", "Masa: 5"],
        ["LATTE         1    85.00", "BROWNIE       1    120.00"],
        ["TOPLAM TUTAR:  205.00 TL", "NAKIT:         250.00 TL", "PARA USTU:     45.00 TL"]
    )

if __name__ == "__main__":
    testleri_olustur()
