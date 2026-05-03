"""
TR: Fis gecmisi sayfasi — tablo, filtreleme, detay, silme.
EN: Receipt history page — table, filtering, detail, deletion.
"""
from nicegui import ui, app
from i18n import t
from theme.style import Theme
from services import db_service

# TR: Fis gecmisi, detay ve silme islemlerini yoneten sayfa
# EN: Page for receipt history, detail view, and deletion


def receipts_page():
    # TR: Dil ve aile bilgisini getir
    # EN: Load language and family context
    lang = app.storage.user.get("language", "en")
    family_id = app.storage.user.get("family_id")

    with ui.row().classes("w-full justify-between items-center mb-6 fade-in"):
        with ui.column().classes("gap-0"):
            ui.label(t("receipts_title", lang)).classes("text-2xl font-bold").style(f"color:{Theme.TEXT}")
            ui.label(t("receipts_subtitle", lang)).classes("text-sm").style(f"color:{Theme.TEXT_MUTED}")
        ui.button(t("add_receipt", lang), icon="add", on_click=lambda: ui.navigate.to("/scan")).classes("btn-primary")

    if not family_id:
        # TR: Aile yoksa bilgi goster
        # EN: Show info when no family exists
        ui.label(t("no_family", lang)).style(f"color:{Theme.TEXT_MUTED}")
        return

    table_container = ui.column().classes("w-full fade-in")
    _render_table(table_container, family_id, lang)


def _render_table(container, family_id, lang):
    # TR: Tabloyu yeniden render etmek icin container'i temizle
    # EN: Clear container before rendering the table
    container.clear()
    receipts = db_service.get_receipts_by_family(family_id, limit=200)

    with container:
        if not receipts:
            # TR: Fis yoksa bos durum goster
            # EN: Show empty state when no receipts
            with ui.card().classes("glass-card p-12 w-full items-center"):
                ui.icon("receipt_long").classes("text-6xl mb-4").style(f"color:{Theme.PRIMARY};opacity:0.3")
                ui.label(t("no_data", lang)).classes("text-lg").style(f"color:{Theme.TEXT_MUTED}")
            return

        with ui.card().classes("glass-card p-4 w-full"):
            # TR: Tablo kolonlari
            # EN: Table columns
            columns = [
                {"name": "date", "label": t("date", lang), "field": "date", "sortable": True, "align": "left"},
                {"name": "store", "label": t("store", lang), "field": "store_name", "sortable": True, "align": "left"},
                {"name": "category", "label": t("category", lang), "field": "category", "sortable": True, "align": "left"},
                {"name": "amount", "label": t("amount", lang), "field": "amount_str", "sortable": True, "align": "right"},
                {"name": "uploaded_by", "label": t("uploaded_by", lang), "field": "uploaded_by", "align": "left"},
                {"name": "type", "label": t("receipt_type", lang), "field": "receipt_type", "align": "center"},
            ]

            # TR: Tablo satirlari
            # EN: Table rows
            rows = []
            for r in receipts:
                rows.append({
                    "id": r["_id"],
                    "date": r.get("date", "-"),
                    "store_name": r.get("store_name", "-"),
                    "category": t(f"cat_{r.get('category','Other')}", lang),
                    "amount_str": f"₺{r.get('total_amount',0):,.2f}",
                    "uploaded_by": r.get("uploaded_by", {}).get("name", "-"),
                    "receipt_type": r.get("receipt_type", "store").upper(),
                })

            # TR: NiceGUI tablo bileşeni
            # EN: NiceGUI table component
            table = ui.table(columns=columns, rows=rows, row_key="id").classes("w-full")
            table.add_slot("body-cell-amount", """
                <q-td :props="props" class="text-right">
                    <span class="font-semibold">{{ props.value }}</span>
                </q-td>
            """)

            # Detail + Delete Dialogs
            # TR: Arama/filtreleme inputu
            # EN: Search/filter input
            with ui.row().classes("w-full justify-end mt-3 gap-2"):
                search_input = ui.input(placeholder=t("search", lang)).props("dense outlined").classes("w-48")
                search_input.on("update:model-value", lambda e: table.filter(e.args))

        # --- Receipt Detail Dialog ---
        # TR: Satira tiklandiginda detay modalini ac
        # EN: Open detail modal when a row is clicked
        def show_detail(receipt_id):
            r = db_service.get_receipt_by_id(receipt_id)
            if not r:
                return
            with ui.dialog() as dlg, ui.card().classes("glass-card p-6").style("min-width:400px"):
                ui.label(r.get("store_name", "-")).classes("text-xl font-bold").style(f"color:{Theme.TEXT}")
                category_key = f"cat_{r.get('category', 'Other')}"
                ui.label(f"{r.get('date','-')} | {t(category_key, lang)}").style(f"color:{Theme.TEXT_MUTED}")
                ui.separator()
                ui.label(f"₺{r.get('total_amount',0):,.2f}").classes("text-2xl font-bold my-2").style(f"color:{Theme.PRIMARY}")

                # TR: Urun detaylari
                # EN: Item details
                items = r.get("items", [])
                if items:
                    for item in items:
                        with ui.row().classes("w-full justify-between"):
                            ui.label(f"{item.get('name','')} x{item.get('quantity',1)}").style(f"color:{Theme.TEXT}")
                            ui.label(f"₺{item.get('price',0):.2f}").style(f"color:{Theme.TEXT}")

                # TR: Barkodlar ve barkod gorselleri
                # EN: Barcodes and barcode images
                barcodes = r.get("barcodes", [])
                if barcodes:
                    ui.separator().classes("my-2")
                    ui.label(t("barcode", lang)).classes("font-semibold text-sm").style(f"color:{Theme.TEXT_MUTED}")
                    for bc in barcodes:
                        with ui.column().classes("w-full items-center gap-1 my-2"):
                            import os
                            from services import ocr_service
                            
                            # TR: Veritabanindaki gorsel yolunu al, yoksa yeniden uret
                            # EN: Use stored image path or generate on the fly
                            barcode_images = r.get("barcode_images", {})
                            img_path = barcode_images.get(bc)
                            if not img_path or not os.path.exists(img_path):
                                img_path = ocr_service.generate_barcode_image(bc)
                            
                            if img_path and os.path.exists(img_path):
                                ui.image(img_path).classes("w-48")
                            
                            ui.label(bc).classes("font-mono text-xs tracking-widest font-bold").style(f"color:{Theme.SECONDARY}")

                # TR: Bagli fis var mi kontrol et
                # EN: Check for linked receipt
                linked = db_service.get_linked_receipt(receipt_id)
                if linked:
                    ui.separator()
                    ui.label(f"🔗 {t('linked_receipt', lang)}: {linked.get('store_name','')} - ₺{linked.get('total_amount',0):.2f}").style(f"color:{Theme.ACCENT}")

                with ui.row().classes("w-full justify-end mt-4 gap-2"):
                    # TR: Fis PDF indir
                    # EN: Download receipt PDF
                    def _download_pdf():
                        from services import export_service
                        pdf_path = export_service.generate_receipt_pdf(r)
                        if pdf_path:
                            ui.download(pdf_path)
                            ui.notify(t("success", lang) if "success" in t.__globals__.get('TR', {}) else "PDF İndirildi", type="positive")
                            
                    ui.button("PDF", icon="picture_as_pdf", on_click=_download_pdf).props("flat").style(f"color:{Theme.PRIMARY}")
                    ui.button(t("delete", lang), icon="delete", color="red",
                              on_click=lambda: _delete(receipt_id, dlg, container, family_id, lang)).props("flat")
                    ui.button(t("back", lang), on_click=dlg.close).props("flat")
            dlg.open()

        def _delete(rid, dlg, container, fid, lang):
            # TR: Fisi sil ve tabloyu guncelle
            # EN: Delete receipt and refresh table
            db_service.delete_receipt(rid)
            dlg.close()
            ui.notify(t("receipt_deleted", lang), type="positive")
            _render_table(container, fid, lang)

        # TR: Tablo satiri tiklama eventi
        # EN: Row click handler
        table.on("row-click", lambda e: show_detail(e.args[1]["id"]))
