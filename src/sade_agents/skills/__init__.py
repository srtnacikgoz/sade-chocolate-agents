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

from sade_agents.skills.narrator_skills import hikayelestir

__all__: list[str] = ["hikayelestir"]
