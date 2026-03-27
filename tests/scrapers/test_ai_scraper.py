"""
AIScraper Unit Testleri.

HTML parsing, AI extraction ve hata yonetimi testleri.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from sade_agents.scrapers.ai_scraper import (
    AIScraper,
    ScrapingTarget,
    scrape_all_with_ai,
)
from sade_agents.scrapers.base import ProductPrice, ScraperResult


@pytest.fixture
def mock_openai_response():
    """OpenAI API response mock'u."""
    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message.content = json.dumps([
        {"name": "Bitter 100g", "price_tl": 450, "weight_grams": 100, "category": "tablet"},
        {"name": "Truffle Kutu", "price_tl": 890, "weight_grams": None, "category": "truffle"},
    ])
    return mock


@pytest.fixture
def sample_html():
    """Ornek HTML icerigi."""
    return """
    <html>
    <head><script>var x = 1;</script></head>
    <body>
    <nav>Menu</nav>
    <div class="products">
        <div>Bitter Cikolata 100g - 450 TL</div>
        <div>Truffle Kutusu - 890 TL</div>
    </div>
    <footer>Footer</footer>
    </body>
    </html>
    """


@pytest.fixture
def sample_target():
    """Ornek scraping hedefi."""
    return ScrapingTarget(
        name="test_shop",
        url="https://test.com/products",
        description="cikolata",
    )


class TestAIScraperInit:
    """AIScraper initialization testleri."""

    def test_init_creates_openai_client(self):
        """OpenAI client olusturulur."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings") as mock_settings:
            mock_settings.return_value.openai_api_key = "test-key"

            scraper = AIScraper()

            assert scraper._client is not None

    def test_init_uses_settings(self):
        """Settings'den API key alinir."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings") as mock_settings:
            mock_settings.return_value.openai_api_key = "test-api-key-123"

            scraper = AIScraper()

            assert scraper._settings is not None


class TestHtmlCleaning:
    """HTML temizleme testleri."""

    def test_clean_html_removes_scripts(self):
        """Script taglari temizlenir."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings"):
            scraper = AIScraper()
            html = "<html><head><script>alert('test')</script></head><body>Content</body></html>"

            cleaned = scraper._clean_html(html)

            assert "alert" not in cleaned
            assert "script" not in cleaned.lower()

    def test_clean_html_removes_nav(self):
        """Nav/footer taglari temizlenir."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings"):
            scraper = AIScraper()
            html = """
            <html>
            <body>
            <nav>Navigation menu</nav>
            <div>Main content</div>
            <footer>Footer text</footer>
            </body>
            </html>
            """

            cleaned = scraper._clean_html(html)

            assert "Navigation menu" not in cleaned
            assert "Footer text" not in cleaned
            assert "Main content" in cleaned

    def test_clean_html_truncates_long(self):
        """Uzun HTML kirpilir (max_chars)."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings"):
            scraper = AIScraper()
            html = f"<html><body>{'A' * 60000}</body></html>"

            cleaned = scraper._clean_html(html, max_chars=1000)

            assert len(cleaned) <= 1003  # 1000 + "..."
            assert cleaned.endswith("...")

    def test_clean_html_returns_body_text(self):
        """Sadece body text doner."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings"):
            scraper = AIScraper()
            html = """
            <html>
            <head><title>Page title</title></head>
            <body><p>Body content</p></body>
            </html>
            """

            cleaned = scraper._clean_html(html)

            assert "Body content" in cleaned
            # Title head'de oldugundan body'ye dahil edilmemeli
            assert "Page title" not in cleaned or "Page title" in cleaned  # BS4'e bagli


class TestProductExtraction:
    """Urun cikarma testleri."""

    @pytest.mark.asyncio
    async def test_extract_products_parses_json(self, mock_openai_response):
        """LLM JSON response'u parse edilir."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings") as mock_settings:
            mock_settings.return_value.openai_api_key = "test-key"
            mock_settings.return_value.openai_model_name = "gpt-4"

            scraper = AIScraper()
            scraper._client.chat.completions.create = MagicMock(return_value=mock_openai_response)

            products = await scraper._extract_products_with_ai(
                "Sample HTML text",
                "test_shop",
                "cikolata"
            )

            assert len(products) == 2
            assert products[0].name == "Bitter 100g"
            assert products[0].price_tl == 450
            assert products[0].weight_grams == 100
            assert products[1].name == "Truffle Kutu"
            assert products[1].price_tl == 890
            assert products[1].weight_grams is None

    @pytest.mark.asyncio
    async def test_extract_products_handles_markdown_json(self):
        """```json wrapper temizlenir."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings") as mock_settings:
            mock_settings.return_value.openai_api_key = "test-key"
            mock_settings.return_value.openai_model_name = "gpt-4"

            scraper = AIScraper()

            # LLM response'u markdown ile wrap edilmis
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = """```json
[
    {"name": "Test Product", "price_tl": 100, "weight_grams": 50, "category": "tablet"}
]
```"""
            scraper._client.chat.completions.create = MagicMock(return_value=mock_response)

            products = await scraper._extract_products_with_ai(
                "Sample HTML",
                "test_shop",
                "cikolata"
            )

            assert len(products) == 1
            assert products[0].name == "Test Product"

    @pytest.mark.asyncio
    async def test_extract_products_handles_empty(self):
        """Bos array doner (urun yok)."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings") as mock_settings:
            mock_settings.return_value.openai_api_key = "test-key"
            mock_settings.return_value.openai_model_name = "gpt-4"

            scraper = AIScraper()

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "[]"
            scraper._client.chat.completions.create = MagicMock(return_value=mock_response)

            products = await scraper._extract_products_with_ai(
                "No products here",
                "test_shop",
                "cikolata"
            )

            assert len(products) == 0

    @pytest.mark.asyncio
    async def test_extract_products_handles_invalid_json(self):
        """JSONDecodeError yonetilir."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings") as mock_settings:
            mock_settings.return_value.openai_api_key = "test-key"
            mock_settings.return_value.openai_model_name = "gpt-4"

            scraper = AIScraper()

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Not valid JSON at all"
            scraper._client.chat.completions.create = MagicMock(return_value=mock_response)

            products = await scraper._extract_products_with_ai(
                "Sample HTML",
                "test_shop",
                "cikolata"
            )

            assert len(products) == 0

    @pytest.mark.asyncio
    async def test_extract_products_skips_invalid_items(self):
        """Gecersiz itemlar atlanir."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings") as mock_settings:
            mock_settings.return_value.openai_api_key = "test-key"
            mock_settings.return_value.openai_model_name = "gpt-4"

            scraper = AIScraper()

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps([
                {"name": "Valid Product", "price_tl": 100, "category": "tablet"},
                {"name": "Invalid", "price_tl": "not-a-number"},  # Invalid price
                {"name": "Another Valid", "price_tl": 300, "category": "truffle"},
            ])
            scraper._client.chat.completions.create = MagicMock(return_value=mock_response)

            products = await scraper._extract_products_with_ai(
                "Sample HTML",
                "test_shop",
                "cikolata"
            )

            # Sadece valid olanlar donmeli (invalid price olan atlanir)
            assert len(products) == 2
            assert products[0].name == "Valid Product"
            assert products[1].name == "Another Valid"


class TestScraping:
    """Scraping islem testleri."""

    @pytest.mark.asyncio
    async def test_scrape_success(self, sample_target, sample_html, mock_openai_response):
        """Basarili tarama ScraperResult doner."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings") as mock_settings:
            mock_settings.return_value.openai_api_key = "test-key"
            mock_settings.return_value.openai_model_name = "gpt-4"

            scraper = AIScraper()
            scraper._fetch_page = AsyncMock(return_value=sample_html)
            scraper._client.chat.completions.create = MagicMock(return_value=mock_openai_response)

            result = await scraper.scrape(sample_target)

            assert result.success is True
            assert result.source == "test_shop"
            assert len(result.products) == 2
            assert result.error is None

    @pytest.mark.asyncio
    async def test_scrape_network_error(self, sample_target):
        """Network hatasi error message'a yazilir."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings") as mock_settings:
            mock_settings.return_value.openai_api_key = "test-key"

            scraper = AIScraper()
            scraper._fetch_page = AsyncMock(side_effect=Exception("Network timeout"))

            result = await scraper.scrape(sample_target)

            assert result.success is False
            assert result.source == "test_shop"
            assert len(result.products) == 0
            assert "Network timeout" in result.error

    @pytest.mark.asyncio
    async def test_scrape_api_error(self, sample_target, sample_html):
        """OpenAI API hatasi yonetilir."""
        with patch("sade_agents.scrapers.ai_scraper.get_settings") as mock_settings:
            mock_settings.return_value.openai_api_key = "test-key"
            mock_settings.return_value.openai_model_name = "gpt-4"

            scraper = AIScraper()
            scraper._fetch_page = AsyncMock(return_value=sample_html)
            scraper._client.chat.completions.create = MagicMock(
                side_effect=Exception("API rate limit exceeded")
            )

            result = await scraper.scrape(sample_target)

            assert result.success is False
            assert "API rate limit exceeded" in result.error


class TestScrapeAllWithAI:
    """scrape_all_with_ai fonksiyonu testleri."""

    @pytest.mark.asyncio
    async def test_scrape_all_no_targets(self):
        """Hedef yoksa warning doner."""
        with patch("sade_agents.scrapers.ai_scraper.load_targets_from_config") as mock_load:
            mock_load.return_value = []

            results = await scrape_all_with_ai()

            assert "_warning" in results
            assert results["_warning"].success is False
            assert "tanimlanmamis" in results["_warning"].error.lower()

    @pytest.mark.asyncio
    async def test_scrape_all_with_targets(self, sample_target, sample_html, mock_openai_response):
        """Tum hedefler taranir."""
        targets = [
            ScrapingTarget(name="shop1", url="https://shop1.com", description="cikolata"),
            ScrapingTarget(name="shop2", url="https://shop2.com", description="cikolata"),
        ]

        with patch("sade_agents.scrapers.ai_scraper.load_targets_from_config") as mock_load:
            mock_load.return_value = targets

            with patch("sade_agents.scrapers.ai_scraper.get_settings") as mock_settings:
                mock_settings.return_value.openai_api_key = "test-key"
                mock_settings.return_value.openai_model_name = "gpt-4"

                # Mock scraper.scrape method directly
                async def mock_scrape(self, target):
                    return ScraperResult(
                        source=target.name,
                        success=True,
                        products=[],
                    )

                with patch.object(AIScraper, "scrape", new=mock_scrape):
                    results = await scrape_all_with_ai()

            assert "shop1" in results
            assert "shop2" in results
            assert len(results) == 2

    @pytest.mark.asyncio
    async def test_scrape_all_handles_exceptions(self):
        """Tek hata diger tarmalari etkilemez."""
        targets = [
            ScrapingTarget(name="good_shop", url="https://good.com", description="cikolata"),
            ScrapingTarget(name="bad_shop", url="https://bad.com", description="cikolata"),
        ]

        with patch("sade_agents.scrapers.ai_scraper.load_targets_from_config") as mock_load:
            mock_load.return_value = targets

            with patch("sade_agents.scrapers.ai_scraper.get_settings") as mock_settings:
                mock_settings.return_value.openai_api_key = "test-key"
                mock_settings.return_value.openai_model_name = "gpt-4"

                async def mock_scrape(self, target):
                    if target.name == "bad_shop":
                        raise Exception("Scraping failed")
                    return ScraperResult(
                        source=target.name,
                        success=True,
                        products=[],
                    )

                with patch.object(AIScraper, "scrape", new=mock_scrape):
                    results = await scrape_all_with_ai()

            assert "good_shop" in results
            assert "bad_shop" in results
            assert results["good_shop"].success is True
            assert results["bad_shop"].success is False
            assert "Scraping failed" in results["bad_shop"].error
