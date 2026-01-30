# Sade Agents

Sade Chocolate için AI destekli iş operasyonları multi-agent sistemi.

## Genel Bakış

6 uzman agent ve 3 orkestrasyon crew'u ile çikolata markası operasyonlarını destekler.

### Agents

| Agent | Rol | Departman | Otonomi |
|-------|-----|-----------|---------|
| The Narrator | Marka sesi, içerik üretimi | Marketing | Autonomous |
| The Pricing Analyst | Rakip fiyat takibi | Finance | Supervised |
| The Growth Hacker | Trend analizi | Marketing | Autonomous |
| The Alchemist | Lezzet/reçete önerileri | Product | Autonomous |
| The Curator | Görsel tasarım | Product | Autonomous |
| The Perfectionist | Kalite denetimi | Operations | Supervised |

### Crews (Multi-Agent Workflows)

| Crew | Pipeline | Kullanım |
|------|----------|----------|
| ProductLaunchCrew | Alchemist → Narrator → Curator → Perfectionist | Yeni ürün lansmanı |
| MarketAnalysisCrew | PricingAnalyst → GrowthHacker → Narrator | Pazar analizi |
| QualityAuditCrew | Perfectionist | İçerik denetimi |

## Kurulum

```bash
# Repository'yi klonla
git clone https://github.com/srtnacikgoz/sade-chocolate-agents.git
cd sade-chocolate-agents

# Virtual environment oluştur
python3 -m venv .venv
source .venv/bin/activate

# Bağımlılıkları kur
pip install -e ".[dev]"

# API key'i ayarla
cp .env.example .env
# .env dosyasına OPENAI_API_KEY ekle
```

## Hızlı Başlangıç

```bash
# Sistem kontrolü (API çağrısı yapmaz)
python scripts/run_crews.py --dry-run

# Tek bir agent çalıştır
python scripts/run_narrator.py --dry-run
python scripts/run_narrator.py --content "Yeni çikolata tanıtımı"

# Crew workflow çalıştır
python scripts/run_crews.py product-launch --flavor "Antep Fıstıklı Bitter"
python scripts/run_crews.py market-analysis --competitor "Vakko"
python scripts/run_crews.py quality-audit --content "İçerik metni" --content-type metin
```

## Detaylı Kullanım

Detaylı kullanım rehberi için: [docs/USAGE.md](docs/USAGE.md)

## Proje Yapısı

```
sade-chocolate-agents/
├── src/sade_agents/
│   ├── agents/          # 6 uzman agent
│   ├── skills/          # Agent yetenekleri (tools)
│   ├── crews/           # Multi-agent workflows
│   └── models/          # Pydantic modelleri
├── scripts/             # CLI çalıştırma scriptleri
├── style_guide/         # Marka görsel rehberi
└── outputs/             # Üretilen çıktılar
```

## Agent Detayları

### The Narrator
Sade Chocolate'ın marka sesini temsil eder. Minimal, sofistike ve beklenmedik içerikler üretir. Tüm pazarlama içeriklerinin birincil kaynağıdır.

### The Pricing Analyst
Rakip fiyatlarını takip eder ve karşılaştırmalı raporlar sunar. Fiyat önerileri için kullanıcı onayı gerektirir (supervised autonomy).

### The Growth Hacker
Sosyal medya trendlerini ve sektör dinamiklerini analiz eder. Trend raporları otomatik üretilir (autonomous).

### The Alchemist
Yeni lezzet kombinasyonları ve reçete önerileri sunar. Sezonluk koleksiyonlar için yaratıcı fikirler üretir.

### The Curator
Ürün etiketleri ve görsel tasarım üretir. Quiet luxury estetiği ile marka görsel kimliğini korur.

### The Perfectionist
Tüm içerikleri marka rehberine göre denetler. LLM-as-Judge pattern ile kalite kontrolü sağlar.

## Crew Detayları

### ProductLaunchCrew
Yeni ürün lansmanı için uçtan uca workflow:
1. **Alchemist:** Lezzet profili ve reçete önerisi
2. **Narrator:** Ürün açıklaması ve pazarlama metni
3. **Curator:** Etiket tasarımı
4. **Perfectionist:** Final kalite denetimi

### MarketAnalysisCrew
Pazar ve rakip analizi:
1. **PricingAnalyst:** Rakip fiyat karşılaştırması
2. **GrowthHacker:** Trend ve fırsat analizi
3. **Narrator:** Özet rapor

### QualityAuditCrew
İçerik denetimi:
1. **Perfectionist:** Marka rehberine uygunluk kontrolü

## Lisans

Proprietary - Sade Chocolate
