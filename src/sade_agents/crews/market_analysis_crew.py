"""
Sade Chocolate - Market Analysis Crew.

Pazar analizi workflow'u:
1. SmartScraper ile GERCEK veri cek
2. PricingAnalyst (fiyat analizi - GERCEK VERİYLE)
3. GrowthHacker (trend)
4. Narrator (ozet)

ONEMLI: Bu crew GERCEK scraper verisi kullanir, LLM hayal gucu DEGIL!
"""

import asyncio
import time
from crewai import Crew, Process

from sade_agents.agents import (
    PricingAnalystAgent,
    GrowthHackerAgent,
    NarratorAgent,
)
from sade_agents.crews.base_crew import create_task_with_context
from sade_agents.models import MarketAnalysisInput, MarketAnalysisOutput
from sade_agents.scrapers import SmartScraper, ScrapingTarget


class MarketAnalysisCrew:
    """
    Pazar analizi workflow'u.

    Pipeline: PricingAnalyst -> GrowthHacker (optional) -> Narrator
    Kullanim: Rakip analizi, fiyatlandirma onerisi, trend raporu

    Agents:
    - PricingAnalyst: Rakip fiyat karsilastirmasi ve konumlandirma
    - GrowthHacker: Sosyal medya trendleri ve hashtag analizi
    - Narrator: Bulgulari 'Sessiz Luks' tonunda ozetler
    """

    def __init__(self) -> None:
        """Agent'lari olusturur."""
        self.pricing = PricingAnalystAgent()
        self.growth = GrowthHackerAgent()
        self.narrator = NarratorAgent()
        self._scraper = SmartScraper()

    async def _fetch_real_data(self, competitor_name: str, competitor_url: str | None) -> str:
        """
        Rakipten GERCEK fiyat verisi ceker.

        Returns:
            Formatli urun/fiyat listesi string'i
        """
        if not competitor_url:
            return f"UYARI: {competitor_name} icin URL tanimlanmamis. Gercek veri cekilemedi."

        target = ScrapingTarget(
            name=competitor_name,
            url=competitor_url,
            description="cikolata urunleri",
        )

        result = await self._scraper.scrape_site(target)

        if not result.success or not result.products:
            error_msg = result.error or "Urun bulunamadi"
            return f"UYARI: {competitor_name} sitesinden veri cekilemedi. Hata: {error_msg}"

        # Urunleri formatla
        lines = [f"GERCEK VERİ - {competitor_name} ({len(result.products)} urun):"]
        lines.append("-" * 50)

        # Fiyat istatistikleri
        prices = [p.price_tl for p in result.products if p.price_tl > 0]
        if prices:
            lines.append(f"Fiyat araligi: {min(prices):.0f} - {max(prices):.0f} TL")
            lines.append(f"Ortalama fiyat: {sum(prices)/len(prices):.0f} TL")
            lines.append("")

        # Urun listesi
        lines.append("Urunler:")
        for p in result.products[:20]:  # Max 20 urun goster
            weight_info = f" ({p.weight_grams}g)" if p.weight_grams else ""
            category_info = f" [{p.category}]" if p.category else ""
            gram_price = ""
            if p.weight_grams and p.price_tl > 0:
                gram_price = f" = {p.price_tl / p.weight_grams:.2f} TL/g"
            lines.append(f"  - {p.name}{weight_info}: {p.price_tl:.0f} TL{gram_price}{category_info}")

        return "\n".join(lines)

    def _create_tasks(self, inputs: MarketAnalysisInput, real_data: str) -> list:
        """Task zinciri olusturur, GERCEK VERİ ile."""
        # Task 1: PricingAnalyst - Fiyat analizi (GERCEK VERİYLE)
        pricing_task = create_task_with_context(
            description=f"""
Rakip fiyat analizi yap: {inputs.competitor_name}

Kategori: {inputs.product_category}

=== GERCEK VERİ (Web sitesinden cekildi) ===
{real_data}
===========================================

ONEMLI - KATIP KURALLAR:
1. Yukaridaki GERCEK VERİYE dayanarak analiz yap
2. Veri yoksa veya hata varsa, bunu acikca belirt
3. ASLA uydurma fiyat/urun yazma!
4. Sadece yukaridaki listede olan urunleri kullan

FIYAT METRIKLERI (Kategoriye Gore):
- Tablet cikolata: TL/gram (gramaj biliniyorsa)
- Truffle/Praline: TL/adet
- Kutu/Set: TL/kutu
- Diger: Sadece TL fiyat

Analiz edilecekler:
- Gercek fiyat araligi (yukaridaki veriden)
- Kategori bazli fiyat analizi (truffle ayri, tablet ayri, vs.)
- Premium segment konumlandirmasi
- Sade icin fiyat onerisi
- Rekabet stratejisi

Cikti formati:
- competitor: Rakip adi
- price_range: Min-Max TL (GERCEK veriden)
- price_by_category: Kategori bazli fiyatlar (truffle: X TL/adet, tablet: Y TL, vs.)
- positioning: Ultra-premium/Premium/Mid-tier
- recommendation: Sade icin tavsiye (kategori bazli)
            """,
            expected_output="JSON: competitor, price_range, price_by_category, positioning, recommendation",
            agent=self.pricing,
        )

        tasks = [pricing_task]
        context_for_summary = [pricing_task]

        # Task 2 (optional): GrowthHacker - Trend analizi
        if inputs.include_trends:
            trend_task = create_task_with_context(
                description=f"""
Pazar trend analizi yap: {inputs.product_category}

Rakip: {inputs.competitor_name}

Analiz edilecekler:
- Trend olan lezzetler
- Sosyal medya sentiment (pozitif/negitif/notr)
- Hashtag hacimleri
- Tuketici davranis degisimleri

Cikti formati:
- trending_flavors: Liste
- social_sentiment: pozitif/negatif/notr
- hashtag_volume: Sayi
- consumer_insights: Liste
                """,
                expected_output="JSON: trending_flavors, social_sentiment, hashtag_volume, consumer_insights",
                agent=self.growth,
                context=[pricing_task],
            )
            tasks.append(trend_task)
            context_for_summary.append(trend_task)

        # Task 3: Narrator - Ozet yaz (GERCEK VERİYE DAYANARAK)
        summary_task = create_task_with_context(
            description=f"""
Pazar analizi bulgularini 'Sessiz Luks' tonunda ozetle.

Rakip: {inputs.competitor_name}

=== GERCEK VERİ (Referans) ===
{real_data}
==============================

KATIP KURALLAR:
1. SADECE yukaridaki gercek urun ve fiyatlara dayan
2. Sadece bilinen urunleri ve fiyatlari kullan
3. Her urun gramla satilmaz! Truffle/Praline adet, kutu set olarak degerlendir
4. ASLA uydurma metrik yazma

Ozet formati:
- Kisa paragraf (3-4 cumle)
- Sofistike, understated ton
- Emoji ve agresif ifadeler YASAK
- SOMUT urun isimleri ve fiyatlar kullan (Dubai Chocolate 745 TL, Truffle 85 TL/adet gibi)
            """,
            expected_output="Tek paragraf ozet metni - GERCEK verilerle",
            agent=self.narrator,
            context=context_for_summary,
        )
        tasks.append(summary_task)

        return tasks

    def kickoff(self, inputs: dict) -> MarketAnalysisOutput:
        """
        Market analysis workflow'unu calistirir.

        SIRA:
        1. SmartScraper ile GERCEK veri cek
        2. Veriyi agent'lara context olarak ver
        3. Agent'lar GERCEK veriye dayanarak analiz yapar

        Args:
            inputs: MarketAnalysisInput field'lari
                - competitor_name: Rakip adi
                - competitor_url: Rakip web sitesi URL'i (ZORUNLU!)
                - product_category: Urun kategorisi
                - include_trends: Trend analizi dahil mi

        Returns:
            MarketAnalysisOutput with pricing_analysis, trend_report, summary
        """
        validated_inputs = MarketAnalysisInput(**inputs)
        start_time = time.time()

        # 1. GERCEK VERİ CEK (async scraper'i sync cagir)
        competitor_url = inputs.get("competitor_url")
        try:
            # Async scraper'i sync context'te calistir
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                real_data = loop.run_until_complete(
                    self._fetch_real_data(validated_inputs.competitor_name, competitor_url)
                )
            finally:
                loop.close()
        except Exception as e:
            real_data = f"HATA: Veri cekilemedi - {str(e)}"

        # 2. Task'lari GERCEK VERİ ile olustur
        tasks = self._create_tasks(validated_inputs, real_data)

        agents = [self.pricing]
        if validated_inputs.include_trends:
            agents.append(self.growth)
        agents.append(self.narrator)

        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

        # Input Sanitization: CrewAI sadece scalar tipler kabul eder
        crewai_inputs = {
            "competitor_name": str(inputs.get("competitor_name", "")),
            "product_category": str(inputs.get("product_category", "premium chocolate")),
            "include_trends": bool(inputs.get("include_trends", True)),
        }

        result = crew.kickoff(inputs=crewai_inputs)
        elapsed = time.time() - start_time

        # Parse result into structured output
        return MarketAnalysisOutput(
            pricing_analysis={
                "raw_output": str(result),
                "real_data_used": real_data[:500] + "..." if len(real_data) > 500 else real_data,
            },
            trend_report={"raw_output": str(result)} if validated_inputs.include_trends else None,
            summary=str(result),
            execution_time_seconds=elapsed,
        )


__all__ = ["MarketAnalysisCrew"]
