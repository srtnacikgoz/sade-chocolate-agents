"""
Sade Chocolate - Crew Factory.

Crew kompozisyonlari icin factory pattern.
Tum crew turlerini tek noktadan olusturur.
"""

from typing import Literal, Union

from sade_agents.crews.product_launch_crew import ProductLaunchCrew
from sade_agents.crews.market_analysis_crew import MarketAnalysisCrew
from sade_agents.crews.quality_audit_crew import QualityAuditCrew


CrewType = Literal["product_launch", "market_analysis", "quality_audit"]


class SadeCrewFactory:
    """
    Sade Chocolate crew factory.

    Desteklenen crew turleri:
    - product_launch: Yeni urun gelistirme workflow'u
    - market_analysis: Pazar analizi workflow'u
    - quality_audit: Kalite denetimi workflow'u

    Kullanim:
        factory = SadeCrewFactory()
        crew = factory.create_product_launch_crew()
        result = crew.kickoff(inputs)
    """

    def create_product_launch_crew(self) -> ProductLaunchCrew:
        """
        ProductLaunchCrew olusturur.

        Pipeline: Alchemist -> Narrator -> Curator -> Perfectionist
        Kullanim: Yeni lezzet gelistirme, receteden onaylanmis etikete

        Returns:
            ProductLaunchCrew instance
        """
        return ProductLaunchCrew()

    def create_market_analysis_crew(self) -> MarketAnalysisCrew:
        """
        MarketAnalysisCrew olusturur.

        Pipeline: PricingAnalyst -> GrowthHacker -> Narrator
        Kullanim: Rakip analizi, fiyatlandirma onerisi, trend raporu

        Returns:
            MarketAnalysisCrew instance
        """
        return MarketAnalysisCrew()

    def create_quality_audit_crew(self) -> QualityAuditCrew:
        """
        QualityAuditCrew olusturur.

        Pipeline: Perfectionist (single agent)
        Kullanim: Herhangi bir icerigin bagimsiz denetimi

        Returns:
            QualityAuditCrew instance
        """
        return QualityAuditCrew()

    def create_crew(
        self, crew_type: CrewType
    ) -> Union[ProductLaunchCrew, MarketAnalysisCrew, QualityAuditCrew]:
        """
        Crew turune gore uygun crew olusturur.

        Args:
            crew_type: 'product_launch', 'market_analysis', veya 'quality_audit'

        Returns:
            Belirtilen turdeki crew instance

        Raises:
            ValueError: Gecersiz crew_type icin
        """
        crew_map = {
            "product_launch": self.create_product_launch_crew,
            "market_analysis": self.create_market_analysis_crew,
            "quality_audit": self.create_quality_audit_crew,
        }

        if crew_type not in crew_map:
            valid_types = ", ".join(crew_map.keys())
            raise ValueError(
                f"Gecersiz crew turu: '{crew_type}'. "
                f"Gecerli turleri: {valid_types}"
            )

        return crew_map[crew_type]()


__all__ = ["SadeCrewFactory", "CrewType"]
