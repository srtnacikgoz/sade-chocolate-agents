# Operations Skills Manifest (Operasyonel Yetenekler)
*Bu klasör, Lojistik ve The Perfectionist ajanlarının kullanacağı denetim araçlarını içerir.*

## 1. Night Shipping Logic (Gece Sevkiyat Mantığı)
- **Hedef:** Kargoların erimeden gitmesini sağlamak.
- **Mekanik:**
    - `Weather_API`: Teslimat adresindeki hava sıcaklığını kontrol eder.
    - `Weather_API`: Teslimat adresindeki hava sıcaklığını kontrol eder.
    - `Decision_Tree`: Sıcaklık > 25°C ise -> "VIP Soğuk Zincir" veya "Erteleme" önerir. < 20°C ise -> "Standart Kargo".
- **Tetikleyici (Trigger):**
    - 🛒 **Her Siparişte:** Müşteri "Ödeme Yap" dediği saniye çalışır.
    - 🗣️ **Sihirli Kelime:** `/kargo_kontrol` veya *"Antalya şu an kaç derece?"*

## 2. Stock Alert System (Stok Bekçisi)
- **Hedef:** "Yok satmayı" yönetmek (Scarcity Marketing).
- **Mekanik:**
    - Stok 10 adedin altına düşünce siteye "Son 10 Ürün!" etiketi basar.
    - Stok 10 adedin altına düşünce siteye "Son 10 Ürün!" etiketi basar.
    - Stok bitince "Bekleme Listesine Katıl" modülünü aktif eder.
- **Tetikleyici (Trigger):**
    - ⚡ **Real-time:** Veritabanında (Stok < 10) olayı gerçekleştiği an.

## 3. The Perfectionist Eye (Mükemmeliyetçi Göz)
- **Hedef:** Siteyi denetlemek.
- **Mekanik:**
    - `Broken_Link_Checker`: Sitedeki kırık linkleri tarar.
    - `Broken_Link_Checker`: Sitedeki kırık linkleri tarar.
    - `UX_Auditor`: Sayfa açılış hızlarını (Lighthouse) ölçer ve raporlar.
- **Tetikleyici (Trigger):**
    - 🌙 **Her Gece 03:00:** Müşteri yokken siteyi tarar, sabah 08:00'de raporu masaya koyar.
    - 🗣️ **Sihirli Kelime:** `/denetle` veya *"Sitede hata var mı?"*
