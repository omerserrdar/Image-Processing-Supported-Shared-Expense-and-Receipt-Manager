"""
TR: ReceiptShare UI - Tasarım Tokenları (Flet 0.21.0+ Uyumlu)
    Bu dosya, uygulamanın genel görsel dilini (renkler, gölgeler, glassmorphism) tanımlar.
EN: ReceiptShare UI - Design Tokens (Flet 0.21.0+ Compatible)
    This file defines the general visual language of the application (colors, shadows, glassmorphism).
"""

import flet as ft

class Style:
    # --- ANA RENK PALETİ | MAIN COLOR PALETTE ---
    # TR: Kurumsal kimliği yansıtan modern ve koyu tema renkleri
    # EN: Modern and dark theme colors reflecting the corporate identity
    BG = "#0b1326"           # Koyu Lacivert (Arka plan) | Dark Navy (Background)
    SURFACE = "#171f33"      # Kart ve bileşen yüzey rengi | Card and component surface color
    PRIMARY = "#ddb7ff"      # Lavanta/Açık Mor (Ana aksiyon rengi) | Lavender/Light Purple (Primary action color)
    SECONDARY = "#4cd7f6"    # Turkuaz (İkincil aksiyon ve vurgu) | Turquoise (Secondary action and emphasis)
    TERTIARY = "#ffafd3"     # Pembe (Üçüncü vurgu rengi) | Pink (Tertiary emphasis color)
    ON_SURFACE = "#dae2fd"   # Yüzey üzerindeki metin rengi | Text color on surface
    OUTLINE = "#988d9f"      # Yardımcı çizgiler ve sönük metinler | Helper lines and faded text
    
    # --- GRADIENTLER (GEÇİŞLİ RENKLER) | GRADIENTS ---
    # TR: Tasarıma derinlik katmak için kullanılan lineer renk geçişleri
    # EN: Linear color transitions used to add depth to the design
    PRIMARY_GRADIENT = ft.LinearGradient(
        begin=ft.alignment.Alignment(-1, -1),
        end=ft.alignment.Alignment(1, 1),
        colors=[PRIMARY, SECONDARY]
    )
    
    # --- GLASSMORPHISM (BUĞULU CAM EFEKTİ) | GLASSMORPHISM ---
    # TR: Modern UI tasarımında kullanılan yarı saydam ve bulanık arka plan stili
    # EN: Translucent and blurred background style used in modern UI
    GLASS_STYLE = {
        "bgcolor": ft.colors.with_opacity(0.6, "#1e293b"), 
        "border": ft.border.all(1, ft.colors.with_opacity(0.08, "white")), 
        "blur": ft.Blur(20, 20, ft.BlurTileMode.MIRROR), 
    }

    # --- NEON GÖLGELER | NEON SHADOWS ---
    # TR: Bileşenlerin parlamasını sağlayan yumuşak ışık efekti
    # EN: Soft light effect that makes components glow
    NEON_SHADOW = ft.BoxShadow(
        blur_radius=15,
        color=ft.colors.with_opacity(0.2, "#a855f7"),
        spread_radius=1,
    )
