"""
Sade Agents - Agent modülleri.

Bu modül, tüm Sade Chocolate agentlarının temel sınıflarını
ve implementasyonlarını içerir.

Agent'lar CrewAI tabanlı olarak inşa edilecek ve her biri
belirli bir iş alanında uzmanlaşacak.
"""

from sade_agents.agents.base import SadeAgent

__all__: list[str] = ["SadeAgent"]
