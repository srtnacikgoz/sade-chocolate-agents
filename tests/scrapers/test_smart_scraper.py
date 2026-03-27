"""SmartScraper unit testleri."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sade_agents.scrapers.ai_scraper import ScrapingTarget
from sade_agents.scrapers.base import ProductPrice, ScraperResult
from sade_agents.scrapers.smart_scraper import (
    DiscoveredPage,
    SiteDiscoveryResult,
    SmartScraper,
    smart_scrape_all,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_html_with_products():
    """Urun iceren ornek HTML."""
    return """
    <html>
    <body>
        <nav>
            <a href="/cikolata">Cikolatalar</a>
            <a href="/truffle">Truffle</a>
            <a href="/hediye">Hediye Kutulari</a>
        </nav>
        <div class="product">
            <h3>Bitter Cikolata 100g</h3>
            <span class="price">450 TL</span>
        </div>
        <div class="product">
            <h3>Sutlu Tablet 150g</h3>
            <span class="price">380 TL</span>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_sitemap_xml():
    """Ornek sitemap.xml icerik."""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://example.com/</loc>
        </url>
        <url>
            <loc>https://example.com/cikolata</loc>
        </url>
        <url>
            <loc>https://example.com/truffle</loc>
        </url>
        <url>
            <loc>https://example.com/hediye-kutu</loc>
        </url>
        <url>
            <loc>https://example.com/blog</loc>
        </url>
    </urlset>
    """


@pytest.fixture
def sample_target():
    """Test icin ornek scraping hedefi."""
    return ScrapingTarget(
        name="test_site",
        url="https://example.com",
        description="test cikolata",
    )


@pytest.fixture
def sample_products():
    """Test icin ornek urun listesi."""
    return [
        ProductPrice(name="Bitter 100g", price_tl=450, weight_grams=100, category="tablet"),
        ProductPrice(name="Sutlu 150g", price_tl=380, weight_grams=150, category="tablet"),
        ProductPrice(name="Truffle Kutu", price_tl=890, weight_grams=200, category="truffle"),
    ]


# ============================================================================
# Test: SmartScraper Init
# ============================================================================


class TestSmartScraperInit:
    """SmartScraper başlatma testleri."""

    def test_init_creates_ai_scraper(self):
        """AIScraper instance'i oluşturulur."""
        scraper = SmartScraper()
        assert hasattr(scraper, "_ai_scraper")
        assert scraper._ai_scraper is not None

    def test_init_clears_visited_urls(self):
        """visited_urls seti boş başlar."""
        scraper = SmartScraper()
        assert isinstance(scraper._visited_urls, set)
        assert len(scraper._visited_urls) == 0


# ============================================================================
# Test: Site Discovery
# ============================================================================


class TestSiteDiscovery:
    """Site keşif fonksiyonları testleri."""

    @pytest.mark.asyncio
    async def test_discover_from_sitemap(self, mock_sitemap_xml):
        """Sitemap bulunduğunda doğru URL'ler döner."""
        scraper = SmartScraper()

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_sitemap_xml)

        # Mock context manager
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response

        mock_session = MagicMock()
        mock_session.get.return_value = mock_context

        mock_session_context = AsyncMock()
        mock_session_context.__aenter__.return_value = mock_session

        with patch("aiohttp.ClientSession", return_value=mock_session_context):
            result = await scraper._discover_site("https://example.com")

            assert result.sitemap_found is True
            assert result.discovery_method == "sitemap"
            assert len(result.product_pages) > 0
            # /blog atlanmali (SKIP_URL_PATTERNS)
            urls = [p.url for p in result.product_pages]
            assert "https://example.com/blog" not in urls
            assert "https://example.com/cikolata" in urls

    @pytest.mark.asyncio
    async def test_discover_from_menu(self, mock_html_with_products):
        """Menu'den ürün sayfaları bulunur."""
        scraper = SmartScraper()

        # Sitemap yok (404), menu var (200)
        mock_response_404 = MagicMock()
        mock_response_404.status = 404

        mock_response_200 = MagicMock()
        mock_response_200.status = 200
        mock_response_200.text = AsyncMock(return_value=mock_html_with_products)

        # Sitemap denemelerinde 404, menu fetch'inde 200
        contexts = []
        for _ in range(3):  # 3 sitemap denemesi
            ctx = AsyncMock()
            ctx.__aenter__.return_value = mock_response_404
            contexts.append(ctx)

        # Menu fetch için 200
        menu_ctx = AsyncMock()
        menu_ctx.__aenter__.return_value = mock_response_200
        contexts.append(menu_ctx)

        mock_session = MagicMock()
        mock_session.get.side_effect = contexts

        mock_session_context = AsyncMock()
        mock_session_context.__aenter__.return_value = mock_session

        with patch("aiohttp.ClientSession", return_value=mock_session_context):
            result = await scraper._discover_site("https://example.com")

            assert result.discovery_method == "menu"
            assert len(result.product_pages) > 0
            urls = [p.url for p in result.product_pages]
            assert any("/cikolata" in u for u in urls)

    @pytest.mark.asyncio
    async def test_discover_with_ai(self, mock_html_with_products):
        """AI keşif çalışır (OpenAI mock)."""
        scraper = SmartScraper()

        # Sitemap ve menu başarısız (link var ama menü değil), AI çağrısı yapılacak
        html_with_links = """
        <html><body>
            <div class="content">
                <a href="/cikolata">Cikolatalar</a>
                <a href="/truffle">Truffle</a>
                <a href="/hakkimizda">Hakkimizda</a>
            </div>
        </body></html>
        """

        mock_response_404 = MagicMock()
        mock_response_404.status = 404

        mock_response_200 = MagicMock()
        mock_response_200.status = 200
        mock_response_200.text = AsyncMock(return_value=html_with_links)

        # OpenAI response mock
        ai_response = [
            {"url": "https://example.com/cikolata", "confidence": 0.9, "reason": "cikolata kategorisi"},
            {"url": "https://example.com/truffle", "confidence": 0.85, "reason": "truffle urunleri"},
        ]

        mock_openai_choice = MagicMock()
        mock_openai_choice.message.content = json.dumps(ai_response)

        mock_openai_response = MagicMock()
        mock_openai_response.choices = [mock_openai_choice]

        # Sitemap'ler 404 (3x), menu 200, AI için 200
        contexts = []
        for _ in range(3):
            ctx = AsyncMock()
            ctx.__aenter__.return_value = mock_response_404
            contexts.append(ctx)

        for _ in range(2):  # menu + AI
            ctx = AsyncMock()
            ctx.__aenter__.return_value = mock_response_200
            contexts.append(ctx)

        mock_session = MagicMock()
        mock_session.get.side_effect = contexts

        mock_session_context = AsyncMock()
        mock_session_context.__aenter__.return_value = mock_session

        with patch("aiohttp.ClientSession", return_value=mock_session_context), \
             patch.object(scraper._client.chat.completions, "create", return_value=mock_openai_response):

            result = await scraper._discover_site("https://example.com")

            assert result.discovery_method == "ai"
            assert len(result.product_pages) > 0

    @pytest.mark.asyncio
    async def test_discovery_priority(self, mock_sitemap_xml):
        """Sitemap > Menu > AI sırası doğru."""
        scraper = SmartScraper()

        # Sitemap bulunduğunda menu/AI çağrılmamalı
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_sitemap_xml)

        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response

        mock_session = MagicMock()
        mock_session.get.return_value = mock_context

        mock_session_context = AsyncMock()
        mock_session_context.__aenter__.return_value = mock_session

        with patch("aiohttp.ClientSession", return_value=mock_session_context):
            result = await scraper._discover_site("https://example.com")

            assert result.discovery_method == "sitemap"
            # Sitemap başarılı oldu, menu/AI çağrılmadı
            assert len(result.product_pages) > 0


# ============================================================================
# Test: URL Filtering
# ============================================================================


class TestUrlFiltering:
    """URL filtreleme testleri."""

    def test_should_skip_url_cart(self):
        """/cart URL'leri atlanır."""
        scraper = SmartScraper()
        assert scraper._should_skip_url("https://example.com/cart") is True
        assert scraper._should_skip_url("https://example.com/sepet") is True

    def test_should_skip_url_login(self):
        """/login URL'leri atlanır."""
        scraper = SmartScraper()
        assert scraper._should_skip_url("https://example.com/login") is True
        assert scraper._should_skip_url("https://example.com/giris") is True

    def test_should_not_skip_product_url(self):
        """/products URL'leri atlanmaz."""
        scraper = SmartScraper()
        assert scraper._should_skip_url("https://example.com/products") is False
        assert scraper._should_skip_url("https://example.com/urunler") is False
        assert scraper._should_skip_url("https://example.com/cikolata") is False

    def test_guess_page_type_product(self):
        """/shop, /urunler doğru tiplendirilir."""
        scraper = SmartScraper()
        assert scraper._guess_page_type("https://example.com/shop") == "product_list"
        assert scraper._guess_page_type("https://example.com/urunler") == "product_list"
        assert scraper._guess_page_type("https://example.com/cikolata") == "product_list"
        assert scraper._guess_page_type("https://example.com/category/truffle") == "product_list"

    def test_guess_page_type_other(self):
        """Bilinmeyen URL'ler 'other' döner."""
        scraper = SmartScraper()
        assert scraper._guess_page_type("https://example.com/about") == "other"
        assert scraper._guess_page_type("https://example.com/contact") == "other"


# ============================================================================
# Test: Scraping
# ============================================================================


class TestScraping:
    """Scraping fonksiyonları testleri."""

    @pytest.mark.asyncio
    async def test_scrape_site_success(self, sample_target, sample_products):
        """Başarılı tarama ürünleri döner."""
        scraper = SmartScraper()

        # Discovery mock
        discovery_result = SiteDiscoveryResult(
            base_url=sample_target.url,
            sitemap_found=True,
            product_pages=[
                DiscoveredPage(url="https://example.com/cikolata", page_type="product_list", confidence=0.9),
            ],
            discovery_method="sitemap",
        )

        # AIScraper.scrape mock
        mock_scrape_result = ScraperResult(
            source=sample_target.name,
            success=True,
            products=sample_products,
        )

        with patch.object(scraper, "_discover_site", return_value=discovery_result), \
             patch.object(scraper._ai_scraper, "scrape", return_value=mock_scrape_result):

            result = await scraper.scrape_site(sample_target)

            assert result.success is True
            assert len(result.products) == 3
            assert result.error is None

    @pytest.mark.asyncio
    async def test_scrape_site_empty_discovery(self, sample_target):
        """Keşif boşsa ana sayfa taranır."""
        scraper = SmartScraper()

        # Boş discovery
        discovery_result = SiteDiscoveryResult(
            base_url=sample_target.url,
            product_pages=[],
        )

        mock_scrape_result = ScraperResult(
            source=sample_target.name,
            success=True,
            products=[ProductPrice(name="Test", price_tl=100, weight_grams=50)],
        )

        with patch.object(scraper, "_discover_site", return_value=discovery_result), \
             patch.object(scraper._ai_scraper, "scrape", return_value=mock_scrape_result):

            result = await scraper.scrape_site(sample_target)

            # Ana sayfa taranmış olmalı
            assert scraper._ai_scraper.scrape.call_count == 1

    @pytest.mark.asyncio
    async def test_scrape_site_parallel(self, sample_target):
        """Birden fazla sayfa paralel taranır."""
        scraper = SmartScraper()

        # 3 sayfa keşfedildi
        discovery_result = SiteDiscoveryResult(
            base_url=sample_target.url,
            product_pages=[
                DiscoveredPage(url="https://example.com/cikolata", page_type="product_list", confidence=0.9),
                DiscoveredPage(url="https://example.com/truffle", page_type="product_list", confidence=0.85),
                DiscoveredPage(url="https://example.com/hediye", page_type="product_list", confidence=0.8),
            ],
        )

        # Her sayfa farklı ürün dönsün
        async def mock_scrape_func(target):
            return ScraperResult(
                source=target.name,
                success=True,
                products=[ProductPrice(name=f"Product from {target.url}", price_tl=500, weight_grams=100)],
            )

        with patch.object(scraper, "_discover_site", return_value=discovery_result), \
             patch.object(scraper._ai_scraper, "scrape", side_effect=mock_scrape_func):

            result = await scraper.scrape_site(sample_target)

            # 3 sayfa taranmış
            assert scraper._ai_scraper.scrape.call_count == 3
            assert len(result.products) == 3

    @pytest.mark.asyncio
    async def test_scrape_site_handles_errors(self, sample_target):
        """Tek sayfa hatası tüm taramayı bozmaz."""
        scraper = SmartScraper()

        discovery_result = SiteDiscoveryResult(
            base_url=sample_target.url,
            product_pages=[
                DiscoveredPage(url="https://example.com/page1", page_type="product_list", confidence=0.9),
                DiscoveredPage(url="https://example.com/page2", page_type="product_list", confidence=0.9),
            ],
        )

        # İlk sayfa başarılı, ikinci hata
        async def mock_scrape_side_effect(target):
            if "page1" in target.url:
                return ScraperResult(source=target.name, success=True, products=[
                    ProductPrice(name="Product 1", price_tl=450, weight_grams=100),
                ])
            else:
                raise Exception("Network error")

        with patch.object(scraper, "_discover_site", return_value=discovery_result), \
             patch.object(scraper._ai_scraper, "scrape", side_effect=mock_scrape_side_effect):

            result = await scraper.scrape_site(sample_target)

            # Hata olmasına rağmen bazı ürünler bulundu
            assert result.success is True
            assert len(result.products) == 1


# ============================================================================
# Test: Deduplication
# ============================================================================


class TestDeduplication:
    """Ürün tekrarlarını kaldırma testleri."""

    def test_deduplicate_products_by_name(self):
        """Aynı isimli ürünler tekrar etmez."""
        scraper = SmartScraper()
        products = [
            ProductPrice(name="Bitter 100g", price_tl=450, weight_grams=100),
            ProductPrice(name="Bitter 100g", price_tl=450, weight_grams=100),
            ProductPrice(name="Sutlu 150g", price_tl=380, weight_grams=150),
        ]

        unique = scraper._deduplicate_products(products)

        assert len(unique) == 2
        names = [p.name for p in unique]
        assert "Bitter 100g" in names
        assert "Sutlu 150g" in names

    def test_deduplicate_case_insensitive(self):
        """Büyük/küçük harf farkı yok sayılır."""
        scraper = SmartScraper()
        products = [
            ProductPrice(name="Bitter Cikolata", price_tl=450, weight_grams=100),
            ProductPrice(name="bitter cikolata", price_tl=450, weight_grams=100),
            ProductPrice(name="BITTER CIKOLATA", price_tl=450, weight_grams=100),
        ]

        unique = scraper._deduplicate_products(products)

        assert len(unique) == 1


# ============================================================================
# Test: smart_scrape_all
# ============================================================================


class TestSmartScrapeAll:
    """smart_scrape_all fonksiyonu testleri."""

    @pytest.mark.asyncio
    async def test_smart_scrape_all_no_targets(self):
        """Hedef yoksa uyarı döner."""
        with patch("sade_agents.scrapers.ai_scraper.load_targets_from_config", return_value=[]):
            result = await smart_scrape_all()

            assert "_warning" in result
            assert result["_warning"].success is False
            assert "tanimlanmamis" in result["_warning"].error.lower()

    @pytest.mark.asyncio
    async def test_smart_scrape_all_with_targets(self):
        """Hedefler taranır, dict döner."""
        targets = [
            ScrapingTarget(name="site1", url="https://site1.com", description="cikolata"),
            ScrapingTarget(name="site2", url="https://site2.com", description="truffle"),
        ]

        mock_result1 = ScraperResult(
            source="site1",
            success=True,
            products=[ProductPrice(name="Product 1", price_tl=450, weight_grams=100)],
        )

        mock_result2 = ScraperResult(
            source="site2",
            success=True,
            products=[ProductPrice(name="Product 2", price_tl=890, weight_grams=200)],
        )

        with patch("sade_agents.scrapers.ai_scraper.load_targets_from_config", return_value=targets), \
             patch.object(SmartScraper, "scrape_site", side_effect=[mock_result1, mock_result2]):

            result = await smart_scrape_all()

            assert "site1" in result
            assert "site2" in result
            assert result["site1"].success is True
            assert result["site2"].success is True
            assert len(result["site1"].products) == 1
            assert len(result["site2"].products) == 1
