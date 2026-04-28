"""
ReceiptShare Web - Analytics Overview Uygulaması (Flet 0.21.0+ Uyumlu)
Bu dosya, uygulamanın ana arayüzünü, navigasyon mantığını ve OCR entegrasyonunu içerir.
"""

import flet as ft
from style_tokens import Style  # Tasarım tokenlarını içeri aktar
import os
import sys

# Proje ana dizinine erişim sağlayarak arka plan modüllerini (parser vb.) yükle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from receipt_parser import ReceiptParser
from paddleocr import PaddleOCR

# --- GLOBAL NESNELER ---
# OCR Motorunu (PaddleOCR) ve Veri Ayrıştırıcıyı (ReceiptParser) bir kez başlat
# use_textline_orientation: Metin yönünü otomatik algılar, lang: Türkçe desteği
ocr_engine = PaddleOCR(use_textline_orientation=True, lang="tr", enable_mkldnn=False)
receipt_parser = ReceiptParser()


def main(page: ft.Page):
    """Flet Uygulamasının Ana Giriş Fonksiyonu"""
    
    # Sayfa genel ayarları (Başlık, Tema ve Pencere Boyutu)
    page.title = "ReceiptShare Web - Analytics Overview"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = Style.BG
    page.window_width = 1400
    page.window_height = 900
    page.padding = 0
    page.spacing = 0

    # --- DURUM YÖNETİMİ (NAVİGASYON) ---
    def route_change(view_name):
        """Menü tıklandığında ekrandaki içeriği değiştiren fonksiyon"""
        if view_name in views:
            # Ana içerik alanını seçilen görünüme güncelle
            content_area.content = views[view_name]
            
            # Sidebar'daki aktif menü öğesinin görsel durumunu güncelle (renk, kenarlık vb.)
            for item in sidebar_items.controls:
                if isinstance(item, ft.Container) and hasattr(item, "data"):
                    is_selected = item.data == view_name
                    # Seçili ise vurgula, değilse normal görünüme döndür
                    item.bgcolor = ft.colors.with_opacity(0.1, Style.PRIMARY) if is_selected else None
                    item.border = ft.Border(right=ft.BorderSide(4, Style.PRIMARY)) if is_selected else None
                    row = item.content
                    row.controls[0].color = Style.PRIMARY if is_selected else Style.OUTLINE
                    row.controls[1].color = Style.PRIMARY if is_selected else Style.OUTLINE
            page.update()

    # --- UI BİLEŞENLERİ (CUSTOM COMPONENTS) ---

    def KPICard(label, value, trend=None, is_up=True, neon_color=None):
        """Üst kısımdaki özet bilgi kartlarını (Toplam Harcama vb.) oluşturan bileşen"""
        shadows = []
        if neon_color:
            # Kartın altına hafif bir neon parlama efekti ekle
            shadows.append(ft.BoxShadow(blur_radius=20, color=ft.colors.with_opacity(0.15, neon_color), spread_radius=1))
        
        return ft.Container(
            **Style.GLASS_STYLE, # Glassmorphism stilini uygula
            expand=True, padding=24, border_radius=24, shadow=shadows,
            content=ft.Column([
                ft.Text(label.upper(), size=10, color=Style.OUTLINE, weight=ft.FontWeight.W_800),
                ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Row([
                    # Trend yönüne göre ikon ve renk ayarla (Yeşil/Kırmızı)
                    ft.Icon(ft.icons.TRENDING_UP if is_up else ft.icons.TRENDING_DOWN, 
                            color=Style.SECONDARY if is_up else ft.colors.ERROR, size=16),
                    ft.Text(trend, size=12, color=Style.SECONDARY if is_up else ft.colors.ERROR, weight=ft.FontWeight.W_600)
                ]) if trend else ft.Container()
            ], spacing=5)
        )

    def InsightCard(title, desc, icon, border_color):
        """AI Öngörüleri ve Bilgi kartlarını oluşturan bileşen"""
        return ft.Container(
            bgcolor=ft.colors.with_opacity(0.03, "white"),
            blur=10,
            expand=True, padding=24, border_radius=24,
            border=ft.Border(
                left=ft.BorderSide(4, border_color),
                top=ft.BorderSide(1, ft.colors.with_opacity(0.1, "white")),
                right=ft.BorderSide(1, ft.colors.with_opacity(0.05, "white")),
                bottom=ft.BorderSide(1, ft.colors.with_opacity(0.05, "white"))
            ),
            content=ft.Column([
                ft.Row([
                    # İkon kutusu
                    ft.Container(content=ft.Icon(icon, color=border_color, size=20), bgcolor=ft.colors.with_opacity(0.1, border_color), padding=10, border_radius=10),
                    # Etiket
                    ft.Container(content=ft.Text("YÜKSEK ETKİ", size=9, weight=ft.FontWeight.BOLD), bgcolor=ft.colors.with_opacity(0.05, "white"), padding=ft.Padding(8, 4, 8, 4), border_radius=5)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                ft.Text(desc, size=13, color=Style.OUTLINE, max_lines=3)
            ], spacing=10)
        )

    def ContributorItem(name, role, amount, receipts, progress, color):
        """Ekip harcamaları listesindeki kişi satırını oluşturan bileşen"""
        return ft.Column([
            ft.Row([
                ft.Row([
                    # Profil Avatarı
                    ft.CircleAvatar(radius=18, bgcolor=ft.colors.with_opacity(0.1, color), content=ft.Icon(ft.icons.PERSON, color=color)),
                    ft.Column([
                        ft.Text(name, size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(role.upper(), size=9, color=Style.OUTLINE, weight=ft.FontWeight.W_600)
                    ], spacing=0)
                ]),
                ft.Column([
                    ft.Text(amount, size=14, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT),
                    ft.Text(f"{receipts} FİŞ", size=9, color=Style.SECONDARY, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT)
                ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=0)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            # Harcama limitine göre doluluk çubuğu
            ft.ProgressBar(value=progress, color=color, bgcolor=ft.colors.with_opacity(0.05, "white"), height=6, border_radius=10)
        ], spacing=10)

    # --- EKRAN GÖRÜNÜMLERİ (VIEWS) ---

    # 1. Analytics Görünümü (Detaylı Harcama Analizi)
    analytics_view = ft.ListView([
        # Başlık Bölümü
        ft.Row([
            ft.Column([
                ft.Text("Analytics Overview", size=28, weight=ft.FontWeight.W_800),
                ft.Text("Kurumsal harcama verilerinizin derinlemesine analizi.", color=Style.OUTLINE)
            ]),
            # Zaman Filtresi Seçici (Simüle edilmiş)
            ft.Container(
                bgcolor=Style.SURFACE, padding=5, border_radius=12, border=ft.border.all(1, ft.colors.with_opacity(0.1, "white")),
                content=ft.Row([
                    ft.Container(content=ft.Text("Son 30 Gün", size=11, weight=ft.FontWeight.BOLD), bgcolor=ft.colors.with_opacity(0.1, Style.PRIMARY), padding=ft.Padding(16, 8, 16, 8), border_radius=8),
                    ft.TextButton("Çeyrek", style=ft.ButtonStyle(color=Style.OUTLINE)),
                    ft.TextButton("Yıllık", style=ft.ButtonStyle(color=Style.OUTLINE)),
                ], spacing=0)
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        # Üst Metrik Kartları
        ft.Row([
            KPICard("Toplam Harcama", "$24,850.40", "geçen aya göre %12 artış", True, Style.PRIMARY),
            KPICard("Ort. Fiş Tutarı", "$142.12", "geçen aya göre %4 azalış", False),
            KPICard("Tarama Sayısı", "1,204", "%99.2 Doğruluk", True),
            KPICard("En Popüler Kategori", "SaaS", "Toplam harcamanın %32'si", True, Style.SECONDARY),
        ], spacing=25),

        # Grafikler Bölümü
        ft.Row([
            # Harcama Trend Grafiği (Bar Chart Simülasyonu)
            ft.Container(
                **Style.GLASS_STYLE, expand=2, padding=32, border_radius=32,
                content=ft.Column([
                    ft.Row([
                        ft.Text("Harcama Trendleri", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Row([ft.Container(width=10, height=10, border_radius=5, bgcolor=Style.PRIMARY), ft.Text("KURUMSAL", size=10, color=Style.OUTLINE)], spacing=5),
                            ft.Row([ft.Container(width=10, height=10, border_radius=5, bgcolor=Style.SECONDARY), ft.Text("BULUT", size=10, color=Style.OUTLINE)], spacing=5),
                        ], spacing=15)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(
                        height=250, padding=ft.Padding(0, 20, 0, 0),
                        content=ft.Row([
                            ft.Column([ft.Container(width=30, height=150, bgcolor=Style.PRIMARY, border_radius=5), ft.Text("H1", size=10)], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.Column([ft.Container(width=30, height=200, bgcolor=Style.SECONDARY, border_radius=5), ft.Text("H2", size=10)], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.Column([ft.Container(width=30, height=120, bgcolor=Style.PRIMARY, border_radius=5), ft.Text("H3", size=10)], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.Column([ft.Container(width=30, height=180, bgcolor=Style.SECONDARY, border_radius=5), ft.Text("H4", size=10)], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.Column([ft.Container(width=30, height=220, bgcolor=Style.PRIMARY, border_radius=5), ft.Text("H5", size=10)], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ], alignment=ft.MainAxisAlignment.SPACE_AROUND, expand=True)
                    )
                ])
            ),
            # Bütçe Sağlığı Bölümü
            ft.Container(
                **Style.GLASS_STYLE, expand=1, padding=32, border_radius=32,
                content=ft.Column([
                    ft.Text("Bütçe Sağlığı", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Toplam aylık limit: $30,000", size=12, color=Style.OUTLINE),
                    ft.Container(height=20),
                    ft.Row([
                        ft.Container(content=ft.Text("KULLANIM", size=10, weight=ft.FontWeight.BOLD, color=Style.SECONDARY), bgcolor=ft.colors.with_opacity(0.1, Style.SECONDARY), padding=ft.Padding(8, 4, 8, 4), border_radius=5),
                        ft.Text("%82", weight=ft.FontWeight.BOLD, color=Style.SECONDARY)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.ProgressBar(value=0.82, color=Style.SECONDARY, bgcolor=ft.colors.with_opacity(0.05, "white"), height=10, border_radius=10),
                    ft.Row([
                        ft.Container(expand=True, bgcolor=ft.colors.with_opacity(0.05, "white"), padding=16, border_radius=15, content=ft.Column([ft.Text("KALAN", size=9, color=Style.OUTLINE), ft.Text("$5,149", weight=ft.FontWeight.BOLD)])),
                        ft.Container(expand=True, bgcolor=ft.colors.with_opacity(0.05, "white"), padding=16, border_radius=15, content=ft.Column([ft.Text("KALAN GÜN", size=9, color=Style.OUTLINE), ft.Text("12", weight=ft.FontWeight.BOLD)])),
                    ], spacing=15),
                    ft.ElevatedButton("Limitleri Düzenle", bgcolor=Style.PRIMARY, color=Style.BG)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        ], spacing=25),

        # AI Öngörüleri Bölümü
        ft.Column([
            ft.Row([ft.Icon(ft.icons.AUTO_AWESOME, color=Style.PRIMARY), ft.Text("AI Finansal Öngörüler", size=18, weight=ft.FontWeight.BOLD)], spacing=10),
            ft.Row([
                InsightCard("Lisans Çakışması", "Ekipler arasında mükerrer Adobe lisansı tespit edildi. Tasarruf: $140/ay.", ft.icons.REPEAT, Style.PRIMARY),
                InsightCard("Yemek Harcaması", "Eğlence ve yemek giderleri geçen yıla göre %18 daha yüksek.", ft.icons.TRENDING_UP, Style.SECONDARY),
                InsightCard("Vergi Avantajı", "12 fiş Teknoloji Kredisi kapsamına giriyor. İşaretlensin mi?", ft.icons.ACCOUNT_BALANCE_WALLET, Style.PRIMARY),
            ], spacing=25)
        ], spacing=15),

        # Alt Bilgi Bölümü
        ft.Row([
            # Kategorik Dağılım
            ft.Container(
                **Style.GLASS_STYLE, expand=1, padding=32, border_radius=32,
                content=ft.Column([
                    ft.Text("Kategorik Dağılım", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    ft.Column([
                        ft.Row([ft.Text("SaaS (%42)", size=12, width=80), ft.ProgressBar(value=0.42, color=Style.PRIMARY, bgcolor=ft.colors.with_opacity(0.1, "white"), expand=True)]),
                        ft.Row([ft.Text("Seyahat (%28)", size=12, width=80), ft.ProgressBar(value=0.28, color=Style.SECONDARY, bgcolor=ft.colors.with_opacity(0.1, "white"), expand=True)]),
                        ft.Row([ft.Text("Ofis (%8)", size=12, width=80), ft.ProgressBar(value=0.08, color=Style.TERTIARY, bgcolor=ft.colors.with_opacity(0.1, "white"), expand=True)]),
                        ft.Row([ft.Text("Diğer (%22)", size=12, width=80), ft.ProgressBar(value=0.22, color=ft.colors.with_opacity(0.4, "white"), bgcolor=ft.colors.with_opacity(0.1, "white"), expand=True)]),
                    ], spacing=20)
                ])
            ),
            # Ekip Harcamaları (Liderlik Tablosu)
            ft.Container(
                **Style.GLASS_STYLE, expand=1, padding=32, border_radius=32,
                content=ft.Column([
                    ft.Row([ft.Text("Ekip Harcamaları", size=18, weight=ft.FontWeight.BOLD), ft.TextButton("Tümü", style=ft.ButtonStyle(color=Style.PRIMARY))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ContributorItem("Ömer", "Ürün Müdürü", "$8,420", "124", 0.85, Style.PRIMARY),
                    ContributorItem("Uğur", "Yazılım Mühendisi", "$6,110", "88", 0.62, ft.colors.with_opacity(0.4, "white")),
                    ContributorItem("Şuğra", "Tasarım Lideri", "$5,800", "94", 0.58, Style.SECONDARY),
                    ContributorItem("Halil", "Pazarlama", "$4,520", "52", 0.45, ft.colors.with_opacity(0.3, "white")),
                ], spacing=20)
            )
        ], spacing=25)
    ], expand=True, spacing=40)

    # 2. Dashboard Görünümü (Fiş Yükleme ve OCR)
    def InfoCardSmall(label, value, is_primary=False):
        """Dashboard'daki özet bilgi kartları"""
        return ft.Container(
            content=ft.Column([
                ft.Text(label.upper(), size=10, color=Style.OUTLINE, weight=ft.FontWeight.W_600),
                ft.Text(value, size=18 if not is_primary else 32, 
                        color=Style.SECONDARY if is_primary else ft.colors.WHITE, 
                        weight=ft.FontWeight.BOLD),
            ], spacing=2),
            padding=16,
            bgcolor=Style.SURFACE,
            border_radius=16,
            border=ft.border.all(1, ft.colors.with_opacity(0.05, "white")),
            expand=True
        )

    # UI Elementlerini Önceden Tanımla
    dashboard_status_text = ft.Text("Fişi Buraya Sürükleyin veya Dosya Seçin", size=20, weight=ft.FontWeight.W_600)
    upload_spinner = ft.ProgressRing(width=24, height=24, color=Style.PRIMARY, visible=False)
    
    # Dosya Seçici Bileşeni
    file_picker = ft.FilePicker()
    page.add(file_picker)

    def on_upload_complete(e):
        """Dosya sunucuya başarıyla yüklendiğinde tetiklenen OCR fonksiyonu"""
        if e.error:
            dashboard_status_text.value = f"Yükleme hatası: {e.error}"
            upload_spinner.visible = False
            page.update()
            return
            
        dashboard_status_text.value = f"Analiz yapılıyor: {e.file_name}..."
        page.update()
        
        try:
            # Arka planda PaddleOCR ile Analiz Süreci
            uploaded_file_path = os.path.join("uploads", e.file_name)
            
            # 1. OCR Tahmini (Metinleri Resimden Çıkar)
            prediction = ocr_engine.predict(uploaded_file_path)
            
            # 2. Veri Ayıklama (Metinleri Mağaza, Tarih vb. Şeklinde Ayrıştır)
            extracted_data = receipt_parser.parse(prediction)
            
            # Sonuçları Arayüzde Göster
            market = extracted_data.get('store_name', 'Bilinmiyor')
            tarih = extracted_data.get('date', 'Bilinmiyor')
            tutar = extracted_data.get('total_amount', '0.00')
            
            dashboard_status_text.value = f"✓ {market} | {tarih} | {tutar} TL"
            dashboard_status_text.color = Style.PRIMARY
        except Exception as ex:
            dashboard_status_text.value = f"Analiz Hatası: {str(ex)}"
            dashboard_status_text.color = ft.colors.RED_400
            
        upload_spinner.visible = False
        page.update()

    def on_file_selected(e):
        """Kullanıcı bir dosya seçtiğinde yüklemeyi başlatan fonksiyon"""
        if e.files and len(e.files) > 0:
            dashboard_status_text.value = "Dosya sunucuya yükleniyor..."
            dashboard_status_text.color = ft.colors.WHITE
            upload_spinner.visible = True
            page.update()
            
            # Dosyayı sunucunun 'uploads/' klasörüne gönder
            upload_list = []
            for f in e.files:
                upload_list.append(ft.FilePickerUploadFile(f.name, upload_url=page.get_upload_url(f.name, 60)))
            file_picker.upload(upload_list)

    # FilePicker olaylarını bağla
    file_picker.on_upload = on_upload_complete
    file_picker.on_result = on_file_selected

    async def btn_browse_click(e):
        """Gözat butonuna basıldığında dosya seçiciyi açan fonksiyon"""
        try:
            await file_picker.pick_files_async(allow_multiple=False)
        except AttributeError:
            file_picker.pick_files(allow_multiple=False)

    # Dashboard ana içeriği
    dashboard_view = ft.Column([
        ft.Row([
            # Dosya Yükleme Alanı
            ft.Container(
                **Style.GLASS_STYLE,
                expand=True, padding=32, border_radius=32,
                content=ft.Column([
                    ft.Container(content=ft.Icon(ft.icons.CLOUD_UPLOAD, size=40, color=Style.PRIMARY), bgcolor=Style.SURFACE, padding=20, border_radius=40, shadow=Style.NEON_SHADOW),
                    ft.Row([upload_spinner, dashboard_status_text], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Text("Desteklenenler: JPEG, PNG, PDF", size=12, color=Style.OUTLINE),
                    ft.ElevatedButton("Dosya Seç", bgcolor=ft.colors.TRANSPARENT, color=Style.PRIMARY, on_click=btn_browse_click)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            ),
            # Yapay Zeka Çıkarım Önizleme Alanı
            ft.Container(
                **Style.GLASS_STYLE,
                expand=True, padding=24, border_radius=32,
                content=ft.Column([
                    ft.Row([ft.Text("AI Veri Çıkarımı", size=18, weight=ft.FontWeight.W_600), ft.Icon(ft.icons.AUTO_AWESOME, color=Style.SECONDARY, size=20)]),
                    ft.Container(height=180, bgcolor=ft.colors.BLACK, border_radius=15, 
                                 content=ft.Image(src="https://picsum.photos/id/2/400/200", opacity=0.3, fit="cover")),
                    ft.Row([InfoCardSmall("Toplam", "$145.00", True), InfoCardSmall("Vergi", "$12.00")]),
                ], spacing=15)
            )
        ], height=400, spacing=30),
        ft.Container(**Style.GLASS_STYLE, padding=24, border_radius=32, expand=True, content=ft.Text("Harcama istatistikleri için Analytics sekmesine göz atın.", color=Style.OUTLINE))
    ], spacing=30, scroll=ft.ScrollMode.AUTO)

    # 3. Receipts Görünümü (Geçmiş Fiş Listesi)
    receipts_view = ft.Column([
        ft.Row([ft.Text("Fiş Kayıtları", size=28, weight=ft.FontWeight.W_800), ft.ElevatedButton("Yeni Fiş Ekle", icon=ft.icons.ADD, bgcolor=Style.PRIMARY, color=Style.BG)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(
            **Style.GLASS_STYLE,
            padding=24, border_radius=32,
            content=ft.Column([
                ft.Row([ft.TextField(hint_text="Fişlerde ara...", expand=True, prefix_icon=ft.icons.SEARCH, border_radius=15, bgcolor=Style.SURFACE, border=ft.InputBorder.NONE), ft.IconButton(ft.icons.FILTER_LIST, icon_color=Style.PRIMARY)]),
                ft.Container(height=20),
                ft.DataTable(
                    columns=[ft.DataColumn(ft.Text("TARIH")), ft.DataColumn(ft.Text("MAGAZA")), ft.DataColumn(ft.Text("KATEGORI")), ft.DataColumn(ft.Text("TUTAR")), ft.DataColumn(ft.Text("ISLEM"))],
                    rows=[
                        ft.DataRow(cells=[ft.DataCell(ft.Text("24.10.2023")), ft.DataCell(ft.Text("MIGROS")), ft.DataCell(ft.Container(content=ft.Text("Market", size=10), bgcolor=ft.colors.with_opacity(0.1, Style.SECONDARY), padding=8, border_radius=10)), ft.DataCell(ft.Text("$45.50")), ft.DataCell(ft.Row([ft.IconButton(ft.icons.VISIBILITY, icon_size=16), ft.IconButton(ft.icons.DELETE, icon_size=16, icon_color="red")]))]),
                        ft.DataRow(cells=[ft.DataCell(ft.Text("22.10.2023")), ft.DataCell(ft.Text("APPLE STORE")), ft.DataCell(ft.Container(content=ft.Text("Elektronik", size=10), bgcolor=ft.colors.with_opacity(0.1, Style.PRIMARY), padding=8, border_radius=10)), ft.DataCell(ft.Text("$1,299.00")), ft.DataCell(ft.Row([ft.IconButton(ft.icons.VISIBILITY, icon_size=16), ft.IconButton(ft.icons.DELETE, icon_size=16, icon_color="red")]))]),
                    ]
                )
            ])
        )
    ], spacing=20, scroll=ft.ScrollMode.AUTO)

    # 4. Teams Görünümü (Ekip Listesi)
    def TeamCard(name, amount):
        return ft.Container(**Style.GLASS_STYLE, width=300, padding=24, border_radius=24, content=ft.Column([ft.Row([ft.Icon(ft.icons.GROUP, color=Style.PRIMARY), ft.Text(name, size=18, weight=ft.FontWeight.BOLD)]), ft.Text(amount, size=16, weight=ft.FontWeight.BOLD, color=Style.SECONDARY)]))

    teams_view = ft.Column([
        ft.Row([ft.Text("Ekipler", size=28, weight=ft.FontWeight.W_800), ft.ElevatedButton("Yeni Ekip Kur", icon=ft.icons.GROUP_ADD, bgcolor=Style.SECONDARY, color=Style.BG)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([TeamCard("Mutfak Giderleri", "$240.20"), TeamCard("Ofis Malzemeleri", "$1,450.00")], spacing=20, wrap=True)
    ], spacing=20, scroll=ft.ScrollMode.AUTO)

    # Görünüm Sözlüğü (Navigasyon için)
    views = {
        "dashboard": dashboard_view,
        "receipts": receipts_view,
        "teams": teams_view,
        "analytics": analytics_view,
        "settings": ft.Container(padding=32, content=ft.Text("Ayarlar Ekranı Çok Yakında!"))
    }

    # --- SIDEBAR & LAYOUT ---
    def NavItem(icon, label, view_id):
        """Yan menüdeki her bir butonu oluşturan bileşen"""
        return ft.Container(
            data=view_id,
            content=ft.Row([
                ft.Icon(icon, color=Style.OUTLINE, size=20),
                ft.Text(label.upper(), size=12, weight=ft.FontWeight.W_600, color=Style.OUTLINE)
            ], alignment=ft.MainAxisAlignment.START),
            padding=ft.Padding(16, 12, 16, 12),
            border_radius=12,
            on_click=lambda _: route_change(view_id)
        )

    # Sidebar Menü Listesi
    sidebar_items = ft.Column([
        NavItem(ft.icons.DASHBOARD, "Dashboard", "dashboard"),
        NavItem(ft.icons.INSIGHTS, "Analytics", "analytics"), 
        NavItem(ft.icons.RECEIPT_LONG, "Fişlerim", "receipts"),
        NavItem(ft.icons.GROUPS, "Ekipler", "teams"),
        NavItem(ft.icons.SETTINGS, "Ayarlar", "settings"),
    ])

    # Sidebar Genel Yapısı
    sidebar = ft.Container(
        width=260, padding=24, bgcolor=ft.colors.with_opacity(0.4, "#0f172a"), blur=20,
        border=ft.Border(right=ft.BorderSide(1, ft.colors.with_opacity(0.1, "white"))),
        content=ft.Column([
            # Logo Alanı
            ft.Row([ft.Container(content=ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET, color=Style.BG, size=20), gradient=Style.PRIMARY_GRADIENT, padding=8, border_radius=10), ft.Text("ReceiptShare", size=20, weight=ft.FontWeight.W_900)]),
            ft.Container(height=30),
            sidebar_items,
            ft.Container(expand=True),
            # Çıkış Butonu
            NavItem(ft.icons.LOGOUT, "ÇIKIŞ YAP", "logout"),
        ])
    )

    # Üst Bilgi Çubuğu (Header)
    header = ft.Container(
        padding=ft.Padding(32, 0, 32, 0), height=70, bgcolor=ft.colors.with_opacity(0.4, Style.BG), blur=20,
        border=ft.Border(bottom=ft.BorderSide(1, ft.colors.with_opacity(0.1, "white"))),
        content=ft.Row([ft.Text("ANALYTICS PORTAL", size=14, weight=ft.FontWeight.W_800), ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON, size=20), radius=18, bgcolor=Style.SURFACE)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

    # Ana İçerik Alanı (Başlangıçta Analytics açık)
    content_area = ft.Container(padding=32, expand=True, content=views["analytics"])
    
    # Tüm Sayfa Düzeni (Sidebar + [Header + Content])
    main_layout = ft.Row([sidebar, ft.Column([header, content_area], expand=True, spacing=0)], expand=True, spacing=0)

    # Sayfaya ekle ve başlangıç durumunu ayarla
    page.add(main_layout)
    route_change("analytics")

if __name__ == '__main__':
    # Uygulamayı Tarayıcıda Başlat
    # upload_dir: Yüklenen fişlerin kaydedileceği klasör
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550, upload_dir="uploads")
0, upload_dir="uploads")
