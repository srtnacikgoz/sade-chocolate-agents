"""
Sade Agents - Kahve Dunyasi Scraper.

Kahve Dunyasi cikolata urunlerini cekmek icin scraper.
"""

from sade_agents.scrapers.base import BaseScraper, ProductPrice, ScraperResult


class KahveDunyasiScraper(BaseScraper):
    """Kahve Dunyasi cikolata urunleri scraper'i."""

    @property
    def name(self) -> str:
        return "kahve_dunyasi"

    @property
    def base_url(self) -> str:
        return "https://www.kahvedunyasi.com"

    async def scrape(self) -> ScraperResult:
        """Kahve Dunyasi'ndan cikolata fiyatlarini ceker."""
        try:
            # Cikolata kategorisi URL'i
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

        # Urun kartlarini bul (site yapisina gore guncellenmeli)
        product_cards = soup.select(".product-card, .product-item, [data-product-id]")

        for card in product_cards:
            try:
                # Urun adi
                name_elem = card.select_one(
                    ".product-name, .product-title, h3, h4, [class*='name']"
                )
                if not name_elem:
                    continue
                name = name_elem.get_text(strip=True)

                # Fiyat
                price_elem = card.select_one(
                    ".product-price, .price, [class*='price']"
                )
                if not price_elem:
                    continue
                price = self._parse_price(price_elem.get_text())
                if price is None:
                    continue

                # Gramaj (urun adinda veya ayri bir elemanda olabilir)
                weight = self._parse_weight(name)
                weight_elem = card.select_one("[class*='weight'], [class*='gram']")
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

                products.append(
                    ProductPrice(
                        name=name,
                        price_tl=price,
                        weight_grams=weight,
                        url=product_url,
                        category="cikolata",
                    )
                )
            except Exception:
                continue  # Hata olan urunu atla

        return products
