"""
TR: Ana panel sayfasi — aile harcama ozeti.
EN: Dashboard page — family spending overview.
"""
from nicegui import ui, app
from i18n import t
from theme.style import Theme
from services import db_service

# TR: Aile harcamalarini ozetleyen ana panel
# EN: Main dashboard summarizing family spending


def dashboard_page():
    # TR: Kullanici dili ve aile bilgisini al
    # EN: Load user language and family info
    lang = app.storage.user.get("language", "en")
    family_id = app.storage.user.get("family_id")

    with ui.row().classes("w-full justify-between items-center mb-6 fade-in"):
        with ui.column().classes("gap-0"):
            ui.label(t("dashboard_title", lang)).classes("text-2xl font-bold").style(f"color:{Theme.TEXT}")
            ui.label(t("dashboard_subtitle", lang)).classes("text-sm").style(f"color:{Theme.TEXT_MUTED}")
        with ui.row().classes("items-center gap-2"):
            # TR: Aylik PDF raporu indir
            # EN: Download monthly PDF report
            def _download_monthly():
                from services import export_service
                from datetime import datetime
                now = datetime.utcnow()
                pdf_path = export_service.generate_monthly_pdf(family_id, now.year, now.month)
                if pdf_path:
                    ui.download(pdf_path)
                    ui.notify(t("success", lang) if "success" in t.__globals__.get('TR', {}) else "Rapor İndirildi", type="positive")
                else:
                    ui.notify(t("no_data", lang), type="warning")
            ui.button("Aylık PDF", icon="picture_as_pdf", on_click=_download_monthly).props("outline dense").style(f"color:{Theme.PRIMARY}; border-color:{Theme.PRIMARY}")
            ui.label(t("this_month", lang)).classes("text-sm px-4 py-2 rounded-xl").style(f"background:rgba(167,139,250,0.1);color:{Theme.PRIMARY}")

    if not family_id:
        # TR: Aile yoksa kullaniciyi aile sayfasina yonlendir
        # EN: If no family, prompt user to create/join one
        with ui.card().classes("glass-card p-12 w-full items-center fade-in"):
            ui.icon("family_restroom").classes("text-6xl mb-4").style(f"color:{Theme.PRIMARY};opacity:0.5")
            ui.label(t("no_family", lang)).classes("text-xl font-semibold mb-2").style(f"color:{Theme.TEXT}")
            ui.button(t("nav_family", lang), on_click=lambda: ui.navigate.to("/family")).classes("btn-primary")
        return

    # TR: Ozet metrikleri al
    # EN: Fetch summary metrics
    summary = db_service.get_family_summary(family_id)
    family = db_service.get_family(family_id)
    budget = family.get("monthly_budget", 0) if family else 0

    with ui.row().classes("w-full gap-5 mb-6 fade-in"):
        # TR: KPI kartlari
        # EN: KPI cards
        _kpi(t("total_spending", lang), f"₺{summary.get('total',0):,.2f}", "payments", Theme.PRIMARY)
        _kpi(t("avg_receipt", lang), f"₺{summary.get('avg',0):,.2f}", "receipt", Theme.SECONDARY)
        _kpi(t("total_receipts", lang), str(summary.get("count",0)), "description", Theme.ACCENT)
        _kpi(t("top_category", lang), t(f"cat_{summary.get('top_category','N/A')}", lang), "category", Theme.SUCCESS)

    if budget > 0:
        # TR: Butce sagligini gorelilestir ve ilerleme cubugu goster
        # EN: Visualize budget health with a progress bar
        spent = summary.get("total", 0)
        pct = min(spent / budget, 1.0)
        clr = Theme.SUCCESS if pct < 0.7 else (Theme.WARNING if pct < 0.9 else Theme.ERROR)
        with ui.card().classes("glass-card p-6 mb-6 w-full fade-in"):
            with ui.row().classes("w-full justify-between items-center mb-3"):
                ui.label(t("budget_health", lang)).classes("text-lg font-semibold").style(f"color:{Theme.TEXT}")
                ui.label(f"₺{spent:,.2f} / ₺{budget:,.2f}").classes("text-sm").style(f"color:{Theme.TEXT_MUTED}")
            ui.linear_progress(value=pct).props(f'color="{clr}" size="12px" rounded')

    with ui.row().classes("w-full gap-5 fade-in"):
        with ui.card().classes("glass-card p-6 flex-1"):
            # TR: Uye bazli harcamalar
            # EN: Member spending breakdown
            ui.label(t("member_spending", lang)).classes("text-lg font-semibold mb-4").style(f"color:{Theme.TEXT}")
            mdata = db_service.get_member_spending(family_id)
            mtotal = sum(m.get("total",0) for m in mdata) or 1
            colors = [Theme.PRIMARY, Theme.SECONDARY, Theme.ACCENT, Theme.SUCCESS, Theme.WARNING]
            for i, m in enumerate(mdata):
                clr = colors[i % len(colors)]
                with ui.column().classes("w-full mb-4"):
                    with ui.row().classes("w-full justify-between items-center"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("person").style(f"color:{clr}")
                            ui.label(m.get("_id","?")).classes("font-medium").style(f"color:{Theme.TEXT}")
                        with ui.row().classes("items-center gap-2"):
                            ui.label(f"₺{m.get('total',0):,.2f}").classes("font-semibold").style(f"color:{Theme.TEXT}")
                            def _dl_user(e, un):
                                # TR: Uye bazli raporu indir
                                # EN: Download per-user report
                                from services import export_service
                                pdf_path = export_service.generate_user_pdf(family_id, un)
                                if pdf_path:
                                    ui.download(pdf_path)
                                    ui.notify(t("success", lang) if "success" in t.__globals__.get('TR', {}) else "Rapor İndirildi", type="positive")
                            ui.button(icon="picture_as_pdf", on_click=lambda e, un=m.get("_id"): _dl_user(e, un)).props("flat dense round").style(f"color:{Theme.TEXT_MUTED}")
                    ui.linear_progress(value=m.get("total",0)/mtotal).props(f'color="{clr}" size="8px" rounded')
            if not mdata:
                ui.label(t("no_data", lang)).style(f"color:{Theme.TEXT_MUTED}")

        with ui.card().classes("glass-card p-6 flex-1"):
            # TR: Son fis listesi
            # EN: Recent receipts list
            ui.label(t("recent_receipts", lang)).classes("text-lg font-semibold mb-4").style(f"color:{Theme.TEXT}")
            receipts = db_service.get_receipts_by_family(family_id, limit=5)
            for r in receipts:
                cat = r.get("category","Other")
                cc = Theme.CATEGORY_COLORS.get(cat, Theme.TEXT_MUTED)
                ic = {"Market":"shopping_cart","Food":"restaurant","Electronics":"devices","Travel":"flight","Health":"local_hospital","Clothing":"checkroom","Education":"school","Bills":"receipt"}.get(cat,"category")
                with ui.row().classes("w-full justify-between items-center py-3").style(f"border-bottom:1px solid {Theme.BORDER}"):
                    with ui.row().classes("items-center gap-3"):
                        ui.icon(ic).style(f"color:{cc}")
                        with ui.column().classes("gap-0"):
                            ui.label(r.get("store_name","-")).classes("font-medium text-sm").style(f"color:{Theme.TEXT}")
                            ui.label(r.get("date","-")).classes("text-xs").style(f"color:{Theme.TEXT_MUTED}")
                    ui.label(f"₺{r.get('total_amount',0):,.2f}").classes("font-semibold").style(f"color:{Theme.TEXT}")
            if not receipts:
                ui.label(t("no_data", lang)).style(f"color:{Theme.TEXT_MUTED}")


def _kpi(label, value, icon, color):
    with ui.card().classes("kpi-card flex-1"):
        with ui.row().classes("w-full justify-between items-start"):
            with ui.column().classes("gap-1"):
                ui.label(label.upper()).classes("text-xs font-bold tracking-wide").style(f"color:{Theme.TEXT_MUTED}")
                ui.label(value).classes("text-2xl font-bold mt-1").style(f"color:{Theme.TEXT}")
            ui.icon(icon).classes("text-2xl p-2 rounded-xl").style(f"color:{color};background:{color}15;")
