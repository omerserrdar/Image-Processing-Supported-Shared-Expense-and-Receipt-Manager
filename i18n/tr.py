"""
TR: Türkçe çeviri sözlüğü.
EN: Turkish translation dictionary.
"""

translations = {
    # TR: Genel etiketler
    # EN: General labels
    "app_name": "ReceiptShare",
    "loading": "Yükleniyor...",
    "save": "Kaydet",
    "cancel": "İptal",
    "delete": "Sil",
    "edit": "Düzenle",
    "confirm": "Onayla",
    "back": "Geri",
    "search": "Ara",
    "filter": "Filtrele",
    "no_data": "Henüz veri yok",
    "success": "Başarılı",
    "error": "Hata",
    "currency": "₺",

    # TR: Kimlik dogrulama
    # EN: Authentication
    "login": "Giriş Yap",
    "register": "Kayıt Ol",
    "logout": "Çıkış Yap",
    "email": "E-posta",
    "password": "Şifre",
    "name": "Ad Soyad",
    "login_title": "Tekrar Hoş Geldin",
    "login_subtitle": "Aile fişlerinizi yönetmek için giriş yapın",
    "register_title": "Hesap Oluştur",
    "register_subtitle": "Aile harcamalarınızı takip etmeye başlayın",
    "no_account": "Hesabınız yok mu?",
    "have_account": "Zaten hesabınız var mı?",
    "login_success": "Tekrar hoş geldiniz!",
    "register_success": "Hesap başarıyla oluşturuldu!",
    "invalid_credentials": "Geçersiz e-posta veya şifre",
    "email_exists": "Bu e-posta zaten kayıtlı",

    # TR: Navigasyon
    # EN: Navigation
    "nav_dashboard": "Ana Panel",
    "nav_scan": "Fiş Tara",
    "nav_receipts": "Fişlerim",
    "nav_analytics": "Analitik",
    "nav_family": "Aile",
    "nav_warranty": "Garanti",
    "nav_settings": "Ayarlar",

    # TR: Ana panel
    # EN: Dashboard
    "dashboard_title": "Aile Özeti",
    "dashboard_subtitle": "Ailenizin harcamalarını bir bakışta takip edin",
    "total_spending": "Toplam Harcama",
    "avg_receipt": "Ort. Fiş",
    "total_receipts": "Toplam Fiş",
    "top_category": "En Çok Harcama",
    "this_month": "Bu Ay",
    "recent_receipts": "Son Fişler",
    "member_spending": "Üye Harcamaları",
    "budget_health": "Bütçe Durumu",

    # TR: Fis tarama
    # EN: Scan
    "scan_title": "Fiş Tara",
    "scan_subtitle": "Verileri otomatik çıkarmak için fiş görseli yükleyin",
    "upload_receipt": "Fiş Yükle",
    "drag_drop": "Sürükle & bırak veya tıklayın",
    "supported_formats": "Desteklenen: PNG, JPG, JPEG",
    "analyzing": "Fiş analiz ediliyor...",
    "analysis_complete": "Analiz tamamlandı!",
    "analysis_failed": "Analiz başarısız. Lütfen tekrar deneyin.",
    "store_name": "Mağaza Adı",
    "receipt_date": "Tarih",
    "total_amount": "Toplam Tutar",
    "category": "Kategori",
    "items": "Ürünler",
    "save_receipt": "Fişi Kaydet",
    "receipt_type": "Fiş Türü",
    "store_receipt": "Mağaza Fişi",
    "pos_receipt": "POS Fişi",
    "merge_with": "Mevcut Fişle Birleştir",
    "select_receipt_to_merge": "Birleştirilecek fişi seçin",
    "merge_success": "Fişler başarıyla birleştirildi!",
    "add_warranty": "Garanti Ekle",
    "warranty_months": "Garanti Süresi (ay)",
    "product_name": "Ürün Adı",
    "add_barcode": "Barkod Ekle",

    # TR: Fis gecmisi
    # EN: Receipts
    "receipts_title": "Fiş Geçmişi",
    "receipts_subtitle": "Tüm aile fişlerini inceleyin ve yönetin",
    "add_receipt": "Fiş Ekle",
    "date": "Tarih",
    "store": "Mağaza",
    "amount": "Tutar",
    "actions": "İşlemler",
    "view_details": "Detayları Gör",
    "delete_receipt": "Fişi Sil",
    "receipt_deleted": "Fiş silindi",
    "linked_receipt": "Bağlı Fiş",
    "uploaded_by": "Yükleyen",

    # TR: Analitik
    # EN: Analytics
    "analytics_title": "Analitik",
    "analytics_subtitle": "Aile harcamalarınız hakkında derin içgörüler",
    "spending_trend": "Harcama Trendi",
    "category_distribution": "Kategori Dağılımı",
    "member_comparison": "Üye Karşılaştırması",
    "daily": "Günlük",
    "weekly": "Haftalık",
    "monthly": "Aylık",

    # TR: Aile
    # EN: Family
    "family_title": "Aile Yönetimi",
    "family_subtitle": "Aile grubunuzu ve üyelerinizi yönetin",
    "create_family": "Aile Oluştur",
    "join_family": "Aileye Katıl",
    "family_name": "Aile Adı",
    "invite_code": "Davet Kodu",
    "enter_invite_code": "Davet kodunu girin",
    "generate_code": "Kod Oluştur",
    "temporary_code": "Geçici Kod (24 saat)",
    "permanent_code": "Kalıcı Kod",
    "copy_code": "Kodu Kopyala",
    "code_copied": "Kod panoya kopyalandı!",
    "members": "Üyeler",
    "admin": "Yönetici",
    "member": "Üye",
    "remove_member": "Üyeyi Çıkar",
    "leave_family": "Aileden Ayrıl",
    "monthly_budget": "Aylık Bütçe",
    "set_budget": "Bütçe Belirle",
    "no_family": "Henüz bir aileye dahil değilsiniz",
    "family_created": "Aile oluşturuldu!",
    "joined_family": "Aileye katıldınız!",
    "invalid_code": "Geçersiz davet kodu",

    # TR: Garanti
    # EN: Warranty
    "warranty_title": "Garanti Takibi",
    "warranty_subtitle": "Garanti talepleri için fişlerinizi kaybetmeyin",
    "active_warranties": "Aktif Garantiler",
    "expired_warranties": "Süresi Dolmuş",
    "expiring_soon": "Yakında Dolacak",
    "days_remaining": "gün kaldı",
    "show_barcode": "Barkodu Göster",
    "barcode": "Barkod",
    "warranty_expired": "Garanti Süresi Doldu",

    # TR: Kategoriler
    # EN: Categories
    "cat_Market": "Market",
    "cat_Food": "Yemek",
    "cat_Electronics": "Elektronik",
    "cat_Travel": "Seyahat",
    "cat_Health": "Sağlık",
    "cat_Clothing": "Giyim",
    "cat_Education": "Eğitim",
    "cat_Bills": "Faturalar",
    "cat_Other": "Diğer",

    # TR: Ayarlar
    # EN: Settings
    "settings_title": "Ayarlar",
    "language": "Dil",
    "language_en": "English",
    "language_tr": "Türkçe",
}
