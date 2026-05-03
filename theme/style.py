"""
TR: NiceGUI tema ve stil tokenları — uygulamanın tüm görsel dili burada tanımlanır.
EN: NiceGUI theme and style tokens — the entire visual language of the app is defined here.
"""

from nicegui import ui


class Theme:
    """
    TR: Merkezi tasarım sistemi. Tüm renkler, gölgeler, ortak stiller burada.
    EN: Central design system. All colors, shadows, common styles defined here.
    """

    # --- Color Palette ---
    # TR: Uygulamanin ana renk paleti
    # EN: Primary application color palette
    BG = "#0a0f1e"
    BG_CARD = "#111827"
    SURFACE = "#1a2236"
    PRIMARY = "#a78bfa"        # Soft violet
    PRIMARY_DARK = "#7c3aed"
    SECONDARY = "#22d3ee"      # Cyan
    ACCENT = "#f472b6"         # Pink
    SUCCESS = "#34d399"        # Emerald
    WARNING = "#fbbf24"        # Amber
    ERROR = "#f87171"          # Red
    TEXT = "#e2e8f0"           # Light slate
    TEXT_MUTED = "#94a3b8"     # Muted slate
    BORDER = "rgba(255,255,255,0.08)"

    # --- Category Colors ---
    # TR: Kategoriye gore renk kodlari
    # EN: Per-category color mapping
    CATEGORY_COLORS = {
        "Market": "#10b981",
        "Food": "#f43f5e",
        "Electronics": "#6366f1",
        "Travel": "#f59e0b",
        "Health": "#06b6d4",
        "Clothing": "#ec4899",
        "Education": "#8b5cf6",
        "Bills": "#ef4444",
        "Other": "#94a3b8",
    }

    @classmethod
    def apply_global(cls):
        """
        TR: Tüm uygulamaya genel CSS stillerini uygular.
        EN: Applies global CSS styles to the entire application.
        """
        # TR: Google Fonts (Inter) fontunu yukle
        # EN: Load Google Fonts (Inter)
        ui.add_head_html("""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
        """)

        # TR: Uygulama geneli CSS kurallari
        # EN: Global CSS rules for the app
        ui.add_css("""
        /* ── Global Reset & Base ── */
        :root {
            --bg: #0a0f1e;
            --bg-card: #111827;
            --surface: #1a2236;
            --primary: #a78bfa;
            --primary-dark: #7c3aed;
            --secondary: #22d3ee;
            --accent: #f472b6;
            --text: #e2e8f0;
            --text-muted: #94a3b8;
            --border: rgba(255,255,255,0.08);
            --radius: 16px;
            --radius-lg: 24px;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background: var(--bg) !important;
            color: var(--text) !important;
        }

        /* ── Quasar Dark Overrides ── */
        .q-page, .q-layout, .q-drawer, .q-header, .q-footer,
        .q-card, .q-dialog, .q-menu {
            background: var(--bg) !important;
            color: var(--text) !important;
        }

        .q-table, .q-table th, .q-table td {
            color: var(--text) !important;
        }

        .q-field__native, .q-field__input {
            color: var(--text) !important;
        }

        /* ── Glass Card ── */
        .glass-card {
            background: rgba(17, 24, 39, 0.7) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: var(--radius-lg) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .glass-card:hover {
            border-color: rgba(167, 139, 250, 0.15) !important;
            box-shadow: 0 8px 32px rgba(167, 139, 250, 0.08) !important;
        }

        /* ── KPI Card ── */
        .kpi-card {
            background: rgba(17, 24, 39, 0.6) !important;
            backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: var(--radius-lg) !important;
            padding: 24px !important;
            transition: all 0.3s ease !important;
        }
        .kpi-card:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 40px rgba(167, 139, 250, 0.1) !important;
        }

        /* ── Neon Glow ── */
        .neon-primary {
            box-shadow: 0 0 20px rgba(167, 139, 250, 0.15),
                        0 0 60px rgba(167, 139, 250, 0.05) !important;
        }
        .neon-secondary {
            box-shadow: 0 0 20px rgba(34, 211, 238, 0.15),
                        0 0 60px rgba(34, 211, 238, 0.05) !important;
        }

        /* ── Sidebar ── */
        .sidebar {
            background: rgba(10, 15, 30, 0.95) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        }

        .nav-item {
            border-radius: 12px !important;
            padding: 10px 16px !important;
            margin: 2px 8px !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
            color: var(--text-muted) !important;
        }
        .nav-item:hover {
            background: rgba(167, 139, 250, 0.08) !important;
            color: var(--primary) !important;
        }
        .nav-item.active {
            background: rgba(167, 139, 250, 0.12) !important;
            color: var(--primary) !important;
            border-right: 3px solid var(--primary) !important;
        }

        /* ── Upload Zone ── */
        .upload-zone {
            border: 2px dashed rgba(167, 139, 250, 0.3) !important;
            border-radius: var(--radius-lg) !important;
            background: rgba(167, 139, 250, 0.03) !important;
            transition: all 0.3s ease !important;
        }
        .upload-zone:hover {
            border-color: var(--primary) !important;
            background: rgba(167, 139, 250, 0.06) !important;
        }

        /* ── Buttons ── */
        .btn-primary {
            background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
            color: white !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            text-transform: none !important;
            transition: all 0.3s ease !important;
        }
        .btn-primary:hover {
            box-shadow: 0 8px 25px rgba(124, 58, 237, 0.3) !important;
            transform: translateY(-1px) !important;
        }

        /* ── Animations ── */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in {
            animation: fadeIn 0.4s ease forwards;
        }

        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 15px rgba(167, 139, 250, 0.1); }
            50% { box-shadow: 0 0 30px rgba(167, 139, 250, 0.2); }
        }
        .pulse-glow {
            animation: pulse-glow 3s infinite;
        }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
            background: rgba(167, 139, 250, 0.2);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover { background: rgba(167, 139, 250, 0.4); }

        /* ── Toast / Notification ── */
        .q-notification {
            border-radius: 12px !important;
            backdrop-filter: blur(10px) !important;
        }
        """)
