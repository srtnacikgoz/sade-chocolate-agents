"""
Sade Agents - Smart Site Discovery Scraper.

Ana URL'den tum siteyi kesfedip urun sayfalarini bulan akilli scraper.
Tek URL verilir, tum urunler bulunur.

MAKSİMUM BECERİ PRENSİBİ:
- Kullanici sadece ana URL verir
- Sistem sitemap, menu, link'leri kesfeder
- Tum urun sayfalarini bulur ve tarar
- Sonuclari birlestirir
"""

import asyncio
import json
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from openai import OpenAI

from sade_agents.config import get_settings
from sade_agents.scrapers.ai_scraper import AIScraper, ScrapingTarget
from sade_agents.scrapers.base import ProductPrice, ScraperResult


@dataclass
class DiscoveredPage:
    """Kesfedilen sayfa."""

    url: str
    page_type: str  # product_list, product_detail, category, other
    confidence: float  # 0-1 arasi, bu sayfanin urun icerme olasiligi


@dataclass
class SiteDiscoveryResult:
    """Site kesif sonucu."""

    base_url: str
    sitemap_found: bool = False
    product_pages: list[DiscoveredPage] = field(default_factory=list)
    category_pages: list[DiscoveredPage] = field(default_factory=list)
    discovery_method: str = ""  # sitemap, menu, links, ai


class SmartScraper:
    """
    Akilli site kesfedici scraper.

    Verilen ana URL'den baslayarak:
    1. Sitemap.xml kontrol eder
    2. Menu/navigation'i parse eder
    3. Urun kategorilerini/sayfalarini bulur
    4. Hepsini tarar
    5. Sonuclari birlestirir

    APTAL SCRAPER vs AKILLI SCRAPER:
    - Aptal: Tek URL tarar, urun bulamazsa bos doner
    - Akilli: Siteyi kesfeder, tum urun sayfalarini bulur, inatla sonuc alir
    """

    # Urun sayfasi olabilecek URL pattern'leri
    PRODUCT_URL_PATTERNS = [
        "/shop", "/store", "/products", "/urunler", "/magaza",
        "/category", "/kategori", "/collection", "/koleksiyon",
        "/cikolata", "/chocolate", "/truffle", "/praline",
        "/tablet", "/kutu", "/hediye", "/gift",
    ]

    # Atlanacak URL pattern'leri
    SKIP_URL_PATTERNS = [
        "/cart", "/sepet", "/checkout", "/odeme",
        "/login", "/giris", "/register", "/kayit",
        "/account", "/hesap", "/contact", "/iletisim",
        "/about", "/hakkimizda", "/blog", "/news",
        "/privacy", "/gizlilik", "/terms", "/kosullar",
        "/faq", "/sss", "/help", "/yardim",
        ".pdf", ".jpg", ".png", ".gif", ".css", ".js",
    ]

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = OpenAI(api_key=self._settings.openai_api_key)
        self._ai_scraper = AIScraper()
        self._visited_urls: set[str] = set()

    async def scrape_site(self, target: ScrapingTarget) -> ScraperResult:
        """
        Akilli site taramasi yapar.

        1. Siteyi kesfet (sitemap, menu, linkler)
        2. Urun sayfalarini bul
        3. Her birini tara
        4. Sonuclari birlestir

        Args:
            target: Scraping hedefi (ana URL)

        Returns:
            Tum urunleri iceren ScraperResult
        """
        self._visited_urls.clear()
        all_products: list[ProductPrice] = []
        errors: list[str] = []

        try:
            # 1. Siteyi kesfet
            discovery = await self._discover_site(target.url)

            # 2. Taranacak sayfalari belirle
            pages_to_scrape = self._prioritize_pages(discovery)

            if not pages_to_scrape:
                # Kesif basarisiz, en azindan ana sayfayi tara
                pages_to_scrape = [DiscoveredPage(
                    url=target.url,
                    page_type="unknown",
                    confidence=0.5,
                )]

            # 3. Her sayfayi tara (paralel)
            scrape_tasks = []
            for page in pages_to_scrape[:10]:  # Max 10 sayfa (token limiti)
                page_target = ScrapingTarget(
                    name=f"{target.name}_{urlparse(page.url).path.replace('/', '_')}",
                    url=page.url,
                    description=target.description,
                )
                scrape_tasks.append(self._ai_scraper.scrape(page_target))

            results = await asyncio.gather(*scrape_tasks, return_exceptions=True)

            # 4. Sonuclari birlestir
            for page, result in zip(pages_to_scrape, results):
                if isinstance(result, Exception):
                    errors.append(f"{page.url}: {str(result)}")
                elif result.success and result.products:
                    all_products.extend(result.products)
                elif result.error:
                    errors.append(f"{page.url}: {result.error}")

            # 5. Tekrar eden urunleri kaldir (isim bazli)
            unique_products = self._deduplicate_products(all_products)

            # Basari durumunu belirle
            success = len(unique_products) > 0
            error_msg = None
            if not success:
                error_msg = f"Urun bulunamadi. Denenen sayfalar: {len(pages_to_scrape)}. "
                if errors:
                    error_msg += f"Hatalar: {'; '.join(errors[:3])}"

            return ScraperResult(
                source=target.name,
                success=success,
                products=unique_products,
                error=error_msg,
            )

        except Exception as e:
            return ScraperResult(
                source=target.name,
                success=False,
                products=[],
                error=f"Site tarama hatasi: {str(e)}",
            )

    async def _discover_site(self, base_url: str) -> SiteDiscoveryResult:
        """
        Siteyi kesfeder - sitemap, menu, linkler.

        Sira:
        1. Sitemap.xml dene
        2. Ana sayfadan menu/nav kesfet
        3. AI ile urun sayfalarini tahmin et
        """
        result = SiteDiscoveryResult(base_url=base_url)
        parsed = urlparse(base_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        # 1. Sitemap dene
        sitemap_pages = await self._try_sitemap(domain)
        if sitemap_pages:
            result.sitemap_found = True
            result.discovery_method = "sitemap"
            for url in sitemap_pages:
                page_type = self._guess_page_type(url)
                if page_type in ("product_list", "category"):
                    result.product_pages.append(DiscoveredPage(
                        url=url,
                        page_type=page_type,
                        confidence=0.8,
                    ))
            if result.product_pages:
                return result

        # 2. Ana sayfadan menu/navigation kesfet
        menu_pages = await self._discover_from_menu(base_url)
        if menu_pages:
            result.discovery_method = "menu"
            result.product_pages.extend(menu_pages)
            if result.product_pages:
                return result

        # 3. AI ile sayfa linklerini analiz et
        ai_pages = await self._discover_with_ai(base_url)
        if ai_pages:
            result.discovery_method = "ai"
            result.product_pages.extend(ai_pages)

        return result

    async def _try_sitemap(self, domain: str) -> list[str]:
        """Sitemap.xml'den URL'leri ceker."""
        sitemap_urls = [
            f"{domain}/sitemap.xml",
            f"{domain}/sitemap_index.xml",
            f"{domain}/sitemap-products.xml",
        ]

        for sitemap_url in sitemap_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        sitemap_url,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as response:
                        if response.status == 200:
                            content = await response.text()
                            return self._parse_sitemap(content, domain)
            except Exception:
                continue

        return []

    def _parse_sitemap(self, content: str, domain: str) -> list[str]:
        """Sitemap XML'ini parse eder."""
        urls = []
        try:
            soup = BeautifulSoup(content, "xml")
            for loc in soup.find_all("loc"):
                url = loc.text.strip()
                # Sadece ayni domain ve urun olabilecek sayfalar
                if domain in url and not self._should_skip_url(url):
                    urls.append(url)
        except Exception:
            pass
        return urls[:50]  # Max 50 URL

    async def _discover_from_menu(self, base_url: str) -> list[DiscoveredPage]:
        """Ana sayfadaki menu/navigation'dan urun sayfalarini bulur."""
        pages = []
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                }
                async with session.get(
                    base_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as response:
                    if response.status != 200:
                        return pages
                    html = await response.text()

            soup = BeautifulSoup(html, "html.parser")
            parsed_base = urlparse(base_url)
            domain = f"{parsed_base.scheme}://{parsed_base.netloc}"

            # Nav, menu, header icindeki linkleri bul
            nav_elements = soup.find_all(["nav", "header", "menu"])
            links = []
            for nav in nav_elements:
                links.extend(nav.find_all("a", href=True))

            # Ayrica class'inda menu/nav olan elementler
            menu_classes = soup.find_all(class_=lambda x: x and ("menu" in x.lower() or "nav" in x.lower()))
            for menu in menu_classes:
                links.extend(menu.find_all("a", href=True))

            # Linkleri isle
            seen_urls = set()
            for link in links:
                href = link.get("href", "")
                if not href or href.startswith("#") or href.startswith("javascript:"):
                    continue

                # Tam URL yap
                full_url = urljoin(base_url, href)

                # Ayni domain mi kontrol et
                if urlparse(full_url).netloc != parsed_base.netloc:
                    continue

                # Atlanacak URL mi?
                if self._should_skip_url(full_url):
                    continue

                # Tekrar mi?
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)

                # Urun sayfasi olabilir mi?
                page_type = self._guess_page_type(full_url)
                if page_type in ("product_list", "category"):
                    # Link metnine de bak
                    link_text = link.get_text(strip=True).lower()
                    confidence = 0.6
                    if any(kw in link_text for kw in ["ürün", "urun", "shop", "mağaza", "magaza", "koleksiyon", "çikolata", "cikolata"]):
                        confidence = 0.9

                    pages.append(DiscoveredPage(
                        url=full_url,
                        page_type=page_type,
                        confidence=confidence,
                    ))

        except Exception:
            pass

        return pages

    async def _discover_with_ai(self, base_url: str) -> list[DiscoveredPage]:
        """AI kullanarak urun sayfalarini kesfeder."""
        pages = []
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                }
                async with session.get(
                    base_url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as response:
                    if response.status != 200:
                        return pages
                    html = await response.text()

            # HTML'den linkleri cikar
            soup = BeautifulSoup(html, "html.parser")
            all_links = []
            parsed_base = urlparse(base_url)

            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if href.startswith("#") or href.startswith("javascript:"):
                    continue
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == parsed_base.netloc:
                    link_text = link.get_text(strip=True)[:50]
                    all_links.append({"url": full_url, "text": link_text})

            # AI'a sor: Hangileri urun sayfasi?
            if not all_links:
                return pages

            # Sadece ilk 30 linki gonder (token tasarrufu)
            links_for_ai = all_links[:30]

            prompt = f"""Bu bir e-ticaret sitesinin ana sayfasindaki linkler.
Cikolata/tatli urunleri iceren sayfalari bul.

Linkler:
{json.dumps(links_for_ai, ensure_ascii=False, indent=2)}

SADECE urun listesi veya kategori sayfasi olabilecekleri sec.
Blog, iletisim, hakkimizda gibi sayfalari SECME.

JSON array dondur:
[
  {{"url": "...", "confidence": 0.9, "reason": "cikolata kategorisi"}}
]

Hicbir uygun sayfa yoksa bos array dondur: []
"""

            response = self._client.chat.completions.create(
                model=self._settings.openai_model_name,
                messages=[
                    {"role": "system", "content": "Sen bir web scraping asistanisin. Sadece JSON dondur."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=1000,
            )

            content = response.choices[0].message.content or "[]"
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()

            ai_results = json.loads(content)
            for item in ai_results:
                if isinstance(item, dict) and "url" in item:
                    pages.append(DiscoveredPage(
                        url=item["url"],
                        page_type="product_list",
                        confidence=float(item.get("confidence", 0.7)),
                    ))

        except Exception:
            pass

        return pages

    def _guess_page_type(self, url: str) -> str:
        """URL'den sayfa tipini tahmin eder."""
        url_lower = url.lower()

        for pattern in self.PRODUCT_URL_PATTERNS:
            if pattern in url_lower:
                return "product_list"

        return "other"

    def _should_skip_url(self, url: str) -> bool:
        """Bu URL atlanmali mi?"""
        url_lower = url.lower()
        for pattern in self.SKIP_URL_PATTERNS:
            if pattern in url_lower:
                return True
        return False

    def _prioritize_pages(self, discovery: SiteDiscoveryResult) -> list[DiscoveredPage]:
        """Sayfalari oncelik sirasina gore siralar."""
        all_pages = discovery.product_pages + discovery.category_pages

        # Confidence'a gore sirala
        all_pages.sort(key=lambda p: p.confidence, reverse=True)

        # Tekrarlari kaldir
        seen = set()
        unique_pages = []
        for page in all_pages:
            if page.url not in seen:
                seen.add(page.url)
                unique_pages.append(page)

        return unique_pages

    def _deduplicate_products(self, products: list[ProductPrice]) -> list[ProductPrice]:
        """Tekrar eden urunleri kaldirir (isim bazli)."""
        seen_names = set()
        unique = []
        for p in products:
            # Normalize isim (kucuk harf, bosluk temizle)
            normalized = p.name.lower().strip()
            if normalized not in seen_names:
                seen_names.add(normalized)
                unique.append(p)
        return unique


async def smart_scrape_all(tenant_id: str = "default") -> dict[str, ScraperResult]:
    """
    Config'deki tum hedefleri AKILLI scraper ile tarar.

    Her hedef icin:
    1. Siteyi kesfet
    2. Urun sayfalarini bul
    3. Hepsini tara
    4. Birlestir

    Args:
        tenant_id: Tenant kimlik

    Returns:
        {source_name: ScraperResult} dict'i
    """
    from sade_agents.scrapers.ai_scraper import load_targets_from_config

    targets = load_targets_from_config(tenant_id)

    if not targets:
        return {"_warning": ScraperResult(
            source="config",
            success=False,
            products=[],
            error="Scraping hedefi tanimlanmamis. UI'dan veya scraping_targets.json'dan rakip ekleyin.",
        )}

    scraper = SmartScraper()
    tasks = [scraper.scrape_site(target) for target in targets]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    output = {}
    for target, result in zip(targets, results, strict=False):
        if isinstance(result, Exception):
            output[target.name] = ScraperResult(
                source=target.name,
                success=False,
                products=[],
                error=str(result),
            )
        else:
            output[target.name] = result

    return output
