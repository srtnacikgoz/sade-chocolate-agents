# Skills Architecture: The "Brain" and "Muscle" Model
*Bu klasördeki 'Skill'ler (Yetenekler) sadece metin değil, kodlanacak Python araçlarının taslağıdır.*

## 1. Analoji: Şef ve Bıçağı
Bu sistemi bir **Profesyonel Mutfak** gibi düşünebilirsin:
- **Agent (Ajan):** **Şef**. Karar verir, plan yapar, tadına bakar. (Örn: "Bu sos çok tatlı oldu, biraz asit lazım.")
- **Skill (Yetenek):** **Blender veya Bıçak**. Düşünmez, sadece işi yapar. (Örn: "Domatesleri 2 saniyede püre haline getir.")

## 2. Teknik Uygulama (Nasıl Çalışıyor?)
Biz `Phase 1` kodlama aşamasına geçtiğimizde, buradaki her bir "Skill" maddesi bir **Python Fonksiyonuna** dönüşecek.

### Örnek Senaryo: Fiyat Analisti
**Adım 1 (Agent Düşünür):**
*"Patron benden Vakko'nun fiyatlarını kontrol etmemi istedi. Bunun için `Competitor_Watchdog` yeteneğine ihtiyacım var."*

**Adım 2 (Skill Çalışır):**
*   **Skill:** `def scrape_vakko_price(url):`
*   Bu kod parçası Vakko.com'a gider, HTML kodlarını tarar, `1.450 TL` fiyatını bulur ve geri döner.

**Adım 3 (Agent Karar Verir):**
*"Gelen veri 1.450 TL. Geçen hafta 1.300 TL idi. Demek ki %15 zam gelmiş. Bunu hemen rapora eklemeliyim."*

## 3. Neden Ayırdık? (Modülerlik)
- **Güvenlik:** Ajanın kafasına göre her siteye girmesini engelleriz. Sadece tanımlı (Skill) araçları kullanabilir.
- **Güncellenebilirlik:** Yarın Vakko sitesini değiştirirse, Ajanı baştan eğitmeyiz. Sadece `scrape_vakko` skill kodunu güncelleriz. Ajan çalışmaya devam eder.

---
**Özet:**
Klasörlerdeki `capability_manifest.md` dosyaları, yazılımcı (ben) için bir **"Fonksiyon Listesi"**dir. Kodlamaya başladığımızda bu listeyi tek tek `python` dosyalarına (`tools.py`) çevireceğiz.
