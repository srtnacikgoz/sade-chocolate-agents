# Roadmap: Sade Chocolate Agents

## Overview

Sade Chocolate için AI destekli iş operasyonları multi-agent sistemi. Temel altyapıdan başlayarak 7 uzman agent (Narrator, Pricing Analyst, Growth Hacker, Alchemist, Curator, Perfectionist) ve bunların skill'lerini inşa edip, orkestrasyon katmanı ile birleştirerek günlük iş akışına entegre edeceğiz.

## Domain Expertise

None

## Phases

**Faz Numaralandırma:**
- Tam sayı fazlar (1, 2, 3): Planlı milestone çalışması
- Ondalık fazlar (2.1, 2.2): Acil eklemeler (INSERTED ile işaretli)

- [x] **Phase 1: Temel Altyapı** - Python + CrewAI çekirdek framework kurulumu (3/3 plan complete) ✅
- [x] **Phase 2: The Narrator** - Marka sesi agenti ve skill'leri (2/2 plan complete) ✅
- [x] **Phase 3: The Pricing Analyst** - Rekabet istihbaratı agenti ve skill'leri (3/3 plan complete) ✅
- [x] **Phase 4: The Growth Hacker** - Trend takip agenti ve skill'leri (1/1 plan complete) ✅
- [x] **Phase 5: The Alchemist** - Lezzet/reçete agenti ve skill'leri (1/1 plan complete) ✅
- [x] **Phase 6: The Curator** - Görsel tasarım agenti ve skill'leri (3/3 plan complete) ✅
- [ ] **Phase 7: The Perfectionist** - UX denetim agenti ve skill'leri
- [ ] **Phase 8: Orkestrasyon** - Chief Architect rolü, agent'lar arası iletişim
- [ ] **Phase 9: Entegrasyon** - Günlük iş akışına dahil etme

## Phase Details

### Phase 1: Temel Altyapı
**Goal**: Python + CrewAI çekirdek framework kurulumu, proje yapısı, temel agent sınıfları
**Depends on**: Nothing (first phase)
**Research**: Likely (CrewAI kurulumu, agent mimari kalıpları)
**Research topics**: CrewAI best practices, agent base class patterns, project structure conventions
**Plans**: TBD

### Phase 2: The Narrator
**Goal**: Marka sesi agenti - "Sessiz Lüks" tonunda içerik üretimi, Monocle/Kinfolk editorial voice
**Depends on**: Phase 1
**Research**: Unlikely (marka sesi zaten belgelenmiş, iç prompt tasarımı)
**Plans**: TBD

### Phase 3: The Pricing Analyst
**Goal**: Rekabet istihbaratı agenti - Vakko, Butterfly gibi rakiplerin fiyat takibi ve analizi
**Depends on**: Phase 1
**Research**: Likely (web scraping araçları, rakip fiyat veri kaynakları)
**Research topics**: Web scraping kütüphaneleri (BeautifulSoup, Playwright), Türk premium çikolata markası web siteleri, fiyat karşılaştırma yaklaşımları
**Plans**: TBD

### Phase 4: The Growth Hacker
**Goal**: Trend takip agenti - Pazar fırsatları, sosyal medya trendleri, büyüme önerileri
**Depends on**: Phase 1
**Research**: Likely (trend izleme yaklaşımları, veri kaynakları)
**Research topics**: Trend API'leri, sosyal medya analiz araçları, Türkiye pazarı veri kaynakları
**Plans**: TBD

### Phase 5: The Alchemist
**Goal**: Lezzet/reçete agenti - Çikolata trendleri, yeni reçete önerileri, malzeme kombinasyonları
**Depends on**: Phase 1
**Research**: Unlikely (alan bilgisi mevcut, Callebaut 811/823, tempering chemistry)
**Plans**: TBD

### Phase 6: The Curator
**Goal**: Görsel tasarım agenti - Gemini 3 Pro ile varyasyon tabanlı ürün etiketi tasarımı, "Sessiz Lüks" estetikli görsel üretim
**Depends on**: Phase 1
**Research**: Complete (Gemini 3 Pro Image API, style guide yaklaşımı)
**Plans**: 3 plans (3/3 complete)
Plans:
- [x] 06-01-PLAN.md — Style guide ve referans yapılandırması ✅
- [x] 06-02-PLAN.md — Curator skills (gorsel_tasarla) ✅
- [x] 06-03-PLAN.md — CuratorAgent ve run scripti ✅

### Phase 7: The Perfectionist
**Goal**: UX denetim agenti - Marka tutarlılığı kontrolü, kalite güvence, iyileştirme önerileri
**Depends on**: Phase 1
**Research**: Unlikely (denetim kalıpları, iç araçlar)
**Plans**: TBD

### Phase 8: Orkestrasyon
**Goal**: Chief Architect rolü - Agent'lar arası iletişim, görev dağıtımı, workflow koordinasyonu
**Depends on**: Phases 2-7
**Research**: Likely (CrewAI multi-agent koordinasyon kalıpları)
**Research topics**: CrewAI crew orchestration, agent communication patterns, task delegation strategies
**Plans**: TBD

### Phase 9: Entegrasyon
**Goal**: Günlük iş akışına dahil etme - CLI araçları, dokümantasyon, kullanım kılavuzları
**Depends on**: Phase 8
**Research**: Unlikely (iç iş akışı, dokümantasyon)
**Plans**: TBD

## Progress

**Execution Order:**
Fazlar numerik sırada çalışır: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9
(Not: Phase 2-7 bağımsız olabilir, paralel çalışılabilir)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Temel Altyapı | 3/3 | Complete | 2026-01-30 |
| 2. The Narrator | 2/2 | Complete | 2026-01-30 |
| 3. The Pricing Analyst | 3/3 | Complete | 2026-01-30 |
| 4. The Growth Hacker | 1/1 | Complete | 2026-01-30 |
| 5. The Alchemist | 1/1 | Complete | 2026-01-30 |
| 6. The Curator | 3/3 | Complete | 2026-01-30 |
| 7. The Perfectionist | 0/TBD | Not started | - |
| 8. Orkestrasyon | 0/TBD | Not started | - |
| 9. Entegrasyon | 0/TBD | Not started | - |
