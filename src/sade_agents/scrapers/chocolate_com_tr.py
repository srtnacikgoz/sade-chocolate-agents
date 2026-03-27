"""
Sade Agents - Chocolate.com.tr Scraper.

Chocolate.com.tr sitesinden fiyat bilgisi cekmek icin scraper.
"""

from sade_agents.scrapers.base import BaseScraper, ProductPrice, ScraperResult


class ChocolateComTrScraper(BaseScraper):
    """Chocolate.com.tr scraper'i."""

    @property
    def name(self) -> str:
        return "chocolate_com_tr"

    @property
    def base_url(self) -> str:
        return "https://www.chocolate.com.tr"

    async def scrape(self) -> ScraperResult:
        """Chocolate.com.tr'den fiyatlari ceker."""
        try:
            # Cikolata kategorisi
            url = f"{self.base_url}/cikolata"
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
            ".product-card, .product-item, .product-box, [data-product]"
        )

        for card in product_cards:
            try:
                # Urun adi
                name_elem = card.select_one(
                    ".product-name, .product-title, h3, [class*='name']"
                )
                if not name_elem:
                    continue
                name = name_elem.get_text(strip=True)

                # Fiyat - birden fazla fiyat olabilir (normal/indirimli)
                # Once indirimli fiyati dene
                price_elem = card.select_one(
                    ".sale-price, .discount-price, .special-price, .price"
                )
                if not price_elem:
                    price_elem = card.select_one("[class*='price']")
                if not price_elem:
                    continue

                price = self._parse_price(price_elem.get_text())
                if price is None:
                    continue

                # Gramaj
                weight = self._parse_weight(name)

                # Ayri gramaj bilgisi varsa
                weight_elem = card.select_one(
                    "[class*='weight'], [class*='gram'], .product-weight"
                )
                if weight is None and weight_elem:
                    weight = self._parse_weight(weight_elem.get_text())

                # URL
                link_elem = card.select_one("a[href]")
                product_url = None
                if link_elem:
                    href = link_elem.get("href", "")
                    if href.startswith("/"):
                        product_url = f"{self.base_url}{href}"
                    elif href.startswith("http"):
                        product_url = href

                # Marka tahmini
                brand = self._extract_brand(name, card)

                products.append(
                    ProductPrice(
                        name=name,
                        price_tl=price,
                        weight_grams=weight,
                        url=product_url,
                        category=brand,  # Marka bilgisini category'de tutuyoruz
                    )
                )
            except Exception:
                continue

        return products

    def _extract_brand(self, name: str, card) -> str:
        """Urun adindan veya karttan marka cikarir."""
        from bs4 import Tag

        # Oncelikle kart icinde marka elementi ara
        if isinstance(card, Tag):
            brand_elem = card.select_one(".brand, [class*='brand'], [class*='marka']")
            if brand_elem:
                return brand_elem.get_text(strip=True).lower()

        # Bilinen markalari kontrol et
        name_lower = name.lower()
        known_brands = [
            "vakko",
            "godiva",
            "lindt",
            "ferrero",
            "toblerone",
            "milka",
            "nestle",
            "eti",
            "ulker",
            "karaca",
        ]

        for brand in known_brands:
            if brand in name_lower:
                return brand

        return "diger"
