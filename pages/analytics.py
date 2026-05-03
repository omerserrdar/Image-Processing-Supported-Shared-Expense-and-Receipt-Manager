"""
TR: Analitik sayfasi — grafikler ve istatistikler.
EN: Analytics page — charts and statistics.
"""
from nicegui import ui, app
from i18n import t
from theme.style import Theme
from services import db_service

# TR: Analitik ekraninda harcama trendleri ve dagilimlar gosterilir
# EN: Analytics screen shows spending trends and distributions


def analytics_page():
    # TR: Dil ve aile bilgisini hazirla
    # EN: Prepare language and family context
    lang = app.storage.user.get("language", "en")
    family_id = app.storage.user.get("family_id")

    with ui.row().classes("w-full justify-between items-center mb-6 fade-in"):
        with ui.column().classes("gap-0"):
            ui.label(t("analytics_title", lang)).classes("text-2xl font-bold").style(f"color:{Theme.TEXT}")
            ui.label(t("analytics_subtitle", lang)).classes("text-sm").style(f"color:{Theme.TEXT_MUTED}")

    if not family_id:
        # TR: Aile yoksa bilgi mesaji goster
        # EN: Show message when no family exists
        ui.label(t("no_family", lang)).style(f"color:{Theme.TEXT_MUTED}")
        return

    # --- Daily Spending Trend (Bar Chart) ---
    # TR: Gunluk harcama trendini bar chart ile goster
    # EN: Render daily spending trend as a bar chart
    with ui.card().classes("glass-card p-6 w-full mb-6 fade-in"):
        ui.label(t("spending_trend", lang)).classes("text-lg font-semibold mb-4").style(f"color:{Theme.TEXT}")
        daily = db_service.get_daily_spending(family_id)
        if daily:
            # TR: EChart konfigrasyonu
            # EN: EChart configuration
            chart_opts = {
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": [d.get("_id", "") for d in daily],
                           "axisLabel": {"color": Theme.TEXT_MUTED}},
                "yAxis": {"type": "value", "axisLabel": {"color": Theme.TEXT_MUTED, "formatter": "₺{value}"}},
                "series": [{
                    "data": [round(d.get("total", 0), 2) for d in daily],
                    "type": "bar",
                    "itemStyle": {
                        "color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                  "colorStops": [
                                      {"offset": 0, "color": Theme.PRIMARY},
                                      {"offset": 1, "color": Theme.PRIMARY_DARK},
                                  ]},
                        "borderRadius": [6, 6, 0, 0],
                    },
                }],
                "grid": {"left": "10%", "right": "5%", "bottom": "15%"},
                "backgroundColor": "transparent",
            }
            ui.echart(chart_opts).classes("w-full").style("height:300px")
        else:
            ui.label(t("no_data", lang)).style(f"color:{Theme.TEXT_MUTED}")

    with ui.row().classes("w-full gap-5 fade-in"):
        # --- Category Distribution (Pie/Doughnut) ---
        # TR: Kategori dagilimi
        # EN: Category distribution
        with ui.card().classes("glass-card p-6 flex-1"):
            ui.label(t("category_distribution", lang)).classes("text-lg font-semibold mb-4").style(f"color:{Theme.TEXT}")
            cats = db_service.get_category_distribution(family_id)
            if cats:
                pie_data = []
                pie_colors = []
                for c in cats:
                    # TR: Kategori adini ve rengini esle
                    # EN: Map category name and color
                    cat_name = c.get("_id", "Other")
                    pie_data.append({"value": round(c.get("total", 0), 2), "name": t(f"cat_{cat_name}", lang)})
                    pie_colors.append(Theme.CATEGORY_COLORS.get(cat_name, Theme.TEXT_MUTED))

                pie_opts = {
                    "tooltip": {"trigger": "item", "formatter": "{b}: ₺{c} ({d}%)"},
                    "series": [{
                        "type": "pie",
                        "radius": ["45%", "70%"],
                        "avoidLabelOverlap": True,
                        "itemStyle": {"borderRadius": 8, "borderColor": Theme.BG_CARD, "borderWidth": 2},
                        "label": {"color": Theme.TEXT, "fontSize": 11},
                        "data": pie_data,
                        "color": pie_colors,
                    }],
                    "backgroundColor": "transparent",
                }
                ui.echart(pie_opts).classes("w-full").style("height:300px")
            else:
                ui.label(t("no_data", lang)).style(f"color:{Theme.TEXT_MUTED}")

        # --- Member Comparison (Horizontal Bar) ---
        # TR: Uye bazli karsilastirma
        # EN: Member comparison chart
        with ui.card().classes("glass-card p-6 flex-1"):
            ui.label(t("member_comparison", lang)).classes("text-lg font-semibold mb-4").style(f"color:{Theme.TEXT}")
            members = db_service.get_member_spending(family_id)
            if members:
            # TR: Etiket ve deger listelerini olustur
            # EN: Build label and value arrays
                m_names = [m.get("_id", "?") for m in members]
                m_vals = [round(m.get("total", 0), 2) for m in members]
                m_colors = [Theme.PRIMARY, Theme.SECONDARY, Theme.ACCENT, Theme.SUCCESS, Theme.WARNING]

                bar_opts = {
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "value", "axisLabel": {"color": Theme.TEXT_MUTED, "formatter": "₺{value}"}},
                    "yAxis": {"type": "category", "data": m_names, "axisLabel": {"color": Theme.TEXT}},
                    "series": [{
                        "type": "bar",
                        "data": [{"value": v, "itemStyle": {"color": m_colors[i % len(m_colors)], "borderRadius": [0, 6, 6, 0]}} for i, v in enumerate(m_vals)],
                    }],
                    "grid": {"left": "20%", "right": "10%", "bottom": "10%"},
                    "backgroundColor": "transparent",
                }
                ui.echart(bar_opts).classes("w-full").style("height:300px")
            else:
                ui.label(t("no_data", lang)).style(f"color:{Theme.TEXT_MUTED}")
