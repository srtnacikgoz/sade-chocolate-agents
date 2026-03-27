# Phase 6: The Curator - Context

**Gathered:** 2026-01-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Görsel tasarım agenti — ürün etiketleri tasarımı. Gemini 3 Pro ile varyasyon tabanlı görsel üretim, Figma entegrasyonu, ve görsel stil kılavuzu oluşturma. v1'de sadece etiket tasarımı, sosyal medya ve ambalaj mockup'ları kapsam dışı.

</domain>

<decisions>
## Implementation Decisions

### Görsel Üretim Yaklaşımı
- **AI Aracı:** Gemini 3 Pro (API erişimi mevcut)
- **Workflow:** Varyasyon tabanlı — önce 3-4 varyasyon üret, seçileni geliştir
- **Template Sistemi:** Figma entegrasyonu (Claude en pratik yöntemi belirleyecek)
- **Üretim Odağı:** Sadece ürün etiketleri (v1 kapsamı)
- **Input:** Ürün bilgisi (ad, lezzet, içerik) → etiket çıktısı
- **Stil Tutarlılığı:** Style guide dosyası (bu fazda oluşturulacak)

### Tasarım Çıktı Formatları
- **Boyutlar:** Sade'nin standart ürün boyutları (planlama sırasında iletilecek)
- **Dosya Formatları:** PNG, SVG, PDF (tüm formatlar)
- **Depolama:** Lokal klasör (outputs/ veya benzeri)
- **Adlandırma:** Ürün bazlı (örn: antep-fistikli-50g-v1.png)

### Marka Görsel Standartları
- **Renk Paleti:** Bu fazda oluşturulacak (Claude "Sessiz Lüks" konseptine uygun palette önerecek)
- **Tipografi:** Mevcut font var (planlama sırasında font adı iletilecek)
- **Style Guide:** İlk görev olarak oluşturulacak, tüm üretimlerde referans olacak

### Onay ve Revizyon Süreci
- **Otonomi Seviyesi:** Her zaman onay (supervised)
- **Revizyon Yöntemi:** Claude en pratik yaklaşımı belirleyecek
- **Revizyon Limiti:** Sınırsız — memnun olana kadar
- **Arşivleme:** Versiyon kontrolü ile (v1, v2... tüm onaylanan versiyonlar saklanır)

### Claude's Discretion
- Figma entegrasyon yöntemi (API, export/import, veya referans)
- Prompt engineering yaklaşımı (Narrator entegrasyonu veya ayrı görsel dil kılavuzu)
- Metin/yazı stratejisi (AI üretimi, sonradan ekleme, veya ayrı katman)
- Revizyon feedback formatı (yazılı, seçenek bazlı, veya hybrid)

</decisions>

<specifics>
## Specific Ideas

- "Sessiz Lüks" (Quiet Luxury) felsefesi görsel dile yansımalı
- Etiketler Monocle/Kinfolk estetiğini yansıtmalı — sofistike, understated
- Vakko, Butterfly gibi premium Türk markalarıyla rekabet edebilir görsel kalite

</specifics>

<deferred>
## Deferred Ideas

- Sosyal medya görselleri — gelecek faz veya v2
- Ambalaj mockup'ları (3D kutu/paket) — gelecek faz veya v2
- Ürün fotoğrafları (product shot) — kapsam dışı

</deferred>

---

*Phase: 06-the-curator*
*Context gathered: 2026-01-30*
