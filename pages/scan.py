"""
TR: Fis tarama sayfasi — gorsel yukleme, Gemini analiz, birlestirme.
EN: Receipt scanning page — image upload, Gemini analysis, merging.
"""
import os, uuid
from datetime import datetime, timedelta
from nicegui import ui, app, events
from i18n import t
from theme.style import Theme
from services import db_service, ocr_service
from config import settings

# TR: Fis yukleme ve Gemini analizi akisini yoneten sayfa
# EN: Page that handles receipt upload and Gemini analysis


def scan_page():
    # TR: Kullanici ve aile bilgilerini al
    # EN: Get user and family context
    lang = app.storage.user.get("language", "en")
    family_id = app.storage.user.get("family_id")
    user_id = app.storage.user.get("user_id")
    user_name = app.storage.user.get("user_name")

    with ui.row().classes("w-full justify-between items-center mb-6 fade-in"):
        with ui.column().classes("gap-0"):
            ui.label(t("scan_title", lang)).classes("text-2xl font-bold").style(f"color:{Theme.TEXT}")
            ui.label(t("scan_subtitle", lang)).classes("text-sm").style(f"color:{Theme.TEXT_MUTED}")

    if not family_id:
        # TR: Aile yoksa bilgi mesaji goster
        # EN: Show message if user is not in a family
        ui.label(t("no_family", lang)).style(f"color:{Theme.TEXT_MUTED}")
        return

    # TR: Analiz sonucunu ve dosya yolunu saklayan basit state
    # EN: Simple state for analysis result and file path
    analysis_result = {"data": None, "image_path": None}

    # --- Upload Zone ---
    # TR: Dosya yukleme ve drag-drop alani
    # EN: Upload and drag-drop area
    with ui.card().classes("glass-card p-8 w-full mb-6 upload-zone fade-in"):
        with ui.column().classes("w-full items-center"):
            ui.icon("cloud_upload").classes("text-5xl mb-3").style(f"color:{Theme.PRIMARY};opacity:0.6")
            ui.label(t("drag_drop", lang)).classes("text-lg font-medium mb-1").style(f"color:{Theme.TEXT}")
            ui.label(t("supported_formats", lang)).classes("text-xs mb-4").style(f"color:{Theme.TEXT_MUTED}")

            async def handle_upload(e: events.UploadEventArguments):
                # TR: Dosya uzantisini kontrol et
                # EN: Validate file extension
                ext = os.path.splitext(e.file.name)[1].lower()
                if ext not in (".png", ".jpg", ".jpeg"):
                    ui.notify("Unsupported format", type="negative")
                    return

                # TR: Dosyayi disk uzerine kaydet
                # EN: Persist the uploaded file to disk
                filename = f"{uuid.uuid4().hex}{ext}"
                filepath = os.path.join(settings.UPLOAD_DIR, filename)
                with open(filepath, "wb") as f:
                    f.write(await e.file.read())

                # TR: Analiz icin state'i guncelle
                # EN: Update state for analysis
                analysis_result["image_path"] = filepath
                ui.notify(t("analyzing", lang), type="info", spinner=True, timeout=10000)

                try:
                    # TR: Gemini OCR analizini calistir
                    # EN: Run Gemini OCR analysis
                    data = await ocr_service.analyze_receipt(filepath)
                    analysis_result["data"] = data
                    _show_result(data, lang, family_id, user_id, user_name, filepath, result_container)
                    ui.notify(t("analysis_complete", lang), type="positive")
                except Exception as ex:
                    ui.notify(f"{t('analysis_failed', lang)}: {ex}", type="negative")

            ui.upload(
                on_upload=handle_upload,
                max_file_size=settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024,
                auto_upload=True,
                label=t("upload_receipt", lang),
            ).classes("w-64").props('accept=".png,.jpg,.jpeg"')

    # --- Result Container ---
    # TR: Analiz sonucu UI'yi buraya render ediyoruz
    # EN: Render analysis result UI here
    result_container = ui.column().classes("w-full fade-in")


def _show_result(data, lang, family_id, user_id, user_name, image_path, container):
    # TR: Sonuc kartini tekrar olusturmak icin eski icerigi temizle
    # EN: Clear container before rebuilding result card
    container.clear()
    with container:
        with ui.card().classes("glass-card p-6 w-full"):
            ui.label(t("analysis_complete", lang)).classes("text-lg font-semibold mb-4").style(f"color:{Theme.SUCCESS}")

            with ui.row().classes("w-full gap-6"):
                # Left: Extracted Data (editable)
                # TR: Modelden gelen alanlari kullaniciya duzeltilebilir sun
                # EN: Present model output as editable fields
                with ui.column().classes("flex-1 gap-3"):
                    store_input = ui.input(label=t("store_name", lang), value=data.get("store_name","")).classes("w-full")
                    date_input = ui.input(label=t("receipt_date", lang), value=data.get("date","")).classes("w-full")
                    amount_input = ui.number(label=f"{t('total_amount', lang)} (₺)", value=data.get("total_amount",0), format="%.2f").classes("w-full")

                    cat_options = ["Market","Food","Electronics","Travel","Health","Clothing","Education","Bills","Other"]
                    category_select = ui.select(cat_options, label=t("category", lang), value=data.get("category","Other")).classes("w-full")

                    receipt_type = ui.select(
                        [t("store_receipt", lang), t("pos_receipt", lang)],
                        label=t("receipt_type", lang),
                        value=t("store_receipt", lang),
                    ).classes("w-full")

                # Right: Items + Barcodes
                # TR: Urun listesi ve barkodlari goruntule
                # EN: Show items and barcodes
                with ui.column().classes("flex-1 gap-3"):
                    ui.label(t("items", lang)).classes("font-semibold").style(f"color:{Theme.TEXT}")
                    items = data.get("items", [])
                    if items:
                        for item in items:
                            with ui.row().classes("w-full items-center gap-2"):
                                ui.label(item.get("name","")).classes("text-sm flex-1").style(f"color:{Theme.TEXT}")
                                ui.label(f"x{item.get('quantity',1)}").classes("text-xs").style(f"color:{Theme.TEXT_MUTED}")
                                ui.label(f"₺{item.get('price',0):.2f}").classes("text-sm font-medium").style(f"color:{Theme.TEXT}")
                    else:
                        ui.label(t("no_data", lang)).classes("text-sm").style(f"color:{Theme.TEXT_MUTED}")

                    barcodes = data.get("barcodes", [])
                    if barcodes:
                        ui.separator()
                        ui.label(t("barcode", lang)).classes("font-semibold").style(f"color:{Theme.TEXT}")
                        for bc in barcodes:
                            ui.label(f"📊 {bc}").classes("text-sm font-mono").style(f"color:{Theme.SECONDARY}")

            # --- Warranty ---
            # TR: Garanti bilgisi ekleme secenegi
            # EN: Warranty info toggle
            has_warranty = ui.checkbox(t("add_warranty", lang), value=data.get("has_warranty", False)).classes("mt-4")
            warranty_months_input = ui.number(
                label=t("warranty_months", lang),
                value=data.get("warranty_months", settings.WARRANTY_DEFAULTS.get(data.get("category","Other"), 0)),
            ).classes("w-48")
            warranty_months_input.bind_visibility_from(has_warranty, "value")

            product_name_input = ui.input(label=t("product_name", lang), value=data.get("product_name", "")).classes("w-full")
            product_name_input.bind_visibility_from(has_warranty, "value")

            # --- Merge Option ---
            # TR: POS + magaza fisini birlestirme secenegi
            # EN: Option to merge store/POS receipts
            ui.separator().classes("my-4")
            merge_check = ui.checkbox(t("merge_with", lang), value=False)
            unlinked = db_service.get_unlinked_receipts(family_id, limit=10)
            merge_options = {f"{r.get('store_name','')} - ₺{r.get('total_amount',0):.2f} ({r.get('date','')})": r["_id"] for r in unlinked}
            merge_select = ui.select(list(merge_options.keys()), label=t("select_receipt_to_merge", lang)).classes("w-full")
            merge_select.bind_visibility_from(merge_check, "value")

            # --- Save Button ---
            # TR: Kaydetme islemini baslat
            # EN: Trigger save flow
            async def save_receipt():
                # TR: Fis turunu normalize et
                # EN: Normalize receipt type
                rtype_val = receipt_type.value
                rtype = "store" if rtype_val == t("store_receipt", lang) else "pos"

                # TR: Garanti alanlarini derle
                # EN: Build warranty payload
                warranty_info = None
                if has_warranty.value:
                    months = int(warranty_months_input.value or 0)
                    try:
                        rd = datetime.strptime(date_input.value, "%Y-%m-%d")
                        expiry = (rd + timedelta(days=months * 30)).strftime("%Y-%m-%d")
                    except Exception:
                        expiry = None
                    warranty_info = {
                        "has_warranty": True,
                        "warranty_months": months,
                        "expiry_date": expiry,
                        "product_name": product_name_input.value,
                    }

                # TR: Barkod görsellerini oluştur | EN: Generate barcode images
                barcode_images = {}
                for bc in barcodes:
                    img_path = ocr_service.generate_barcode_image(bc)
                    if img_path:
                        barcode_images[bc] = img_path

                # TR: Kaydedilecek dokumani olustur
                # EN: Compose receipt document to persist
                doc = {
                    "family_id": family_id,
                    "uploaded_by": {"user_id": user_id, "name": user_name},
                    "store_name": store_input.value,
                    "date": date_input.value,
                    "total_amount": float(amount_input.value or 0),
                    "currency": "TRY",
                    "category": category_select.value,
                    "items": data.get("items", []),
                    "barcodes": barcodes,
                    "barcode_images": barcode_images,
                    "receipt_type": rtype,
                    "receipt_group_id": None,
                    "image_path": image_path,
                    "warranty_info": warranty_info or {"has_warranty": False},
                }

                # TR: Fis kaydini veritabanina ekle
                # EN: Insert receipt into database
                receipt_id = db_service.insert_receipt(doc)

                if merge_check.value and merge_select.value:
                    # TR: Birlestirme icin group_id ata
                    # EN: Assign group_id to link receipts
                    other_id = merge_options[merge_select.value]
                    group_id = uuid.uuid4().hex
                    db_service.link_receipts(receipt_id, other_id, group_id)
                    ui.notify(t("merge_success", lang), type="positive")

                saved_count = len(barcode_images)
                if barcodes:
                    # TR: Barkod gorsel sayisini bilgilendir
                    # EN: Inform how many barcode images were generated
                    ui.notify(f"✅ {saved_count}/{len(barcodes)} barcode images generated", type="info")

                # TR: Basarili kayit bildirimi ve UI temizligi
                # EN: Success notification and UI reset
                ui.notify(t("success", lang), type="positive")
                container.clear()
                with container:
                    ui.label("✅ " + t("success", lang)).classes("text-lg").style(f"color:{Theme.SUCCESS}")

            ui.button(t("save_receipt", lang), on_click=save_receipt, icon="save").classes("btn-primary mt-4 self-end")
