"""
Sade Agents - Scrapers modulu.

Rakip cikolata sitelerinden fiyat bilgisi cekmek icin scraper'lar.

AKILLI SCRAPER (SmartScraper):
- Ana URL verilir, tum site kesfedilir
- Urun sayfalari otomatik bulunur
- Hepsi taranir, sonuclar birlestirilir

ESKİ SCRAPER (AIScraper):
- Tek sayfa tarar
- SmartScraper tarafindan kullanilir
"""

from sade_agents.scrapers.base import BaseScraper, ProductPrice, ScraperResult
from sade_agents.scrapers.ai_scraper import (
    AIScraper,
    ScrapingTarget,
    scrape_all_with_ai,
    load_targets_from_config,
    load_targets_from_file,
    load_targets_from_firebase,
)
from sade_agents.scrapers.smart_scraper import (
    SmartScraper,
    DiscoveredPage,
    SiteDiscoveryResult,
    smart_scrape_all,
)

__all__ = [
    # Base
    "BaseScraper",
    "ProductPrice",
    "ScraperResult",
    # AI Scraper (tek sayfa)
    "AIScraper",
    "ScrapingTarget",
    "scrape_all_with_ai",
    "load_targets_from_config",
    "load_targets_from_file",
    "load_targets_from_firebase",
    # Smart Scraper (site kesfedici) - VARSAYILAN
    "SmartScraper",
    "DiscoveredPage",
    "SiteDiscoveryResult",
    "smart_scrape_all",
    # Eski (deprecated)
    "get_all_scrapers",
    "scrape_all_competitors",
]


def get_all_scrapers() -> list[BaseScraper]:
    """
    DEPRECATED: Eski CSS-tabanli scraper'lar.

    Bunun yerine scrape_all_competitors() kullanin.
    AI scraper config dosyasindan hedef okur.
    """
    import warnings

    warnings.warn(
        "get_all_scrapers() deprecated. Bunun yerine scrape_all_competitors() kullanin.",
        DeprecationWarning,
        stacklevel=2,
    )

    from sade_agents.scrapers.chocolate_com_tr import ChocolateComTrScraper
    from sade_agents.scrapers.kahve_dunyasi import KahveDunyasiScraper
    from sade_agents.scrapers.vakko import VakkoScraper

    return [
        KahveDunyasiScraper(),
        VakkoScraper(),
        ChocolateComTrScraper(),
    ]


async def scrape_all_competitors(tenant_id: str = "default") -> dict[str, ScraperResult]:
    """
    Config'deki tum rakiplerden fiyat bilgisi toplar.

    AKILLI SCRAPER KULLANIR:
    - Her rakip icin siteyi kesfeder
    - Urun sayfalarini otomatik bulur
    - Hepsini tarar, sonuclari birlestirir

    Hedefler su sirada aranir:
    1. Firebase (tenants/{tenant_id}/scraping_targets)
    2. scraping_targets.json dosyasi

    Args:
        tenant_id: Tenant kimlik (Firebase icin)

    Returns:
        {scraper_name: ScraperResult} dict'i
    """
    # AKILLI SCRAPER - site kesfedici
    return await smart_scrape_all(tenant_id)
