"""
TR: ReceiptShare v2 — Ana uygulama giris noktasi.
    NiceGUI + FastAPI + MongoDB Atlas + Gemini Vision API
EN: ReceiptShare v2 — Main application entry point.
"""
import os
from nicegui import ui, app
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings
from theme.style import Theme
from i18n import t

from pages.login import login_page
from pages.dashboard import dashboard_page
from pages.scan import scan_page
from pages.receipts import receipts_page
from pages.analytics import analytics_page
from pages.family import family_page
from pages.warranty import warranty_page
from services import db_service


# ──────────────────────────────────────────────
#  AUTH MIDDLEWARE
# ──────────────────────────────────────────────
# TR: Yetkilendirme kontrolunun tum isteklerde devreye girdigi katman
# EN: Global authorization layer that runs on every request

class AuthMiddleware(BaseHTTPMiddleware):
    """TR: Kimlik dogrulama middleware'i | EN: Authentication middleware"""

    # TR: Login disinda serbest erisim verilecek yollar
    # EN: Paths that bypass authentication checks
    UNRESTRICTED = {"/login", "/_nicegui", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next):
        # TR: Istegin hedef yolunu belirle
        # EN: Resolve the requested path
        path = request.url.path

        # TR: Login ve statik dosya isteklerini dogrudan gecir
        # EN: Allow unrestricted paths and static assets to pass through
        if any(path.startswith(p) for p in self.UNRESTRICTED):
            return await call_next(request)

        # TR: Oturumda dogrulanmis kullanici yoksa login'e yonlendir
        # EN: Redirect to login if the user is not authenticated
        if not app.storage.user.get("authenticated"):
            return RedirectResponse("/login")

        # TR: Yetkili istekleri uygulamaya ilet
        # EN: Forward authorized requests to the app
        return await call_next(request)


app.add_middleware(AuthMiddleware)


# ──────────────────────────────────────────────
#  SHARED LAYOUT
# ──────────────────────────────────────────────
# TR: Sidebar + icerik kolonunu tum sayfalarda tekrar kullanilabilir hale getirir
# EN: Provides a reusable sidebar + content layout for all pages

def _sidebar_layout(page_func):
    """TR: Sidebar + icerik alani olan sayfa sablonu | EN: Page template with sidebar + content"""

    def wrapper():
        # TR: Tema ve UI stilini her sayfada uygula
        # EN: Apply global theme styles per page render
        Theme.apply_global()
        lang = app.storage.user.get("language", "en")
        current_path = ui.context.client.page.path

        with ui.row().classes("w-full min-h-screen").style(f"background:{Theme.BG}"):
            # --- Sidebar ---
            with ui.column().classes("sidebar h-screen py-6 px-2").style("width:240px;position:sticky;top:0"):
                # Brand
                with ui.row().classes("items-center gap-2 px-4 mb-8"):
                    ui.icon("receipt_long").classes("text-2xl").style(f"color:{Theme.PRIMARY}")
                    ui.label("ReceiptShare").classes("text-lg font-black").style(f"color:{Theme.TEXT}")

                # TR: Sidebar navigasyon kalemleri
                # EN: Sidebar navigation items
                nav_items = [
                    ("dashboard", "nav_dashboard", "dashboard"),
                    ("scan", "nav_scan", "document_scanner"),
                    ("receipts", "nav_receipts", "receipt_long"),
                    ("analytics", "nav_analytics", "insights"),
                    ("family", "nav_family", "family_restroom"),
                    ("warranty", "nav_warranty", "verified_user"),
                ]

                for route, label_key, icon in nav_items:
                    # TR: Aktif sayfa icin vurgulu stil uygula
                    # EN: Highlight the active route in the sidebar
                    is_active = current_path == f"/{route}"
                    cls = "nav-item active" if is_active else "nav-item"

                    with ui.row().classes(f"{cls} items-center gap-3 w-full cursor-pointer").on(
                        "click", lambda _, r=route: ui.navigate.to(f"/{r}")
                    ):
                        ui.icon(icon).classes("text-lg")
                        ui.label(t(label_key, lang)).classes("text-sm font-medium")

                # TR: Bosluk ile alt aksiyonlari sayfanin altina it
                # EN: Push actions to the bottom with a spacer
                ui.space()

                # TR: Dil degistirici
                # EN: Language switcher
                with ui.row().classes("mx-4 mb-4 p-1 rounded-full items-center justify-center gap-0").style(f"background:{Theme.SURFACE}; border: 1px solid {Theme.BORDER}"):
                    def set_lang(code):
                        # TR: Dil tercihini session + DB uzerinde sakla
                        # EN: Persist language in session and DB
                        app.storage.user["language"] = code
                        user_id = app.storage.user.get("user_id")
                        if user_id:
                            db_service.update_user_language(user_id, code)
                        ui.navigate.to(current_path)

                    btn_classes = "rounded-full px-4 py-1 text-xs font-bold cursor-pointer transition-colors"
                    active_style = f"background:{Theme.PRIMARY}; color:{Theme.BG};"
                    inactive_style = f"background:transparent; color:{Theme.TEXT_MUTED};"

                    ui.label("EN").classes(btn_classes).style(active_style if lang == "en" else inactive_style).on("click", lambda: set_lang("en"))
                    ui.label("TR").classes(btn_classes).style(active_style if lang == "tr" else inactive_style).on("click", lambda: set_lang("tr"))

                # TR: Cikis aksiyonu
                # EN: Logout action
                def logout():
                    # TR: Session bilgisini temizle ve login sayfasina git
                    # EN: Clear session storage and return to login
                    app.storage.user.clear()
                    ui.navigate.to("/login")

                with ui.row().classes("nav-item items-center gap-3 w-full cursor-pointer").on("click", lambda _: logout()):
                    ui.icon("logout").classes("text-lg")
                    ui.label(t("logout", lang)).classes("text-sm font-medium")

            # --- Main Content ---
            with ui.column().classes("flex-1 p-8 overflow-auto"):
                # Header Bar
                with ui.row().classes("w-full justify-between items-center mb-6").style(
                    f"border-bottom:1px solid {Theme.BORDER};padding-bottom:16px"
                ):
                    # TR: Kullanici adini ust barda goster
                    # EN: Show current user name in the header
                    user_name = app.storage.user.get("user_name", "")
                    ui.label(f"👋 {user_name}").classes("text-sm font-medium").style(f"color:{Theme.TEXT_MUTED}")

                    with ui.row().classes("items-center gap-2"):
                        ui.icon("person").classes("text-lg p-2 rounded-full").style(
                            f"color:{Theme.PRIMARY};background:{Theme.PRIMARY}15;cursor:pointer"
                        )

                # TR: Sayfaya ozel icerigi render et
                # EN: Render page-specific content
                page_func()

    return wrapper


# ──────────────────────────────────────────────
#  PAGES
# ──────────────────────────────────────────────
# TR: NiceGUI route deklarasyonlari
# EN: NiceGUI route declarations

@ui.page("/login")
def login():
    # TR: Login/kayit ekrani
    # EN: Login/registration screen
    login_page()


@ui.page("/dashboard")
@_sidebar_layout
def dashboard():
    # TR: Aile harcama ozeti paneli
    # EN: Family spending overview dashboard
    dashboard_page()


@ui.page("/scan")
@_sidebar_layout
def scan():
    # TR: Fis tarama ve analiz sayfasi
    # EN: Receipt scanning and analysis page
    scan_page()


@ui.page("/receipts")
@_sidebar_layout
def receipts():
    # TR: Fis gecmisi sayfasi
    # EN: Receipt history page
    receipts_page()


@ui.page("/analytics")
@_sidebar_layout
def analytics():
    # TR: Analitik ve grafikler
    # EN: Analytics and charts
    analytics_page()


@ui.page("/family")
@_sidebar_layout
def family():
    # TR: Aile yonetimi sayfasi
    # EN: Family management page
    family_page()


@ui.page("/warranty")
@_sidebar_layout
def warranty():
    # TR: Garanti takip sayfasi
    # EN: Warranty tracking page
    warranty_page()


@ui.page("/")
def root():
    # TR: Kok yol -> login
    # EN: Root route -> login
    ui.navigate.to("/login")


# ──────────────────────────────────────────────
#  RUN
# ──────────────────────────────────────────────
# TR: Uygulama dogrudan calistirildiginda sunucuyu baslat
# EN: Start the server when the module is executed directly

if __name__ in {"__main__", "__mp_main__"}:
    # TR: Baslangic bilgilerini consola yaz
    # EN: Print startup metadata to console
    print(f"\n🚀 ReceiptShare v{settings.APP_VERSION}")
    print(f"   Port: {settings.APP_PORT}")
    print(f"   DB:   {settings.MONGODB_DB_NAME}")
    print(f"   AI:   {settings.GEMINI_MODEL}\n")

    # TR: NiceGUI uygulamasini calistir
    # EN: Run the NiceGUI application
    ui.run(
        title=settings.APP_NAME,
        port=settings.APP_PORT,
        storage_secret=settings.SECRET_KEY,
        dark=True,
        reload=True,
    )
