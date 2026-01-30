"""
Sade Agents - The Pricing Analyst Skills.

The Pricing Analyst agent'ın kullandığı skill'ler.
Rekabet istihbaratı ve fiyat analizi yetenekleri.
"""

from crewai.tools import tool


# Mock fiyat verileri (gerçek scraping ileride eklenebilir)
RAKIP_FIYATLARI = {
    "vakko": [
        {"urun": "Vakko Sütlü Tablet", "gramaj": 100, "fiyat": 450, "tl_gram": 4.50},
        {"urun": "Vakko Bitter %70", "gramaj": 100, "fiyat": 480, "tl_gram": 4.80},
        {"urun": "Vakko Fındıklı", "gramaj": 80, "fiyat": 420, "tl_gram": 5.25},
        {"urun": "Vakko Ruby", "gramaj": 85, "fiyat": 520, "tl_gram": 6.12},
    ],
    "butterfly": [
        {"urun": "Butterfly Bitter %55", "gramaj": 80, "fiyat": 320, "tl_gram": 4.00},
        {"urun": "Butterfly Sütlü", "gramaj": 80, "fiyat": 300, "tl_gram": 3.75},
        {"urun": "Butterfly Karamelli", "gramaj": 75, "fiyat": 340, "tl_gram": 4.53},
    ],
    "divan": [
        {"urun": "Divan Fındıklı Tablet", "gramaj": 90, "fiyat": 280, "tl_gram": 3.11},
        {"urun": "Divan Sütlü Tablet", "gramaj": 90, "fiyat": 260, "tl_gram": 2.89},
        {"urun": "Divan Bitter", "gramaj": 85, "fiyat": 270, "tl_gram": 3.18},
    ],
    "baylan": [
        {"urun": "Baylan Klasik Sütlü", "gramaj": 100, "fiyat": 180, "tl_gram": 1.80},
        {"urun": "Baylan Bitter", "gramaj": 100, "fiyat": 200, "tl_gram": 2.00},
    ],
    "marie_antoinette": [
        {"urun": "Marie Antoinette Truffle Box", "gramaj": 120, "fiyat": 850, "tl_gram": 7.08},
        {"urun": "Marie Antoinette Single Origin", "gramaj": 70, "fiyat": 620, "tl_gram": 8.86},
    ],
}


def _format_rakip_verileri(rakip: str) -> str:
    """Rakip verilerini tablo formatında döner."""
    if rakip == "tumu":
        rakipler = list(RAKIP_FIYATLARI.keys())
    elif rakip in RAKIP_FIYATLARI:
        rakipler = [rakip]
    else:
        return f"Bilinmeyen rakip: {rakip}. Geçerli seçenekler: vakko, butterfly, divan, baylan, marie_antoinette, tumu"

    lines = ["## Rakip Fiyat Verileri\n"]
    lines.append("| Rakip | Ürün | Gramaj | Fiyat (TL) | TL/Gram |")
    lines.append("|-------|------|--------|------------|---------|")

    for r in rakipler:
        for urun in RAKIP_FIYATLARI[r]:
            lines.append(
                f"| {r.title()} | {urun['urun']} | {urun['gramaj']}g | {urun['fiyat']} TL | {urun['tl_gram']:.2f} |"
            )

    return "\n".join(lines)


def _hesapla_ozet_istatistikler() -> str:
    """Tüm rakipler için özet istatistikler hesaplar."""
    tum_fiyatlar = []
    for rakip, urunler in RAKIP_FIYATLARI.items():
        for urun in urunler:
            tum_fiyatlar.append({
                "rakip": rakip,
                "urun": urun["urun"],
                "tl_gram": urun["tl_gram"],
            })

    # Sırala
    sirali = sorted(tum_fiyatlar, key=lambda x: x["tl_gram"])
    en_ucuz = sirali[0]
    en_pahali = sirali[-1]

    # Ortalama
    ortalama = sum(x["tl_gram"] for x in tum_fiyatlar) / len(tum_fiyatlar)

    lines = [
        "\n## Özet İstatistikler\n",
        f"- **En ucuz:** {en_ucuz['urun']} ({en_ucuz['rakip'].title()}) - {en_ucuz['tl_gram']:.2f} TL/g",
        f"- **En pahalı:** {en_pahali['urun']} ({en_pahali['rakip'].title()}) - {en_pahali['tl_gram']:.2f} TL/g",
        f"- **Pazar ortalaması:** {ortalama:.2f} TL/g",
    ]

    return "\n".join(lines)


@tool
def fiyat_kontrol(rakip: str = "tumu") -> str:
    """
    Rakip çikolata markalarının fiyatlarını kontrol eder ve analiz için veri sağlar.

    Bu tool premium çikolata pazarındaki rakiplerin fiyatlarını TL/gram bazında
    karşılaştırır. Şu anda mock veriler kullanıyor, ileride gerçek web scraping
    ile güncellenebilir.

    Args:
        rakip: Kontrol edilecek rakip. Seçenekler:
               - "vakko" - Vakko Chocolate
               - "butterfly" - Butterfly Chocolate
               - "divan" - Divan
               - "baylan" - Baylan
               - "marie_antoinette" - Marie Antoinette (Zorlu)
               - "tumu" (default) - Tüm rakipler

    Returns:
        Rakip fiyat raporu: TL/gram bazında karşılaştırma tablosu ve analiz prompt'u

    Kullanım:
        fiyat_kontrol()  # Tüm rakipler
        fiyat_kontrol("vakko")  # Sadece Vakko
    """
    # Fiyat verilerini formatla
    veri_tablosu = _format_rakip_verileri(rakip)

    # Özet istatistikler
    if rakip == "tumu":
        ozet = _hesapla_ozet_istatistikler()
    else:
        ozet = ""

    # Analiz prompt template
    prompt_template = f"""
{veri_tablosu}
{ozet}

---

## ANALİZ TALİMATLARI

Yukarıdaki rakip fiyat verilerini analiz et ve şu soruları yanıtla:

### 1. Pazar Konumlandırması
- Premium segment (>5 TL/g): Hangi rakipler?
- Orta segment (3-5 TL/g): Hangi rakipler?
- Ekonomik segment (<3 TL/g): Hangi rakipler?

### 2. Sade İçin Öneriler
Sade Chocolate'ın hedefi:
- TL/gram: 4.50-5.50 TL arası
- Marka primi: 1.5x (Hammadde + Lojistik + Ambalaj)
- Pozisyon: Premium ama en pahalı değil

Bu verilere göre:
- Sade hangi rakiplerle doğrudan rekabet ediyor?
- Önerilen fiyat aralığı ne olmalı?
- Zam/indirim yapılmalı mı?

### 3. Dikkat Edilecek Sinyaller
- Vakko zam yaptı mı? (Referans fiyat değişimi)
- Yeni ürün lansmanları var mı?
- Fiyat savaşı riski var mı?

---

**NOT:** Bu veriler mock verilerdir. Gerçek fiyatlar için web sitelerini kontrol edin.
"""

    return prompt_template


__all__ = ["fiyat_kontrol"]
