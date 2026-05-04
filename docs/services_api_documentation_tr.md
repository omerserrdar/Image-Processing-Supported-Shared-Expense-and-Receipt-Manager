# Servisler (API) Teknik Dokümantasyonu

Bu belge, "Görüntü İşleme Destekli Paylaşımlı Gider ve Fiş Yöneticisi" projesinde kullanılan dahili servislerin teknik detaylarını içerir.

---

## 1. Veritabanı Servisi (`services/db_service.py`)
Kullanıcı yönetimi, aile grupları, fiş kayıtları ve analitik hesaplamalar dahil olmak üzere tüm MongoDB etkileşimlerini yönetir.

### Kullanıcı Yönetimi
- **`create_user(name, email, password_hash) -> str`**: Yeni bir kullanıcı oluşturur ve `user_id` döndürür.
- **`find_user_by_email(email) -> dict`**: E-posta adresine göre kullanıcı dökümanını bulur.
- **`find_user_by_id(user_id) -> dict`**: ID'ye göre kullanıcı dökümanını bulur.
- **`update_user_family(user_id, family_id, role)`**: Kullanıcıyı bir aile grubuna bağlar.

### Aile Yönetimi
- **`create_family(name, creator_id, creator_name) -> dict`**: Yeni bir aile grubu başlatır.
- **`generate_invite_code(family_id, permanent=False) -> str`**: Aileye katılmak için davet kodu oluşturur.
- **`add_member_to_family(family_id, user_id, user_name)`**: Var olan bir aileye yeni üye ekler.
- **`update_family_budget(family_id, budget)`**: Aylık harcama limitini belirler.

### Fiş Yönetimi
- **`insert_receipt(data) -> str`**: Bir fiş dökümanını kaydeder.
- **`get_receipts_by_family(family_id, limit=100) -> list`**: Bir ailenin son harcamalarını getirir.
- **`link_receipts(rid1, rid2, group_id)`**: İki fişi gruplandırır (örneğin; market fişi + POS slipi).
- **`get_unlinked_receipts(family_id, limit=20)`**: Henüz bir gruba dahil edilmemiş fişleri bulur.

### Analiz (Pandas Tabanlı)
- **`get_family_summary(family_id, year, month)`**: Toplam harcama, ortalama ve en çok harcanan kategoriyi döndürür.
- **`get_category_distribution(family_id, year, month)`**: Harcamaların kategori bazlı dağılımını verir.
- **`get_member_spending(family_id, year, month)`**: Aile üyelerinin kişi başı harcamalarını verir.
- **`get_daily_spending(family_id, year, month)`**: Ay içindeki günlük harcama grafiği verilerini sağlar.

---

## 2. OCR Servisi (`services/ocr_service.py`)
Akıllı veri çıkarma ve barkod üretimi için Google Gemini Vision API'yi kullanır.

### Temel Fonksiyonlar
- **`async analyze_receipt(image_path) -> dict`**: 
  - **Açıklama**: Fiş analizinin ana giriş noktasıdır.
  - **Mantık**: Kullanıcı arayüzünün donmaması için ağır API çağrısını arka plan iş parçacığında (thread) çalıştırır.
  - **Çıktı**: Mağaza adı, tarih, toplam tutar, kategori, ürün listesi, barkodlar ve garanti durumu bilgilerini içeren yapılandırılmış bir JSON döner.

- **`generate_barcode_image(barcode_number, format="code128") -> str`**:
  - **Açıklama**: Metin tabanlı bir barkod veya seri numarasını taranabilir bir görsele dönüştürür.
  - **Formatlar**: `ean13`, `ean8` ve `code128` formatlarını destekler.
  - **Dönüş**: Oluşturulan `.png` barkod görselinin dosya yolunu döndürür.

### AI Prompt Mantığı
Servis, Gemini'ye şu verileri araması talimatını veren özel bir `RECEIPT_PROMPT` kullanır:
- Mağaza detayları ve tarihler.
- Ayrıntılı ürün listeleri.
- **Seri numaraları ve IMEI** (garanti belgeleri için kritik).
- Garanti durumu bayrakları.

---

## 3. Entegrasyon Örneği (`scan.py` kullanımı)

```python
from services import ocr_service, db_service

# 1. Görseli analiz et
data = await ocr_service.analyze_receipt(filepath)

# 2. (Opsiyonel) Çıkarılan barkodlar için görsel üret
for bc in data['barcodes']:
    ocr_service.generate_barcode_image(bc)

# 3. Veritabanına kaydet
receipt_id = db_service.insert_receipt(doc)
```
