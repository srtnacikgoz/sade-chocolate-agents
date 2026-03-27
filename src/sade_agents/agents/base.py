"""
Sade Chocolate - Temel Agent Base Class.

"The Connoisseur Chip" felsefesi:
Sadece kod değil, çikolata craft'ını bilen dijital şef ruhu.
"""

import logging
from typing import Literal

from crewai import Agent

logger = logging.getLogger(__name__)


class SadeAgent(Agent):
    """
    Tüm Sade Chocolate agent'larının base class'ı.

    Her Sade agent'ı:
    - Marka sesini korur (sessiz lüks)
    - Kendi departmanını bilir
    - Belirlenen otonomi seviyesinde çalışır

    Attributes:
        brand_voice: Marka sesi tonu ("sessiz_luks" default)
        department: Agent'ın departmanı
        autonomy_level: Otonomi seviyesi (autonomous, supervised, mixed)
    """

    # Sade'ye özgü özellikler (class attributes)
    brand_voice: str = "sessiz_luks"
    department: Literal["finance", "marketing", "operations", "product"] = "operations"
    autonomy_level: Literal["autonomous", "supervised", "mixed"] = "mixed"

    def __init__(
        self,
        *,
        brand_voice: str = "sessiz_luks",
        department: Literal["finance", "marketing", "operations", "product"] = "operations",
        autonomy_level: Literal["autonomous", "supervised", "mixed"] = "mixed",
        **kwargs,
    ) -> None:
        """
        SadeAgent oluşturur.

        Args:
            brand_voice: Marka sesi tonu
            department: Agent'ın ait olduğu departman
            autonomy_level: Otonomi seviyesi
            **kwargs: CrewAI Agent parametreleri (role, goal, backstory, etc.)
        """
        super().__init__(**kwargs)

        self.brand_voice = brand_voice
        self.department = department
        self.autonomy_level = autonomy_level

        logger.debug(
            "SadeAgent oluşturuldu: %s (department=%s, autonomy=%s)",
            kwargs.get("role", "Unknown"),
            department,
            autonomy_level,
        )

    def log_action(self, action: str, details: str = "") -> None:
        """
        Agent aksiyonunu loglar.

        Args:
            action: Aksiyon adı
            details: Ek detaylar
        """
        logger.info(
            "[%s] %s: %s %s",
            self.department.upper(),
            getattr(self, "role", "Agent"),
            action,
            details,
        )


__all__ = ["SadeAgent"]
