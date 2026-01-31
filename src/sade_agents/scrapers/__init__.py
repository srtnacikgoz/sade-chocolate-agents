"""
Sade Agents - Scrapers modulu.

Rakip cikolata sitelerinden fiyat bilgisi cekmek icin scraper'lar.
"""

from sade_agents.scrapers.base import BaseScraper, ProductPrice, ScraperResult

__all__ = [
    "BaseScraper",
    "ProductPrice",
    "ScraperResult",
    "get_all_scrapers",
    "scrape_all_competitors",
]


def get_all_scrapers() -> list[BaseScraper]:
    """Tum mevcut scraper'lari dondurur."""
    from sade_agents.scrapers.chocolate_com_tr import ChocolateComTrScraper
    from sade_agents.scrapers.kahve_dunyasi import KahveDunyasiScraper
    from sade_agents.scrapers.vakko import VakkoScraper

    return [
        KahveDunyasiScraper(),
        VakkoScraper(),
        ChocolateComTrScraper(),
    ]


async def scrape_all_competitors() -> dict[str, ScraperResult]:
    """
    Tum rakiplerden fiyat bilgisi toplar.

    Returns:
        {scraper_name: ScraperResult} dict'i
    """
    import asyncio

    scrapers = get_all_scrapers()
    tasks = [scraper.scrape() for scraper in scrapers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    output = {}
    for scraper, result in zip(scrapers, results, strict=False):
        if isinstance(result, Exception):
            output[scraper.name] = ScraperResult(
                source=scraper.name,
                success=False,
                error=str(result),
                products=[],
            )
        else:
            output[scraper.name] = result

    return output
