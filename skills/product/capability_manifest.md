# Product Skills Manifest (Ürün Geliştirme Yetenekleri)
*Bu klasör, The Alchemist (Baş Şef) ajanının kullanacağı yaratıcı araçları içerir.*

## 1. Flavor Matrix (Lezzet Matrisi)
- **Hedef:** Bilimsel olarak uyumlu gıdaları eşleştirmek.
- **Mekanik:**
    - `Pairing_Algorithm`: "Çilek verdiysem yanına ne gider?" sorusuna "Balzamik Sirke" veya "Karabiber" cevabını veren veritabanı.
    - `Pairing_Algorithm`: "Çilek verdiysem yanına ne gider?" sorusuna "Balzamik Sirke" veya "Karabiber" cevabını veren veritabanı.
    - `Seasonality_Checker`: O ay hangi meyvenin mevsimi olduğunu kontrol eder (Örn: "Ocak ayında Kestane kullan").
- **Tetikleyici (Trigger):**
    - 🗓️ **Aylık (Her Ayın 1'i):** Gelecek ayın mevsimsel ürünlerini raporlar.
    - 🗣️ **Sihirli Kelime:** `/eslesme` veya *"Bunun yanına ne gider?"*

## 2. Menu Scout (Menü Ajanı)
- **Hedef:** Michelin yıldızlı restoranların tatlı menülerini analiz etmek.
- **Mekanik:**
    - Dünyanın en iyi 50 restoranının web sitesini tarar.
    - Ortak kelimeleri bulur (Örn: Herkes "Yuzu" kullanmaya başladıysa bu bir sinyaldir).

## 3. Reddit Trend Listener
- **Hedef:** `r/AskCulinary` ve `r/Pastry` sublarını dinlemek.
- **Mekanik:** Profesyonel şeflerin tartıştığı teknik sorunları ve yeni keşfedilen teknikleri raporlar.

## 4. Label Wizard (Etiket Sihirbazı)
*The Curator Ajanı için*
- **Hedef:** Okuyan bilgilenmeli, gören büyülenmeli.
- **Mekanik:**
    - `Info_Architect`: Ürün içeriğini (Fındık, Bal, Krema) hiyerarşik dizer. Alerjenleri şık bir ikonla belirtir.
    - `Aesthetic_Renderer`: "Dall-E 3" veya "Midjourney" promptları üreterek etiketin arka planına ürünün aromasını (Örn: Dumanlı isli doku) yansıtan soyut sanat eserleri çizer.
- **Tetikleyici (Trigger):**
    - 🎨 **On Demand:** Yeni reçete onaylandığı an çalışır.
    - 🗣️ **Sihirli Kelime:** `/etiket_tasarla` veya *"Vitrini hazırla."*
