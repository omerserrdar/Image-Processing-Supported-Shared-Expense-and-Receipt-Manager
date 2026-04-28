"""
ReceiptShare UI - Tasarim Tokenlari (Flet 0.84.0+)
"""

import flet as ft

class Style:
    # --- Renk Paleti ---
    BG = "#0b1326"
    SURFACE = "#171f33"
    PRIMARY = "#ddb7ff"
    SECONDARY = "#4cd7f6"
    TERTIARY = "#ffafd3"
    ON_SURFACE = "#dae2fd"
    OUTLINE = "#988d9f"
    
    # --- Gradyanlar ---
    PRIMARY_GRADIENT = ft.LinearGradient(
        begin=ft.alignment.Alignment(-1, -1),
        end=ft.alignment.Alignment(1, 1),
        colors=[PRIMARY, SECONDARY]
    )
    
    # --- Glassmorphism Efekti ---
    GLASS_STYLE = {
        "bgcolor": ft.colors.with_opacity(0.6, "#1e293b"),
        "border": ft.border.all(1, ft.colors.with_opacity(0.08, "white")),
        "blur": ft.Blur(20, 20, ft.BlurTileMode.MIRROR),
    }

    # --- Neon Shadows ---
    NEON_SHADOW = ft.BoxShadow(
        blur_radius=15,
        color=ft.colors.with_opacity(0.2, "#a855f7"),
        spread_radius=1,
    )
