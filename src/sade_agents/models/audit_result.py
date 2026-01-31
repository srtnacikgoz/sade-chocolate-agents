"""
Sade Chocolate - Audit Result Models.

Denetim sonuclari icin Pydantic modelleri.
The Perfectionist agent'in cikti formati.
"""

from typing import Literal
from pydantic import BaseModel, Field


class AuditResult(BaseModel):
    """
    Denetim sonucu yapisal modeli.

    The Perfectionist agent'in her denetim icin urettigi standart cikti.
    JSON olarak serialize edilebilir, type-safe.
    """

    content_type: Literal["metin", "fiyat_analizi", "trend_raporu", "recete", "gorsel_prompt"]
    source_agent: Literal["narrator", "pricing", "growth", "alchemist", "curator"]

    # Puanlama (0-100)
    overall_score: int = Field(ge=0, le=100, description="Genel marka uyum puani")
    tone_score: int = Field(ge=0, le=100, description="Ton uyumu puani")
    vocabulary_score: int = Field(ge=0, le=100, description="Kelime secimi puani")
    structure_score: int = Field(ge=0, le=100, description="Yapi uyumu puani")

    # Karar
    verdict: Literal["onay", "revizyon", "red"] = Field(
        description="onay: 80+, revizyon: 50-79, red: <50"
    )

    # Geri bildirim
    issues: list[str] = Field(default_factory=list, description="Tespit edilen sorunlar (Turkce)")
    suggestions: list[str] = Field(default_factory=list, description="Somut iyilestirme onerileri (Turkce)")
    summary_tr: str = Field(description="2-3 cumlelik Turkce ozet")

    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "metin",
                "source_agent": "narrator",
                "overall_score": 78,
                "tone_score": 85,
                "vocabulary_score": 70,
                "structure_score": 80,
                "verdict": "revizyon",
                "issues": ["'Harika' kelimesi yasak listede"],
                "suggestions": ["'Harika' yerine 'Beklenmedik' kullanin"],
                "summary_tr": "Icerik genel olarak iyi, kucuk ton duzeltmeleri gerekli."
            }
        }


# Icerik turune gore denetim kriterleri
AUDIT_CRITERIA_BY_TYPE: dict[str, dict] = {
    "narrator_output": {
        "kritik": ["yasak_ifadeler", "ton_uyumu", "emoji_kontrolu"],
        "onemli": ["kelime_secimi", "cumle_uzunlugu"],
        "opsiyonel": ["hashtag_formati"],
        "threshold": 75,
    },
    "curator_output": {
        "kritik": ["renk_paleti_uyumu", "tipografi_kurallari", "white_space"],
        "onemli": ["kompozisyon", "text_limit"],
        "opsiyonel": ["referans_uyumu"],
        "threshold": 80,
    },
    "pricing_output": {
        "kritik": ["marka_tonu", "sayisal_dogruluk"],
        "onemli": ["format_tutarliligi"],
        "opsiyonel": [],
        "threshold": 70,
    },
    "alchemist_output": {
        "kritik": ["teknik_dogruluk", "marka_tonu"],
        "onemli": ["aciklama_kalitesi"],
        "opsiyonel": [],
        "threshold": 70,
    },
    "growth_output": {
        "kritik": ["marka_tonu", "uygun_dil"],
        "onemli": ["format_tutarliligi"],
        "opsiyonel": [],
        "threshold": 65,
    }
}


__all__ = ["AuditResult", "AUDIT_CRITERIA_BY_TYPE"]
