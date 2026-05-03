"""
TR: Giriş ve kayıt sayfası.
EN: Login and registration page.
"""

from nicegui import ui, app
from i18n import t
from services import auth_service
from theme.style import Theme

# TR: Login ve kayit akisini yoneten UI sayfasi
# EN: UI page that handles login and registration flow


def login_page():
    """TR: Login/Register sayfasını render eder | EN: Renders the login/register page"""
    # TR: Tema ve stil uygulamalarini baslat
    # EN: Initialize theme and styles
    Theme.apply_global()

    lang = app.storage.user.get("language", "en")

    # TR: Zaten giris yapildiysa dashboard'a yonlendir
    # EN: If already authenticated, go to dashboard
    if app.storage.user.get("authenticated"):
        ui.navigate.to("/dashboard")
        return

    with ui.column().classes("w-full min-h-screen items-center justify-center").style(
        f"background: linear-gradient(135deg, {Theme.BG} 0%, #1a1040 50%, {Theme.BG} 100%);"
    ):
        # --- Logo & Brand ---
        # TR: Marka alani
        # EN: Branding area
        with ui.column().classes("items-center mb-8 fade-in"):
            with ui.row().classes("items-center gap-3"):
                ui.icon("receipt_long").classes("text-4xl").style(f"color: {Theme.PRIMARY}")
                ui.label("ReceiptShare").classes("text-4xl font-black").style(f"color: {Theme.TEXT}")
            ui.label(t("login_subtitle", lang)).classes("text-sm mt-2").style(f"color: {Theme.TEXT_MUTED}")

        # --- Auth Card ---
        # TR: Giris/Kayit form kutusu
        # EN: Login/Register form card
        with ui.card().classes("glass-card p-8 fade-in").style("width: 420px; max-width: 90vw;"):
            # TR: Giris/kayit modunu kontrol eden state
            # EN: State that toggles login/register mode
            is_login = {"value": True}

            title_label = ui.label(t("login_title", lang)).classes("text-2xl font-bold mb-1").style(f"color: {Theme.TEXT}")
            subtitle_label = ui.label(t("login_subtitle", lang)).classes("text-sm mb-6").style(f"color: {Theme.TEXT_MUTED}")

            # --- Form Fields ---
            # TR: Form alanlari
            # EN: Form fields
            name_field = ui.input(
                label=t("name", lang),
                placeholder="John Doe",
            ).classes("w-full mb-2").style(f"color: {Theme.TEXT}")
            name_field.visible = False

            email_field = ui.input(
                label=t("email", lang),
                placeholder="email@example.com",
            ).classes("w-full mb-2").style(f"color: {Theme.TEXT}")

            password_field = ui.input(
                label=t("password", lang),
                placeholder="••••••••",
                password=True,
                password_toggle_button=True,
            ).classes("w-full mb-4").style(f"color: {Theme.TEXT}")

            # --- Error Display ---
            # TR: Hata mesajlari icin alan
            # EN: Error message container
            error_label = ui.label("").classes("text-sm mb-2").style(f"color: {Theme.ERROR}; display: none;")

            def show_error(msg: str):
                # TR: Hata mesajini goster
                # EN: Show error message
                error_label.text = msg
                error_label.style(f"color: {Theme.ERROR}; display: block;")

            def hide_error():
                # TR: Hata mesajini gizle
                # EN: Hide error message
                error_label.style("display: none;")

            # --- Submit Handler ---
            # TR: Giris/Kayit islemini calistir
            # EN: Execute login/registration
            async def handle_submit():
                hide_error()

                email = email_field.value.strip()
                password = password_field.value.strip()

                if not email or not password:
                    show_error("Please fill in all fields")
                    return

                if is_login["value"]:
                    # TR: Giris yap
                    # EN: Perform login
                    result = auth_service.login(email, password)
                    if result["success"]:
                        user = result["user"]
                        # TR: Session storage'a kullanici bilgilerini yaz
                        # EN: Persist user info into session storage
                        app.storage.user["authenticated"] = True
                        app.storage.user["user_id"] = user["_id"]
                        app.storage.user["user_name"] = user["name"]
                        app.storage.user["user_email"] = user["email"]
                        app.storage.user["family_id"] = user.get("family_id")
                        app.storage.user["role"] = user.get("role")
                        app.storage.user["language"] = user.get("language", "en")
                        ui.notify(t("login_success", lang), type="positive")
                        ui.navigate.to("/dashboard")
                    else:
                        show_error(t("invalid_credentials", lang))
                else:
                    # TR: Kayit ol
                    # EN: Perform registration
                    name = name_field.value.strip()
                    if not name:
                        show_error("Please enter your name")
                        return
                    if len(password) < 6:
                        show_error("Password must be at least 6 characters")
                        return

                    result = auth_service.register(name, email, password)
                    if result["success"]:
                        # TR: Kayit sonrasi otomatik giris
                        # EN: Auto login after registration
                        login_result = auth_service.login(email, password)
                        if login_result["success"]:
                            user = login_result["user"]
                            # TR: Session storage'a kullanici bilgilerini yaz
                            # EN: Persist user info into session storage
                            app.storage.user["authenticated"] = True
                            app.storage.user["user_id"] = user["_id"]
                            app.storage.user["user_name"] = user["name"]
                            app.storage.user["user_email"] = user["email"]
                            app.storage.user["family_id"] = user.get("family_id")
                            app.storage.user["role"] = user.get("role")
                            app.storage.user["language"] = user.get("language", "en")
                            ui.notify(t("register_success", lang), type="positive")
                            ui.navigate.to("/dashboard")
                    else:
                        show_error(t(result.get("error", "error"), lang))

            submit_btn = ui.button(
                t("login", lang),
                on_click=handle_submit,
            ).classes("w-full btn-primary py-3 text-base")

            # --- Toggle Login/Register ---
            # TR: Mod degistirme linki
            # EN: Toggle between login/register
            with ui.row().classes("w-full justify-center mt-4"):
                toggle_label = ui.label(t("no_account", lang)).classes("text-sm").style(f"color: {Theme.TEXT_MUTED}")
                toggle_link = ui.link(t("register", lang)).classes("text-sm font-semibold").style(f"color: {Theme.PRIMARY}")

            def toggle_mode():
                # TR: Formu login<->register moduna gecir
                # EN: Switch form mode login<->register
                is_login["value"] = not is_login["value"]
                if is_login["value"]:
                    title_label.text = t("login_title", lang)
                    subtitle_label.text = t("login_subtitle", lang)
                    name_field.visible = False
                    submit_btn.text = t("login", lang)
                    toggle_label.text = t("no_account", lang)
                    toggle_link.text = t("register", lang)
                else:
                    title_label.text = t("register_title", lang)
                    subtitle_label.text = t("register_subtitle", lang)
                    name_field.visible = True
                    submit_btn.text = t("register", lang)
                    toggle_label.text = t("have_account", lang)
                    toggle_link.text = t("login", lang)
                hide_error()

            toggle_link.on("click", lambda _: toggle_mode())

        # --- Language Selector (bottom) ---
        # TR: Giris ekraninda dil secimi
        # EN: Language selector on login screen
        with ui.row().classes("mt-6 gap-4 fade-in"):
            ui.button("🇬🇧 English", on_click=lambda: _set_lang("en")).props("flat dense").style(f"color: {Theme.TEXT_MUTED}")
            ui.button("🇹🇷 Türkçe", on_click=lambda: _set_lang("tr")).props("flat dense").style(f"color: {Theme.TEXT_MUTED}")

    def _set_lang(code):
        # TR: Dil tercihine gore sayfayi yenile
        # EN: Update language preference and reload
        app.storage.user["language"] = code
        ui.navigate.to("/login")
