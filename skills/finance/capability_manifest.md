# Finance Skills Manifest (Finansal Yetenekler)
*Bu klasör, Pricing Analyst ve CFO ajanlarının kullanacağı hesaplama araçlarını içerir.*

## 1. Competitor Watchdog (Rakip Gözcüsü)
- **Hedef:** Vakko, Butterfly, Marie Antoinette (Zorlu), Baylan ve Divan fiyatlarını anlık takip etmek.
- **Mekanik:**
    - `Web Scraper`: Hedef sitelerden "Ürün Adı", "Gramaj" ve "Fiyat" verisini çeker.
    - `Web Scraper`: Hedef sitelerden "Ürün Adı", "Gramaj" ve "Fiyat" verisini çeker.
    - `Unit_Converter`: Tüm fiyatları ortak paydaya (TL/Gram) dönüştürür.
- **Tetikleyici (Trigger):**
    - ⏰ **Her Sabah 09:00'da** otomatik çalışır.
    - 🚨 **Acil Durum:** Dolar kuru %5 oynarsa anında çalışır.
    - 🗣️ **Sihirli Kelime:** `/fiyat_kontrol` veya *"Rakipler ne alemde?"*

## 2. Dynamic Pricing Engine (Dinamik Fiyat Motoru)
- **Hedef:** Kar marjını koruyarak en rekabetçi fiyatı önermek.
- **Formül:** `(Hammadde + Lojistik + Ambalaj) * 1.5 (Marka Primi) = Satış Fiyatı`.
- **Formül:** `(Hammadde + Lojistik + Ambalaj) * 1.5 (Marka Primi) = Satış Fiyatı`.
- **Girdi:** Callebaut ve Fıstık borsası verileri (API veya manuel güncelleme).
- **Tetikleyici (Trigger):**
    - 🔄 **Rakip Gözcüsü** (Competitor Watchdog) raporda "Vakko Zam Yaptı" dediği an çalışır.
    - 🗣️ **Sihirli Kelime:** `/fiyat_hesapla` veya *"Bunu kaça satmalıyız?"*

## 3. Margin Protector (Kar Koruyucu)
- **Hedef:** Fıstık fiyatı artınca alarm vermek.
- **Hedef:** Fıstık fiyatı artınca alarm vermek.
- **Mekanik:** `Trigger`: Eğer hammadde maliyeti %10 artarsa, yöneticiye "Zam yapalım mı?" bildirimi gönderir.
- **Tetikleyici (Trigger):**
    - 📦 **Stok Girişi Yapıldığında:** Yeni fıstık faturası sisteme girildiğinde maliyeti yeniden hesaplar.
    - 🗣️ **Sihirli Kelime:** `/maliyet_analizi` veya *"Hala karda mıyız?"*
