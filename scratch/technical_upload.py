import flet as ft
import os

def main(page: ft.Page):
    # --- 1. Klasör Kontrolü ---
    # uploads klasörü yoksa fiziksel olarak oluşturulur
    upload_path = os.path.join(os.getcwd(), "uploads")
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    # --- 2. Sayfa ve URL Yapılandırması ---
    page.title = "Flet Web - Teknik Dosya Yükleme"
    # Kullanıcının istediği özel upload base URL tanımı
    page.upload_url = "/api/upload" 
    
    # İlerleme durumunu göstermek için bir UI bileşeni
    progress_bar = ft.ProgressBar(width=400, color="blue", visible=False)
    status_text = ft.Text()

    # --- 3. on_upload (İlerleme Takibi) Olayı ---
    def on_upload_progress(e: ft.FilePickerUploadEvent):
        """Dosya yüklenirken ilerleme durumunu yakalar"""
        progress_bar.visible = True
        progress_bar.value = e.progress
        status_text.value = f"Yükleniyor: %{int(e.progress * 100)} - {e.file_name}"
        
        if e.progress == 1.0:
            status_text.value = f"Başarılı: {e.file_name} fiziksel olarak uploads/ klasörüne kaydedildi."
            status_text.color = "green"
            progress_bar.visible = False
        
        page.update()

    # --- 4. on_result (Dosya Seçme Sonrası) Mantığı ---
    def process_result(e: ft.FilePickerResultEvent):
        """Dosya seçildikten sonra upload listesini hazırlar ve başlatır"""
        if e.files:
            upload_files_list = []
            for f in e.files:
                # Her dosya için 600 saniye (10 dk) geçerli imzalı URL üretilir
                # page.upload_url ile uyumlu çalışır
                destination_url = page.get_upload_url(f.name, 600)
                
                upload_files_list.append(
                    ft.FilePickerUploadFile(
                        f.name,
                        upload_url=destination_url,
                    )
                )
            
            # Yükleme işlemini fiziksel olarak başlat
            picker.upload(upload_files_list)
            page.update()

    # --- 5. FilePicker Tanımı ---
    picker = ft.FilePicker(
        on_result=process_result,
        on_upload=on_upload_progress
    )
    page.overlay.append(picker)

    # --- 6. Arayüz ---
    page.add(
        ft.Column([
            ft.Text("Güvenli Dosya Yükleme Paneli", size=20, weight="bold"),
            ft.ElevatedButton(
                "Yüklenecek Dosyayı Seç", 
                icon=ft.icons.FOLDER_OPEN,
                on_click=lambda _: picker.pick_files(allow_multiple=True)
            ),
            ft.Divider(),
            status_text,
            progress_bar
        ], horizontal_alignment="center", spacing=20)
    )

# --- 7. Uygulama Başlatma ---
if __name__ == "__main__":
    os.environ["FLET_SECRET_KEY"] = "flet_secret_key_123"
    # upload_dir: Flet sunucusunun dosyaları kaydedeceği fiziksel yol
    ft.app(
        target=main, 
        view=ft.AppView.WEB_BROWSER,
        upload_dir="uploads",
        port=8551
    )
