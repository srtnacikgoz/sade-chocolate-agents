"""
Sade Agents - AI-Powered Scraper.

HTML'i LLM'e verip urun/fiyat cikartan akilli scraper.
Site yapisi degisse bile calisir.
"""

import json
from dataclasses import dataclass

import aiohttp
from openai import OpenAI

from sade_agents.config import get_settings
from sade_agents.scrapers.base import ProductPrice, ScraperResult


@dataclass
class ScrapingTarget:
    """Scrape edilecek hedef."""

    name: str  # Kaynak adi (vakko, kahve_dunyasi, vs)
    url: str  # Urun sayfasi URL'i
    description: str  # Ne ariyoruz (cikolata, truffle, vs)


class AIScraper:
    """
    AI-destekli web scraper.

    HTML'i ceker, LLM'e verir, yapilandirilmis urun verisi alir.
    CSS selector'lara bagimli degil.
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = OpenAI(api_key=self._settings.openai_api_key)

    async def scrape(self, target: ScrapingTarget) -> ScraperResult:
        """
        Hedef URL'den urun bilgilerini ceker.

        Args:
            target: Scraping hedefi

        Returns:
            ScraperResult ile urun listesi
        """
        try:
            # 1. HTML'i cek
            html = await self._fetch_page(target.url)

            # 2. HTML'i temizle (cok uzunsa kirp)
            cleaned_html = self._clean_html(html)

            # 3. LLM'e ver, urun cikar
            products = await self._extract_products_with_ai(
                cleaned_html, target.name, target.description
            )

            return ScraperResult(
                source=target.name,
                success=True,
                products=products,
            )
        except Exception as e:
            return ScraperResult(
                source=target.name,
                success=False,
                products=[],
                error=str(e),
            )

    async def _fetch_page(self, url: str, timeout: int = 30) -> str:
        """Sayfa HTML'ini ceker."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
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

    def _clean_html(self, html: str, max_chars: int = 50000) -> str:
        """
        HTML'i temizler ve kisaltir.

        Script, style, nav, footer gibi gereksiz kisimları atar.
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        # Gereksiz elementleri kaldir
        for tag in soup.find_all(["script", "style", "nav", "footer", "header", "noscript", "iframe"]):
            tag.decompose()

        # Sadece body icerigini al
        body = soup.find("body")
        if body:
            text = body.get_text(separator=" ", strip=True)
        else:
            text = soup.get_text(separator=" ", strip=True)

        # Cok uzunsa kirp
        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        return text

    async def _extract_products_with_ai(
        self, html_text: str, source_name: str, description: str
    ) -> list[ProductPrice]:
        """LLM kullanarak HTML'den urun bilgilerini cikarir."""

        prompt = f"""Bu bir {source_name} web sitesinden alinan metin.
{description} urunlerinin fiyat bilgilerini cikar.

Her urun icin su bilgileri JSON formatinda ver:
- name: Urun adi
- price_tl: Fiyat (sadece sayi, TL cinsinden)
- weight_grams: Gramaj (varsa, sadece sayi)
- category: Kategori (tablet, truffle, draje, hediye_kutu, diger)

SADECE JSON array dondur, baska bir sey yazma. Ornek:
[
  {{"name": "Bitter Cikolata 100g", "price_tl": 450, "weight_grams": 100, "category": "tablet"}},
  {{"name": "Truffle Kutusu", "price_tl": 890, "weight_grams": 200, "category": "truffle"}}
]

Eger urun bulamazsan bos array dondur: []

Site metni:
{html_text}
"""

        response = self._client.chat.completions.create(
            model=self._settings.openai_model_name,
            messages=[
                {
                    "role": "system",
                    "content": "Sen bir veri cikarma asistanisin. Sadece JSON formatinda cevap ver.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=4000,
        )

        content = response.choices[0].message.content or "[]"

        # JSON parse et
        try:
            # Bazen LLM ```json ... ``` ile sarar, temizle
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()

            products_data = json.loads(content)
        except json.JSONDecodeError:
            return []

        # ProductPrice objelerine cevir
        products = []
        for p in products_data:
            try:
                products.append(
                    ProductPrice(
                        name=p.get("name", ""),
                        price_tl=float(p.get("price_tl", 0)),
                        weight_grams=int(p["weight_grams"]) if p.get("weight_grams") else None,
                        category=p.get("category"),
                    )
                )
            except (ValueError, TypeError):
                continue

        return products


def load_targets_from_firebase(tenant_id: str = "default") -> list[ScrapingTarget]:
    """
    Firebase'den scraping hedeflerini yukler.

    Args:
        tenant_id: Tenant kimlik

    Returns:
        ScrapingTarget listesi (bos olabilir)
    """
    settings = get_settings()

    if not settings.is_firebase_configured():
        return []

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        # Firebase app zaten baslatildiysa tekrar baslatma
        try:
            firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate(settings.firebase_credentials_path)
            firebase_admin.initialize_app(cred, {"projectId": settings.firebase_project_id})

        db = firestore.client()

        # tenants/{tenant_id}/scraping_targets collection'indan oku
        targets_ref = db.collection("tenants").document(tenant_id).collection("scraping_targets")
        docs = targets_ref.stream()

        targets = []
        for doc in docs:
            data = doc.to_dict()
            if data.get("active", True):  # Sadece aktif hedefler
                targets.append(
                    ScrapingTarget(
                        name=data.get("name", doc.id),
                        url=data["url"],
                        description=data.get("description", "urunler"),
                    )
                )

        return targets
    except Exception:
        # Firebase hatasi - sessizce bos don, dosyadan okunacak
        return []


def load_targets_from_file() -> list[ScrapingTarget]:
    """
    JSON dosyasindan scraping hedeflerini yukler.

    Returns:
        ScrapingTarget listesi (bos olabilir)
    """
    from pathlib import Path

    settings = get_settings()
    config_path = Path(settings.scraping_targets_file)

    # Mutlak yol degilse, proje kokune gore
    if not config_path.is_absolute():
        project_root = Path(__file__).parent.parent.parent.parent
        config_path = project_root / config_path

    if not config_path.exists():
        return []

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    targets = []
    for t in data.get("targets", []):
        targets.append(
            ScrapingTarget(
                name=t["name"],
                url=t["url"],
                description=t.get("description", "urunler"),
            )
        )

    return targets


def load_targets_from_config(tenant_id: str = "default") -> list[ScrapingTarget]:
    """
    Scraping hedeflerini yukler.

    Oncelik sirasi:
    1. Firebase (varsa ve yapilandirilmissa)
    2. JSON dosyasi (fallback)

    Args:
        tenant_id: Tenant kimlik (Firebase icin)

    Returns:
        ScrapingTarget listesi (bos olabilir)
    """
    # Oncelikle Firebase'den dene
    targets = load_targets_from_firebase(tenant_id)

    if targets:
        return targets

    # Firebase bossa veya yapilandirilmamissa dosyadan oku
    return load_targets_from_file()


async def scrape_all_with_ai(tenant_id: str = "default") -> dict[str, ScraperResult]:
    """
    Config'deki tum hedefleri AI scraper ile tarar.

    Hedefler su sirada aranir:
    1. Firebase (tenants/{tenant_id}/scraping_targets)
    2. scraping_targets.json dosyasi

    Args:
        tenant_id: Tenant kimlik

    Returns:
        {source_name: ScraperResult} dict'i
    """
    import asyncio

    targets = load_targets_from_config(tenant_id)

    if not targets:
        # Hedef tanimlanmamis
        return {"_warning": ScraperResult(
            source="config",
            success=False,
            products=[],
            error="Scraping hedefi tanimlanmamis. UI'dan veya scraping_targets.json dosyasindan rakip ekleyin.",
        )}

    scraper = AIScraper()
    tasks = [scraper.scrape(target) for target in targets]
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
