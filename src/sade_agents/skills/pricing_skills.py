"""
Sade Agents - Pricing Analyst Skills.

The Pricing Analyst agent'in finansal zekasi.
Rakip istihbarati (Competitor Watchdog) ve dinamik fiyatlandirma motoru.

Competitors:
- Vakko L'Atelier (Pazar Lideri - Referans)
- Butterfly (Butik Rakip)
- Marie Antoinette (Nis/Ozel)
- Baylan (Klasik Luks)
- Divan (Giris Seviyesi Bariyer)
"""

import asyncio
from typing import Any, Dict, List, Optional
from crewai.tools import tool

# -------------------------------------------------------------------------
# CONSTANTS & CONFIG
# -------------------------------------------------------------------------

# Jewel Fee: Tekli ve ozel urunler icin uygulanan "Sanat Eseri" primi
JEWEL_FEE_MULTIPLIER = 1.25  # %25 Premium

# Hammadde maliyetleri (TL/kg - Mock, Phase 2'de ERP'den gelecek)
COST_BASE = {
    "kakao_ruby": 650.0,    # Ruby cikolata hammadesi
    "kakao_bitter": 450.0,
    "kakao_sutlu": 420.0,
    "fistik_antep": 1100.0, # Boz fistik
    "ambalaj_luks": 85.0,   # Kutu basi maliyet
}

# -------------------------------------------------------------------------
# MOCK DATA (Fallback)
# -------------------------------------------------------------------------
# Gercek scraping kapaliysa veya hata verirse kullanilacak guncel veriler.
# Tarih: 30.01.2026
RAKIP_FIYATLARI = {
    "vakko": [
        {"urun": "Vakko Pralin (Kutu)", "gramaj": 250, "fiyat": 2900, "tl_gram": 11.60},
        {"urun": "Vakko Tablet", "gramaj": 100, "fiyat": 950, "tl_gram": 9.50},
    ],
    "butterfly": [
        {"urun": "Butterfly Kesif Serisi", "gramaj": 140, "fiyat": 1486, "tl_gram": 10.62},
        {"urun": "Butterfly Tablet", "gramaj": 80, "fiyat": 750, "tl_gram": 9.37},
    ],
    "marie_antoinette": [
        {"urun": "MA Ozel Koleksiyon", "gramaj": 200, "fiyat": 1900, "tl_gram": 9.50},
    ],
    "baylan": [
        {"urun": "Baylan Klasik", "gramaj": 300, "fiyat": 2550, "tl_gram": 8.50},
    ],
    "divan": [
        {"urun": "Divan Arduaz", "gramaj": 250, "fiyat": 1150, "tl_gram": 4.60},
        {"urun": "Divan Pralin", "gramaj": 250, "fiyat": 1930, "tl_gram": 7.72},
    ],
}

# -------------------------------------------------------------------------
# CORE FUNCTIONS
# -------------------------------------------------------------------------

def _calculate_jewel_price(base_price: float) -> float:
    """
    Sade'nin 'Jewel Fee' stratejisini uygular.
    Tekli, ozel ve el yapimi urunlere %25 'Sanat Eseri' primi ekler.
    """
    return base_price * JEWEL_FEE_MULTIPLIER

def _get_competitor_data(source: str = "mock") -> Dict[str, List[Dict[str, Any]]]:
    """
    Rakip fiyat verilerini getirir.
    Phase 2'de buraya 'scrapers' modulu baglanacak.
    """
    # Simdilik sadece mock donduruyoruz, ama yapi hazir.
    return RAKIP_FIYATLARI

def _format_price_table(data: Dict[str, List[Dict[str, Any]]]) -> str:
    """Veriyi Markdown tablosuna cevirir."""
    lines = ["| Marka | Ürün | Gramaj | Fiyat | TL/Gr |", "|---|---|---|---|---|"]
    
    for brand, products in data.items():
        brand_name = brand.replace("_", " ").title()
        for p in products:
            lines.append(
                f"| {brand_name} | {p['urun']} | {p['gramaj']}g | {p['fiyat']} TL | **{p['tl_gram']:.2f}** |"
            )
    return "\n".join(lines)

# -------------------------------------------------------------------------
# TOOLS (Exposed to Agent)
# -------------------------------------------------------------------------

@tool("fiyat_kontrol")
def fiyat_kontrol(rakip: str = "tumu") -> str:
    """
    Rakip fiyatlarini analiz eder. 'Magic Word' tetikleyicisi: /fiyat_kontrol
    
    Args:
        rakip (str): 'vakko', 'butterfly', 'divan' veya 'tumu'.
    
    Returns:
        str: Rakip fiyat tablosu ve Sade icin stratejik oneri.
    """
    all_data = _get_competitor_data()
    
    # Filtreleme
    if rakip and rakip != "tumu":
        if rakip in all_data:
            filtered_data = {rakip: all_data[rakip]}
        else:
            return f"HATA: '{rakip}' listemizde yok. (Gecerli: vakko, butterfly, divan...)"
    else:
        filtered_data = all_data

    table = _format_price_table(filtered_data)
    
    # Analiz Promptu (Agent'in yorumlamasi icin)
    analysis = f"""
    ## 📊 FİYAT ANALİZ RAPORU
    
    {table}
    
    ---
    ### 🧠 Stratejik Konumlandirma (Sade Chocolate)
    
    **Hedef:** "Ulasilabilir Luks" degil, "Sessiz Luks".
    **Referans:** Vakko'nun hemen alti, Divan'in cok ustu.
    
    **Maliyet Notu:**
    - Hammadde artis trendi var (Kakao +%15).
    - 'Jewel Fee' (%25 Prim) el yapimi urunlerde uygulanmali.
    
    Bu tabloya bakarak:
    1. Sade'nin 100g Tablet fiyati ne olmali?
    2. Hangi rakipler "Tehlikeli" derecede ucuzladi?
    3. Zam yapma zamani geldi mi?
    """
    
    return analysis

@tool("maliyet_analizi")
def maliyet_analizi(urun_tipi: str, gramaj: int) -> str:
    """
    Bir urunun tahmini maliyetini ve satis fiyatini hesaplar.
    
    Args:
        urun_tipi (str): 'ruby_tablet', 'fistikli_bar', etc.
        gramaj (int): Urunun net agirligi.
    """
    # Basit maliyet hesaplama (Ornek)
    # Phase 2'de dinamik recete motoruna baglanacak.
    
    base_cost = 0.0
    
    if "ruby" in urun_tipi.lower():
        # Ruby maliyeti: 650 TL/kg -> 0.65 TL/g
        raw_material = (COST_BASE["kakao_ruby"] / 1000) * gramaj
        packaging = COST_BASE["ambalaj_luks"]
        base_cost = raw_material + packaging
    elif "fistik" in urun_tipi.lower():
        # Fistikli karisim (%40 fistik varsayimi)
        fistik_cost = (COST_BASE["fistik_antep"] / 1000) * (gramaj * 0.4)
        chocolate_cost = (COST_BASE["kakao_sutlu"] / 1000) * (gramaj * 0.6)
        packaging = COST_BASE["ambalaj_luks"]
        base_cost = fistik_cost + chocolate_cost + packaging
    else:
        # Standart Bitter
        raw_material = (COST_BASE["kakao_bitter"] / 1000) * gramaj
        packaging = COST_BASE["ambalaj_luks"] * 0.8 # Daha basit kutu
        base_cost = raw_material + packaging
        
    # Satis Fiyati Onerisi (x3.5 Mark-up + Jewel Fee)
    base_price = base_cost * 3.5
    final_price = _calculate_jewel_price(base_price)
    
    return f"""
    ## 💰 MALİYET ANALİZİ: {urun_tipi.title()} ({gramaj}g)
    
    - **Hammadde + Ambalaj:** {base_cost:.2f} TL
    - **Operasyonel Maliyet:** {(base_cost * 0.5):.2f} TL (Tahmini)
    - **Basabas Noktasi:** {(base_cost * 1.5):.2f} TL
    
    ---
    ### 🏷️ FIYAT ONERISI
    
    **Taban Fiyat (x3.5):** {base_price:.2f} TL
    **Sade 'Jewel' Fiyati (+%25):** {final_price:.2f} TL
    
    *Not: Bu fiyat, rakiplere gore (Orn: Vakko {11.60 * gramaj:.2f} TL) hala rekabetci mi?*
    """
