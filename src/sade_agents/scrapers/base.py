"""
Sade Agents - Scraper Base Interface.

Tum scraper'larin uymasi gereken temel arayuz.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ProductPrice:
    """Urun fiyat bilgisi modeli."""

    name: str  # Urun adi
    price_tl: float  # Fiyat (TL)
    weight_grams: int | None = None  # Gramaj
    price_per_gram: float | None = None  # TL/gram
    url: str | None = None  # Urun sayfasi URL'i
    category: str | None = None  # Kategori (tablet, truffle, vs)

    def __post_init__(self) -> None:
        """TL/gram hesapla (eger verilmemisse)."""
        if self.price_per_gram is None and self.weight_grams and self.weight_grams > 0:
            self.price_per_gram = round(self.price_tl / self.weight_grams, 2)


@dataclass
class ScraperResult:
    """Scraper sonuc modeli."""

    source: str  # Kaynak site adi
    success: bool
    products: list[ProductPrice]
    error: str | None = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def product_count(self) -> int:
        """Urun sayisini dondurur."""
        return len(self.products)

    @property
    def avg_price_per_gram(self) -> float | None:
        """Ortalama TL/gram hesaplar."""
        valid_prices = [p.price_per_gram for p in self.products if p.price_per_gram]
        if not valid_prices:
            return None
        return round(sum(valid_prices) / len(valid_prices), 2)


class BaseScraper(ABC):
    """Tum scraper'lar icin temel sinif."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Scraper/kaynak adi."""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Site ana URL'i."""
        pass

    @abstractmethod
    async def scrape(self) -> ScraperResult:
        """
        Site'dan fiyat bilgisi toplar.

        Returns:
            ScraperResult icinde urun listesi
        """
        pass

    async def _fetch_page(self, url: str, timeout: int = 30) -> str:
        """
        Sayfa icerigini ceker.

        Args:
            url: Cekilecek URL
            timeout: Timeout suresi (saniye)

        Returns:
            HTML icerigi
        """
        import aiohttp

        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            }
            async with session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response.raise_for_status()
                return await response.text()

    def _parse_price(self, price_text: str) -> float | None:
        """
        Fiyat metnini float'a cevirir.

        Ornekler:
            "450,00 TL" -> 450.0
            "1.250,50 ₺" -> 1250.5
        """
        import re

        if not price_text:
            return None

        # Temizle
        cleaned = price_text.strip()
        cleaned = re.sub(r"[TL₺\s]", "", cleaned)  # Para birimi ve bosluk kaldir
        cleaned = cleaned.replace(".", "")  # Binlik ayirici kaldir
        cleaned = cleaned.replace(",", ".")  # Ondalik virgul -> nokta

        try:
            return float(cleaned)
        except ValueError:
            return None

    def _parse_weight(self, text: str) -> int | None:
        """
        Gramaj metnini int'e cevirir.

        Ornekler:
            "100g" -> 100
            "150 gram" -> 150
            "0.5 kg" -> 500
        """
        import re

        if not text:
            return None

        # Kilogram kontrolu
        kg_match = re.search(r"(\d+(?:[.,]\d+)?)\s*kg", text.lower())
        if kg_match:
            kg = float(kg_match.group(1).replace(",", "."))
            return int(kg * 1000)

        # Gram kontrolu
        g_match = re.search(r"(\d+)\s*(?:g|gram)", text.lower())
        if g_match:
            return int(g_match.group(1))

        return None
