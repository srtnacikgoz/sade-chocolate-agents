"""
Sade Chocolate - Workflow Models.

Multi-agent workflow'lari icin Pydantic input/output modelleri.
Orkestrasyon katmaninda type-safe veri akisi saglar.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field

from sade_agents.models.audit_result import AuditResult


class ProductLaunchInput(BaseModel):
    """
    Urun gelistirme workflow'u icin giris modeli.

    Yeni bir cikolata urunu olusturma surecini baslatir.
    Alchemist, Narrator, Curator ve opsiyonel olarak Perfectionist agent'larini icerir.
    """

    flavor_concept: str = Field(
        description="Lezzet konsepti aciklamasi (ornegin: 'Antep Fistikli', 'Lavanta Bal')"
    )
    target_audience: str = Field(
        default="Quiet luxury consumers",
        description="Hedef kitle segmenti"
    )
    price_range_min: float = Field(
        default=100.0,
        description="Minimum fiyat (TL)"
    )
    price_range_max: float = Field(
        default=200.0,
        description="Maksimum fiyat (TL)"
    )
    include_audit: bool = Field(
        default=True,
        description="Perfectionist agent ile kalite denetimi yapilsin mi"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "flavor_concept": "Antep Fistikli",
                "target_audience": "Quiet luxury consumers",
                "price_range_min": 150.0,
                "price_range_max": 200.0,
                "include_audit": True
            }
        }


class ProductLaunchOutput(BaseModel):
    """
    Urun gelistirme workflow'u cikti modeli.

    Tum agent ciktilarini birlestirir: recete, hikaye, etiket ve denetim.
    """

    recipe: dict = Field(
        description="Alchemist agent'in urettigi recete bilgisi"
    )
    story: dict = Field(
        description="Narrator agent'in urettigi hikaye, caption ve tasting note"
    )
    label_paths: list[str] = Field(
        description="Curator agent'in olusturdugu etiket dosya yollari"
    )
    audit: Optional[AuditResult] = Field(
        default=None,
        description="Perfectionist agent'in denetim sonucu (include_audit=True ise)"
    )
    execution_time_seconds: float = Field(
        description="Toplam workflow calisma suresi (saniye)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "recipe": {
                    "name": "Antep Fistikli",
                    "base_chocolate": "Bitter %70",
                    "ingredients": ["Antep fistigi", "Kakaolu ceviz"],
                    "technique": "Temperli dokum"
                },
                "story": {
                    "product_story": "Antep'in ustaligi...",
                    "social_caption": "Sade'den yeni lezzet.",
                    "tasting_note": "Ilk isirisin ardidan..."
                },
                "label_paths": ["outputs/labels/antep_fistikli_v1.png"],
                "audit": None,
                "execution_time_seconds": 45.2
            }
        }


class MarketAnalysisInput(BaseModel):
    """
    Pazar analizi workflow'u giris modeli.

    Rakip analizi ve trend arastirmasi icin kullanilir.
    PricingAnalyst ve opsiyonel olarak GrowthHacker agent'larini icerir.
    """

    competitor_name: str = Field(
        description="Analiz edilecek rakip adi (ornegin: 'Vakko', 'Godiva')"
    )
    product_category: str = Field(
        default="premium chocolate",
        description="Odaklanilacak urun kategorisi"
    )
    include_trends: bool = Field(
        default=True,
        description="GrowthHacker trend analizi dahil edilsin mi"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "competitor_name": "Vakko",
                "product_category": "premium chocolate",
                "include_trends": True
            }
        }


class MarketAnalysisOutput(BaseModel):
    """
    Pazar analizi workflow'u cikti modeli.

    Fiyatlandirma analizi, trend raporu ve ozet icerir.
    """

    pricing_analysis: dict = Field(
        description="PricingAnalyst agent'in fiyat karsilastirmasi ve onerisi"
    )
    trend_report: Optional[dict] = Field(
        default=None,
        description="GrowthHacker agent'in trend raporu (include_trends=True ise)"
    )
    summary: str = Field(
        description="Narrator agent'in bulgulari ozetleyen metni"
    )
    execution_time_seconds: float = Field(
        description="Toplam workflow calisma suresi (saniye)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pricing_analysis": {
                    "competitor": "Vakko",
                    "price_range": "180-350 TL",
                    "positioning": "Ultra-premium",
                    "recommendation": "150-200 TL arasi konumlandirma"
                },
                "trend_report": {
                    "trending_flavors": ["tuzsuz karamel", "matcha"],
                    "social_sentiment": "pozitif",
                    "hashtag_volume": 12500
                },
                "summary": "Vakko ultra-premium segmentinde konumlanmis...",
                "execution_time_seconds": 32.8
            }
        }


class QualityAuditInput(BaseModel):
    """
    Kalite denetimi workflow'u giris modeli.

    Tek bir icerik parcasinin Perfectionist agent ile denetimi icin.
    Bagimsiz denetim calistirmak icin kullanilir.
    """

    content: str = Field(
        description="Denetlenecek icerik (metin veya prompt)"
    )
    content_type: Literal["metin", "gorsel_prompt", "fiyat_analizi", "trend_raporu", "recete"] = Field(
        description="Icerik turu - denetim kriterlerini belirler"
    )
    source_agent: Literal["narrator", "curator", "pricing", "growth", "alchemist"] = Field(
        description="Icerigi ureten kaynak agent"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Sade'nin en yeni lezzeti, Antep'in ustaligi ile bulusuyor.",
                "content_type": "metin",
                "source_agent": "narrator"
            }
        }


class QualityAuditOutput(BaseModel):
    """
    Kalite denetimi workflow'u cikti modeli.

    Yapisal denetim sonucu ve basari durumu icerir.
    """

    audit_result: AuditResult = Field(
        description="Yapilandirilmis denetim sonucu"
    )
    passed: bool = Field(
        description="Icerik esik degerini gectiyse True"
    )
    execution_time_seconds: float = Field(
        description="Denetim calisma suresi (saniye)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "audit_result": {
                    "content_type": "metin",
                    "source_agent": "narrator",
                    "overall_score": 85,
                    "tone_score": 90,
                    "vocabulary_score": 80,
                    "structure_score": 85,
                    "verdict": "onay",
                    "issues": [],
                    "suggestions": ["Daha kisa cumleler tercih edilebilir"],
                    "summary_tr": "Icerik marka tonuna uygun, kucuk iyilestirmeler onerilebilir."
                },
                "passed": True,
                "execution_time_seconds": 8.5
            }
        }


__all__ = [
    "ProductLaunchInput",
    "ProductLaunchOutput",
    "MarketAnalysisInput",
    "MarketAnalysisOutput",
    "QualityAuditInput",
    "QualityAuditOutput",
]
