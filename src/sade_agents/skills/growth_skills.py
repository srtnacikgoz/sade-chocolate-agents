"""
Sade Agents - The Growth Hacker Skills.

The Growth Hacker agent'ın kullandığı skill'ler.
Trend takibi ve büyüme fırsatları yetenekleri.
"""

from crewai.tools import tool


# Mock trend verileri (gerçek API/scraping ileride eklenebilir)
TREND_VERILERI = {
    "x_twitter": [
        {
            "hashtag": "#artisanchocolate",
            "mentions": 2400,
            "sentiment": "pozitif",
            "trend": "yukselis",
        },
        {
            "hashtag": "#turkishsweets",
            "mentions": 1800,
            "sentiment": "pozitif",
            "trend": "stabil",
        },
        {
            "hashtag": "#premiumgifts",
            "mentions": 3200,
            "sentiment": "notr",
            "trend": "yukselis",
        },
        {
            "hashtag": "#cikolata",
            "mentions": 4500,
            "sentiment": "pozitif",
            "trend": "stabil",
        },
        {
            "hashtag": "#chocolatelover",
            "mentions": 8900,
            "sentiment": "pozitif",
            "trend": "yukselis",
        },
    ],
    "instagram": [
        {"trend": "Minimalist ambalaj", "engagement": "yuksek", "segment": "luks"},
        {"trend": "Single origin çikolata", "engagement": "orta", "segment": "gurme"},
        {"trend": "Hediye kutusu", "engagement": "cok_yuksek", "segment": "kurumsal"},
        {"trend": "Bean-to-bar storytelling", "engagement": "yuksek", "segment": "gurme"},
        {"trend": "Sustainable packaging", "engagement": "orta", "segment": "luks"},
    ],
    "reddit": [
        {
            "subreddit": "r/chocolate",
            "topic": "Turkish chocolate brands",
            "upvotes": 156,
            "sentiment": "merakli",
        },
        {
            "subreddit": "r/snackexchange",
            "topic": "Premium chocolates",
            "upvotes": 89,
            "sentiment": "pozitif",
        },
        {
            "subreddit": "r/FoodPorn",
            "topic": "Artisan chocolate close-ups",
            "upvotes": 2300,
            "sentiment": "pozitif",
        },
    ],
    "pazar_sinyalleri": [
        {
            "sinyal": "Zorlu Center yeni gıda katta açılış",
            "tip": "firsat",
            "oncelik": "yuksek",
        },
        {
            "sinyal": "Vakko yeni çikolata serisi lansmanı",
            "tip": "rakip",
            "oncelik": "orta",
        },
        {
            "sinyal": "Nişantaşı butik trendi devam ediyor",
            "tip": "lokasyon",
            "oncelik": "orta",
        },
        {
            "sinyal": "Kurumsal hediye sezonu yaklaşıyor (Şubat)",
            "tip": "sezon",
            "oncelik": "yuksek",
        },
        {
            "sinyal": "Bebek'te yeni premium cafe açılışları",
            "tip": "lokasyon",
            "oncelik": "dusuk",
        },
    ],
}


def _format_twitter_verileri() -> str:
    """X (Twitter) verilerini tablo formatında döner."""
    lines = ["### X (Twitter) Trendleri\n"]
    lines.append("| Hashtag | Mentions | Sentiment | Trend |")
    lines.append("|---------|----------|-----------|-------|")

    for item in TREND_VERILERI["x_twitter"]:
        trend_emoji = "📈" if item["trend"] == "yukselis" else "➡️"
        hashtag = item["hashtag"]
        mentions = item["mentions"]
        sentiment = item["sentiment"]
        trend = item["trend"]
        lines.append(f"| {hashtag} | {mentions:,} | {sentiment} | {trend_emoji} {trend} |")

    return "\n".join(lines)


def _format_instagram_verileri() -> str:
    """Instagram verilerini tablo formatında döner."""
    lines = ["\n### Instagram Trendleri\n"]
    lines.append("| Trend | Engagement | Segment |")
    lines.append("|-------|------------|---------|")

    for item in TREND_VERILERI["instagram"]:
        lines.append(
            f"| {item['trend']} | {item['engagement']} | {item['segment']} |"
        )

    return "\n".join(lines)


def _format_reddit_verileri() -> str:
    """Reddit verilerini tablo formatında döner."""
    lines = ["\n### Reddit Konuşmaları\n"]
    lines.append("| Subreddit | Konu | Upvotes | Sentiment |")
    lines.append("|-----------|------|---------|-----------|")

    for item in TREND_VERILERI["reddit"]:
        subreddit = item["subreddit"]
        topic = item["topic"]
        upvotes = item["upvotes"]
        sentiment = item["sentiment"]
        lines.append(f"| {subreddit} | {topic} | {upvotes} | {sentiment} |")

    return "\n".join(lines)


def _format_pazar_sinyalleri() -> str:
    """Pazar sinyallerini tablo formatında döner."""
    lines = ["\n### Pazar Sinyalleri\n"]
    lines.append("| Sinyal | Tip | Öncelik |")
    lines.append("|--------|-----|---------|")

    oncelik_emoji = {"yuksek": "🔴", "orta": "🟡", "dusuk": "🟢"}

    for item in TREND_VERILERI["pazar_sinyalleri"]:
        emoji = oncelik_emoji.get(item["oncelik"], "⚪")
        sinyal = item["sinyal"]
        tip = item["tip"]
        oncelik = item["oncelik"]
        lines.append(f"| {sinyal} | {tip} | {emoji} {oncelik} |")

    return "\n".join(lines)


def _hesapla_ozet_istatistikler() -> str:
    """Tüm platformlar için özet istatistikler hesaplar."""
    # Twitter özeti
    twitter_data = TREND_VERILERI["x_twitter"]
    toplam_mentions = sum(item["mentions"] for item in twitter_data)
    yukselis_count = sum(1 for item in twitter_data if item["trend"] == "yukselis")

    # Instagram özeti
    instagram_data = TREND_VERILERI["instagram"]
    yuksek_engagement = sum(
        1 for item in instagram_data if item["engagement"] in ["yuksek", "cok_yuksek"]
    )

    # Reddit özeti
    toplam_upvotes = sum(item["upvotes"] for item in TREND_VERILERI["reddit"])

    # Pazar sinyalleri özeti
    pazar_data = TREND_VERILERI["pazar_sinyalleri"]
    yuksek_oncelik = sum(1 for item in pazar_data if item["oncelik"] == "yuksek")

    lines = [
        "\n## 📊 Özet İstatistikler\n",
        f"- **X (Twitter):** {toplam_mentions:,} toplam mention, "
        f"{yukselis_count} yükselen trend",
        f"- **Instagram:** {yuksek_engagement} yüksek engagement'lı trend",
        f"- **Reddit:** {toplam_upvotes:,} toplam upvote",
        f"- **Pazar Sinyalleri:** {yuksek_oncelik} yüksek öncelikli fırsat",
    ]

    return "\n".join(lines)


@tool
def sosyal_nabiz(platform: str = "tumu") -> str:
    """
    Sosyal medya ve pazar trendlerini kontrol eder ve analiz için veri sağlar.

    Bu tool X (Twitter), Instagram, Reddit ve pazar sinyallerinden trend verilerini
    toplar ve Growth Hacker agent'ın analiz yapması için formatlar.
    Şu anda mock veriler kullanıyor, ileride gerçek API'larla güncellenebilir.

    Args:
        platform: Kontrol edilecek platform. Seçenekler:
                  - "x_twitter" - X (Twitter) hashtag trendleri
                  - "instagram" - Instagram içerik trendleri
                  - "reddit" - Reddit konuşmaları
                  - "pazar" - Pazar sinyalleri (açılışlar, rakipler, sezonlar)
                  - "tumu" (default) - Tüm platformlar

    Returns:
        Trend raporu: Platform bazlı trend tabloları ve analiz prompt'u

    Kullanım:
        sosyal_nabiz()  # Tüm platformlar
        sosyal_nabiz("x_twitter")  # Sadece Twitter
        sosyal_nabiz("instagram")  # Sadece Instagram
        sosyal_nabiz("pazar")  # Sadece pazar sinyalleri
    """
    sections = []
    sections.append("# 📡 Sosyal Nabız Raporu\n")

    if platform == "tumu":
        sections.append(_format_twitter_verileri())
        sections.append(_format_instagram_verileri())
        sections.append(_format_reddit_verileri())
        sections.append(_format_pazar_sinyalleri())
        sections.append(_hesapla_ozet_istatistikler())
    elif platform == "x_twitter":
        sections.append(_format_twitter_verileri())
    elif platform == "instagram":
        sections.append(_format_instagram_verileri())
    elif platform == "reddit":
        sections.append(_format_reddit_verileri())
    elif platform == "pazar":
        sections.append(_format_pazar_sinyalleri())
    else:
        valid_options = "x_twitter, instagram, reddit, pazar, tumu"
        return f"Bilinmeyen platform: {platform}. Geçerli seçenekler: {valid_options}"

    # Analiz prompt template
    analiz_template = """

---

## 🎯 ANALİZ TALİMATLARI

Yukarıdaki trend verilerini analiz et ve şu soruları yanıtla:

### 1. Öne Çıkan Trendler
- Hangi hashtag/trend en çok konuşuluyor?
- Yükselen trendler neler? (📈 işaretli)
- Sade için uygulanabilir olanlar hangileri?

### 2. Fırsat Değerlendirmesi
Sade Chocolate için:
- **Hemen değerlendir:** Yüksek öncelikli, zamanlaması kritik
- **Takipte tut:** Orta öncelikli, gelişmeleri izle
- **Şimdilik geç:** Düşük öncelikli veya uyumsuz

### 3. Rakip İstihbaratı
- Rakiplerden gelen sinyaller var mı?
- Sade nasıl farklılaşabilir?
- Defensive aksiyonlar gerekli mi?

### 4. Aksiyon Önerileri
Her öneri için:
- **Ne:** Yapılacak aksiyon
- **Neden:** Bu trend/sinyal neden önemli
- **Ne zaman:** Aciliyet seviyesi
- **Kim:** Hangi departman/agent devreye girmeli

---

**NOT:** Bu veriler mock verilerdir. Gerçek veriler için sosyal medya API'larını entegre edin.
"""

    sections.append(analiz_template)

    return "\n".join(sections)


__all__ = ["sosyal_nabiz"]
