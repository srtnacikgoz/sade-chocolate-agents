"""
Sade Chocolate - Test Agent.

Sistemin çalıştığını doğrulamak için basit bir agent.
"""

from sade_agents.agents.base import SadeAgent


class TestAgent(SadeAgent):
    """
    Sistemin doğru çalıştığını test eden agent.

    Bu agent production'da kullanılmaz, sadece setup doğrulaması içindir.
    """

    def __init__(self) -> None:
        """TestAgent oluşturur."""
        super().__init__(
            role="Test Agent",
            goal="Sade Chocolate agent sisteminin çalıştığını doğrulamak",
            backstory="""
            Ben Sade Chocolate'ın test agent'ıyım.
            Görevim sistemin düzgün kurulduğunu ve çalıştığını doğrulamak.
            Basit görevleri yerine getirerek altyapının sağlam olduğunu kanıtlarım.
            """,
            department="operations",
            autonomy_level="supervised",
            verbose=True,
        )


__all__ = ["TestAgent"]
