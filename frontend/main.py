import flet as ft
import os
import sys

# TR: Proje ana dizinine erişim sağlayarak arka plan modüllerini yükle
# EN: Access project root directory to load backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from style_tokens import Style
from database.db_manager import DatabaseManager
from receipt_parser import ReceiptParser
from paddleocr import PaddleOCR

# --- GLOBAL NESNELER ---
ocr_engine = PaddleOCR(use_textline_orientation=True, lang="tr", enable_mkldnn=False)
receipt_parser = ReceiptParser()
db = DatabaseManager() # Veritabanını başlat


def main(page: ft.Page):
    """Flet Uygulamasının Ana Giriş Fonksiyonu"""
    
    # Sayfa genel ayarları
    page.title = "ReceiptShare Web - Analytics Overview"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = Style.BG
    page.window.width = 1400
    page.window.height = 900
    page.padding = 0
    page.spacing = 0

    # --- UI REFERANSLARI (Dinamik Güncelleme İçin) ---
    total_spent_text = ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
    scan_count_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
    
    # Son Fiş Özeti Referansları
    last_receipt_title = ft.Text("Son Fiş Özeti", size=18, weight=ft.FontWeight.W_600)
    last_receipt_store = ft.Text("Henüz Veri Yok", size=14, color=Style.OUTLINE)
    last_receipt_total = ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD, color=Style.SECONDARY)
    last_receipt_date = ft.Text("-", size=18, weight=ft.FontWeight.BOLD)

    receipts_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("TARIH")), 
            ft.DataColumn(ft.Text("MAGAZA")), 
            ft.DataColumn(ft.Text("KATEGORI")), 
            ft.DataColumn(ft.Text("TUTAR")), 
            ft.DataColumn(ft.Text("ISLEM"))
        ],
        rows=[]
    )

    def refresh_ui_data():
        """Veritabanındaki güncel verileri çekip arayüzü yeniler"""
        try:
            print(f"DEBUG: Veritabanı bağlantısı kontrol ediliyor: {db.db_name}")
            stats = db.get_stats()
            total_spent_text.value = f"${stats['total']:,.2f}"
            scan_count_text.value = str(stats['count'])
            
            # Tabloyu güncelle
            rows = db.get_all_receipts()
            print(f"DEBUG: Toplam {len(rows)} fiş bulundu.")
            
            receipts_table.rows = []
            
            if rows:
                # En son fişi "Son Fiş Özeti" kartına yaz
                last = rows[0]
                last_receipt_store.value = str(last[2]).upper()
                last_receipt_total.value = f"${last[4]:.2f}"
                last_receipt_date.value = str(last[1])

                for r in rows:
                    receipts_table.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(r[1]))),
                            ft.DataCell(ft.Text(str(r[2]))),
                            ft.DataCell(ft.Container(content=ft.Text(str(r[3]), size=10), bgcolor=ft.colors.with_opacity(0.1, r[5]), padding=8, border_radius=10)),
                            ft.DataCell(ft.Text(f"${r[4]:.2f}")),
                            ft.DataCell(ft.Row([ft.IconButton(ft.icons.VISIBILITY, icon_size=16), ft.IconButton(ft.icons.DELETE, icon_size=16, icon_color="red")]))
                        ])
                    )
            page.update()
        except Exception as e:
            print(f"HATA (Veritabanı): {e}")

    # --- DURUM YÖNETİMİ (NAVİGASYON) ---
    def route_change(view_name):
        """Menü tıklandığında ekrandaki içeriği değiştiren fonksiyon"""
        if view_name in views:
            content_area.content = views[view_name]
            refresh_ui_data() # Verileri tazele
            
            for item in sidebar_items.controls:
                if isinstance(item, ft.Container) and item.data:
                    is_selected = item.data == view_name
                    item.bgcolor = ft.colors.with_opacity(0.1, Style.PRIMARY) if is_selected else None
                    item.border = ft.Border(right=ft.BorderSide(4, Style.PRIMARY)) if is_selected else None
                    
                    if isinstance(item.content, ft.Row):
                        row = item.content
                        row.controls[0].color = Style.PRIMARY if is_selected else Style.OUTLINE
                        row.controls[1].color = Style.PRIMARY if is_selected else Style.OUTLINE
            page.update()

    # --- UI BİLEŞENLERİ ---

    def KPICard(label, value_control, trend=None, is_up=True, neon_color=None):
        shadows = []
        if neon_color:
            shadows.append(ft.BoxShadow(blur_radius=20, color=ft.colors.with_opacity(0.15, neon_color), spread_radius=1))
        
        return ft.Container(
            **Style.GLASS_STYLE,
            expand=True, padding=24, border_radius=24, shadow=shadows,
            content=ft.Column([
                ft.Text(label.upper(), size=10, color=Style.OUTLINE, weight=ft.FontWeight.W_800),
                value_control, 
                ft.Row([
                    ft.Icon(ft.icons.TRENDING_UP if is_up else ft.icons.TRENDING_DOWN, 
                            color=Style.SECONDARY if is_up else ft.colors.ERROR, size=16),
                    ft.Text(trend, size=12, color=Style.SECONDARY if is_up else ft.colors.ERROR, weight=ft.FontWeight.W_600)
                ]) if trend else ft.Container()
            ], spacing=5)
        )

    def InsightCard(title, desc, icon, border_color):
        return ft.Container(
            bgcolor=ft.colors.with_opacity(0.03, "white"),
            blur=10, expand=True, padding=24, border_radius=24,
            border=ft.Border(left=ft.BorderSide(4, border_color), top=ft.BorderSide(1, ft.colors.with_opacity(0.1, "white"))),
            content=ft.Column([
                ft.Row([
                    ft.Container(content=ft.Icon(icon, color=border_color, size=20), bgcolor=ft.colors.with_opacity(0.1, border_color), padding=10, border_radius=10),
                    ft.Container(content=ft.Text("YÜKSEK ETKİ", size=9, weight=ft.FontWeight.BOLD), bgcolor=ft.colors.with_opacity(0.05, "white"), padding=ft.Padding(8, 4, 8, 4), border_radius=5)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                ft.Text(desc, size=13, color=Style.OUTLINE, max_lines=3)
            ], spacing=10)
        )

    def ContributorItem(name, role, amount, receipts, progress, color):
        return ft.Column([
            ft.Row([
                ft.Row([
                    ft.CircleAvatar(radius=18, bgcolor=ft.colors.with_opacity(0.1, color), content=ft.Icon(ft.icons.PERSON, color=color)),
                    ft.Column([ft.Text(name, size=14, weight=ft.FontWeight.BOLD), ft.Text(role.upper(), size=9, color=Style.OUTLINE)], spacing=0)
                ]),
                ft.Column([ft.Text(amount, size=14, weight=ft.FontWeight.BOLD), ft.Text(f"{receipts} FİŞ", size=9, color=Style.SECONDARY)], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=0)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.ProgressBar(value=progress, color=color, height=6, border_radius=10)
        ], spacing=10)

    # --- VIEWS ---

    analytics_view = ft.ListView([
        ft.Row([
            ft.Column([ft.Text("Analytics Overview", size=28, weight=ft.FontWeight.W_800), ft.Text("Kurumsal harcama verilerinizin derinlemesine analizi.", color=Style.OUTLINE)]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Row([
            KPICard("Toplam Harcama", total_spent_text, "geçen aya göre %12 artış", True, Style.PRIMARY),
            KPICard("Ort. Fiş Tutarı", ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD), "sabit", True),
            KPICard("Tarama Sayısı", scan_count_text, "%99.2 Doğruluk", True),
            KPICard("En Popüler Kategori", ft.Text("Yemek", size=32, weight=ft.FontWeight.BOLD), "aktif", True, Style.SECONDARY),
        ], spacing=25),

        ft.Row([
            ft.Container(
                **Style.GLASS_STYLE, expand=2, padding=32, border_radius=32,
                content=ft.Column([
                    ft.Text("Harcama Trendleri", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(height=250, content=ft.Text("Grafik verileri yükleniyor...", color=Style.OUTLINE, text_align=ft.TextAlign.CENTER))
                ])
            ),
            ft.Container(
                **Style.GLASS_STYLE, expand=1, padding=32, border_radius=32,
                content=ft.Column([
                    ft.Text("Bütçe Sağlığı", size=18, weight=ft.FontWeight.BOLD),
                    ft.ProgressBar(value=0.82, color=Style.SECONDARY, height=10, border_radius=10),
                    ft.ElevatedButton("Limitleri Düzenle", bgcolor=Style.PRIMARY, color=Style.BG)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        ], spacing=25),

        ft.Row([
            InsightCard("Lisans Çakışması", "Ekipler arasında mükerrer Adobe lisansı tespit edildi.", ft.icons.REPEAT, Style.PRIMARY),
            InsightCard("Yemek Harcaması", "Geçen aya göre %18 artış.", ft.icons.TRENDING_UP, Style.SECONDARY),
        ], spacing=25)
    ], expand=True, spacing=40)

    dashboard_view = ft.Column([
        ft.Row([
            ft.Container(
                **Style.GLASS_STYLE, expand=True, padding=32, border_radius=32,
                content=ft.Column([
                    ft.Container(content=ft.Icon(ft.icons.CLOUD_UPLOAD, size=40, color=Style.PRIMARY), bgcolor=Style.SURFACE, padding=20, border_radius=40),
                    ft.Text("Fişi Buraya Sürükleyin", size=20, weight=ft.FontWeight.W_600),
                    ft.ElevatedButton("Dosya Seç", bgcolor=ft.colors.TRANSPARENT, color=Style.PRIMARY)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            ),
            ft.Container(
                **Style.GLASS_STYLE, expand=True, padding=24, border_radius=32,
                content=ft.Column([
                    ft.Row([last_receipt_title, ft.Icon(ft.icons.HISTORY, color=Style.SECONDARY, size=20)]),
                    ft.Column([ft.Text("MAĞAZA", size=10, color=Style.OUTLINE), last_receipt_store], spacing=2),
                    ft.Container(height=100, bgcolor=ft.colors.with_opacity(0.05, "white"), border_radius=15, 
                                 alignment=ft.alignment.center,
                                 content=ft.Icon(ft.icons.RECEIPT, size=40, color=Style.PRIMARY, opacity=0.5)),
                    ft.Row([
                        ft.Container(content=ft.Column([ft.Text("TOPLAM", size=10, color=Style.OUTLINE), last_receipt_total], spacing=2), padding=16, bgcolor=Style.SURFACE, border_radius=16, expand=True),
                        ft.Container(content=ft.Column([ft.Text("TARİH", size=10, color=Style.OUTLINE), last_receipt_date], spacing=2), padding=16, bgcolor=Style.SURFACE, border_radius=16, expand=True),
                    ], spacing=15),
                ], spacing=15)
            )
        ], height=400, spacing=30)
    ], spacing=30, scroll=ft.ScrollMode.AUTO)

    receipts_view = ft.Column([
        ft.Row([ft.Text("Fiş Kayıtları", size=28, weight=ft.FontWeight.W_800), ft.ElevatedButton("Yeni Fiş Ekle", icon=ft.icons.ADD, bgcolor=Style.PRIMARY, color=Style.BG)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(**Style.GLASS_STYLE, padding=24, border_radius=32, content=receipts_table)
    ], spacing=20, scroll=ft.ScrollMode.AUTO)

    views = {
        "dashboard": dashboard_view,
        "analytics": analytics_view,
        "receipts": receipts_view,
        "teams": ft.Container(padding=32, content=ft.Text("Ekipler Yakında!")),
        "settings": ft.Container(padding=32, content=ft.Text("Ayarlar Yakında!"))
    }

    # --- SIDEBAR ---
    def NavItem(icon, label, view_id):
        return ft.Container(
            data=view_id,
            content=ft.Row([ft.Icon(icon, color=Style.OUTLINE, size=20), ft.Text(label.upper(), size=12, weight=ft.FontWeight.W_600, color=Style.OUTLINE)], alignment=ft.MainAxisAlignment.START),
            padding=ft.Padding(20, 12, 16, 12), border_radius=12,
            on_click=lambda _: route_change(view_id)
        )

    sidebar_items = ft.Column([
        NavItem(ft.icons.DASHBOARD, "Dashboard", "dashboard"),
        NavItem(ft.icons.INSIGHTS, "Analytics", "analytics"), 
        NavItem(ft.icons.RECEIPT_LONG, "Fişlerim", "receipts"),
        NavItem(ft.icons.GROUPS, "Ekipler", "teams"),
        NavItem(ft.icons.SETTINGS, "Ayarlar", "settings"),
    ], spacing=5)

    sidebar = ft.Container(
        width=260, padding=24, bgcolor=Style.BG, border=ft.Border(right=ft.BorderSide(1, ft.colors.with_opacity(0.1, "white"))),
        content=ft.Column([
            ft.Row([ft.Container(content=ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET, color=Style.BG, size=20), gradient=Style.PRIMARY_GRADIENT, padding=8, border_radius=10), ft.Text("ReceiptShare", size=20, weight=ft.FontWeight.W_900)]),
            ft.Container(height=30), sidebar_items, ft.Container(expand=True), NavItem(ft.icons.LOGOUT, "ÇIKIŞ YAP", "logout"),
        ])
    )

    header = ft.Container(
        padding=ft.Padding(32, 0, 32, 0), height=70, bgcolor=Style.BG, border=ft.Border(bottom=ft.BorderSide(1, ft.colors.with_opacity(0.1, "white"))),
        content=ft.Row([ft.Text("ANALYTICS PORTAL", size=14, weight=ft.FontWeight.W_800), ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON), radius=18)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

    content_area = ft.Container(padding=32, expand=True, content=views["analytics"])
    main_layout = ft.Row([sidebar, ft.Column([header, content_area], expand=True, spacing=0)], expand=True, spacing=0)

    page.add(main_layout)
    refresh_ui_data()
    route_change("analytics")

if __name__ == '__main__':
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550, upload_dir="uploads")
