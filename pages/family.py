"""
TR: Aile yonetimi sayfasi — olusturma, katilma, davet kodu, uyeler.
EN: Family management page — creation, joining, invite codes, members.
"""
from nicegui import ui, app
from i18n import t
from theme.style import Theme
from services import db_service

# TR: Aile olusturma, katilma ve uye yonetimi sayfasi
# EN: Family creation, joining, and member management page


def family_page():
    # TR: Kullanici ve aile context
    # EN: User and family context
    lang = app.storage.user.get("language", "en")
    family_id = app.storage.user.get("family_id")
    user_id = app.storage.user.get("user_id")
    user_name = app.storage.user.get("user_name")

    with ui.row().classes("w-full justify-between items-center mb-6 fade-in"):
        with ui.column().classes("gap-0"):
            ui.label(t("family_title", lang)).classes("text-2xl font-bold").style(f"color:{Theme.TEXT}")
            ui.label(t("family_subtitle", lang)).classes("text-sm").style(f"color:{Theme.TEXT_MUTED}")

    # TR: Sayfa icerigini dinamik olarak yeniden render etmek icin container
    # EN: Container used to re-render content dynamically
    content = ui.column().classes("w-full fade-in")

    if family_id:
        # TR: Aile bilgisi varsa paneli goster
        # EN: Show family panel if family exists
        family = db_service.get_family(family_id)
        if family:
            _show_family_panel(content, family, user_id, lang)
        else:
            # TR: Aile kaydi yoksa session bilgisini sifirla
            # EN: Reset session if family record is missing
            app.storage.user["family_id"] = None
            _show_no_family(content, user_id, user_name, lang)
    else:
        _show_no_family(content, user_id, user_name, lang)


def _show_no_family(container, user_id, user_name, lang):
    # TR: Aile yoksa olusturma/katilma bloklari
    # EN: Create/join blocks when no family
    with container:
        with ui.row().classes("w-full gap-6"):
            # --- Create Family ---
            with ui.card().classes("glass-card p-8 flex-1"):
                ui.icon("group_add").classes("text-4xl mb-3").style(f"color:{Theme.PRIMARY}")
                ui.label(t("create_family", lang)).classes("text-xl font-bold mb-2").style(f"color:{Theme.TEXT}")

                name_input = ui.input(label=t("family_name", lang), placeholder="Boz Ailesi").classes("w-full mb-4")

                async def create():
                    # TR: Aile adi kontrolu ve kayit
                    # EN: Validate family name and create
                    name = name_input.value.strip()
                    if not name:
                        ui.notify("Please enter a family name", type="warning")
                        return
                    result = db_service.create_family(name, user_id, user_name)
                    app.storage.user["family_id"] = result["family_id"]
                    app.storage.user["role"] = "admin"
                    ui.notify(t("family_created", lang), type="positive")
                    ui.navigate.to("/family")

                ui.button(t("create_family", lang), icon="add", on_click=create).classes("btn-primary w-full")

            # --- Join Family ---
            with ui.card().classes("glass-card p-8 flex-1"):
                ui.icon("login").classes("text-4xl mb-3").style(f"color:{Theme.SECONDARY}")
                ui.label(t("join_family", lang)).classes("text-xl font-bold mb-2").style(f"color:{Theme.TEXT}")

                code_input = ui.input(label=t("invite_code", lang), placeholder="ABC12345").classes("w-full mb-4")

                async def join():
                    # TR: Davet kodu ile aileye katilma
                    # EN: Join family using invite code
                    code = code_input.value.strip()
                    if not code:
                        ui.notify(t("enter_invite_code", lang), type="warning")
                        return
                    family = db_service.find_family_by_invite_code(code)
                    if not family:
                        ui.notify(t("invalid_code", lang), type="negative")
                        return

                    # TR: Zaten uye mi kontrol et
                    # EN: Check if already a member
                    for m in family.get("members", []):
                        if m.get("user_id") == user_id:
                            ui.notify("Already a member", type="warning")
                            return

                    db_service.add_member_to_family(family["_id"], user_id, user_name)
                    app.storage.user["family_id"] = family["_id"]
                    app.storage.user["role"] = "member"
                    ui.notify(t("joined_family", lang), type="positive")
                    ui.navigate.to("/family")

                ui.button(t("join_family", lang), icon="login", on_click=join).classes("btn-primary w-full")


def _show_family_panel(container, family, user_id, lang):
    # TR: Aile panelinin ana gosterimi
    # EN: Main family panel rendering
    family_id = family["_id"]

    # TR: Admin yetkisi kontrolu
    # EN: Admin role check
    is_admin = app.storage.user.get("role") == "admin"

    with container:
        # --- Family Info Card ---
        # TR: Aile adi ve butce bilgisi
        # EN: Family name and budget info
        with ui.card().classes("glass-card p-6 w-full mb-6"):
            with ui.row().classes("w-full justify-between items-center"):
                with ui.row().classes("items-center gap-3"):
                    ui.icon("family_restroom").classes("text-3xl").style(f"color:{Theme.PRIMARY}")
                    with ui.column().classes("gap-0"):
                        ui.label(family.get("name", "")).classes("text-xl font-bold").style(f"color:{Theme.TEXT}")
                        ui.label(f"{len(family.get('members',[]))} {t('members', lang)}").style(f"color:{Theme.TEXT_MUTED}")

                if is_admin:
                    # TR: Admin butce guncellemesi yapabilir
                    # EN: Admin can update monthly budget
                    budget_input = ui.number(
                        label=f"{t('monthly_budget', lang)} (₺)",
                        value=family.get("monthly_budget", 0),
                        format="%.0f",
                    ).classes("w-40")

                    async def save_budget():
                        # TR: Yeni butceyi kaydet
                        # EN: Persist updated budget
                        db_service.update_family_budget(family_id, float(budget_input.value or 0))
                        ui.notify(t("success", lang), type="positive")

                    ui.button(t("set_budget", lang), icon="save", on_click=save_budget).props("flat dense").style(f"color:{Theme.PRIMARY}")

        # --- Invite Codes ---
        # TR: Davet kodu uretim alani (sadece admin)
        # EN: Invite code generation (admin only)
        if is_admin:
            with ui.card().classes("glass-card p-6 w-full mb-6"):
                ui.label(t("invite_code", lang)).classes("text-lg font-semibold mb-4").style(f"color:{Theme.TEXT}")

                with ui.row().classes("gap-3"):
                    async def gen_temp():
                        # TR: Gecici kod uret
                        # EN: Generate temporary code
                        code = db_service.generate_invite_code(family_id, permanent=False)
                        ui.notify(f"📋 {code}", type="positive", timeout=10000)
                        code_display.text = code

                    async def gen_perm():
                        # TR: Kalici kod uret
                        # EN: Generate permanent code
                        code = db_service.generate_invite_code(family_id, permanent=True)
                        ui.notify(f"📋 {code}", type="positive", timeout=10000)
                        code_display.text = code

                    ui.button(t("temporary_code", lang), icon="timer", on_click=gen_temp).classes("btn-primary")
                    ui.button(t("permanent_code", lang), icon="all_inclusive", on_click=gen_perm).props("outline").style(f"color:{Theme.PRIMARY}")

                code_display = ui.label("").classes("text-2xl font-mono font-bold mt-4 tracking-widest").style(f"color:{Theme.SECONDARY}")

                # TR: Mevcut kodlari listele
                # EN: Show existing codes
                existing_codes = family.get("invite_codes", [])
                if existing_codes:
                    ui.separator().classes("my-3")
                    for ic in existing_codes[-3:]:
                        perm = "♾️" if ic.get("permanent") else "⏱️ 24h"
                        ui.label(f"{ic.get('code','')} — {perm}").classes("text-sm font-mono").style(f"color:{Theme.TEXT_MUTED}")

        # --- Members List ---
        # TR: Uye listesi ve admin aksiyonlari
        # EN: Member list and admin actions
        with ui.card().classes("glass-card p-6 w-full"):
            ui.label(t("members", lang)).classes("text-lg font-semibold mb-4").style(f"color:{Theme.TEXT}")

            colors = [Theme.PRIMARY, Theme.SECONDARY, Theme.ACCENT, Theme.SUCCESS, Theme.WARNING]
            for i, member in enumerate(family.get("members", [])):
                clr = colors[i % len(colors)]
                with ui.row().classes("w-full justify-between items-center py-3").style(f"border-bottom:1px solid {Theme.BORDER}"):
                    with ui.row().classes("items-center gap-3"):
                        ui.icon("person").classes("text-xl p-2 rounded-full").style(f"color:{clr};background:{clr}15;")
                        with ui.column().classes("gap-0"):
                            ui.label(member.get("name", "")).classes("font-medium").style(f"color:{Theme.TEXT}")
                            role = member.get("role", "member")
                            role_label = t("admin", lang) if role == "admin" else t("member", lang)
                            ui.label(role_label.upper()).classes("text-xs font-bold").style(
                                f"color:{Theme.PRIMARY}" if role == "admin" else f"color:{Theme.TEXT_MUTED}"
                            )
                    if is_admin and member.get("user_id") != user_id:
                        mid = member.get("user_id")
                        ui.button(icon="remove_circle", on_click=lambda _, m=mid: _remove(m, family_id, lang, container, user_id)).props("flat dense").style(f"color:{Theme.ERROR}")


def _remove(member_id, family_id, lang, container, user_id):
    # TR: Uye cikarma islemi
    # EN: Remove member action
    db_service.remove_member_from_family(family_id, member_id)
    ui.notify(t("success", lang), type="positive")
    container.clear()
    family = db_service.get_family(family_id)
    if family:
        _show_family_panel(container, family, user_id, lang)
