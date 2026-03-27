# Phase 7: The Perfectionist - Context

**Gathered:** 2026-01-30
**Status:** Ready for planning

<domain>
## Phase Boundary

UX denetim agenti - Diğer agentların ürettiği içerikleri (metin, fiyat analizi, trend raporu, reçete, görsel) denetleyerek marka tutarlılığı ve kalite güvence sağlayan agent. İyileştirme önerileri sunar.

</domain>

<decisions>
## Implementation Decisions

### Denetim kapsamı
- Claude hangi agent çıktılarının denetim gerektirdiğine karar verecek
- Claude uygun tetikleme mekanizmasını belirleyecek (otomatik, talep üzerine, batch)
- Claude önceliklendirme mantığını belirleyecek
- Claude uygun saklama stratejisini belirleyecek

### Değerlendirme kriterleri
- Claude uygun ölçüm yöntemini belirleyecek (puan, pass/fail, kategori)
- Claude hangi kalite boyutlarının kritik olduğuna karar verecek
- **Değerlendirme referansı:** Hem style guide (06-01) hem de onaylanmış geçmiş örnekler benchmark olarak kullanılacak
- Claude içerik türüne göre dinamik eşik uygulayacak

### Geri bildirim formatı
- Claude içerik türüne göre uygun rapor formatını seçecek
- **İyileştirme önerileri:** Somut alternatifler sunulacak ("Bunu şöyle değiştir" gibi direkt öneriler)
- **Dil:** Tüm geri bildirimler Türkçe olacak
- **Detay seviyesi:** Önce özet, istenirse detay (talep üzerine)

### Müdahale seviyesi
- Claude sorun ciddiyetine göre müdahale seviyesini belirleyecek
- Claude ciddiyet seviyesine göre davranış belirleyecek (blokaj, uyarı, log)
- Claude uygun iletişim modelini belirleyecek (agentlara feedback, merkezi rapor)
- **Override politikası:** Kullanıcı tam kontrol sahibi - Perfectionist sadece tavsiye verir, kullanıcı istediği çıktıyı onaylayabilir

### Claude's Discretion
- Hangi çıktıların denetim gerektirdiği
- Tetikleme mekanizması (otomatik/manuel/batch)
- Önceliklendirme mantığı
- Ölçüm yöntemi ve kalite boyutları
- Minimum kabul eşiği (içerik türüne göre)
- Rapor formatı (içerik türüne göre)
- Müdahale ve iletişim modeli

</decisions>

<specifics>
## Specific Ideas

- Style guide referansı: `.planning/phases/06-the-curator/06-01-PLAN.md` içindeki "Sessiz Lüks" estetik tanımları
- Mevcut onaylanmış içerikler de benchmark olarak kullanılacak
- Türkçe geri bildirim zorunlu
- Kullanıcı override hakkı korunuyor - agent tavsiye niteliğinde

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 07-the-perfectionist*
*Context gathered: 2026-01-30*
