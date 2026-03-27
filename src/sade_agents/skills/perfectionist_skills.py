"""
Sade Chocolate - The Perfectionist Skills.

UX denetim ve marka tutarliligi kontrolu icin skill fonksiyonlari.
LLM-as-Judge pattern'i ile calisan denetim araclari.
"""

import json
from pathlib import Path
from typing import Literal

from crewai.tools import tool

# Style guide paths
STYLE_GUIDE_DIR = Path(__file__).parent.parent.parent.parent / "style_guide"


@tool
def denetle(
    icerik: str,
    icerik_turu: Literal["metin", "fiyat_analizi", "trend_raporu", "recete", "gorsel_prompt"],
    kaynak_agent: Literal["narrator", "pricing", "growth", "alchemist", "curator"]
) -> str:
    """
    Agent ciktisini 'Sessiz Luks' marka sesine gore denetler.

    Style guide ve onaylanmis ornekleri benchmark olarak kullanir.
    Turkce geri bildirim ve somut iyilestirme onerileri sunar.

    Args:
        icerik: Denetlenecek icerik (metin, JSON, prompt vs.)
        icerik_turu: Icerik tipi (metin, fiyat_analizi, trend_raporu, recete, gorsel_prompt)
        kaynak_agent: Icerigi ureten agent (narrator, pricing, growth, alchemist, curator)

    Returns:
        LLM icin hazir denetim prompt'u (AuditResult formatinda cikti bekler)
    """
    # Icerik turune gore threshold ve kriterler
    thresholds = {
        "metin": 75,
        "fiyat_analizi": 70,
        "trend_raporu": 65,
        "recete": 70,
        "gorsel_prompt": 80,
    }
    threshold = thresholds.get(icerik_turu, 70)

    prompt = f"""
Asagidaki icerigi "Sessiz Luks" marka sesine gore denetle.

## DENETLENECEK ICERIK
```
{icerik}
```

## METADATA
- Icerik Turu: {icerik_turu}
- Kaynak Agent: {kaynak_agent}
- Minimum Esik: {threshold}/100

## DENETIM KRITERLERI

### YASAK IFADELER (Bunlari gormek ciddi puan dusurur)
- "Hemen Al!", "Kacirma!", "Sok Fiyat!", "Inanilmaz firsat!"
- "Son sans!", "Sinirli stok!", "Acele edin!"
- Coklu unlem isareti (!!)
- Emoji kullanimi
- Abartili sifatlar: "muhtesem", "harika", "enfes", "super", "inanilmaz"

### TERCIH EDILEN IFADELER (Bonus puan)
- "Beklenmedik", "Kendilinden", "Kesfetmeye davet"
- "Fark edenler icin", "Bilen bilir", "Sessizce"
- Tek unlem veya hic unlem
- Kisa, oz cumleler

### TON DEGERLENDIRMESI (Monocle/Kinfolk estetigi)
- Sofistike ama gosterissiz
- Hikaye anlatan, satis yapmayan
- Merak uyandiran, zorlamayan
- Premium hissiyat, understated ton

### ICERIK TURUNE OZEL KRITERLER
{"- Gorsel prompt: Renk paleti uyumu, tipografi kurallari, white space" if icerik_turu == "gorsel_prompt" else ""}
{"- Metin: Cumle uzunlugu, kelime secimi, emoji kontrolu" if icerik_turu == "metin" else ""}
{"- Fiyat analizi: Sayisal dogruluk, format tutarliligi" if icerik_turu == "fiyat_analizi" else ""}
{"- Recete: Teknik dogruluk, aciklama kalitesi" if icerik_turu == "recete" else ""}
{"- Trend raporu: Uygun dil, format tutarliligi" if icerik_turu == "trend_raporu" else ""}

## BEKLENEN CIKTI FORMATI

Asagidaki JSON formatinda cikti uret:

{{
    "content_type": "{icerik_turu}",
    "source_agent": "{kaynak_agent}",
    "overall_score": <0-100 arasi genel puan>,
    "tone_score": <0-100 arasi ton uyumu>,
    "vocabulary_score": <0-100 arasi kelime secimi>,
    "structure_score": <0-100 arasi yapi uyumu>,
    "verdict": "<onay (80+) | revizyon_gerekli (50-79) | red (<50)>",
    "issues": ["Sorun 1 (Turkce)", "Sorun 2 (Turkce)"],
    "suggestions": ["Oneri 1 - somut alternatif (Turkce)", "Oneri 2 (Turkce)"],
    "summary_tr": "2-3 cumlelik Turkce ozet"
}}

## ONEMLI KURALLAR
1. Tum geri bildirimler TURKCE olmali
2. Her sorun icin SOMUT alternatif oner
3. Verdict esik degerine gore otomatik belirle: {threshold}+ = onay
4. Kisa icerik = kotu demek degil. "Sessiz Luks" ozlu olmayi sever.

Simdi icerigi denetle ve JSON formatinda sonuc don.
"""
    return prompt.strip()


@tool
def stil_kilavuzu_yukle() -> str:
    """
    Style guide dosyalarini yukler (brand_colors, typography, style_config).

    The Perfectionist'in denetim sirasinda referans olarak kullandigi
    marka stil tanimlari.

    Returns:
        JSON formatinda birlestirilmis style guide
    """
    guide: dict = {}

    # Brand colors
    colors_path = STYLE_GUIDE_DIR / "brand_colors.json"
    if colors_path.exists():
        with open(colors_path, "r", encoding="utf-8") as f:
            guide["brand_colors"] = json.load(f)

    # Typography
    typography_path = STYLE_GUIDE_DIR / "typography.json"
    if typography_path.exists():
        with open(typography_path, "r", encoding="utf-8") as f:
            guide["typography"] = json.load(f)

    # Style config
    config_path = STYLE_GUIDE_DIR / "style_config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            guide["style_config"] = json.load(f)

    if not guide:
        return json.dumps({
            "error": "Style guide dosyalari bulunamadi",
            "expected_path": str(STYLE_GUIDE_DIR),
            "expected_files": ["brand_colors.json", "typography.json", "style_config.json"]
        }, ensure_ascii=False, indent=2)

    return json.dumps(guide, ensure_ascii=False, indent=2)


@tool
def onaylanmis_ornekler_yukle(icerik_turu: Literal["metin", "gorsel_prompt", "fiyat_analizi", "trend_raporu", "recete"]) -> str:
    """
    Daha once onaylanmis ornek ciktilari yukler (benchmark icin).

    The Perfectionist bu ornekleri referans olarak kullanarak
    yeni iceriklerin kalitesini degerlendirir.

    Args:
        icerik_turu: Hangi tip icerik ornekleri (metin, gorsel_prompt, vs.)

    Returns:
        JSON formatinda onaylanmis ornek listesi
    """
    # Baslangic ornekleri - zamanla birikmeli
    approved_examples_db: dict[str, list[dict]] = {
        "metin": [
            {
                "ornek": "Beklenmedik. Cikolatanin rengini degistirmek icin boyaya ihtiyaci yoktur.",
                "puan": 95,
                "neden_iyi": "Kisa, gizemli, satis yapmayan, merak uyandiran",
                "kaynak": "narrator"
            },
            {
                "ornek": "Bazi tatlar anlatilmaz, sadece hissedilir.",
                "puan": 92,
                "neden_iyi": "Ozlu, sofistike, davet eden ton",
                "kaynak": "narrator"
            },
            {
                "ornek": "Fark edenler icin. %72 kakao, Ekvador mahsulu.",
                "puan": 88,
                "neden_iyi": "Hedef kitleyi tanimliyor, gosteris yok, bilgi ozlu",
                "kaynak": "narrator"
            }
        ],
        "gorsel_prompt": [
            {
                "ornek": "Create a premium product label for a quiet luxury chocolate brand. Minimalist design, ample white space, elegant serif typography. Color palette: dark chocolate brown (#3D2314), cream (#F5F0E8). No flashy elements.",
                "puan": 90,
                "neden_iyi": "Quiet luxury estetigi, teknik detaylar net, kacinilacaklar belirtilmis",
                "kaynak": "curator"
            }
        ],
        "fiyat_analizi": [
            {
                "ornek": "Vakko Chocolate 100g tablet: 280 TL. Sade pozisyonu: Premium segment, karsilastirma endeksi 0.95.",
                "puan": 85,
                "neden_iyi": "Nesnel ton, sayisal veriler net, yorum minimal",
                "kaynak": "pricing"
            }
        ],
        "trend_raporu": [],
        "recete": [
            {
                "ornek": "Tuz kristali aktivasyonu: Fleur de sel, %70 bitter uzerine son dakika serpistrisi. Termal sok yasak - oda sicakliginda birakinca tuz erir, tat dengesi bozulur.",
                "puan": 88,
                "neden_iyi": "Teknik dogru, pratik, 'yasak' acik belirtilmis",
                "kaynak": "alchemist"
            }
        ]
    }

    examples = approved_examples_db.get(icerik_turu, [])

    if not examples:
        return json.dumps({
            "icerik_turu": icerik_turu,
            "ornekler": [],
            "not": f"'{icerik_turu}' icin henuz onaylanmis ornek yok. Ilk onaylanan icerikler benchmark olarak eklenecek."
        }, ensure_ascii=False, indent=2)

    return json.dumps({
        "icerik_turu": icerik_turu,
        "ornek_sayisi": len(examples),
        "ornekler": examples
    }, ensure_ascii=False, indent=2)


__all__ = ["denetle", "stil_kilavuzu_yukle", "onaylanmis_ornekler_yukle"]
