"""
Sade Agents - The Alchemist Skills.

The Alchemist agent'ın kullandığı skill'ler.
Lezzet eşleştirme, mevsimsel malzemeler ve çikolata bilgisi yetenekleri.
"""

from datetime import datetime

from crewai.tools import tool


# Lezzet eşleştirme verileri (flavor pairing database)
LEZZET_ESLESTIRMELERI = {
    "bitter_cikolata": {
        "klasik": ["portakal", "nane", "kahve", "fındık", "badem"],
        "cesur": ["lavanta", "biberiye", "acı biber", "zeytinyağı", "deniz tuzu"],
        "meyveli": ["ahududu", "vişne", "çilek", "muz", "incir"],
    },
    "sutlu_cikolata": {
        "klasik": ["karamel", "vanilya", "fındık", "hindistancevizi"],
        "cesur": ["tuzlu karamel", "bal", "zencefil", "tarçın"],
        "meyveli": ["muz", "çilek", "şeftali", "kayısı"],
    },
    "beyaz_cikolata": {
        "klasik": ["frambuaz", "limon", "hindistancevizi", "macadamia"],
        "cesur": ["matcha", "gül", "lavanta", "safran"],
        "meyveli": ["mango", "maracuja", "ananas", "kivi"],
    },
    "ruby_cikolata": {
        "klasik": ["frambuaz", "çilek", "limon", "hindistancevizi"],
        "cesur": ["gül", "nar", "hibiskus"],
        "meyveli": ["vişne", "böğürtlen", "yaban mersini"],
    },
}

# Mevsimsel malzeme takvimi
MEVSIMSEL_MALZEMELER = {
    "ocak": ["kestane", "hurma", "portakal", "greyfurt", "nar"],
    "subat": ["kan portakalı", "limon", "kestane", "hurma"],
    "mart": ["çilek (erken)", "limon", "erik (erken)"],
    "nisan": ["çilek", "erik", "kayısı (erken)"],
    "mayis": ["çilek", "kiraz", "kayısı", "erik"],
    "haziran": ["kiraz", "kayısı", "şeftali", "erik"],
    "temmuz": ["şeftali", "kayısı", "böğürtlen", "ahududu", "dut"],
    "agustos": ["şeftali", "üzüm", "incir", "karpuz", "kavun"],
    "eylul": ["incir", "üzüm", "elma", "armut"],
    "ekim": ["elma", "armut", "ayva", "nar"],
    "kasim": ["ayva", "nar", "kestane", "hurma"],
    "aralik": ["kestane", "hurma", "portakal", "tarçın"],
}

# Çikolata çeşitleri ve teknik bilgileri
CIKOLATA_BILGISI = {
    "callebaut_811": {
        "tip": "bitter",
        "kakao": 54.5,
        "notlar": "Dengeli, hafif meyvemsi notlar, çok yönlü",
        "kullanim": "Ganache, pralin, tablet, enrobing",
        "tempering": "31-32°C",
    },
    "callebaut_823": {
        "tip": "sütlü",
        "kakao": 33.6,
        "notlar": "Kremamsı, karamel tonları, yumuşak",
        "kullanim": "Mousse, truffle, dipping",
        "tempering": "29-30°C",
    },
    "callebaut_w2": {
        "tip": "beyaz",
        "kakao_yagi": 28,
        "notlar": "Vanilya, taze süt, kremamsı",
        "kullanim": "Ganache, dekorasyon, karışım",
        "tempering": "27-28°C",
    },
    "callebaut_ruby": {
        "tip": "ruby",
        "notlar": "Doğal pembe renk, hafif meyvemsi ekşilik",
        "kullanim": "Dekorasyon, özel ürünler",
        "tempering": "28-29°C",
    },
    "valrhona_guanaja": {
        "tip": "bitter",
        "kakao": 70,
        "notlar": "Yoğun, meyveli, hafif acı, kompleks",
        "kullanim": "Premium tablet, ganache, tasting",
        "tempering": "31-32°C",
    },
    "valrhona_jivara": {
        "tip": "sütlü",
        "kakao": 40,
        "notlar": "Karamel, malt, bisküvi, dengeli",
        "kullanim": "Pralin, mousse, bonbon",
        "tempering": "29-30°C",
    },
}


def _get_ay_adi() -> str:
    """Şu anki ayın Türkçe adını döner."""
    ay_isimleri = {
        1: "ocak", 2: "subat", 3: "mart", 4: "nisan",
        5: "mayis", 6: "haziran", 7: "temmuz", 8: "agustos",
        9: "eylul", 10: "ekim", 11: "kasim", 12: "aralik",
    }
    return ay_isimleri[datetime.now().month]


def _format_eslestirmeler(cikolata_tipi: str) -> str:
    """Lezzet eşleştirmelerini tablo formatında döner."""
    if cikolata_tipi not in LEZZET_ESLESTIRMELERI:
        valid = ", ".join(LEZZET_ESLESTIRMELERI.keys())
        return f"Bilinmeyen çikolata tipi: {cikolata_tipi}. Geçerli: {valid}"

    eslestirmeler = LEZZET_ESLESTIRMELERI[cikolata_tipi]
    tip_gosterim = cikolata_tipi.replace("_", " ").title()

    lines = [f"## 🍫 {tip_gosterim} Lezzet Eşleştirmeleri\n"]
    lines.append("| Kategori | Malzemeler |")
    lines.append("|----------|------------|")

    for kategori, malzemeler in eslestirmeler.items():
        emoji = {"klasik": "⭐", "cesur": "🌶️", "meyveli": "🍓"}.get(kategori, "")
        malzeme_str = ", ".join(malzemeler)
        lines.append(f"| {emoji} {kategori.title()} | {malzeme_str} |")

    return "\n".join(lines)


def _format_mevsimsel() -> str:
    """Şu anki ayın mevsimsel malzemelerini döner."""
    ay = _get_ay_adi()
    malzemeler = MEVSIMSEL_MALZEMELER.get(ay, [])

    lines = [f"\n## 📅 Mevsimsel Malzemeler ({ay.title()})\n"]

    if malzemeler:
        for malzeme in malzemeler:
            lines.append(f"- {malzeme}")
    else:
        lines.append("- Veri bulunamadı")

    # Bir sonraki ay önerisi
    ay_listesi = list(MEVSIMSEL_MALZEMELER.keys())
    suanki_index = ay_listesi.index(ay)
    sonraki_ay = ay_listesi[(suanki_index + 1) % 12]
    sonraki_malzemeler = MEVSIMSEL_MALZEMELER[sonraki_ay]

    lines.append(f"\n**Gelecek ay ({sonraki_ay.title()}):** {', '.join(sonraki_malzemeler[:3])}...")

    return "\n".join(lines)


def _format_cikolata_bilgisi() -> str:
    """Çikolata çeşitleri hakkında teknik bilgi döner."""
    lines = ["\n## 🎓 Çikolata Teknik Bilgileri\n"]
    lines.append("| Çeşit | Tip | Kakao | Tempering | Kullanım |")
    lines.append("|-------|-----|-------|-----------|----------|")

    for cesit, bilgi in CIKOLATA_BILGISI.items():
        cesit_ad = cesit.replace("_", " ").title()
        tip = bilgi["tip"]
        kakao = bilgi.get("kakao", bilgi.get("kakao_yagi", "-"))
        kakao_str = f"%{kakao}" if kakao != "-" else "-"
        tempering = bilgi.get("tempering", "-")
        kullanim = bilgi.get("kullanim", "-")[:30]
        lines.append(f"| {cesit_ad} | {tip} | {kakao_str} | {tempering} | {kullanim} |")

    return "\n".join(lines)


@tool
def lezzet_pisileri(malzeme: str = "bitter_cikolata", mod: str = "eslestir") -> str:
    """
    Lezzet eşleştirmeleri, mevsimsel malzemeler ve çikolata bilgisi sağlar.

    Bu tool The Alchemist agent'ın lezzet kombinasyonları ve reçete önerileri
    için kullandığı ana bilgi kaynağıdır. Flavor pairing bilimi ve mevsimsellik
    prensiplerini birleştirir.

    Args:
        malzeme: Çikolata tipi veya sorgu. Çikolata tipleri:
                 - "bitter_cikolata" - Bitter/dark chocolate eşleştirmeleri
                 - "sutlu_cikolata" - Sütlü/milk chocolate eşleştirmeleri
                 - "beyaz_cikolata" - Beyaz/white chocolate eşleştirmeleri
                 - "ruby_cikolata" - Ruby chocolate eşleştirmeleri
        mod: İşlem modu. Seçenekler:
             - "eslestir" - Verilen çikolata için lezzet eşleştirmeleri
             - "mevsim" - Şu anki ayın mevsimsel malzemeleri
             - "bilgi" - Çikolata çeşitleri hakkında teknik bilgi
             - "tumu" - Tüm bilgiler (eşleştirme + mevsim + teknik)

    Returns:
        Lezzet raporu: Eşleştirme tabloları, mevsimsel öneriler ve analiz

    Kullanım:
        lezzet_pisileri("bitter_cikolata", "eslestir")  # Bitter eşleştirmeleri
        lezzet_pisileri("sutlu_cikolata", "eslestir")   # Sütlü eşleştirmeleri
        lezzet_pisileri("", "mevsim")                   # Bu ayın malzemeleri
        lezzet_pisileri("", "bilgi")                    # Teknik çikolata bilgisi
        lezzet_pisileri("bitter_cikolata", "tumu")      # Tüm bilgiler
    """
    sections = ["# 🧪 Lezzet Laboratuvarı Raporu\n"]

    if mod == "eslestir":
        sections.append(_format_eslestirmeler(malzeme))
    elif mod == "mevsim":
        sections.append(_format_mevsimsel())
    elif mod == "bilgi":
        sections.append(_format_cikolata_bilgisi())
    elif mod == "tumu":
        sections.append(_format_eslestirmeler(malzeme))
        sections.append(_format_mevsimsel())
        sections.append(_format_cikolata_bilgisi())
    else:
        return f"Bilinmeyen mod: {mod}. Geçerli: eslestir, mevsim, bilgi, tumu"

    # Analiz prompt template
    analiz_template = """

---

## 🎯 REÇETECİ TALİMATLARI

Yukarıdaki lezzet verilerini kullanarak reçete önerileri geliştir:

### 1. Konsept Oluşturma
- Hangi çikolata bazı kullanılacak?
- Ana lezzet profili ne olacak? (klasik/cesur/meyveli)
- Mevsimsel malzemelerden hangisi uygun?

### 2. Kombinasyon Önerisi
Her öneri için:
- **Ana Malzemeler:** Çikolata + 2-3 eşleştirme
- **Neden Çalışır:** Flavor pairing açıklaması
- **Teknik Not:** Tempering, oran, dikkat edilecekler

### 3. Ürün Konsepti
- **İsim Önerisi:** "Sessiz Lüks" markasına uygun
- **Hedef Segment:** Premium/gurme/kurumsal hediye
- **Sezon:** Hangi dönem için ideal

### 4. Üretim Notları
- Couverture seçimi (Callebaut/Valrhona)
- Ganache/pralin oranları
- Raf ömrü değerlendirmesi

---

**NOT:** Bu veriler Sade Chocolate ürün geliştirme referansıdır.
"""

    sections.append(analiz_template)

    return "\n".join(sections)


__all__ = ["lezzet_pisileri"]
