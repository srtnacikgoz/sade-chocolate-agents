"""
Sade Agents - Product Design Skills.

The Curator ve The Alchemist agent'larinin kullandigi yaratici araclar.
Gorsel tasarim (etiket) ve lezzet mimarisi (recete) yetenekleri.
"""

from crewai.tools import tool

# -------------------------------------------------------------------------
# CONFIG & STYLES
# -------------------------------------------------------------------------

STYLE_GUIDE = {
    "font_primary": "Cormorant Garamond (Serif)",
    "font_secondary": "Outfit (Sans-serif)",
    "colors": {
        "ruby": "Muted Rose / Soft Pink",
        "dark": "Obsidian Black / Deep Cocoa",
        "gold": "Antique Gold Foil",
        "paper": "Textured Cream Stock"
    },
    "layout": "Minimalist, centered typography, negative space heavy"
}

# -------------------------------------------------------------------------
# PRODUCT TOOLS
# -------------------------------------------------------------------------

@tool("etiket_tasarla")
def etiket_tasarla(urun_adi: str, konsept: str) -> str:
    """
    Urun icin etiket tasarim prompt'u olusturur.
    'The Curator' agent'i tarafindan kullanilir.

    Args:
        urun_adi: Urunun adi (Orn: 'Ruby Tablet')
        konsept: Tasarim konsepti/hikayesi

    Returns:
        Midjourney/DALL-E icin hazirlanmis detayli gorsel prompt.
    """
    
    # Renk paleti secimi
    if "ruby" in urun_adi.lower():
        color_theme = STYLE_GUIDE["colors"]["ruby"]
    elif "bitter" in urun_adi.lower() or "dark" in urun_adi.lower():
        color_theme = STYLE_GUIDE["colors"]["dark"]
    else:
        color_theme = "Neutral Beige / Warm Grey"

    prompt = f"""
    **DESIGN PROMPT FOR LABEL GENERATION**
    
    **Subject:** Premium chocolate bar label design for '{urun_adi}'.
    **Style:** Quiet Luxury, Minimalist, Sophisticated.
    **Brand Voice:** Understated elegance. No shouting.
    
    **Visual Elements:**
    - **Typography:** {STYLE_GUIDE['font_primary']} for the product name. Elegant, high-contrast serif.
    - **Secondary Type:** {STYLE_GUIDE['font_secondary']} for details. Clean sans-serif.
    - **Color Palette:** {color_theme} background with {STYLE_GUIDE['colors']['gold']} accents.
    - **Material:** Visualize as printed on {STYLE_GUIDE['colors']['paper']}. Visible paper texture.
    - **Layout:** {STYLE_GUIDE['layout']}. Lots of breathing room.
    
    **Concept**: {konsept}
    
    **Composition:**
    - Front view, flat lay or slight angle.
    - Soft, natural lighting (Golden Hour).
    - No cartoons, no mascots, no excessive vector art.
    - Focus on typography and texture.
    
    --ar 4:5 --q 2 --v 6.0
    """
    
    return prompt.strip()

@tool("lezzet_pisileri")
def lezzet_pisileri(mevsim: str = "kis") -> str:
    """
    Mevsimsel lezzet eslesmeleri ve malzeme onerilari sunar.
    'The Alchemist' agent'i tarafindan kullanilir.

    Args:
        mevsim: 'kis', 'ilkbahar', 'yaz', 'sonbahar'

    Returns:
        Mevsime uygun malzeme listesi ve pairing onerileri.
    """
    ingredients = {
        "kis": ["kestane", "hurma", "portakal", "greyfurt", "nar"],
        "ilkbahar": ["cilek", "murerver cicegi", "badem caglası", "gül"],
        "yaz": ["kiraz", "incir", "lavanta", "seftali"],
        "sonbahar": ["balkabagi", "ayva", "ceviz", "tarcin"]
    }
    
    selected = ingredients.get(mevsim, ingredients["kis"])
    
    return f"""
    # 🧪 Lezzet Laboratuvarı Raporu
    
    ## 📅 Mevsimsel Malzemeler ({mevsim.title()})
    
    {'\n'.join([f'- {i}' for i in selected])}
    
    **Gelecek ay (Subat):** kan portakalı, limon, kestane...
    
    ---
    
    ## 🎯 REÇETECİ TALİMATLARI
    
    Yukarıdaki lezzet verilerini kullanarak reçete önerileri geliştir:
    
    ### 1. Konsept Oluşturma
    - Hangi çikolata bazı kullanılacak?
    - Ana lezzet profili ne olacak? (klasik/cesur/meyveli)
    - Mevsimsel malzemelerden hangisi uygun?
    
    ### 2. Kombinasyon Önerisi
    Her öneri için:
    - **Ana Malzemeler:** Çikolata + 2-3 eşleştirme
    - **Neden Çalışır:** Flavor pairing açıklaması
    - **Teknik Not:** Tempering, oran, dikkat edilecekler
    
    ### 3. Ürün Konsepti
    - **İsim Önerisi:** "Sessiz Lüks" markasına uygun
    - **Hedef Segment:** Premium/gurme/kurumsal hediye
    - **Sezon:** Hangi dönem için ideal
    
    ### 4. Üretim Notları
    - Couverture seçimi (Callebaut/Valrhona)
    - Ganache/pralin oranları
    - Raf ömrü değerlendirmesi
    
    ---
    
    **NOT:** Bu veriler Sade Chocolate ürün geliştirme referansıdır.
    """

__all__ = ["etiket_tasarla", "lezzet_pisileri"]
