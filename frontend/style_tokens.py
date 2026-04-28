"""
ReceiptShare UI - Tasarım Tokenları (Flet 0.21.0+ Uyumlu)
Bu dosya, uygulamanın genel görsel dilini (renkler, gölgeler, glassmorphism) tanımlar.
"""

import flet as ft

class Style:
    # --- ANA RENK PALETİ ---
    # Kurumsal kimliği yansıtan modern ve koyu tema renkleri
    BG = "#0b1326"           # Koyu Lacivert (Arka plan)
    SURFACE = "#171f33"      # Kart ve bileşen yüzey rengi
    PRIMARY = "#ddb7ff"      # Lavanta/Açık Mor (Ana aksiyon rengi)
    SECONDARY = "#4cd7f6"    # Turkuaz (İkincil aksiyon ve vurgu)
    TERTIARY = "#ffafd3"     # Pembe (Üçüncü vurgu rengi)
    ON_SURFACE = "#dae2fd"   # Yüzey üzerindeki metin rengi
    OUTLINE = "#988d9f"      # Yardımcı çizgiler ve sönük metinler
    
    # --- GRADIENTLER (GEÇİŞLİ RENKLER) ---
    # Tasarıma derinlik katmak için kullanılan lineer renk geçişleri
    PRIMARY_GRADIENT = ft.LinearGradient(
        begin=ft.alignment.Alignment(-1, -1),
        end=ft.alignment.Alignment(1, 1),
        colors=[PRIMARY, SECONDARY]
    )
    
    # --- GLASSMORPHISM (BUĞULU CAM EFEKTİ) ---
    # Modern UI tasarımında kullanılan yarı saydam ve bulanık arka plan stili
    GLASS_STYLE = {
        "bgcolor": ft.colors.with_opacity(0.6, "#1e293b"), # Yarı saydam koyu gri/mavi
        "border": ft.border.all(1, ft.colors.with_opacity(0.08, "white")), # İnce beyaz kenarlık
        "blur": ft.Blur(20, 20, ft.BlurTileMode.MIRROR), # Arkadaki içeriği bulanıklaştır
    }

    # --- NEON GÖLGELER ---
    # Bileşenlerin parlamasını sağlayan yumuşak ışık efekti
    NEON_SHADOW = ft.BoxShadow(
        blur_radius=15,
        color=ft.colors.with_opacity(0.2, "#a855f7"),
        spread_radius=1,
    )
