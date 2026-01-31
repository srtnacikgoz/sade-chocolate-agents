"""
Sade Agents - Vakko Chocolate Scraper.

Vakko cikolata urunlerini cekmek icin scraper.
"""

from sade_agents.scrapers.base import BaseScraper, ProductPrice, ScraperResult


class VakkoScraper(BaseScraper):
    """Vakko Chocolate urunleri scraper'i."""

    @property
    def name(self) -> str:
        return "vakko"

    @property
    def base_url(self) -> str:
        return "https://www.vakkochocolate.com"

    async def scrape(self) -> ScraperResult:
        """Vakko Chocolate'tan fiyatlari ceker."""
        try:
            # Ana sayfa veya urunler sayfasi
            url = f"{self.base_url}/urunler"
            html = await self._fetch_page(url)

            products = self._parse_products(html)

            return ScraperResult(
                source=self.name,
                success=True,
                products=products,
            )
        except Exception as e:
            return ScraperResult(
                source=self.name,
                success=False,
                products=[],
                error=str(e),
            )

    def _parse_products(self, html: str) -> list[ProductPrice]:
        """HTML'den urun bilgilerini parse eder."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        products = []

        # Urun kartlarini bul
        product_cards = soup.select(
            ".product-card, .product-item, .product, [class*='product']"
        )

        for card in product_cards:
            try:
                # Urun adi
                name_elem = card.select_one("h2, h3, h4, .title, .name, [class*='title']")
                if not name_elem:
                    continue
                name = name_elem.get_text(strip=True)

                # Fiyat
                price_elem = card.select_one(".price, [class*='price'], [class*='fiyat']")
                if not price_elem:
                    continue
                price = self._parse_price(price_elem.get_text())
                if price is None:
                    continue

                # Gramaj
                weight = self._parse_weight(name)
                desc_elem = card.select_one(".description, .desc, [class*='desc']")
                if weight is None and desc_elem:
                    weight = self._parse_weight(desc_elem.get_text())

                # URL
                link_elem = card.select_one("a[href]")
                product_url = None
                if link_elem:
                    href = link_elem.get("href", "")
                    if href.startswith("/"):
                        product_url = f"{self.base_url}{href}"
                    elif href.startswith("http"):
                        product_url = href

                # Kategori tahmini
                category = self._guess_category(name)

                products.append(
                    ProductPrice(
                        name=name,
                        price_tl=price,
                        weight_grams=weight,
                        url=product_url,
                        category=category,
                    )
                )
            except Exception:
                continue

        return products

    def _guess_category(self, name: str) -> str:
        """Urun adina gore kategori tahmin eder."""
        name_lower = name.lower()

        if any(kw in name_lower for kw in ["tablet", "bar"]):
            return "tablet"
        if any(kw in name_lower for kw in ["truffle", "trüf"]):
            return "truffle"
        if any(kw in name_lower for kw in ["draje", "badem"]):
            return "draje"
        if any(kw in name_lower for kw in ["kutu", "box", "hediye"]):
            return "hediye_kutu"

        return "diger"
