"""
Sade Chocolate - Crews Modulu.

Multi-agent crew kompozisyonlari ve yardimci fonksiyonlar.
"""

from sade_agents.crews.base_crew import (
    create_task_with_context,
    timed_execution,
    requires_approval,
)
from sade_agents.crews.factory import SadeCrewFactory, CrewType
from sade_agents.crews.market_analysis_crew import MarketAnalysisCrew
from sade_agents.crews.product_launch_crew import ProductLaunchCrew
from sade_agents.crews.quality_audit_crew import QualityAuditCrew


__all__: list[str] = [
    # Base utilities
    "create_task_with_context",
    "timed_execution",
    "requires_approval",
    # Factory
    "SadeCrewFactory",
    "CrewType",
    # Crews
    "MarketAnalysisCrew",
    "ProductLaunchCrew",
    "QualityAuditCrew",
]
