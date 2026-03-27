"""
Sade Agents - The Growth Hacker Skills.

The Growth Hacker agent'ın kullandığı skill'ler.
Trend takibi ve büyüme fırsatları yetenekleri.

Reddit API entegrasyonu ile GERCEK veri ceker.
API yoksa mock veriye fallback yapar.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from crewai.tools import tool

from sade_agents.config import get_settings

logger = logging.getLogger(__name__)

# Varsayilan takip edilecek subreddit'ler
# Config'den veya UI'dan degistirilebilir
DEFAULT_SUBREDDITS = [
    "chocolate",
    "snackexchange",
    "FoodPorn",
    "Candy",
    "DessertPorn",
]

# Arama keyword'leri (cikolata ile ilgili)
SEARCH_KEYWORDS = [
    "artisan chocolate",
    "premium chocolate",
    "turkish chocolate",
    "bean to bar",
    "truffle",
    "praline",
]


def _get_reddit_client():
    """
    Reddit API client'i olusturur.

    Returns:
        praw.Reddit instance veya None (API yapılandırılmamışsa)
    """
    settings = get_settings()

    if not settings.is_reddit_configured():
        logger.info("Reddit API yapilandirilmamis, mock veri kullanilacak")
        return None

    try:
        import praw

        reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )
        # Baglanti testi
        reddit.user.me()  # Read-only modda None doner, hata vermez
        return reddit
    except ImportError:
        logger.warning("praw kurulu degil: pip install praw")
        return None
    except Exception as e:
        logger.error(f"Reddit baglanti hatasi: {e}")
        return None


def _fetch_subreddit_posts(reddit, subreddit_name: str, limit: int = 10) -> list[dict]:
    """
    Bir subreddit'ten son postlari ceker.

    Args:
        reddit: praw.Reddit instance
        subreddit_name: Subreddit adi (r/ olmadan)
        limit: Cekilecek post sayisi

    Returns:
        Post listesi (dict'ler)
    """
    posts = []
    try:
        subreddit = reddit.subreddit(subreddit_name)

        for post in subreddit.hot(limit=limit):
            # Son 7 gun icerisindeki postlar
            post_time = datetime.fromtimestamp(post.created_utc)
            if datetime.now() - post_time > timedelta(days=7):
                continue

            posts.append({
                "title": post.title,
                "score": post.score,
                "num_comments": post.num_comments,
                "url": f"https://reddit.com{post.permalink}",
                "created": post_time.strftime("%Y-%m-%d"),
                "subreddit": subreddit_name,
            })
    except Exception as e:
        logger.warning(f"r/{subreddit_name} cekilemedi: {e}")

    return posts


def _search_reddit(reddit, query: str, limit: int = 10) -> list[dict]:
    """
    Reddit'te arama yapar.

    Args:
        reddit: praw.Reddit instance
        query: Arama sorgusu
        limit: Sonuc sayisi

    Returns:
        Arama sonuclari (dict'ler)
    """
    results = []
    try:
        for post in reddit.subreddit("all").search(query, sort="relevance", time_filter="week", limit=limit):
            results.append({
                "title": post.title,
                "score": post.score,
                "num_comments": post.num_comments,
                "url": f"https://reddit.com{post.permalink}",
                "subreddit": post.subreddit.display_name,
            })
    except Exception as e:
        logger.warning(f"Arama hatasi '{query}': {e}")

    return results


def _analyze_sentiment(text: str) -> str:
    """
    Basit keyword-based sentiment analizi.

    Ileride AI ile gelistirilebilir.
    """
    text_lower = text.lower()

    positive_words = ["love", "amazing", "best", "great", "delicious", "perfect", "recommend", "favorite"]
    negative_words = ["bad", "worst", "terrible", "disappointing", "overpriced", "avoid", "hate"]

    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)

    if pos_count > neg_count:
        return "pozitif"
    elif neg_count > pos_count:
        return "negatif"
    return "notr"


def _get_real_reddit_data() -> dict[str, Any]:
    """
    Reddit API'den gercek veri ceker.

    Returns:
        Kategorize edilmis Reddit verileri
    """
    reddit = _get_reddit_client()

    if reddit is None:
        return None  # Fallback to mock

    data = {
        "subreddit_posts": [],
        "search_results": [],
        "trending_topics": [],
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    # Subreddit'lerden postlari cek
    for sub in DEFAULT_SUBREDDITS:
        posts = _fetch_subreddit_posts(reddit, sub, limit=5)
        data["subreddit_posts"].extend(posts)

    # Keyword aramalari
    for keyword in SEARCH_KEYWORDS[:3]:  # Ilk 3 keyword (rate limit icin)
        results = _search_reddit(reddit, keyword, limit=5)
        data["search_results"].extend(results)

    # Trending topics (en cok upvote alan)
    all_posts = data["subreddit_posts"] + data["search_results"]
    sorted_posts = sorted(all_posts, key=lambda x: x["score"], reverse=True)
    data["trending_topics"] = sorted_posts[:10]

    return data


# Mock veri (API yoksa fallback)
MOCK_TREND_VERILERI = {
    "reddit": [
        {
            "subreddit": "r/chocolate",
            "title": "Best Turkish chocolate brands?",
            "score": 156,
            "num_comments": 45,
            "sentiment": "merakli",
        },
        {
            "subreddit": "r/snackexchange",
            "title": "Premium chocolates from Turkey",
            "score": 89,
            "num_comments": 23,
            "sentiment": "pozitif",
        },
        {
            "subreddit": "r/FoodPorn",
            "title": "Artisan chocolate close-ups [OC]",
            "score": 2300,
            "num_comments": 87,
            "sentiment": "pozitif",
        },
        {
            "subreddit": "r/Candy",
            "title": "Bean-to-bar chocolate recommendations",
            "score": 234,
            "num_comments": 56,
            "sentiment": "pozitif",
        },
        {
            "subreddit": "r/chocolate",
            "title": "Single origin vs blend - which do you prefer?",
            "score": 445,
            "num_comments": 123,
            "sentiment": "notr",
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
            "sinyal": "Kurumsal hediye sezonu yaklaşıyor",
            "tip": "sezon",
            "oncelik": "yuksek",
        },
    ],
}


def _format_real_reddit_data(data: dict) -> str:
    """Gercek Reddit verisini formatlar."""
    lines = ["### Reddit Verileri (GERCEK)\n"]
    lines.append(f"*Guncelleme: {data['fetch_time']}*\n")

    # Trending topics
    lines.append("#### Trending Konular\n")
    lines.append("| Baslik | Subreddit | Score | Yorumlar |")
    lines.append("|--------|-----------|-------|----------|")

    for post in data["trending_topics"][:10]:
        title = post["title"][:50] + "..." if len(post["title"]) > 50 else post["title"]
        lines.append(f"| {title} | r/{post['subreddit']} | {post['score']:,} | {post.get('num_comments', '-')} |")

    # Subreddit ozeti
    lines.append("\n#### Takip Edilen Subreddit'ler\n")
    subreddit_counts = {}
    for post in data["subreddit_posts"]:
        sub = post["subreddit"]
        subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1

    for sub, count in subreddit_counts.items():
        lines.append(f"- r/{sub}: {count} post")

    return "\n".join(lines)


def _format_mock_reddit_data() -> str:
    """Mock Reddit verisini formatlar."""
    lines = ["### Reddit Konuşmaları (MOCK)\n"]
    lines.append("*⚠️ Reddit API yapilandirilmamis - ornek veri gosteriliyor*\n")
    lines.append("| Subreddit | Konu | Score | Sentiment |")
    lines.append("|-----------|------|-------|-----------|")

    for item in MOCK_TREND_VERILERI["reddit"]:
        lines.append(
            f"| {item['subreddit']} | {item['title'][:40]}... | {item['score']} | {item['sentiment']} |"
        )

    return "\n".join(lines)


def _format_pazar_sinyalleri() -> str:
    """Pazar sinyallerini formatlar."""
    lines = ["\n### Pazar Sinyalleri\n"]
    lines.append("| Sinyal | Tip | Öncelik |")
    lines.append("|--------|-----|---------|")

    oncelik_emoji = {"yuksek": "🔴", "orta": "🟡", "dusuk": "🟢"}

    for item in MOCK_TREND_VERILERI["pazar_sinyalleri"]:
        emoji = oncelik_emoji.get(item["oncelik"], "⚪")
        lines.append(f"| {item['sinyal']} | {item['tip']} | {emoji} {item['oncelik']} |")

    return "\n".join(lines)


def _hesapla_ozet(data: dict | None) -> str:
    """Ozet istatistikler."""
    lines = ["\n## 📊 Özet\n"]

    if data:
        # Gercek veri ozeti
        total_posts = len(data["subreddit_posts"]) + len(data["search_results"])
        top_score = max((p["score"] for p in data["trending_topics"]), default=0)
        lines.append(f"- **Toplam post:** {total_posts}")
        lines.append(f"- **En yuksek score:** {top_score:,}")
        lines.append(f"- **Takip edilen subreddit:** {len(DEFAULT_SUBREDDITS)}")
        lines.append(f"- **Veri kaynagi:** Reddit API (GERCEK)")
    else:
        # Mock veri ozeti
        lines.append(f"- **Toplam post:** {len(MOCK_TREND_VERILERI['reddit'])} (mock)")
        lines.append(f"- **Pazar sinyali:** {len(MOCK_TREND_VERILERI['pazar_sinyalleri'])}")
        lines.append(f"- **Veri kaynagi:** Mock (API yapilandirilmamis)")

    return "\n".join(lines)


@tool
def sosyal_nabiz(platform: str = "tumu") -> str:
    """
    Reddit ve pazar trendlerini kontrol eder ve analiz icin veri saglar.

    Reddit API yapilandirilmissa GERCEK veri ceker.
    Yapilandirilmamissa mock veri doner.

    Args:
        platform: Kontrol edilecek platform. Secenekler:
                  - "reddit" - Reddit postlari ve trendleri
                  - "pazar" - Pazar sinyalleri (acilislar, rakipler, sezonlar)
                  - "tumu" (default) - Tum kaynaklar

    Returns:
        Trend raporu: Platform bazli tablo ve analiz prompt'u

    Kullanim:
        sosyal_nabiz()  # Tum kaynaklar
        sosyal_nabiz("reddit")  # Sadece Reddit
        sosyal_nabiz("pazar")  # Sadece pazar sinyalleri
    """
    sections = []
    sections.append("# 📡 Sosyal Nabız Raporu\n")

    # Reddit API'den veri cekmeyi dene
    real_data = None
    if platform in ("tumu", "reddit"):
        real_data = _get_real_reddit_data()

    if platform == "tumu":
        if real_data:
            sections.append(_format_real_reddit_data(real_data))
        else:
            sections.append(_format_mock_reddit_data())
        sections.append(_format_pazar_sinyalleri())
        sections.append(_hesapla_ozet(real_data))
    elif platform == "reddit":
        if real_data:
            sections.append(_format_real_reddit_data(real_data))
        else:
            sections.append(_format_mock_reddit_data())
        sections.append(_hesapla_ozet(real_data))
    elif platform == "pazar":
        sections.append(_format_pazar_sinyalleri())
    else:
        return f"Bilinmeyen platform: {platform}. Gecerli: reddit, pazar, tumu"

    # Analiz talimatlari
    analiz = """

---

## 🎯 ANALİZ TALİMATLARI

### 1. Öne Çıkan Trendler
- En çok konuşulan konular neler?
- Yüksek score'lu postların ortak özellikleri?
- Sade için uygulanabilir içgörüler?

### 2. Fırsat Değerlendirmesi
- **Hemen değerlendir:** Viral potansiyeli olan, zamanlama kritik
- **Takipte tut:** İlginç ama henüz olgunlaşmamış
- **Geç:** Sade'nin segmentine uymuyor

### 3. İçerik Fikirleri
Reddit'te popüler olan konulardan Sade için:
- Sosyal medya içerik fikirleri
- Blog/makale konuları
- Ürün geliştirme ipuçları

### 4. Aksiyon Önerileri
Her öneri için: Ne, Neden, Ne zaman, Kim

---
"""
    sections.append(analiz)

    # API durumu notu
    settings = get_settings()
    if not settings.is_reddit_configured():
        sections.append("""
**⚠️ Reddit API Kurulumu:**
1. https://www.reddit.com/prefs/apps adresine git
2. "Create App" → "script" sec
3. .env dosyasina ekle:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   ```
4. `pip install praw` calistir
""")

    return "\n".join(sections)


@tool
def reddit_ara(query: str, limit: int = 10) -> str:
    """
    Reddit'te belirli bir konuyu arar.

    Args:
        query: Arama sorgusu (ornegin "artisan chocolate turkey")
        limit: Maksimum sonuc sayisi (varsayilan 10)

    Returns:
        Arama sonuclari tablosu

    Kullanim:
        reddit_ara("premium chocolate brands")
        reddit_ara("bean to bar", 5)
    """
    reddit = _get_reddit_client()

    if reddit is None:
        return f"❌ Reddit API yapilandirilmamis. '{query}' aranamadi.\n\nKurulum icin sosyal_nabiz() calistirin."

    results = _search_reddit(reddit, query, limit)

    if not results:
        return f"'{query}' icin sonuc bulunamadi."

    lines = [f"# Reddit Arama: '{query}'\n"]
    lines.append(f"*{len(results)} sonuc bulundu*\n")
    lines.append("| Baslik | Subreddit | Score |")
    lines.append("|--------|-----------|-------|")

    for r in results:
        title = r["title"][:45] + "..." if len(r["title"]) > 45 else r["title"]
        lines.append(f"| {title} | r/{r['subreddit']} | {r['score']:,} |")

    return "\n".join(lines)


__all__ = ["sosyal_nabiz", "reddit_ara"]
