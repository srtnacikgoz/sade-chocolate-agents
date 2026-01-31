"""
Sade Chocolate - Market Analysis Crew.

Pazar analizi workflow'u:
PricingAnalyst (fiyat) -> GrowthHacker (trend) -> Narrator (ozet)
"""

import time
from crewai import Crew, Process

from sade_agents.agents import (
    PricingAnalystAgent,
    GrowthHackerAgent,
    NarratorAgent,
)
from sade_agents.crews.base_crew import create_task_with_context
from sade_agents.models import MarketAnalysisInput, MarketAnalysisOutput


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

    def _create_tasks(self, inputs: MarketAnalysisInput) -> list:
        """Task zinciri olusturur, context bagimliliklari ile."""
        # Task 1: PricingAnalyst - Fiyat analizi
        pricing_task = create_task_with_context(
            description=f"""
Rakip fiyat analizi yap: {inputs.competitor_name}

Kategori: {inputs.product_category}

Analiz edilecekler:
- Rakip fiyat araligi
- Premium segment konumlandirmasi
- Sade icin fiyat onerisi
- Rekabet stratejisi

Cikti formati:
- competitor: Rakip adi
- price_range: Min-Max TL
- positioning: Ultra-premium/Premium/Mid-tier
- recommendation: Sade icin tavsiye fiyat araligi
            """,
            expected_output="JSON: competitor, price_range, positioning, recommendation",
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

        # Task 3: Narrator - Ozet yaz
        summary_task = create_task_with_context(
            description=f"""
Pazar analizi bulgularini 'Sessiz Luks' tonunda ozetle.

Rakip: {inputs.competitor_name}

Ozet formati:
- Kisa paragraf (3-4 cumle)
- Sofistike, understated ton
- Emoji ve agresif ifadeler YASAK
- Monocle editoru gibi
            """,
            expected_output="Tek paragraf ozet metni",
            agent=self.narrator,
            context=context_for_summary,
        )
        tasks.append(summary_task)

        return tasks

    def kickoff(self, inputs: dict) -> MarketAnalysisOutput:
        """
        Market analysis workflow'unu calistirir.

        Args:
            inputs: MarketAnalysisInput field'lari

        Returns:
            MarketAnalysisOutput with pricing_analysis, trend_report, summary
        """
        validated_inputs = MarketAnalysisInput(**inputs)
        tasks = self._create_tasks(validated_inputs)

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

        start_time = time.time()

        # Input Sanitization: CrewAI sadece scalar tipler kabul eder
        crewai_inputs = {
            "competitor_name": str(inputs.get("competitor_name", "")),
            "product_category": str(inputs.get("product_category", "premium chocolate")),
            "include_trends": bool(inputs.get("include_trends", True)),
        }

        result = crew.kickoff(inputs=crewai_inputs)
        elapsed = time.time() - start_time

        # Parse result into structured output
        # Note: In production, parse actual CrewAI output
        return MarketAnalysisOutput(
            pricing_analysis={"raw_output": str(result)},
            trend_report={"raw_output": str(result)} if validated_inputs.include_trends else None,
            summary=str(result),
            execution_time_seconds=elapsed,
        )


__all__ = ["MarketAnalysisCrew"]
