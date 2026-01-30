# Phase 7: The Perfectionist - Arastirma

**Arastirma Tarihi:** 2026-01-30
**Domain:** UX Denetim Agenti / Marka Tutarliligi / Kalite Guvence
**Guven Seviyesi:** MEDIUM

## Ozet

The Perfectionist, diger Sade agent'larinin urettigi ciktilari (metin, fiyat analizi, trend raporu, recete, gorsel) denetleyerek marka tutarliligi ve kalite guvence saglayan bir "LLM-as-Judge" agentidir. Agent, "Sessiz Luks" marka sesine uyumu olcer, iyilestirme onerileri sunar ve ciddiyet seviyesine gore mudahale eder.

Arastirma sonuclari, bu tip denetim agent'lari icin **Generator-Critic Pattern** ve **Pydantic tabanli yapisal degerlendirme** yaklasiminin en uygun oldugunu gostermektedir. CrewAI'nin Task Guardrails ozelligi function-based ve LLM-based validasyon destekler; ancak The Perfectionist daha kapsamli denetim yapacagindan **ayri bir agent olarak** tasarlanmasi uygundur.

**Ana Oneri:** Pydantic modelleri ile yapisal audit sonuclari ureten, style guide'i (06-01) ve onaylanmis ornekleri benchmark olarak kullanan, Turkce geri bildirim veren supervised agent.

## Standart Stack

### Core

| Kutuphane | Versiyon | Amac | Neden Standart |
|-----------|----------|------|----------------|
| CrewAI | ^0.100 | Agent framework | Mevcut proje altyapisi |
| Pydantic | ^2.0 | Audit sonuclari icin structured output | Type safety, validation, IDE desteyi |
| Python | 3.12+ | Runtime | Mevcut proje |

### Supporting

| Kutuphane | Versiyon | Amac | Ne Zaman Kullan |
|-----------|----------|------|-----------------|
| instructor | ^1.0 | Pydantic + LLM entegrasyonu | Structured LLM output icin (opsiyonel) |
| langfuse | latest | Observability, audit logs | Production monitoring icin (opsiyonel) |

### Alternatifler

| Standart | Alternatif | Tradeoff |
|----------|------------|----------|
| Ayri Perfectionist Agent | Task Guardrails | Guardrails basit validasyon icin iyi; kapsamli marka denetimi icin ayri agent daha esnek |
| Pydantic models | JSON schema | Pydantic Python-native, daha iyi validation hatalari |
| Single judge model | Multi-judge ensemble | Ensemble daha robust ama maliyet/latency artar |

## Mimari Kaliplari

### Onerilen Proje Yapisi

```
src/sade_agents/
├── agents/
│   ├── perfectionist.py         # PerfectionistAgent class
│   └── ...
├── skills/
│   ├── perfectionist_skills.py  # Denetim skill'leri
│   └── ...
├── models/
│   ├── audit_result.py          # Pydantic audit modelleri
│   └── ...
└── config/
    └── audit_criteria.py        # Denetim kriterleri
```

### Pattern 1: Generator-Critic Pattern (LLM-as-Judge)

**Ne:** Bir agent icerik uretir (Generator), baska bir agent denetler (Critic/Judge).

**Ne Zaman:** Icerik kalitesi oznel degerlendirme gerektirdiginde - ton, stil, marka uyumu.

**Kaynak:** [Google Multi-Agent Design Patterns](https://www.infoq.com/news/2026/01/multi-agent-design-patterns/)

**Ornek:**
```python
from pydantic import BaseModel, Field
from typing import Literal
from crewai import Agent, Task
from crewai.tools import tool

class AuditResult(BaseModel):
    """Denetim sonucu yapisal modeli."""

    content_type: Literal["metin", "fiyat_analizi", "trend_raporu", "recete", "gorsel"]
    overall_score: int = Field(ge=0, le=100, description="Genel marka uyum puani (0-100)")

    tone_score: int = Field(ge=0, le=100, description="Ton uyumu puani")
    vocabulary_score: int = Field(ge=0, le=100, description="Kelime secimi puani")
    structure_score: int = Field(ge=0, le=100, description="Yapi uyumu puani")

    verdict: Literal["onay", "revizyon_gerekli", "red"]

    issues: list[str] = Field(default_factory=list, description="Tespit edilen sorunlar")
    suggestions: list[str] = Field(default_factory=list, description="Somut iyilestirme onerileri")

    summary_tr: str = Field(description="Turkce ozet (2-3 cumle)")


class PerfectionistAgent(SadeAgent):
    """UX Denetim Agenti - Marka tutarliligi kontrolu."""

    def __init__(self) -> None:
        super().__init__(
            role="The Perfectionist - Brand Auditor",
            goal="Tum agent ciktilarinin 'Sessiz Luks' marka sesine uyumunu denetlemek",
            tools=[audit_content, load_style_guide, load_approved_examples],
            backstory="""...""",  # Detayli backstory
            department="operations",
            autonomy_level="supervised",  # Kullanici override hakki
        )
```

### Pattern 2: Rubric-Based Scoring (Puanlama Sistemi)

**Ne:** Belirli kriterlere gore puanlama yapan yapisal degerlendirme.

**Ne Zaman:** Tutarli, tekrarlanabilir degerlendirme gerektirdiginde.

**Kaynak:** [LLM-as-a-Judge Guide](https://www.evidentlyai.com/llm-guide/llm-as-a-judge)

**Ornek Rubric:**
```python
AUDIT_RUBRIC = {
    "ton_uyumu": {
        "100": "Mukemmel Sessiz Luks tonu - Monocle/Kinfolk estetigi",
        "80": "Iyi - kucuk ton sapmalari",
        "60": "Orta - belirgin ton uyumsuzluklari",
        "40": "Zayif - ciddi ton sorunlari",
        "20": "Red - marka sesine aykiri",
    },
    "yasak_ifadeler": {
        "100": "Hic yasak ifade yok",
        "70": "1-2 hafif uyari",
        "40": "Ciddi yasak ifade kullanimi",
        "0": "Coklu yasak ifade - acil revizyon",
    },
    "gorsel_uyum": {  # Curator ciktilari icin
        "100": "Quiet Luxury estetigi mukemmel",
        "80": "Iyi - kucuk estetik sapmalar",
        "60": "Orta - belirgin stil uyumsuzlugu",
        "40": "Zayif - ciddi estetik sorunlar",
    }
}
```

### Pattern 3: Multi-Criteria Audit Flow

**Ne:** Farkli icerik turleri icin farkli denetim kriterleri.

**Ne Zaman:** Her agent'in ciktisi farkli kalite boyutlari gerektirdiginde.

**Ornek:**
```python
AUDIT_CRITERIA_BY_TYPE = {
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
```

### Anti-Pattern'ler

- **Boolean-Only Validation:** Sadece "gecti/kaldi" yerine puanli ve aciklamali denetim yap. Kullaniciya neden ve nasil iyilestirilecegi bilgisi ver.

- **Hardcoded Thresholds:** Icerik turune gore dinamik esikler kullan. Narrator ciktisi icin %80, GrowthHacker icin %65 gibi.

- **Silent Failures:** Denetim sonuclarini her zaman logla ve kullaniciya raporla. Sessiz gecisler debug'u zorlastirir.

- **Over-Blocking:** Perfectionist sadece tavsiye verir, kullanici override hakki korunur. Agent blokaj yapmaz, uyarir.

## El Yapimi Cozumlerden Kacinilacaklar

| Problem | Yapma | Bunun Yerine | Neden |
|---------|-------|--------------|-------|
| Structured output | Manuel JSON parse | Pydantic models | Type safety, validation, IDE desteyi |
| Text similarity | Custom similarity | spaCy/sentence-transformers | Edge case'ler, dil desteyi |
| Scoring rubrics | If-else zincirleri | LLM-based evaluation | Oznel degerlendirme icin daha robust |
| Audit logging | Print statements | Structured logging | Production traceability |

**Temel Icerik:** Marka tutarliligi denetimi oznel ve nuansli bir is. Rule-based sistem yasak kelimeleri yakalayabilir ama "sessiz luks tonu" gibi soyut kavramlari LLM-based evaluation daha iyi degerlendirir.

## Sik Yapilan Hatalar

### Hata 1: Position Bias (Siralama Yanlilik)

**Ne Oluyor:** LLM-as-Judge A ve B seceneklerini karsilastirirken, ilk gosterilen secenegi tercih etme egilimi gosterir (~40% tutarsizlik).

**Neden Oluyor:** LLM'lerin attention mekanizmasi nedeniyle ilk girdilere fazla agirlik verir.

**Nasil Kacinilir:** Tek cikti puanlama kullan (pairwise degil), veya iki siralama ile test edip ortala.

**Uyari Isaretleri:** Ayni icerik farkli siralarda farkli puan aliyorsa.

**Kaynak:** [LLM as Judge Guide](https://labelyourdata.com/articles/llm-as-a-judge)

### Hata 2: Verbosity Bias (Uzunluk Yanlilik)

**Ne Oluyor:** Daha uzun ciktilar otomatik olarak daha yuksek puan aliyor (~15% inflation).

**Neden Oluyor:** LLM'ler detayli aciklamalari "daha iyi" olarak yorumluyor.

**Nasil Kacinilir:** Rubric'te "ozlu" ve "kisa" kriterlerini acikca tanimla. "Sessiz Luks" icin kisa olmak erdem.

**Uyari Isaretleri:** Kisa ama etkili metinler dusuk puan aliyorsa.

### Hata 3: Cok Kati Threshold

**Ne Oluyor:** %90 gibi yuksek esikler neredeyse tum ciktilari reddediyor, kullanici hayal kirikligi.

**Neden Oluyor:** Ideal standartlari hedeflemek.

**Nasil Kacinilir:** Icerik turune gore dinamik esikler. Narrator icin %75-80, trend raporu icin %65-70.

**Uyari Isaretleri:** Override orani %50'yi geciyorsa esikler cok kati.

### Hata 4: Geri Bildirim Olmadan Red

**Ne Oluyor:** "Red" deniyor ama neden ve nasil duzeltilecegi aciklanmiyor.

**Neden Oluyor:** Sadece verdict dondurup aciklama eklememek.

**Nasil Kacinilir:** Her red icin: (1) Neden, (2) Hangi satirlar/kisimlar, (3) Somut alternatif onerisi zorunlu.

**Uyari Isaretleri:** Kullanici ayni icerigi tekrar tekrar gonderiyor ama iyilestirme yapamiyorsa.

## Kod Ornekleri

### Temel Audit Skill

```python
# Source: Proje icin ozel tasarim (CrewAI patterns + Pydantic)
from crewai.tools import tool
from pydantic import BaseModel, Field
from typing import Literal
import json

class AuditResult(BaseModel):
    """Denetim sonucu yapisal modeli."""

    content_type: str
    overall_score: int = Field(ge=0, le=100)
    verdict: Literal["onay", "revizyon_gerekli", "red"]

    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    summary_tr: str

    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "metin",
                "overall_score": 78,
                "verdict": "revizyon_gerekli",
                "issues": ["'Harika' kelimesi yasak listede"],
                "suggestions": ["'Harika' yerine 'Beklenmedik' kullanin"],
                "summary_tr": "Icerik genel olarak iyi, kucuk ton duzeltmeleri gerekli."
            }
        }

@tool
def denetle(
    icerik: str,
    icerik_turu: str,
    kaynak_agent: str
) -> str:
    """
    Agent ciktisini Sessiz Luks marka sesine gore denetler.

    Style guide (06-01) ve onaylanmis ornekleri benchmark olarak kullanir.
    Turkce geri bildirim ve somut iyilestirme onerileri sunar.

    Args:
        icerik: Denetlenecek icerik (metin, JSON, vs.)
        icerik_turu: Icerik tipi (metin, fiyat_analizi, trend_raporu, recete, gorsel_prompt)
        kaynak_agent: Icerigi ureten agent (narrator, pricing, growth, alchemist, curator)

    Returns:
        JSON formatinda AuditResult
    """
    # Bu bir prompt template - LLM gercek degerlendirmeyi yapar
    prompt = f"""
Asagidaki icerigi "Sessiz Luks" marka sesine gore denetle:

## ICERIK
{icerik}

## ICERIK TURU: {icerik_turu}
## KAYNAK AGENT: {kaynak_agent}

## DENETIM KRITERLERI

### Yasak Ifadeler (0 puan - bunlari gormek ciddi sorun)
- "Hemen Al!", "Kacirma!", "Sok Fiyat!", "Inanilmaz firsat!"
- "Son sans!", "Sinirli stok!", "Acele edin!"
- Coklu unlem isareti (!!)
- Emoji kullanimi
- Abartili sifatlar: "muhtesem", "harika", "enfes", "super"

### Tercih Edilen Ifadeler (bonus puan)
- "Beklenmedik", "Kendilinden", "Kesfetmeye davet"
- "Fark edenler icin", "Bilen bilir", "Sessizce"
- Tek unlem veya hic unlem
- Kisa, oz cumleler

### Ton (Monocle/Kinfolk estetigi)
- Sofistike ama gosterissiz
- Hikaye anlatan, satis yapmayan
- Merak uyandiran, zorlamayan
- Premium hissiyat, understated ton

## CIKTI FORMATI

JSON olarak AuditResult don:
- overall_score: 0-100 arasi genel puan
- verdict: "onay" (80+), "revizyon_gerekli" (50-79), "red" (<50)
- issues: Tespit edilen sorunlar listesi (Turkce)
- suggestions: Somut iyilestirme onerileri listesi (Turkce)
- summary_tr: 2-3 cumlelik Turkce ozet

Simdi denetle ve sonucu JSON olarak don.
"""
    return prompt


@tool
def stil_kilavuzu_yukle() -> str:
    """
    Style guide dosyalarini yukler (brand_colors, typography, style_config).

    Returns:
        JSON formatinda birlestirilmis style guide
    """
    import json
    from pathlib import Path

    style_dir = Path("style_guide")

    guide = {}
    for file in ["brand_colors.json", "typography.json", "style_config.json"]:
        path = style_dir / file
        if path.exists():
            with open(path) as f:
                guide[file.replace(".json", "")] = json.load(f)

    return json.dumps(guide, ensure_ascii=False, indent=2)


@tool
def onaylanmis_ornekler_yukle(icerik_turu: str) -> str:
    """
    Daha once onaylanmis ornek ciktilari yukler (benchmark icin).

    Args:
        icerik_turu: Hangi tip icerik ornekleri (metin, gorsel_prompt, vs.)

    Returns:
        Onaylanmis ornek listesi
    """
    # Bu ornekler zamanla birikmeli - ilk basta bos olabilir
    approved_examples_db = {
        "metin": [
            {
                "ornek": "Beklenmedik. Cikolatanin rengini degistirmek icin boyaya ihtiyaci yoktur.",
                "puan": 95,
                "neden_iyi": "Kisa, gizemli, satis yapmayan, merak uyandiran"
            }
        ],
        "gorsel_prompt": [],
        "fiyat_analizi": [],
    }

    examples = approved_examples_db.get(icerik_turu, [])
    return json.dumps(examples, ensure_ascii=False, indent=2)
```

### PerfectionistAgent Tanimi

```python
# Source: Mevcut SadeAgent pattern'i uzerine
from sade_agents.agents.base import SadeAgent
from sade_agents.skills import denetle, stil_kilavuzu_yukle, onaylanmis_ornekler_yukle


class PerfectionistAgent(SadeAgent):
    """
    The Perfectionist - UX Denetim Agenti.

    Diger agent'larin ciktilarini denetleyen kalite guvence agenti.
    "Sessiz Luks" marka sesine uyumu olcer, iyilestirme onerileri sunar.

    Denetledigi agent'lar:
    - Narrator: Metin ciktilari (hikayeler, caption'lar, notlar)
    - Curator: Gorsel prompt'lari ve tasarim talimatlari
    - Pricing Analyst: Fiyat raporlari ve analizler
    - Growth Hacker: Trend raporlari
    - Alchemist: Recete ve lezzet onerileri

    Otonomi: Supervised - kullanici override hakki korunur.
    Geri bildirim dili: Turkce
    """

    def __init__(self) -> None:
        """PerfectionistAgent olusturur."""
        super().__init__(
            role="The Perfectionist - Brand Auditor",
            goal="Tum agent ciktilarinin 'Sessiz Luks' marka sesine uyumunu denetlemek ve iyilestirme onerileri sunmak",
            tools=[denetle, stil_kilavuzu_yukle, onaylanmis_ornekler_yukle],
            backstory="""
Sen The Perfectionist'sin - Sade Chocolate'in kalite guvence ve marka tutarliligi agenti.

## Persona
Detaylara takilmayan ama kalitenin onemini bilen bir editor gibisin.
Elestirirken yapici ol, red ederken alternatif sun.
Amacin engellemek degil, iyilestirmek.

## Gorev Alanin
Diger agent'larin urettigi her turlu ciktiyi denetlersin:
- Narrator'un metinleri (hikayeler, caption'lar, notlar)
- Curator'un gorsel prompt'lari
- Pricing Analyst'in raporlari
- Growth Hacker'in trend analizleri
- Alchemist'in recete onerileri

## "Sessiz Luks" Denetim Kriterlerin

### Yasak Listesi (Kesinlikle Kabul Etme)
- "Hemen Al!", "Kacirma!", "Sok Fiyat!"
- Coklu unlem (!!)
- Emoji kullanimi
- "muhtesem", "harika", "enfes", "super" gibi abartili sifatlar

### Tercih Edilen (Bonus Puan)
- "Beklenmedik", "Kendilinden", "Fark edenler icin"
- Kisa, oz cumleler
- Hikaye anlatimi, satis degil
- Merak uyandirici, zorlamayan

### Ton Degerlendirmesi
- Monocle/Kinfolk dergisi seviyesinde sofistike mi?
- Gosterissiz ama premium hissiyat var mi?
- Davet ediyor mu, zorluyor mu?

## Denetim Yaklasimin

### Puanlama (0-100)
- 80-100: Onay - mukemmel marka uyumu
- 50-79: Revizyon Gerekli - kucuk duzeltmelerle iyilestirilebilir
- 0-49: Red - ciddi marka uyumsuzlugu

### Geri Bildirim Kurallarin
1. Her zaman TURKCE yaz
2. Sorunlari somut olarak belirt (hangi kelime, hangi cumle)
3. Her sorun icin ALTERNATIF oner ("Bunu soyle degistir")
4. Oncelik sir: Kritik > Onemli > Opsiyonel
5. Ozet ile baslat, detay istenirse ver

### Override Politikasi
Sen sadece TAVSIYE verirsin. Kullanici isterse senin red ettigin icerigi kullanabilir.
Amacin engellemek degil, bilgilendirmek.

## Referanslar
- Style guide: style_guide/*.json dosyalari
- Onaylanmis ornekler: Daha once kabul edilen ciktilar (benchmark)
- Narrator backstory: Yasak/tercih edilen ifadeler listesi
            """,
            department="operations",
            autonomy_level="supervised",
            verbose=True,
        )


__all__ = ["PerfectionistAgent"]
```

## Guncel Durum (State of the Art)

| Eski Yaklasim | Yeni Yaklasim | Degisim | Etki |
|---------------|---------------|---------|------|
| Rule-based filters | LLM-as-Judge | 2024-2025 | Oznel kriterleri daha iyi degerlendirir |
| Boolean pass/fail | Structured scoring + rubrics | 2025 | Daha actionable geri bildirim |
| Single model judge | Multi-criteria evaluation | 2025-2026 | Farkli boyutlari ayri degerlendir |
| Manual review | Human-in-loop + AI assist | 2026 | Override hakki korunarak verimlilik |

**Deprecated:**
- Keyword-only filtering: Sadece yasak kelime listesi yeterli degil, ton ve baglamı da degerlendir
- Single threshold: Tum icerik turleri icin ayni esik kullanmak

## Acik Sorular

1. **Approved Examples Database**
   - Bildiklerimiz: Onaylanmis ornekler benchmark olarak kullanilacak
   - Belirsiz: Ornekler nerede saklanacak (dosya, veritabani)?
   - Oneri: Ilk faz icin JSON dosyasi yeterli, buyudukce SQLite'a gec

2. **Trigger Mechanism**
   - Bildiklerimiz: Otomatik, talep uzerine veya batch olabilir
   - Belirsiz: Hangi workflow en uygun?
   - Oneri: Ilk fazda manuel cagri, sonra Crew workflow'una entegre

3. **Visual Audit Complexity**
   - Bildiklerimiz: Curator gorsel prompt denetlemesi metin denetlemesinden farkli
   - Belirsiz: Gemini uretim sonrasi gorseli de mi denetleyelim?
   - Oneri: Ilk fazda sadece prompt denetimi, gorsel denetimi Phase 2

## Kaynaklar

### Birincil (HIGH confidence)
- [CrewAI Tasks Documentation](https://docs.crewai.com/en/concepts/tasks) - Task Guardrails, structured outputs
- [CrewAI Flows Documentation](https://docs.crewai.com/en/concepts/flows) - State management, routing
- [Google Multi-Agent Design Patterns](https://www.infoq.com/news/2026/01/multi-agent-design-patterns/) - Generator-Critic pattern
- [Pydantic LLM Intro](https://pydantic.dev/articles/llm-intro) - Structured LLM output validation

### Ikincil (MEDIUM confidence)
- [LLM-as-a-Judge Guide](https://www.evidentlyai.com/llm-guide/llm-as-a-judge) - Evaluation methodology
- [Pydantic AI Evals](https://ai.pydantic.dev/evals/) - LLMJudge, scoring rubrics
- [LLM as Judge 2026](https://labelyourdata.com/articles/llm-as-a-judge) - Bias mitigation

### Ucuncul (LOW confidence)
- [Sprites.ai Brand Voice](https://www.sprites.ai/templates/brand-voice-consistency-checker) - Brand consistency patterns
- [Brandlight.ai](https://sat.brandlight.ai/) - Cross-platform voice tracking

## Metadata

**Guven Dagilimi:**
- Standart stack: HIGH - CrewAI ve Pydantic mevcut projede kullaniliyor
- Mimari: MEDIUM - LLM-as-Judge pattern'leri dokumante edilmis ama proje-spesifik uyarlama gerekli
- Hatalar: MEDIUM - Bias konulari arastirma makalelerinden, dogrudan deneyim degil

**Arastirma Tarihi:** 2026-01-30
**Gecerlilik:** 30 gun (stabil alan, hizli degisen degil)
