"""
Sade Agents - Skill modülleri.

Bu modül, agent'ların kullanacağı skill'leri (yetenekleri) içerir.
Her skill, belirli bir görevi yerine getiren Python fonksiyonu olarak
implement edilir.

Skill kategorileri:
- Marka: Ses tonu, içerik üretimi
- Analitik: Fiyat takibi, trend analizi
- Yaratıcı: Reçete, tasarım
- Kalite: Denetim, iyileştirme
"""

from sade_agents.skills.alchemist_skills import lezzet_pisileri
from sade_agents.skills.curator_skills import gorsel_tasarla
from sade_agents.skills.growth_skills import sosyal_nabiz
from sade_agents.skills.narrator_skills import hikayelestir
from sade_agents.skills.pricing_skills import fiyat_kontrol

__all__: list[str] = [
    "fiyat_kontrol",
    "gorsel_tasarla",
    "hikayelestir",
    "lezzet_pisileri",
    "sosyal_nabiz",
]
