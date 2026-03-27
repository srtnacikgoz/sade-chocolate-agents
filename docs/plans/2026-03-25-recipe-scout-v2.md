# Recipe Scout V2 — Öğrenen Reçete Keşif Ajanı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reçete Scout'u HTML çıktı, inline puanlama UI ve öğrenme döngüsü ile yeniden inşa etmek.

**Architecture:** Agent her gün 8 kategoriden 16 reçete bulur → HTML dosyasına yazar → kullanıcı HTML'de puanlar → `learn.sh` puanları işler → `data/preferences.json` güncellenir → sonraki çalışmada agent tercihleri okur ve aramalarını buna göre şekillendirir.

**Tech Stack:** Bash, Claude CLI, vanilla HTML/CSS/JS (no dependencies)

---

## Dosya Yapısı

```
recete-agent/
├── prompts/
│   └── system.md              # Modify: HTML çıktı talimatı, bileşen etiketleme, öğrenme konteksti
├── templates/
│   └── report.html            # Create: puanlama UI'li HTML şablonu (referans olarak prompt'a gömülecek)
├── data/
│   └── preferences.json       # Generated: learn.sh tarafından üretilir, scout.sh tarafından okunur
├── scout.sh                   # Modify: HTML çıktı, preferences enjeksiyonu
├── learn.sh                   # Create: puanları işle → preferences güncelle
└── README.md                  # Modify: yeni kullanım
```

Çıktı dizini (kullanıcı tarafı):
```
~/recettes/
├── 2026-03-25.html            # Günlük HTML rapor
├── scores/
│   └── 2026-03-25-scores.json # Puanlama export'u (HTML'den indirilir)
```

---

### Task 1: Dizin Yapısını Hazırla

- [ ] **Step 1: Gerekli dizinleri oluştur**

```bash
cd /Users/sertanacikgoz/Developer/recete-agent
mkdir -p templates data
mkdir -p ~/recettes/scores
```

- [ ] **Step 2: .gitkeep dosyası ekle**

```bash
touch data/.gitkeep
```

---

### Task 2: HTML Şablonu — Puanlama UI'li Rapor Sayfası

**Files:**
- Create: `templates/report.html`

Bu dosya hem referans şablon hem de system prompt'a gömülecek HTML yapısıdır. Agent bu yapıyı takip ederek çıktı üretecek. Placeholder'lar `{{UPPERCASE}}` formatında — agent bunları gerçek verilerle dolduracak.

- [ ] **Step 1: HTML iskeletini oluştur**

Temel yapı:
- Responsive, tek sayfa, koyu/açık tema desteği (toggle butonlu)
- Header: tarih, taranan kaynak sayısı, tema toggle, export butonu
- 8 kategori bölümü, her birinde 2 reçete kartı
- Footer: keşfedilen kaynaklar tablosu

```html
<!DOCTYPE html>
<html lang="tr" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reçete Scout — {{TARIH}}</title>
  <!-- Inline CSS — no external dependencies -->
</head>
<body>
  <header>
    <div class="header-top">
      <h1>Reçete Scout</h1>
      <div class="header-actions">
        <button onclick="toggleTheme()" class="theme-toggle" title="Tema Değiştir">🌓</button>
        <button onclick="exportScores()" class="export-btn">Puanları Dışa Aktar</button>
      </div>
    </div>
    <p class="date">{{TARIH}}</p>
    <p class="stats">Taranan kaynak: {{KAYNAK_SAYISI}} | Toplam reçete: 16</p>
  </header>

  <main>
    <!-- Her kategori bir section -->
    <section class="category" id="viennoiserie">
      <h2>Viennoiserie</h2>
      <!-- Reçete kartları buraya -->
    </section>
    <!-- ... toplam 8 kategori -->
  </main>

  <footer>
    <h2>Keşfedilen Kaynaklar</h2>
    <table>
      <thead><tr><th>Kaynak</th><th>Tür</th><th>Not</th></tr></thead>
      <tbody>
        <!-- Agent doldurur -->
      </tbody>
    </table>
  </footer>

  <!-- Inline JS — no external dependencies -->
  <script>
    // ... scoring logic
  </script>
</body>
</html>
```

- [ ] **Step 2: Reçete kartı bileşenini tasarla**

Her kart şu bilgileri gösterir + puanlama formu içerir. `data-score` attribute'u karmaşıklık skoru için zorunlu.

```html
<article class="recipe-card" data-id="1" data-category="viennoiserie">
  <!-- Üst kısım: Reçete bilgisi -->
  <div class="recipe-info">
    <h3>
      <span class="recipe-name-tr">Reçete Adı Türkçe</span>
      <span class="recipe-name-original">Original Name</span>
    </h3>
    <a href="{{LINK}}" target="_blank" rel="noopener" class="source">Kaynak: {{ŞEF/BLOG}}</a>
    <div class="difficulty">Zorluk: ⭐⭐⭐</div>
    <p class="why-selected">Neden seçildi açıklaması...</p>
    <div class="ingredients">
      <strong>Ana malzemeler:</strong>
      <ul><li>malzeme 1</li><li>malzeme 2</li></ul>
    </div>
    <div class="components">
      <strong>Bileşenler:</strong>
      <span class="component-tag">dacquoise</span>
      <span class="component-tag">crémeux</span>
      <span class="component-tag">glaçage miroir</span>
    </div>
    <p class="tech-note">Teknik not...</p>
    <div class="complexity" data-score="3">Karmaşıklık: <span class="complexity-bar"></span> 3/5</div>
  </div>

  <!-- Alt kısım: Puanlama formu -->
  <div class="scoring-form">
    <div class="stars">
      <label>Puan:</label>
      <button class="star" data-value="1">★</button>
      <button class="star" data-value="2">★</button>
      <button class="star" data-value="3">★</button>
      <button class="star" data-value="4">★</button>
      <button class="star" data-value="5">★</button>
    </div>
    <div class="tags">
      <label>Etiketler:</label>
      <button class="tag-btn" data-tag="teknik">teknik</button>
      <button class="tag-btn" data-tag="yaratici">yaratıcı</button>
      <button class="tag-btn" data-tag="klasik">klasik</button>
      <button class="tag-btn" data-tag="sunum">sunum</button>
      <button class="tag-btn" data-tag="uygulanabilir">uygulanabilir</button>
      <button class="tag-btn" data-tag="trend">trend</button>
      <button class="tag-btn" data-tag="ilham">ilham</button>
      <button class="tag-btn" data-tag="mevsimsel">mevsimsel</button>
    </div>
    <textarea class="comment" placeholder="Yorum (opsiyonel)..." rows="2"></textarea>
  </div>
</article>
```

- [ ] **Step 3: CSS tasarımı**

Gereksinimler:
- Temiz, okunabilir tipografi (system fonts)
- Kartlar grid layout (1 kolon mobile, 2 kolon desktop)
- Puanlama formu her kartın altında, compact
- Seçilen yıldızlar sarı renk, seçilmeyenler gri
- Seçilen tag'ler belirgin arka plan renk değişimi
- Kategori bölümleri arasında net ayrım (border + spacing)
- Print-friendly (`@media print` ile puanlama formları gizlenir)
- Bileşen tag'leri küçük pill/badge şeklinde
- Karmaşıklık skoru görsel bar olarak (CSS ile dolu/boş kutucuklar)
- Dark mode: `[data-theme="dark"]` selector ile koyu renkler
- Export butonu belirgin, sabit header'da

- [ ] **Step 4: JavaScript — Puanlama mantığı (tam implementasyon)**

```javascript
// === State Management ===
const STORAGE_KEY = 'scores-{{TARIH}}';
let scores = {};

// === Star Rating ===
function updateStarUI(card, value) {
  card.querySelectorAll('.star').forEach(star => {
    const starValue = parseInt(star.dataset.value);
    star.classList.toggle('filled', starValue <= value);
  });
}

document.querySelectorAll('.star').forEach(star => {
  star.addEventListener('click', (e) => {
    const card = e.target.closest('.recipe-card');
    const id = card.dataset.id;
    const value = parseInt(e.target.dataset.value);
    scores[id] = scores[id] || {};
    scores[id].puan = value;
    updateStarUI(card, value);
    saveToLocalStorage();
  });
});

// === Tag Toggle ===
document.querySelectorAll('.tag-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const card = e.target.closest('.recipe-card');
    const id = card.dataset.id;
    const tag = e.target.dataset.tag;
    scores[id] = scores[id] || {};
    scores[id].tags = scores[id].tags || [];
    const idx = scores[id].tags.indexOf(tag);
    if (idx > -1) scores[id].tags.splice(idx, 1);
    else scores[id].tags.push(tag);
    e.target.classList.toggle('selected');
    saveToLocalStorage();
  });
});

// === Comment ===
document.querySelectorAll('.comment').forEach(textarea => {
  textarea.addEventListener('input', (e) => {
    const card = e.target.closest('.recipe-card');
    const id = card.dataset.id;
    scores[id] = scores[id] || {};
    scores[id].yorum = e.target.value;
    saveToLocalStorage();
  });
});

// === LocalStorage Persistence ===
function saveToLocalStorage() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(scores));
}

function loadFromLocalStorage() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (!saved) return;

  scores = JSON.parse(saved);

  Object.entries(scores).forEach(([id, data]) => {
    const card = document.querySelector(`.recipe-card[data-id="${id}"]`);
    if (!card) return;

    // Restore stars
    if (data.puan) {
      updateStarUI(card, data.puan);
    }

    // Restore tags
    if (data.tags) {
      data.tags.forEach(tag => {
        const btn = card.querySelector(`.tag-btn[data-tag="${tag}"]`);
        if (btn) btn.classList.add('selected');
      });
    }

    // Restore comment
    if (data.yorum) {
      const textarea = card.querySelector('.comment');
      if (textarea) textarea.value = data.yorum;
    }
  });
}

// === Theme Toggle ===
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  html.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
  localStorage.setItem('theme', html.getAttribute('data-theme'));
}

// === Export ===
function exportScores() {
  const exportData = {
    tarih: '{{TARIH}}',
    puanlamaTarihi: new Date().toISOString(),
    receteler: {}
  };

  document.querySelectorAll('.recipe-card').forEach(card => {
    const id = card.dataset.id;
    const category = card.dataset.category;
    const name = card.querySelector('.recipe-name-tr').textContent;
    const source = card.querySelector('.source').href;
    const components = [...card.querySelectorAll('.component-tag')].map(t => t.textContent);
    const complexity = parseInt(card.querySelector('.complexity').dataset.score) || 0;

    exportData.receteler[id] = {
      ad: name,
      kategori: category,
      kaynak: source,
      bilesenler: components,
      karmasiklik: complexity,
      ...(scores[id] || {}) // puan, tags, yorum
    };
  });

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = '{{TARIH}}-scores.json';
  a.click();
  URL.revokeObjectURL(url);
}

// === Init ===
document.addEventListener('DOMContentLoaded', () => {
  // Restore theme
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) document.documentElement.setAttribute('data-theme', savedTheme);

  // Restore scores
  loadFromLocalStorage();
});
```

- [ ] **Step 5: Tüm parçaları birleştirip `templates/report.html`'i yaz**

Tüm CSS inline `<style>` tag'inde, tüm JS inline `<script>` tag'inde. Dış bağımlılık yok.
Placeholder'lar: `{{TARIH}}`, `{{KAYNAK_SAYISI}}`, `{{LINK}}`, `{{ŞEF/BLOG}}`, reçete içerikleri.
Agent bu şablondaki yapıyı aynen kullanacak, sadece placeholder'ları ve örnek kartları gerçek verilerle dolduracak.

- [ ] **Step 6: Tarayıcıda doğrula**

Dosyayı tarayıcıda aç. Kontrol listesi:
- [ ] 8 kategori bölümü görünüyor
- [ ] Yıldız tıklama çalışıyor ve visual feedback veriyor (sarı/gri)
- [ ] Tag toggle çalışıyor (selected class ekleniyor/kalkıyor)
- [ ] Yorum yazılabiliyor
- [ ] Export butonu `{{TARIH}}-scores.json` dosyası indiriyor
- [ ] Sayfa yenilenince puanlar korunuyor (localStorage)
- [ ] Mobile responsive (tek kolon)
- [ ] Dark mode toggle çalışıyor
- [ ] Bileşen tag'leri pill şeklinde görünüyor
- [ ] `data-score` attribute doğru parse ediliyor (export JSON'da `karmasiklik` NaN değil)

---

### Task 3: System Prompt Güncellemesi

**Files:**
- Modify: `prompts/system.md`

NOT: Mevcut system prompt zaten 8 kategori / 16 reçete yapısında. Bu task'ta yapılacak:
- Haftalık tema referanslarını temizle (README'de var, prompt'ta yok)
- Markdown çıktı formatını HTML'e dönüştür
- Bileşen etiketleme talimatı ekle
- Karmaşıklık skoru talimatı ekle
- Öğrenme konteksti bölümü ekle
- Kalite filtresi ekle

- [ ] **Step 1: Çıktı formatı bölümünü markdown'dan HTML'e dönüştür**

Mevcut prompt'taki `## Çıktı Formatı` bölümünü (satır 58-140 civarı) tamamen değiştir.

Yeni talimat:
- "Çıktıyı HTML formatında yaz"
- HTML yapısını `templates/report.html` şablonundan referans al
- Her reçete kartının `data-id` (1-16 sıralı) ve `data-category` attribute'larını doldur
- Bileşen tag'lerini `<span class="component-tag">` olarak ekle
- Karmaşıklık skorunu `<div class="complexity" data-score="X">` olarak yaz (data-score ZORUNLU)
- CSS ve JS bloklarını şablondan AYNEN kopyala, değiştirme
- `{{TARIH}}` placeholder'ını günün tarihiyle değiştir

- [ ] **Step 2: Bileşen etiketleme talimatı ekle**

Yeni bölüm ekle — `## Bileşen Etiketleme`:

Agent'a her reçetenin alt bileşenlerini etiketlemesini söyle:
- Pasta bileşenleri: `mousse`, `crémeux`, `dacquoise`, `sablé`, `glaçage miroir`, `insert`, `croustillant`, `biscuit joconde`, `ganache montée`, `pralin`, `confit`, `meringue`, `choux`, `feuilletage`, `brioche`, `crème diplomat`, `namelaka`, `praliné`, `streusel`, `crème mousseline`, `pâte sucrée`, `pâte feuilletée`, `crème d'amande`, `compote`, `gelée` vb.
- Her reçete için teknik bileşenleri `<span class="component-tag">` olarak listele
- Basit reçetelerde bile (ör: cookie) teknik bileşenleri çıkar (ör: `brown butter`, `temper chocolate`)

- [ ] **Step 3: Karmaşıklık skoru talimatı ekle**

Yeni bölüm ekle — `## Karmaşıklık Skoru`:

Agent her reçeteye 1-5 karmaşıklık skoru verir ve `data-score` attribute'una yazar:
1. Tek bileşen, temel teknik (ör: basit cookie)
2. 2 bileşen veya bir orta seviye teknik (ör: tartolet + crème)
3. 3+ bileşen, birden fazla teknik (ör: tart + crémeux + meringue)
4. 4+ bileşen, ileri teknikler (ör: entremet + insert + glaçage)
5. 5+ bileşen, master seviye (ör: çok katmanlı entremet + şeker işçiliği)

- [ ] **Step 4: Kalite filtresi ekle**

Yeni bölüm ekle — `## Kalite Filtresi`:
- "Ev yapımı", "kolay", "5 malzemeli" tarzı reçeteleri ELEME
- Çok bileşenli, teknik derinliği olan reçeteleri tercih et
- Minimum: En az 2 farklı teknik bileşen içermeli (sadece "kek + krema" yeterli değil)
- Hedef seviye: Haute pâtisserie — profesyonel pastane menüsüne girebilecek kalite

- [ ] **Step 5: Öğrenme konteksti bölümünü ekle**

Prompt'un en sonuna ekle:

```
## Tercih Profili (Öğrenilen)

{{PREFERENCES}}

Eğer tercih profili boşsa, kendi en iyi yargını kullan.
Eğer doluysa, bu tercihlere uygun reçeteler bulmaya öncelik ver ama çeşitliliği koru — her gün en az 4 reçete "keşif" amaçlı tercih profilinin dışından olmalı.
```

---

### Task 4: Öğrenme Motoru — `learn.sh`

**Files:**
- Create: `learn.sh`

Bu script `~/recettes/scores/` altındaki tüm JSON dosyalarını okur ve `data/preferences.json` üretir.

- [ ] **Step 1: Temel script yapısını oluştur**

```bash
#!/bin/bash
# learn.sh — Puanlardan öğrenme çıkar, preferences.json güncelle
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCORES_DIR="$HOME/recettes/scores"
PREFS_FILE="$SCRIPT_DIR/data/preferences.json"

mkdir -p "$SCRIPT_DIR/data"
mkdir -p "$SCORES_DIR"

# Puan dosyası var mı kontrol et
SCORE_COUNT=$(find "$SCORES_DIR" -name "*-scores.json" -type f | wc -l | tr -d ' ')
if [ "$SCORE_COUNT" -eq 0 ]; then
  echo "Henüz puanlanmış dosya yok. Önce HTML raporları puanlayıp export edin."
  exit 0
fi

echo "📊 Puanlar analiz ediliyor..."
echo "📁 Puan dosyaları: $SCORE_COUNT adet"
```

- [ ] **Step 2: Claude CLI ile analiz + doğrulama**

```bash
# Tüm puan dosyalarını birleştir
COMBINED=$(cat "$SCORES_DIR"/*-scores.json | jq -s '.')

claude -p "
Sen bir öğrenme motorusun. Aşağıdaki puanlama verilerinden kullanıcının tercih profilini çıkar.

## Puanlama Verileri
$COMBINED

## Çıkar ve JSON olarak yaz:

1. **stil_profili**: Yüksek puanlı (4-5) reçetelerin ortak özellikleri
   - tercih_edilen_bilesenler: En çok beğenilen bileşen kombinasyonları
   - tercih_edilen_teksturler: Beğenilen tekstür kontrastları
   - tercih_edilen_lezzet_aileleri: Beğenilen lezzet profilleri
   - karmasiklik_tercihi: Ortalama beğenilen karmaşıklık skoru

2. **kaynak_kalite_haritasi**: Her kaynağın ortalama puanı
   - yuksek_kalite: 4+ ortalama alan kaynaklar
   - dusuk_kalite: 2.5 altı ortalama alan kaynaklar

3. **bilesen_tercihleri**: Yüksek puanlı reçetelerde sık geçen bileşenler ve kombinasyonlar

4. **kacinilacaklar**: Düşük puanlı (1-2) reçetelerin ortak özellikleri

5. **tag_analizi**: Hangi tag'ler yüksek puanla birlikte geliyor (ör: 'teknik' tag'i olan reçeteler ortalama 4.2 puan)

6. **kullanici_yorumlari_ozet**: Yorumlardan çıkarılan anahtar bilgiler

JSON formatında $PREFS_FILE dosyasına yaz. SADECE geçerli JSON yaz, markdown code block kullanma.
" \
  --allowedTools "Read,Write" \
  --max-budget-usd 1

# Doğrulama: dosya oluştu mu ve geçerli JSON mu?
if [ ! -f "$PREFS_FILE" ]; then
  echo "❌ HATA: preferences.json oluşturulamadı."
  exit 1
fi

if ! jq empty "$PREFS_FILE" 2>/dev/null; then
  echo "❌ HATA: preferences.json geçersiz JSON. Dosya siliniyor, tekrar deneyin."
  rm -f "$PREFS_FILE"
  exit 1
fi

echo "✅ Tercih profili güncellendi: $PREFS_FILE"
echo "📊 Özet:"
jq '.stil_profili.karmasiklik_tercihi // "henüz veri yok"' "$PREFS_FILE"
```

- [ ] **Step 3: Çalıştırılabilir yap**

```bash
chmod +x learn.sh
```

---

### Task 5: `scout.sh` Güncellemesi

**Files:**
- Modify: `scout.sh`

- [ ] **Step 1: Script'i tamamen yeniden yaz**

```bash
#!/bin/bash
# Reçete Scout Agent — Her gün 8 kategoriden 16 reçete keşfeder
#
# Kullanım:
#   ./scout.sh
#
# Çıktı: ~/recettes/YYYY-MM-DD.html

set -euo pipefail

DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="$HOME/recettes"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PREFS_FILE="$SCRIPT_DIR/data/preferences.json"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/scores"

echo "📅 $DATE — Reçete Scout başlıyor..."
echo "📁 Çıktı: $OUTPUT_DIR/$DATE.html"

# System prompt'u oku
PROMPT=$(cat "$SCRIPT_DIR/prompts/system.md")

# HTML şablonunu oku
TEMPLATE=$(cat "$SCRIPT_DIR/templates/report.html")

# Tercih dosyası varsa oku
if [ -f "$PREFS_FILE" ]; then
  PREFERENCES=$(cat "$PREFS_FILE")
  echo "🧠 Öğrenilmiş tercihler yüklendi."
else
  PREFERENCES="Henüz tercih verisi yok. Kendi en iyi yargını kullan."
  echo "🆕 İlk çalışma — tercih profili henüz yok."
fi

cd "$OUTPUT_DIR"

claude -p "
$PROMPT

## Tercih Profili (Öğrenilen)

$PREFERENCES

## HTML Şablon (bu yapıyı AYNEN takip et, sadece içerik kısımlarını doldur)

$TEMPLATE

## Çıktı
Bugünün tarihi: $DATE
Sonucu $DATE.html dosyasına yaz (mevcut dizine).
HTML şablonundaki placeholder'ları gerçek reçete verileriyle doldur.
CSS ve JavaScript kodunu AYNEN koru, değiştirme.
{{TARIH}} placeholder'larını $DATE ile değiştir.
" \
  --allowedTools "WebSearch,WebFetch,Read,Write" \
  --max-budget-usd 5

echo "✅ Tamamlandı: $OUTPUT_DIR/$DATE.html"
```

NOT: Preferences enjeksiyonu artık placeholder substitution yerine doğrudan prompt'a append ediliyor. Bu, bash special characters sorununu ortadan kaldırıyor. System prompt'taki `{{PREFERENCES}}` placeholder'ı kaldırılacak, çünkü scout.sh tercihleri doğrudan prompt'un sonuna ekliyor.

- [ ] **Step 2: Doğrulama**

```bash
chmod +x scout.sh
./scout.sh
# Kontrol:
# - ~/recettes/YYYY-MM-DD.html dosyası oluştu mu?
# - Tarayıcıda açılıyor mu?
# - 8 kategori, 16 reçete var mı?
# - Puanlama UI çalışıyor mu?
# - Bileşen tag'leri var mı?
# - data-score attribute'ları var mı?
```

---

### Task 6: README Güncellemesi

**Files:**
- Modify: `README.md`

- [ ] **Step 1: README'yi yeniden yaz**

```markdown
# Reçete Scout Agent

Haute pâtisserie reçete keşif ajanı. Her gün 8 kategoriden 16 profesyonel reçete bulur,
HTML rapor üretir, kullanıcı puanlarından öğrenir.

## Kullanım

```bash
# Günlük keşif çalıştır
./scout.sh

# Puanları öğrenme motoruna aktar
./learn.sh
```

## Akış

1. `./scout.sh` → `~/recettes/YYYY-MM-DD.html` üretir
2. HTML'i tarayıcıda aç → reçeteleri puanla (yıldız + etiket + yorum)
3. "Puanları Dışa Aktar" butonuna tıkla → `YYYY-MM-DD-scores.json` indirilir
4. İndirilen JSON'u `~/recettes/scores/` klasörüne taşı
5. `./learn.sh` → puanlardan tercih profili üretir (`data/preferences.json`)
6. Sonraki `./scout.sh` çalışmasında agent tercihlerini kullanır

## Kategoriler (her gün hepsi taranır)

| Kategori | Açıklama |
|----------|----------|
| Viennoiserie | Kruvasan, brioche, pain au chocolat, danish, kouign-amann |
| Tart & Tartolet | Tart, tartolet, galette, crostata |
| Entremets & Mousse | Mousse pasta, bavarian, charlotte, çok katmanlı |
| Petit Gâteau | Financier, madeleine, canelé, sablé, macaron |
| Çikolata | Bonbon, truffle, tablette, ganache, pralin |
| Trend | Sosyal medyada viral, yeni çıkan tatlılar |
| Uluslararası | Japon, Kore, İtalyan, İskandinav, Güney Amerika |
| Sandviç | Kruvasan sandviç, focaccia, brioche sandviç, tuzlu ürünler |

## Puanlama Etiketleri

`teknik` `yaratıcı` `klasik` `sunum` `uygulanabilir` `trend` `ilham` `mevsimsel`

## Otomatik Çalıştırma

```bash
# crontab -e ile ekle:
0 7 * * * /Users/sertanacikgoz/Developer/recete-agent/scout.sh
```
```

---

## Review Notları

Bu plan review sonrası düzeltilen konular:

1. **C1**: System prompt zaten 8 kategori/16 reçete yapısında — Task 3 bunu açıkça belirtiyor
2. **C2**: `learn.sh`'e JSON doğrulama eklendi (dosya varlığı + `jq empty`)
3. **C3**: Export dosya adı her yerde `YYYY-MM-DD-scores.json` olarak standartlaştırıldı
4. **C4**: `data-score` attribute'u HTML kartına eklendi: `<div class="complexity" data-score="3">`
5. **I1**: `loadFromLocalStorage()` tam implementasyonu yazıldı (stars, tags, comment restore)
6. **I2**: `updateStarUI()` fonksiyonu tanımlandı
7. **I3**: `DOMContentLoaded` event listener eklendi
8. **I5**: Placeholder substitution yerine doğrudan append yaklaşımı kullanıldı
9. **I6**: Dizin oluşturma Task 1'e taşındı
10. **S4**: Dark mode toggle butonu ve JS'i eklendi
11. **S5**: `scout.sh` header yorumu düzeltildi
