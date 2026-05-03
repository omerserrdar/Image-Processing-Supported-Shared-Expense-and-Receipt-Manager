"""
TR: Garanti takibi sayfasi — aktif garantiler, barkod gosterimi.
EN: Warranty tracking page — active warranties, barcode display.
"""
import os
from datetime import datetime
from nicegui import ui, app
from i18n import t
from theme.style import Theme
from services import db_service, ocr_service

# TR: Garanti kayitlarini listeleyen ve barkod gosteren sayfa
# EN: Page that lists warranties and displays barcodes


def warranty_page():
    # TR: Dil ve aile context
    # EN: Language and family context
    lang = app.storage.user.get("language", "en")
    family_id = app.storage.user.get("family_id")

    with ui.row().classes("w-full justify-between items-center mb-6 fade-in"):
        with ui.column().classes("gap-0"):
            ui.label(t("warranty_title", lang)).classes("text-2xl font-bold").style(f"color:{Theme.TEXT}")
            ui.label(t("warranty_subtitle", lang)).classes("text-sm").style(f"color:{Theme.TEXT_MUTED}")

    if not family_id:
        # TR: Aile yoksa bilgi goster
        # EN: Show info when no family exists
        ui.label(t("no_family", lang)).style(f"color:{Theme.TEXT_MUTED}")
        return

    # TR: Garanti bilgisi olan fisleri getir
    # EN: Fetch receipts that include warranty info
    warranties = db_service.get_warranty_receipts(family_id)
    today = datetime.utcnow().date()

    # TR: Aktif/yakinda dolacak/suresi dolmus olarak ayir
    # EN: Split into active/expiring soon/expired buckets
    active, expiring, expired = [], [], []
    for w in warranties:
        wi = w.get("warranty_info", {})
        expiry_str = wi.get("expiry_date")
        if not expiry_str:
            active.append(w)
            continue
        try:
            expiry = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            if expiry < today:
                expired.append(w)
            elif (expiry - today).days <= 30:
                expiring.append(w)
            else:
                active.append(w)
        except ValueError:
            active.append(w)

    # --- Stats ---
    # TR: Durum metrikleri
    # EN: Status metrics
    with ui.row().classes("w-full gap-5 mb-6 fade-in"):
        _stat_card(t("active_warranties", lang), str(len(active)), "verified_user", Theme.SUCCESS)
        _stat_card(t("expiring_soon", lang), str(len(expiring)), "warning", Theme.WARNING)
        _stat_card(t("expired_warranties", lang), str(len(expired)), "error", Theme.ERROR)

    # --- Active + Expiring ---
    # TR: Listeyi oncelik sirasiyla birlestir
    # EN: Merge lists in priority order
    all_items = [(w, "active") for w in active] + [(w, "expiring") for w in expiring] + [(w, "expired") for w in expired]

    if not all_items:
        with ui.card().classes("glass-card p-12 w-full items-center fade-in"):
            ui.icon("verified_user").classes("text-6xl mb-4").style(f"color:{Theme.PRIMARY};opacity:0.3")
            ui.label(t("no_data", lang)).classes("text-lg").style(f"color:{Theme.TEXT_MUTED}")
        return

    with ui.column().classes("w-full gap-4 fade-in"):
        for w, status in all_items:
            wi = w.get("warranty_info", {})
            expiry_str = wi.get("expiry_date", "")
            product = wi.get("product_name") or w.get("store_name", "")
            barcodes = w.get("barcodes", [])

            # TR: Kalan gun sayisini hesapla
            # EN: Calculate remaining days
            days_left = None
            if expiry_str:
                try:
                    expiry = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                    days_left = (expiry - today).days
                except ValueError:
                    pass

            # TR: Duruma gore renk/ikon sec
            # EN: Choose color/icon by status
            if status == "expired":
                border_color = Theme.ERROR
                status_icon = "cancel"
            elif status == "expiring":
                border_color = Theme.WARNING
                status_icon = "warning"
            else:
                border_color = Theme.SUCCESS
                status_icon = "check_circle"

            with ui.card().classes("glass-card p-5 w-full").style(f"border-left:4px solid {border_color} !important"):
                with ui.row().classes("w-full justify-between items-center"):
                    with ui.row().classes("items-center gap-3"):
                        ui.icon(status_icon).classes("text-xl").style(f"color:{border_color}")
                        with ui.column().classes("gap-0"):
                            ui.label(product).classes("font-semibold text-base").style(f"color:{Theme.TEXT}")
                            ui.label(f"{w.get('store_name','')} — {w.get('date','')}").classes("text-xs").style(f"color:{Theme.TEXT_MUTED}")

                    with ui.row().classes("items-center gap-4"):
                        if days_left is not None:
                            if days_left > 0:
                                ui.label(f"{days_left} {t('days_remaining', lang)}").classes("text-sm font-medium").style(f"color:{border_color}")
                            else:
                                ui.label(t("warranty_expired", lang)).classes("text-sm font-medium").style(f"color:{Theme.ERROR}")

                        if barcodes:
                            # TR: Barkod dialogunu ac
                            # EN: Open barcode dialog
                            ui.button(t("show_barcode", lang), icon="qr_code",
                                      on_click=lambda _, bcs=barcodes, prod=product: _show_barcode_dialog(bcs, prod, lang)).props("flat dense").style(f"color:{Theme.SECONDARY}")


def _show_barcode_dialog(barcodes, product_name, lang):
    # TR: Barkodlari modal icinde goster
    # EN: Display barcodes inside a modal dialog
    with ui.dialog() as dlg, ui.card().classes("glass-card p-6 items-center").style("min-width:350px"):
        ui.label(product_name).classes("text-lg font-bold mb-2").style(f"color:{Theme.TEXT}")
        ui.label(t("barcode", lang)).classes("text-sm mb-4").style(f"color:{Theme.TEXT_MUTED}")

        for bc in barcodes:
            ui.label(bc).classes("text-xl font-mono font-bold tracking-widest mb-2").style(f"color:{Theme.SECONDARY}")

            # TR: Barkod gorselini olustur
            # EN: Generate barcode image
            barcode_path = ocr_service.generate_barcode_image(bc)
            if barcode_path and os.path.exists(barcode_path):
                ui.image(barcode_path).classes("w-64 mb-4")
            else:
                ui.label("⚠️ Could not generate barcode image").classes("text-sm").style(f"color:{Theme.WARNING}")

            ui.separator()

        ui.button(t("back", lang), on_click=dlg.close).props("flat").style(f"color:{Theme.PRIMARY}")
    dlg.open()


def _stat_card(label, value, icon, color):
    # TR: Ust KPI karti
    # EN: Top KPI card
    with ui.card().classes("kpi-card flex-1"):
        with ui.row().classes("items-center gap-3"):
            ui.icon(icon).classes("text-2xl").style(f"color:{color}")
            with ui.column().classes("gap-0"):
                ui.label(value).classes("text-2xl font-bold").style(f"color:{Theme.TEXT}")
                ui.label(label).classes("text-xs font-bold").style(f"color:{Theme.TEXT_MUTED}")
