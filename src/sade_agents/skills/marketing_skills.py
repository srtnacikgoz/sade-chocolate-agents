"""
Sade Agents - Marketing Skills.

Growth Hacker agent'in kullandigi pazar arastirma araclari.
Sosyal medya trendleri (gundem) ve kampanya performans analizi.
"""

from crewai.tools import tool

# -------------------------------------------------------------------------
# MOCK DATA
# -------------------------------------------------------------------------
# Phase 2'de gercek Instagram/Pinterest API'larina baglanacak.

TREND_DATA = {
    "genel": {
        "rising_stars": ["Yuzu", "Matcha", "Tahin", "Lavanta"],
        "declining": ["Red Velvet", "Oreo", "Bal Kabagi"],
        "sentiment": "Pozitif (%78)",
        "viral_hashtags": ["#sadeleziz", "#cikolataaski", "#quietluxury", "#artisan"]
    },
    "ruby": {
        "rising_stars": ["Orman Meyveleri", "Sampanya", "Gul"],
        "sentiment": "Cok Yuksek (%92) - Merak uyandiriyor",
        "viral_hashtags": ["#rubychocolate", "#pinkchocolate", "#dogalpembe"]
    }
}

# -------------------------------------------------------------------------
# MARKETING TOOLS
# -------------------------------------------------------------------------

@tool("gundem_analizi")
def gundem_analizi(odak: str = "genel") -> str:
    """
    Sosyal medya ve pazar trendlerini analiz eder.
    'The Growth Hacker' agent'i tarafindan kullanilir.

    Args:
        odak: 'genel' veya ozel bir kategori (orn: 'ruby')

    Returns:
        Trend raporu (Markdown).
    """
    
    data = TREND_DATA.get(odak, TREND_DATA["genel"])
    
    return f"""
    # 📈 Pazar ve Trend Raporu: {odak.upper()}
    
    ## 🌟 Yükselen Yıldızlar (Rising Stars)
    Su an sosyal medyada (Instagram/Pinterest) en cok konusulan lezzetler:
    {', '.join(data['rising_stars'])}
    
    ## 📉 Düşüştekiler
    Populerligini yitirenler:
    {', '.join(data.get('declining', []))}
    
    ## 💬 Duygu Analizi (Sentiment)
    **Skor:** {data['sentiment']}
    **Yorum Özeti:** Tüketici "yapay" tatlardan kaçıyor, "hikayesi olan" ürün arıyor.
    
    ## #️⃣ Viral Hashtagler
    {', '.join(data['viral_hashtags'])}
    
    ---
    
    **Growth Hacker İpucu:**
    Eğer yeni ürün çıkaracaksanız, yukselen yildizlardan birini (Örn: {data['rising_stars'][0]}) 
    kullanmaniz viral etkiyi %40 artirabilir.
    """

__all__ = ["gundem_analizi"]
