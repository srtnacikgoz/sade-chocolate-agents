"""
Sade Chocolate - The Curator Skills.

Gorsel tasarim ve etiket uretimi icin skill fonksiyonlari.
Gemini 3 Pro Image API ile entegre calisir.
"""

import json
import os
from pathlib import Path
from typing import Literal

from crewai.tools import tool

# Style guide paths
STYLE_GUIDE_DIR = Path(__file__).parent.parent.parent.parent / "style_guide"


def _load_style_config() -> dict:
    """Style guide konfigurasyonunu yukle."""
    config_path = STYLE_GUIDE_DIR / "style_config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "aesthetic": "quiet_luxury",
        "style_keywords": [
            "elegant",
            "minimalist",
            "sophisticated",
            "timeless",
            "refined",
        ],
        "avoid_keywords": [
            "flashy",
            "loud",
            "busy",
            "cluttered",
            "cheap",
        ],
        "composition": {
            "layout": "minimalist, centered",
            "white_space": "ample white space",
            "balance": "asymmetric sophistication",
        },
        "label_specs": {
            "aspect_ratio": "3:4",
            "resolution": "2K",
            "text_max_chars": 25,
            "dpi": 300,
        },
    }


def _load_brand_colors() -> dict:
    """Marka renk paletini yukle."""
    colors_path = STYLE_GUIDE_DIR / "brand_colors.json"
    if colors_path.exists():
        with open(colors_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "primary": {
            "hex": "#3D2314",
            "name": "Sade Brown",
            "usage": "Main brand color, chocolate tone",
        },
        "secondary": {
            "hex": "#F5F0E8",
            "name": "Cream",
            "usage": "Background, soft contrast",
        },
        "accent": {
            "hex": "#8B7355",
            "name": "Warm Taupe",
            "usage": "Text, subtle highlights",
        },
    }


def _build_label_prompt(
    urun_adi: str, urun_gramaj: str, urun_aciklama: str, style_config: dict, colors: dict
) -> str:
    """Gemini icin narrative prompt olustur."""
    keywords = ", ".join(style_config.get("style_keywords", ["elegant"]))
    avoid = ", ".join(style_config.get("avoid_keywords", ["flashy"]))

    # Max 25 karakter etiket metni
    label_text = f"{urun_adi} {urun_gramaj}"
    if len(label_text) > 25:
        label_text = label_text[:22] + "..."

    # Renk bilgilerini al
    primary_hex = colors.get("primary", {}).get("hex", "#3D2314")
    secondary_hex = colors.get("secondary", {}).get("hex", "#F5F0E8")

    prompt = f"""
Create a premium product label for a quiet luxury chocolate brand named Sade.

Product: {urun_adi} - {urun_aciklama}
Label Text: "{label_text}" (render this text clearly)

Design Aesthetic:
{keywords}

Color Palette:
- Primary (chocolate): {primary_hex}
- Secondary (cream): {secondary_hex}
- Use neutral, muted tones throughout

Composition:
- {style_config.get('composition', {}).get('layout', 'minimalist, centered')}
- {style_config.get('composition', {}).get('white_space', 'ample white space')}
- Typography: elegant serif or clean sans-serif, excellent legibility

AVOID: {avoid}

The design should feel timeless, sophisticated, and whisper luxury rather than shout it.
Render the text clearly with proper spacing for print-ready output at 300 DPI.
"""
    return prompt.strip()


@tool
def gorsel_tasarla(
    urun_adi: str,
    urun_gramaj: str = "50g",
    urun_aciklama: str = "",
    mod: Literal["prompt", "varyasyon_prompt", "bilgi"] = "prompt",
) -> str:
    """
    Urun etiketi icin gorsel tasarim promptu ve bilgisi uretir.

    Bu skill, The Curator agent'in gorsel tasarim workflow'unu destekler.
    Gemini 3 Pro Image API icin optimize edilmis narrative promptlar olusturur.

    Args:
        urun_adi: Urun adi (ornek: "Antep Fistikli", "Ruby Tablet")
        urun_gramaj: Urun gramaji (ornek: "50g", "85g", "100g")
        urun_aciklama: Urun aciklamasi/lezzet notlari
        mod: Islem modu
            - "prompt": Tek bir tasarim promptu olustur
            - "varyasyon_prompt": 3-4 varyasyon icin prompt seti olustur
            - "bilgi": Style guide ve specs bilgisi dondur

    Returns:
        Gemini API icin hazir prompt veya bilgi metni

    Ornek:
        gorsel_tasarla("Bitter Orange", "85g", "Portakal parcali bitter cikolata")
        gorsel_tasarla("Ruby Tablet", mod="varyasyon_prompt")
        gorsel_tasarla("", mod="bilgi")
    """
    sections = []

    # Style config ve renkleri yukle
    style_config = _load_style_config()
    brand_colors = _load_brand_colors()

    if mod == "bilgi":
        # Style guide bilgisi
        sections.append("# Sade Chocolate - Gorsel Stil Kilavuzu\n")
        sections.append(f"**Estetik:** {style_config.get('aesthetic', 'quiet_luxury')}")
        sections.append(
            f"**Stil Anahtar Kelimeleri:** {', '.join(style_config.get('style_keywords', []))}"
        )
        sections.append(
            f"**Kacinilacaklar:** {', '.join(style_config.get('avoid_keywords', []))}"
        )

        specs = style_config.get("label_specs", {})
        sections.append("\n## Etiket Teknik Ozellikleri")
        sections.append(f"- Aspect Ratio: {specs.get('aspect_ratio', '3:4')}")
        sections.append(f"- Cozunurluk: {specs.get('resolution', '2K')}")
        sections.append(f"- Max Metin: {specs.get('text_max_chars', 25)} karakter")
        sections.append(f"- DPI: {specs.get('dpi', 300)}")

        sections.append("\n## Renk Paleti")
        for color_name, color_data in brand_colors.items():
            if isinstance(color_data, dict):
                sections.append(
                    f"- {color_name}: {color_data.get('hex', 'N/A')} - {color_data.get('usage', '')}"
                )

        return "\n".join(sections)

    elif mod == "varyasyon_prompt":
        # 3 varyasyon icin farkli yaklasimlari vurgulayan promptlar
        sections.append(f"# Etiket Varyasyonlari: {urun_adi} {urun_gramaj}\n")
        sections.append("3 farkli varyasyon icin Gemini'ye gonderilecek promptlar:\n")

        base_prompt = _build_label_prompt(
            urun_adi, urun_gramaj, urun_aciklama, style_config, brand_colors
        )

        variations = [
            (
                "Klasik Minimalist",
                "Focus on extreme minimalism. Single focal point, maximum white space, text as the hero element.",
            ),
            (
                "Organik Dokulu",
                "Add subtle organic texture (paper grain, fabric weave). Warm, tactile feeling while maintaining elegance.",
            ),
            (
                "Geometrik Sofistike",
                "Introduce subtle geometric elements (thin lines, gentle shapes). Modern sophistication, architectural feel.",
            ),
        ]

        for i, (var_name, var_addition) in enumerate(variations, 1):
            sections.append(f"## Varyasyon {i}: {var_name}")
            sections.append(f"```\n{base_prompt}\n\nVariation Focus: {var_addition}\n```\n")

        sections.append("\n---")
        sections.append("## Agent Talimatlari")
        sections.append("1. Her varyasyonu sirayla Gemini API'ye gonder")
        sections.append(f"2. Sonuclari outputs/labels/{urun_adi}/v1/ klasorune kaydet")
        sections.append("3. Kullaniciya 3 varyasyonu sun, secim bekle")
        sections.append("4. Secilen varyasyonu refinement icin hazir tut")

        return "\n".join(sections)

    else:  # mod == "prompt"
        # Tek prompt
        prompt = _build_label_prompt(
            urun_adi, urun_gramaj, urun_aciklama, style_config, brand_colors
        )

        sections.append(f"# Etiket Tasarim Promptu: {urun_adi}\n")
        sections.append("Gemini 3 Pro Image API icin hazir prompt:\n")
        sections.append(f"```\n{prompt}\n```")

        sections.append("\n---")
        sections.append("## Teknik Notlar")
        specs = style_config.get("label_specs", {})
        sections.append(f"- Aspect Ratio: {specs.get('aspect_ratio', '3:4')}")
        sections.append(f"- Cozunurluk: {specs.get('resolution', '2K')}")
        sections.append("- Format: PNG (300 DPI)")

        sections.append("\n## Agent Talimatlari")
        sections.append("1. Bu promptu Gemini API'ye gonder")
        sections.append("2. Uretilen gorseli degerlendirmek icin kullaniciya sun")
        sections.append("3. Refinement talepleri varsa conversational editing uygula")

        return "\n".join(sections)


__all__ = ["gorsel_tasarla"]
