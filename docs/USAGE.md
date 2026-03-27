# Sade Agents Kullanım Rehberi

## İçindekiler

1. [Gereksinimler](#gereksinimler)
2. [Agent'ları Tek Tek Çalıştırma](#agentları-tek-tek-çalıştırma)
3. [Crew Workflow'ları](#crew-workflowları)
4. [Örnek Senaryolar](#örnek-senaryolar)
5. [Sorun Giderme](#sorun-giderme)

## Gereksinimler

- Python 3.11+
- OpenAI API key (GPT-4 erişimi)
- Gemini API key (görsel üretim için, opsiyonel)

### Ortam Değişkenleri

`.env` dosyasında aşağıdaki değişkenleri ayarlayın:

```bash
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...  # Opsiyonel, Curator için
```

## Agent'ları Tek Tek Çalıştırma

Her agent için ayrı CLI script'i mevcuttur. `--dry-run` flag'i ile API çağrısı yapmadan test edebilirsiniz.

### The Narrator - Marka Sesi

Sade Chocolate'ın marka sesini temsil eder. Minimal, sofistike içerikler üretir.

```bash
# Dry-run (API çağrısı yapmaz)
python3 scripts/run_narrator.py --dry-run

# İçerik üret
python3 scripts/run_narrator.py --content "Yeni sezonluk çikolata koleksiyonu"

# Dosyadan içerik oku
python3 scripts/run_narrator.py --file input.txt
```

**Çıktı:** Marka sesine uygun pazarlama içeriği

### The Pricing Analyst - Fiyat Takibi

Rakip fiyatlarını takip eder ve karşılaştırmalı raporlar sunar.

```bash
# Dry-run
python3 scripts/run_pricing_analyst.py --dry-run

# Rakip analizi
python3 scripts/run_pricing_analyst.py --competitor "Vakko"

# Çoklu rakip
python3 scripts/run_pricing_analyst.py --competitor "Vakko" --competitor "Kahve Dünyası"
```

**Çıktı:** Fiyat karşılaştırma raporu (supervised - öneri sunar, kullanıcı onaylar)

### The Growth Hacker - Trend Analizi

Sosyal medya trendlerini ve sektör dinamiklerini analiz eder.

```bash
# Dry-run
python3 scripts/run_growth_hacker.py --dry-run

# Platform bazlı analiz
python3 scripts/run_growth_hacker.py --platform instagram
python3 scripts/run_growth_hacker.py --platform tiktok

# Genel trend analizi
python3 scripts/run_growth_hacker.py
```

**Çıktı:** Trend raporu (autonomous - otomatik üretilir)

### The Alchemist - Lezzet Önerileri

Yeni lezzet kombinasyonları ve reçete önerileri sunar.

```bash
# Dry-run
python3 scripts/run_alchemist.py --dry-run

# Sezon bazlı öneri
python3 scripts/run_alchemist.py --season summer
python3 scripts/run_alchemist.py --season winter

# Malzeme bazlı öneri
python3 scripts/run_alchemist.py --ingredient "antep fıstığı"
```

**Çıktı:** Lezzet profili ve reçete önerisi

### The Curator - Görsel Tasarım

Ürün etiketleri ve görsel tasarım üretir. Quiet luxury estetiği kullanır.

```bash
# Dry-run
python3 scripts/run_curator.py --dry-run

# Etiket tasarımı
python3 scripts/run_curator.py --product "Ruby Çikolata" --style minimal

# Farklı stiller
python3 scripts/run_curator.py --product "Badem Pralin" --style elegant
python3 scripts/run_curator.py --product "Portakal Bitter" --style bold
```

**Çıktı:** Etiket görseli (outputs/ dizinine kaydedilir)

### The Perfectionist - Kalite Denetimi

Tüm içerikleri marka rehberine göre denetler.

```bash
# Dry-run
python3 scripts/run_perfectionist.py --dry-run

# Metin denetimi
python3 scripts/run_perfectionist.py --content "Denetlenecek metin" --type metin

# Görsel denetimi
python3 scripts/run_perfectionist.py --file image.png --type gorsel

# İnteraktif mod
python3 scripts/run_perfectionist.py --interactive
```

**Çıktı:** Kalite raporu (supervised - öneriler sunar, kullanıcı onaylar)

## Crew Workflow'ları

Crew'lar birden fazla agent'ı sıralı olarak çalıştırır. CrewAI Sequential Process kullanır.

### Genel Kullanım

```bash
# Mevcut crew'ları listele
python3 scripts/run_crews.py --help

# Dry-run (tüm crew'lar için)
python3 scripts/run_crews.py --dry-run
```

### Product Launch Crew

Yeni ürün lansmanı için komple workflow.

**Pipeline:** Alchemist → Narrator → Curator → Perfectionist

```bash
# Temel kullanım
python3 scripts/run_crews.py product-launch --flavor "Antep Fıstıklı Bitter"

# Tam parametre seti
python3 scripts/run_crews.py product-launch \
  --flavor "Antep Fıstıklı Bitter" \
  --audience "Premium segment" \
  --price-min 120 \
  --price-max 180 \
  --season winter

# Dry-run
python3 scripts/run_crews.py product-launch --flavor "Test" --dry-run
```

**Çıktı:**
- Lezzet profili (Alchemist)
- Ürün açıklaması (Narrator)
- Etiket tasarımı (Curator)
- Kalite raporu (Perfectionist)

### Market Analysis Crew

Pazar ve rakip analizi.

**Pipeline:** PricingAnalyst → GrowthHacker → Narrator

```bash
# Temel kullanım
python3 scripts/run_crews.py market-analysis --competitor "Vakko"

# Kategori belirterek
python3 scripts/run_crews.py market-analysis \
  --competitor "Vakko" \
  --category "premium chocolate"

# Çoklu rakip
python3 scripts/run_crews.py market-analysis \
  --competitor "Vakko" \
  --competitor "Kahve Dünyası"
```

**Çıktı:**
- Fiyat karşılaştırması (PricingAnalyst)
- Trend analizi (GrowthHacker)
- Özet rapor (Narrator)

### Quality Audit Crew

İçerik kalite denetimi.

**Pipeline:** Perfectionist (tek agent)

```bash
# Metin denetimi
python3 scripts/run_crews.py quality-audit \
  --content "Denetlenecek içerik" \
  --content-type metin \
  --source narrator

# Dosyadan denetim
python3 scripts/run_crews.py quality-audit \
  --file content.txt \
  --content-type metin

# Görsel denetimi
python3 scripts/run_crews.py quality-audit \
  --file label.png \
  --content-type gorsel
```

**Çıktı:**
- Kalite skoru (0-100)
- Marka uyumu değerlendirmesi
- İyileştirme önerileri

## Örnek Senaryolar

### Senaryo 1: Yeni Sezon Ürünü Lansmanı

```bash
# 1. Önce lezzet önerisi al
python3 scripts/run_alchemist.py --season winter

# 2. Beğendiğiniz lezzet için tam workflow çalıştır
python3 scripts/run_crews.py product-launch \
  --flavor "Karamel Tuzlu Badem" \
  --audience "Premium segment" \
  --season winter
```

### Senaryo 2: Rakip Takibi

```bash
# Haftalık rakip analizi
python3 scripts/run_crews.py market-analysis \
  --competitor "Vakko" \
  --competitor "Kahve Dünyası" \
  --category "premium chocolate"
```

### Senaryo 3: İçerik Kalite Kontrolü

```bash
# Instagram postu için denetim
python3 scripts/run_crews.py quality-audit \
  --content "Çikolatanın en saf hali, beklenmedik." \
  --content-type metin \
  --source narrator

# Etiket görseli için denetim
python3 scripts/run_crews.py quality-audit \
  --file outputs/label_ruby.png \
  --content-type gorsel
```

### Senaryo 4: Hızlı İçerik Üretimi

```bash
# Sadece metin gerekiyorsa Narrator'ı tek başına kullan
python3 scripts/run_narrator.py --content "Valentine's Day koleksiyonu tanıtımı"
```

## Sorun Giderme

### API Key Hatası

```
❌ HATA: OPENAI_API_KEY gerekli!
```

**Çözüm:**
1. `.env.example` dosyasını `.env` olarak kopyalayın
2. `OPENAI_API_KEY=sk-...` ekleyin
3. API key'in GPT-4 erişimi olduğundan emin olun

### Import Hatası

```
ModuleNotFoundError: No module named 'sade_agents'
```

**Çözüm:**
```bash
# Virtual environment aktif mi?
source .venv/bin/activate

# Paket kurulu mu?
pip install -e ".[dev]"

# Test et
python3 scripts/run_crews.py --dry-run
```

### Crew Çalışmıyor

1. Virtual environment aktif mi?
   ```bash
   source .venv/bin/activate
   ```

2. Paket kurulu mu?
   ```bash
   pip install -e ".[dev]"
   ```

3. API key geçerli mi?
   ```bash
   python3 -c "import openai; print('OK')"
   ```

### Görsel Üretim Hatası

```
❌ Gemini API key gerekli!
```

**Çözüm:**
1. Google AI Studio'dan Gemini API key alın
2. `.env` dosyasına `GEMINI_API_KEY=...` ekleyin

### Timeout Hatası

```
TimeoutError: API call timed out
```

**Çözüm:**
- İnternet bağlantınızı kontrol edin
- API rate limit'e takılmış olabilirsiniz, birkaç dakika bekleyin
- `--dry-run` ile test edin

## Performans İpuçları

1. **Dry-run kullanın:** API maliyetlerinden kaçınmak için önce `--dry-run` ile test edin
2. **Tek agent:** Sadece metin gerekiyorsa crew yerine tek agent kullanın
3. **Cache:** Tekrarlanan sorgular için sonuçlar cache'lenir

## İletişim

Sorular ve öneriler için: [GitHub Issues](https://github.com/srtnacikgoz/sade-chocolate-agents/issues)
