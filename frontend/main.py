import flet as ft
import os
import sys
import pandas as pd
import cv2
import threading
import numpy as np

os.environ["FLET_SECRET_KEY"] = "ipt_ocr_secure_key_123"

# TR: Proje ana dizinine erişim sağlayarak arka plan modüllerini yükle
# EN: Access project root directory to load backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import traceback
import time
from style_tokens import Style
from database.db_manager import DatabaseManager
from receipt_parser import ReceiptParser
try:
    from paddleocr import PaddleOCR  # type: ignore
except Exception:
    PaddleOCR = None

# --- GLOBAL NESNELER | GLOBAL OBJECTS ---
# TR: OCR motorunu ve veritabanı yöneticisini uygulama genelinde kullanmak için başlatıyoruz.
# EN: Initializing the OCR engine and database manager for application-wide use.
ocr_engine = (
    PaddleOCR(
        use_textline_orientation=True, 
        lang="tr", 
        enable_mkldnn=False, # Disable due to (Unimplemented) error in some environments
        text_det_unclip_ratio=2.0,
        text_det_box_thresh=0.5
    )
    if PaddleOCR is not None
    else None
)
receipt_parser = ReceiptParser()
db = DatabaseManager() # Veritabanını başlat | Initialize database


def main(page: ft.Page):
    """
    TR: Flet uygulamasının ana giriş fonksiyonu. Sayfa ayarlarını ve düzenini başlatır.
    EN: Main entry function for the Flet App. Initializes page settings and layout.
    """
    
    # Sayfa genel ayarları
    page.title = "ReceiptShare Web - Analytics Overview"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = Style.BG
    page.window.width = 1400
    page.window.height = 900
    page.padding = 0
    page.spacing = 0
    
    # TR: Teknik gereksinim: Özel upload URL tanımı
    # EN: Technical requirement: Custom upload URL definition
    page.upload_url = "/api/upload"

    # --- UI YÖNETİMİ | UI MANAGEMENT ---
    # TR: Kullanıcıya geri bildirim vermek için SnackBar nesnesi
    # EN: SnackBar object to provide feedback to the user
    status_snack = ft.SnackBar(ft.Text(""), duration=4000)
    page.overlay.append(status_snack)
    
    # TR: Analiz sırasında dönecek halka | EN: Progress ring for analysis phase
    progress_ring = ft.ProgressRing(width=16, height=16, stroke_width=2, color=Style.PRIMARY, visible=False)
    
    last_status_update = 0

    def show_status(text, color=None, force=False):
        """
        TR: Durum bildirimlerini güncelleyen yardımcı fonksiyon.
        EN: Helper function to update status notifications.
        """
        nonlocal last_status_update
        now = time.time()
        # Throttling: 0.5 saniyede bir güncelle (force=True hariç)
        if not force and (now - last_status_update) < 0.5:
            return
            
        last_status_update = now
        status_snack.content.value = text
        status_snack.bgcolor = color
        status_snack.open = True
        page.update()

    # --- IMAGE PREPROCESSING ---
    def preprocess_image(img):
        """
        TR: OCR doğruluğunu artırmak için görüntüyü iyileştirir (gri tonlama, gürültü azaltma, eşikleme).
        EN: Improves image for better OCR accuracy (grayscale, denoising, thresholding).
        """
        # 1. Gri tonlamaya çevir
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Resim çok büyükse küçült (Hız ve bellek için)
        # Resize if too large for speed and memory
        h, w = gray.shape
        max_dim = 1000
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            gray = cv2.resize(gray, (int(w * scale), int(h * scale)))

        # 3. Gürültü azaltma
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # 3. Adaptif eşikleme (Gölge ve ışık değişimlerini dengeler)
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # 4. Keskinleştirme (Opsiyonel ama rakamlar için faydalı olabilir)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(thresh, -1, kernel)
        
        # 5. PaddleOCR 3 kanal (BGR) bekleyebilir, geri çevir
        # PaddleOCR might expect 3 channels (BGR), convert back
        final_img = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
        
        return final_img

    # --- DOSYA YÜKLEME VE OCR MANTIĞI | FILE UPLOAD & OCR LOGIC ---
    def on_upload_result(e: ft.FilePickerUploadEvent):
        """
        TR: Dosya yükleme ilerlemesini ve tamamlanmasını yönetir.
        EN: Manages file upload progress and completion.
        """
        if e.error:
            show_status(f"Upload Error: {e.error}", ft.colors.ERROR, force=True)
            return

        if e.progress < 1.0:
            show_status(f"Uploading: %{int(e.progress * 100)}")
            return
            
        file_path = os.path.join(os.path.abspath("uploads"), e.file_name)
        print(f"DEBUG: Yükleme tamamlandı, dosya yolu: {file_path}")
        
        show_status("File received, analyzing...", Style.SECONDARY, force=True)
        
        def run_ocr_task():
            """
            TR: OCR işlemini ve veritabanı kaydını arka planda yürüten alt görev.
            EN: Background sub-task that executes OCR processing and database recording.
            """
            progress_ring.visible = True
            page.update()
            try:
                print(f"DEBUG: OCR Görevi Başladı - Dosya: {file_path}")
                if ocr_engine is None:
                    # PaddleOCR kurulu değilse, dosyayı DB'ye "işlenmedi" olarak kaydeder.
                    db.add_receipt(
                        store_name="OCR DISABLED",
                        date="2026-01-01",
                        amount=0.0,
                        category_name="Other",
                    )
                    refresh_ui_data()
                    show_status("PaddleOCR not installed!", ft.colors.ERROR)
                    return

                # TR: Windows dosya yolları (boşluk/türkçe karakter) için imdecode kullan
                # EN: Use imdecode for Windows file paths (space/turkish characters)
                img_array = np.fromfile(file_path, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                if img is None: 
                    print(f"HATA: Resim decode edilemedi: {file_path}")
                    raise FileNotFoundError(f"Resim decode edilemedi: {file_path}")
                
                # TR: Ön işlem uygula
                # EN: Apply preprocessing
                processed_img = preprocess_image(img)
                
                print(f"DEBUG: OCR Tahmini Başlıyor... (Görüntü Boyutu: {img.shape})")
                prediction = ocr_engine.predict(processed_img)
                print("DEBUG: OCR Tahmini Bitti, Parse Ediliyor...")
                data = receipt_parser.parse(prediction)
                print(f"DEBUG: Parse Sonucu: {data}")
                
                # TR: Veritabanına kaydet
                # EN: Save to database
                store = data.get('store_name', 'Unknown Store')
                date = data.get('date', '2026-01-01')
                if date == "Not Found" or not date: date = "2026-01-01"
                total = data.get('total_amount', 0.0)
                
                db.add_receipt(store, date, total, "Other")
                print("DEBUG: Veritabanına kaydedildi.")
                
                # TR: Arayüzü güncelle (Dinamik Grafikler ve Tablo)
                # EN: Update UI (Dynamic Charts and Table)
                refresh_ui_data()
                show_status(f"Analysis Successful: {store}", Style.PRIMARY, force=True)
            except Exception as ex:
                print(f"HATA (OCR İşlemi): {ex}")
                traceback.print_exc()
                show_status(f"Analysis Error: {ex}", ft.colors.ERROR, force=True)
            finally:
                progress_ring.visible = False
                page.update()

        # TR: OCR işlemini arayüzü dondurmamak için ayrı bir thread'de çalıştır
        # EN: Run OCR in a separate thread to avoid freezing the UI
        threading.Thread(target=run_ocr_task, daemon=True).start()

    def on_file_picker_result(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            file = e.files[0]
            print(f"DEBUG: Seçilen dosya: {file.name}")
            upload_url = page.get_upload_url(file.name, 120) # 120 sn timeout
            print(f"DEBUG: Oluşturulan Upload URL: {upload_url}")
            file_picker.upload([ft.FilePickerUploadFile(file.name, upload_url=upload_url)])
            show_status(f"Starting upload: {file.name}", force=True)

    file_picker = ft.FilePicker(on_result=on_file_picker_result, on_upload=on_upload_result)
    page.overlay.append(file_picker)

    # --- UI REFERANSLARI (Dinamik Güncelleme İçin) | UI REFERENCES (For Dynamic Updates) ---
    total_spent_text = ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
    avg_spent_text = ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
    scan_count_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE)
    
    # Son Fiş Özeti Referansları
    last_receipt_title = ft.Text("Last Receipt Summary", size=18, weight=ft.FontWeight.W_600)
    last_receipt_store = ft.Text("No Data Yet", size=14, color=Style.OUTLINE)
    last_receipt_total = ft.Text("$0.00", size=32, weight=ft.FontWeight.BOLD, color=Style.SECONDARY)
    last_receipt_date = ft.Text("-", size=18, weight=ft.FontWeight.BOLD)
    
    # Dinamik Kategori Dağılımı Referansı
    category_list_column = ft.Column(spacing=20)

    # Dinamik Harcama Trend Grafiği (Pandas ile beslenecek)
    expense_chart = ft.BarChart(
        bar_groups=[],
        border=ft.border.all(1, ft.colors.with_opacity(0.1, "white")),
        left_axis=ft.ChartAxis(labels_size=40),
        bottom_axis=ft.ChartAxis(labels_size=40),
        horizontal_grid_lines=ft.ChartGridLines(color=ft.colors.with_opacity(0.05, "white"), width=1, dash_pattern=[3, 3]),
        tooltip_bgcolor=ft.colors.with_opacity(0.8, Style.BG),
        max_y=1000,
        interactive=True,
    )

    receipts_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("DATE")), 
            ft.DataColumn(ft.Text("STORE")), 
            ft.DataColumn(ft.Text("CATEGORY")), 
            ft.DataColumn(ft.Text("AMOUNT")), 
            ft.DataColumn(ft.Text("ACTION"))
        ],
        rows=[]
    )

    def refresh_ui_data():
        """
        TR: Veritabanındaki güncel verileri çekip arayüzü ve grafikleri yeniler.
        EN: Fetches latest data from the database and refreshes the UI and charts.
        """
        try:
            print(f"DEBUG: Veritabanı bağlantısı kontrol ediliyor: {db.db_name}")
            stats = db.get_stats()
            total_spent_text.value = f"${stats['total']:,.2f}"
            scan_count_text.value = str(stats['count'])
            
            # Ortalama harcamayı hesapla
            avg = stats['total'] / stats['count'] if stats['count'] > 0 else 0
            avg_spent_text.value = f"${avg:,.2f}"
            
            # --- PANDAS İLE GRAFİK VERİSİ İŞLEME | CHART DATA PROCESSING WITH PANDAS ---
            df = db.get_analytics_df()
            if not df.empty:
                # TR: Tarihi pandas datetime nesnesine çevir ve geçersizleri at (NaT)
                df['receipt_date'] = pd.to_datetime(df['receipt_date'], errors='coerce')
                df = df.dropna(subset=['receipt_date'])
                
                # Günlük bazda toplam tutarı grupla
                daily_df = df.groupby(df['receipt_date'].dt.date)['total_amount'].sum().reset_index()
                daily_df = daily_df.sort_values('receipt_date')
                
                # Grafiği güncelle
                bar_groups = []
                labels = []
                max_y = 0
                for i, row in daily_df.iterrows():
                    val = float(row['total_amount'])
                    if val > max_y: max_y = val
                    
                    # Çubuk (Bar) oluştur
                    bar_groups.append(
                        ft.BarChartGroup(
                            x=i,
                            bar_rods=[ft.BarChartRod(from_y=0, to_y=val, width=15, color=Style.PRIMARY, tooltip=f"{row['receipt_date']}\n{val:.2f} USD")],
                        )
                    )
                    # Alt eksen etiketi oluştur (Örn: 20 Haz)
                    date_str = row['receipt_date'].strftime('%d %b')
                    labels.append(ft.ChartAxisLabel(value=i, label=ft.Container(ft.Text(date_str, size=9, color=Style.OUTLINE), padding=2)))
                
                expense_chart.bar_groups = bar_groups
                expense_chart.bottom_axis.labels = labels
                expense_chart.max_y = max_y * 1.2 if max_y > 0 else 1000

                # PANDAS İLE KATEGORİ DAĞILIMI
                cat_df = df.groupby('category_name').agg({'total_amount':'sum', 'color_code':'first'}).reset_index()
                total_cat_sum = cat_df['total_amount'].sum()
                
                cat_controls = []
                for _, crow in cat_df.sort_values('total_amount', ascending=False).iterrows():
                    cat_name = crow['category_name']
                    cat_val = float(crow['total_amount'])
                    cat_color = crow['color_code'] if pd.notna(crow['color_code']) else Style.PRIMARY
                    percentage = cat_val / total_cat_sum if total_cat_sum > 0 else 0
                    
                    cat_controls.append(
                        ft.Row([
                            ft.Text(f"{cat_name} (%{int(percentage*100)})", size=12, width=120),
                            ft.ProgressBar(value=percentage, color=cat_color, bgcolor=ft.colors.with_opacity(0.1, "white"), expand=True),
                            ft.Text(f"${cat_val:.2f}", size=12, weight=ft.FontWeight.BOLD)
                        ])
                    )
                category_list_column.controls = cat_controls

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
                    def delete_action(rid=r[0]):
                        db.delete_receipt(rid)
                        refresh_ui_data()
                        show_status("Receipt deleted.", Style.PRIMARY, force=True)

                    receipts_table.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(r[1]))),
                            ft.DataCell(ft.Text(str(r[2]))),
                            ft.DataCell(ft.Container(content=ft.Text(str(r[3]), size=10), bgcolor=ft.colors.with_opacity(0.1, r[5]), padding=8, border_radius=10)),
                            ft.DataCell(ft.Text(f"${r[4]:.2f}")),
                            ft.DataCell(ft.Row([
                                ft.IconButton(ft.icons.VISIBILITY, icon_size=16), 
                                ft.IconButton(ft.icons.DELETE, icon_size=16, icon_color="red", on_click=lambda _, rid=r[0]: delete_action(rid))
                            ]))
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
                    ft.Container(content=ft.Text("HIGH IMPACT", size=9, weight=ft.FontWeight.BOLD), bgcolor=ft.colors.with_opacity(0.05, "white"), padding=ft.Padding(8, 4, 8, 4), border_radius=5)
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
                ft.Column([ft.Text(amount, size=14, weight=ft.FontWeight.BOLD), ft.Text(f"{receipts} RECEIPTS", size=9, color=Style.SECONDARY)], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=0)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.ProgressBar(value=progress, color=color, height=6, border_radius=10)
        ], spacing=10)

    # --- VIEWS ---

    analytics_view = ft.ListView([
        ft.Row([
            ft.Column([ft.Text("Analytics Overview", size=28, weight=ft.FontWeight.W_800), ft.Text("Deep dive analysis of your corporate spending data.", color=Style.OUTLINE)]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Row([
            KPICard("Total Spending", total_spent_text, "12% increase from last month", True, Style.PRIMARY),
            KPICard("Avg. Receipt", avg_spent_text, "stable", True),
            KPICard("Scan Count", scan_count_text, "99.2% Accuracy", True),
            KPICard("Popular Category", ft.Text("Food", size=32, weight=ft.FontWeight.BOLD), "active", True, Style.SECONDARY),
        ], spacing=25),

        ft.Row([
            ft.Container(
                **Style.GLASS_STYLE, expand=2, padding=32, border_radius=32,
                content=ft.Column([
                    ft.Text("Daily Spending Trend", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(height=250, padding=ft.Padding(0, 20, 0, 0), content=expense_chart)
                ])
            ),
            ft.Container(
                **Style.GLASS_STYLE, expand=1, padding=32, border_radius=32,
                content=ft.Column([
                    ft.Text("Budget Health", size=18, weight=ft.FontWeight.BOLD),
                    ft.ProgressBar(value=0.82, color=Style.SECONDARY, height=10, border_radius=10),
                    ft.ElevatedButton("Edit Limits", bgcolor=Style.PRIMARY, color=Style.BG)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        ], spacing=25),

        ft.Row([
            InsightCard("License Conflict", "Duplicate Adobe licenses detected among teams.", ft.icons.REPEAT, Style.PRIMARY),
            InsightCard("Food Spending", "18% increase from last month.", ft.icons.TRENDING_UP, Style.SECONDARY),
        ], spacing=25),

        # Kategori Dağılımı ve Ek Özellikler
        ft.Row([
            ft.Container(
                **Style.GLASS_STYLE, expand=1, padding=32, border_radius=32,
                content=ft.Column([
                    ft.Text("Categorical Distribution", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    category_list_column
                ])
            ),
            # Boş veya Liderlik tablosu için yer tutucu
            ft.Container(expand=1)
        ], spacing=25)
    ], expand=True, spacing=40)

    dashboard_view = ft.Column([
        ft.Row([
            ft.Container(
                **Style.GLASS_STYLE, expand=True, padding=32, border_radius=32,
                content=ft.Column([
                    ft.Container(content=ft.Icon(ft.icons.CLOUD_UPLOAD, size=40, color=Style.PRIMARY), bgcolor=Style.SURFACE, padding=20, border_radius=40),
                    ft.Text("Drag & Drop Receipt Here", size=20, weight=ft.FontWeight.W_600),
                    ft.ElevatedButton("Select File", bgcolor=ft.colors.TRANSPARENT, color=Style.PRIMARY, on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["png"]))
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            ),
            ft.Container(
                **Style.GLASS_STYLE, expand=True, padding=24, border_radius=32,
                content=ft.Column([
                    ft.Row([last_receipt_title, ft.Icon(ft.icons.HISTORY, color=Style.SECONDARY, size=20)]),
                    ft.Column([ft.Text("STORE", size=10, color=Style.OUTLINE), last_receipt_store], spacing=2),
                    ft.Container(height=100, bgcolor=ft.colors.with_opacity(0.05, "white"), border_radius=15, 
                                 alignment=ft.alignment.center,
                                 content=ft.Icon(ft.icons.RECEIPT, size=40, color=Style.PRIMARY, opacity=0.5)),
                    ft.Row([
                        ft.Container(content=ft.Column([ft.Text("TOTAL", size=10, color=Style.OUTLINE), last_receipt_total], spacing=2), padding=16, bgcolor=Style.SURFACE, border_radius=16, expand=True),
                        ft.Container(content=ft.Column([ft.Text("DATE", size=10, color=Style.OUTLINE), last_receipt_date], spacing=2), padding=16, bgcolor=Style.SURFACE, border_radius=16, expand=True),
                    ], spacing=15),
                ], spacing=15)
            )
        ], height=400, spacing=30)
    ], spacing=30, scroll=ft.ScrollMode.AUTO)

    receipts_view = ft.Column([
        ft.Row([ft.Text("Receipt Records", size=28, weight=ft.FontWeight.W_800), ft.ElevatedButton("Add New Receipt", icon=ft.icons.ADD, bgcolor=Style.PRIMARY, color=Style.BG, on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["png"]))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(**Style.GLASS_STYLE, padding=24, border_radius=32, content=receipts_table)
    ], spacing=20, scroll=ft.ScrollMode.AUTO)

    views = {
        "dashboard": dashboard_view,
        "analytics": analytics_view,
        "receipts": receipts_view,
        "teams": ft.Container(padding=32, content=ft.Text("Teams Coming Soon!")),
        "settings": ft.Container(padding=32, content=ft.Text("Settings Coming Soon!"))
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
        NavItem(ft.icons.RECEIPT_LONG, "My Receipts", "receipts"),
        NavItem(ft.icons.GROUPS, "Teams", "teams"),
        NavItem(ft.icons.SETTINGS, "Settings", "settings"),
    ], spacing=5)

    sidebar = ft.Container(
        width=260, padding=24, bgcolor=Style.BG, border=ft.Border(right=ft.BorderSide(1, ft.colors.with_opacity(0.1, "white"))),
        content=ft.Column([
            ft.Row([ft.Container(content=ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET, color=Style.BG, size=20), gradient=Style.PRIMARY_GRADIENT, padding=8, border_radius=10), ft.Text("ReceiptShare", size=20, weight=ft.FontWeight.W_900)]),
            ft.Container(height=30), sidebar_items, ft.Container(expand=True), NavItem(ft.icons.LOGOUT, "LOGOUT", "logout"),
        ])
    )

    header = ft.Container(
        padding=ft.Padding(32, 0, 32, 0), height=70, bgcolor=Style.BG, border=ft.Border(bottom=ft.BorderSide(1, ft.colors.with_opacity(0.1, "white"))),
        content=ft.Row([
            ft.Row([ft.Text("ANALYTICS PORTAL", size=14, weight=ft.FontWeight.W_800), progress_ring], spacing=15), 
            ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON), radius=18)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

    content_area = ft.Container(padding=32, expand=True, content=views["analytics"])
    main_layout = ft.Row([sidebar, ft.Column([header, content_area], expand=True, spacing=0)], expand=True, spacing=0)

    page.add(main_layout)
    refresh_ui_data()
    route_change("analytics")

if __name__ == '__main__':
    upload_path = os.path.abspath("uploads")
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550, upload_dir=upload_path)
