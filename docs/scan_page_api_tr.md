# Fiş Tarama Sayfası (scan.py) Teknik Dokümantasyonu

Bu belge, "Görüntü İşleme Destekli Paylaşımlı Gider ve Fiş Yöneticisi" projesindeki `pages/scan.py` modülünün teknik uygulamasını ve iç mantığını açıklar.

## Genel Bakış
`scan.py` dosyası, NiceGUI framework'ü kullanılarak oluşturulmuş **Fiş Tarama Sayfası**'nı tanımlar. Temel amacı; kullanıcıların fiş görsellerini yüklemesine, Gemini destekli OCR servisi ile analiz etmesine, çıkarılan verileri inceleyip düzenlemesine ve sonuçları MongoDB veritabanına kaydetmesine olanak tanımaktır.

---

## Ana Bileşenler

### 1. `scan_page()`
Sayfanın giriş fonksiyonudur. UI düzenini kurar ve yüksek seviyeli state (durum) yönetimini yapar.

- **Amacı**: Tarama panelini, kullanıcı bağlamını (aile_id, kullanıcı_id) ve yükleme alanını başlatır.
- **İç Durum (State)**:
  - `analysis_result`: OCR'dan gelen JSON verisini (`data`) ve yüklenen dosyanın yerel yolunu (`image_path`) saklar.
- **Temel Mantık**:
  - Kullanıcının bir aileye bağlı olup olmadığını kontrol eder.
  - `ui.upload` bileşenini oluşturur.
  - Dosya yükleme işlemini yönetmek için `handle_upload(e)` fonksiyonunu tanımlar.

### 2. `_show_result(data, lang, family_id, user_id, user_name, image_path, container)`
Analiz sonuçlarını düzenlenebilir bir kart olarak ekrana yansıtan yardımcı (private) fonksiyondur.

- **Argümanlar**:
  - `data`: `ocr_service.analyze_receipt` tarafından döndürülen ham JSON verisi.
  - `lang`: Mevcut dil ayarı (i18n için).
  - `container`: Sonuçların render edileceği NiceGUI sütunu.
- **İşlevsellik**:
  - Önceki sonuçları temizler.
  - OCR verileriyle önceden doldurulmuş giriş alanları (Mağaza Adı, Tarih, Tutar, Kategori) oluşturur.
  - Ürün listesini ve çıkarılan barkodları listeler.
  - Garanti takibi seçeneklerini sunar.
  - Bu fişi mevcut eşleşmemiş fişlerle bağlamak için "Birleştir" (Merge) seçeneği sunar (örneğin; mağaza fişi ile POS slipini eşleştirmek).

---

## Teknik Akışlar

### A. Yükleme ve Analiz Akışı
1.  **Dosya Seçimi**: Kullanıcı `.png`, `.jpg` veya `.jpeg` dosyası seçer.
2.  **Kayıt**: `handle_upload` dosyayı benzersiz bir UUID ile `uploads/` dizinine kaydeder.
3.  **OCR Tetikleme**: `await ocr_service.analyze_receipt(filepath)` fonksiyonu çağrılır.
4.  **UI Güncelleme**: Analiz tamamlandığında, verileri göstermek için `_show_result` tetiklenir.

### B. Kaydetme Akışı
`_show_result` içindeki "Kaydet" butonu ile tetiklenir.

1.  **Normalizasyon**: UI girişlerini veritabanı uyumlu değerlere (`"store"` or `"pos"`) dönüştürür.
2.  **Garanti İşleme**: Eğer "Garanti Ekle" seçiliyse, fiş tarihi ve süresine göre bitiş tarihini hesaplar.
3.  **Barkod Görseli Üretimi**: Çıkarılan her barkod için `ocr_service.generate_barcode_image(bc)` çağrılarak görsel dosyası oluşturulur.
4.  **Veritabanı Kaydı**: Hazırlanan doküman `db_service.insert_receipt(doc)` ile kaydedilir.
5.  **Bağlama (Opsiyonel)**: Eğer birleştirme seçildiyse, iki fişi gruplandırmak için `db_service.link_receipts` çağrılır.

---

## Dış Bağımlılıklar ve Servisler
Modül şu dahili servisleri kullanır:

- **`services.db_service`**: Veritabanı kayıt ve sorgulama işlemleri.
- **`services.ocr_service`**: Gemini Vision API analizi ve barkod üretimi.
- **`config.settings`**: Klasör yolları ve dosya boyutu sınırları.
- **`theme.style.Theme`**: Tasarım tutarlılığı için stil değişkenleri.

---

## UI Etkileşimleri (NiceGUI)
- **`ui.upload`**: `auto_upload=True` ve belirli mime-türleri için yapılandırılmıştır.
- **`ui.bind_visibility_from`**: Garanti alanlarını ve birleştirme seçeneklerini onay kutularına göre dinamik olarak gösterip gizler.
- **`container.clear()`**: Birden fazla tarama yapıldığında görünümü sıfırlamak için kullanılır.
