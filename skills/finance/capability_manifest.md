# Finance Skills Manifest (Finansal Yetenekler)
*Bu klasör, Pricing Analyst ve CFO ajanlarının kullanacağı hesaplama araçlarını içerir.*

## 1. Competitor Watchdog (Rakip Gözcüsü)
- **Hedef:** Vakko, Butterfly ve Läderach fiyatlarını anlık takip etmek.
- **Mekanik:**
    - `Web Scraper`: Hedef sitelerden "Ürün Adı", "Gramaj" ve "Fiyat" verisini çeker.
    - `Unit_Converter`: Tüm fiyatları ortak paydaya (TL/Gram) dönüştürür.

## 2. Dynamic Pricing Engine (Dinamik Fiyat Motoru)
- **Hedef:** Kar marjını koruyarak en rekabetçi fiyatı önermek.
- **Formül:** `(Hammadde + Lojistik + Ambalaj) * 1.5 (Marka Primi) = Satış Fiyatı`.
- **Girdi:** Callebaut ve Fıstık borsası verileri (API veya manuel güncelleme).

## 3. Margin Protector (Kar Koruyucu)
- **Hedef:** Fıstık fiyatı artınca alarm vermek.
- **Mekanik:** `Trigger`: Eğer hammadde maliyeti %10 artarsa, yöneticiye "Zam yapalım mı?" bildirimi gönderir.
