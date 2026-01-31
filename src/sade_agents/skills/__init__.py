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
from sade_agents.skills.codegen_skills import (
    generate_streamlit_code,
    verify_generated_code,
    load_reference_examples,
)
from sade_agents.skills.curator_skills import gorsel_tasarla
from sade_agents.skills.design_skills import fetch_figma_design, extract_design_tokens
from sade_agents.skills.growth_skills import sosyal_nabiz
from sade_agents.skills.narrator_skills import hikayelestir
from sade_agents.skills.perfectionist_skills import denetle, stil_kilavuzu_yukle, onaylanmis_ornekler_yukle
from sade_agents.skills.pricing_skills import fiyat_kontrol

__all__: list[str] = [
    "denetle",
    "extract_design_tokens",
    "fetch_figma_design",
    "fiyat_kontrol",
    "generate_streamlit_code",
    "gorsel_tasarla",
    "hikayelestir",
    "lezzet_pisileri",
    "load_reference_examples",
    "onaylanmis_ornekler_yukle",
    "sosyal_nabiz",
    "stil_kilavuzu_yukle",
    "verify_generated_code",
]
