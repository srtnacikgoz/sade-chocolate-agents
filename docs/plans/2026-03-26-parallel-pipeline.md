# Paralel Pipeline — Hızlı Reçete Keşfi

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tek agent + dev prompt mimarisini 3 aşamalı paralel pipeline'a dönüştürerek keşif süresini ~10dk'dan ~2-3dk'ya düşürmek.

**Architecture:** Aşama 1: 8 paralel Sonnet agent kategori başına 2 reçete URL'si bulur (JSON). Aşama 2: 16 paralel Haiku agent her URL'den detay çıkarır (JSON). Aşama 3: Node.js JSON'u HTML şablonuna render eder (LLM yok). HTML template prompt'a hiç girmez.

**Tech Stack:** Node.js, Claude CLI (`--model sonnet`, `--model haiku`), `child_process.spawn`, `Promise.all`

---

## Dosya Yapısı

```
recete-agent/
├── server.js                    # Modify: handleScout → pipeline orchestrator
├── prompts/
│   ├── search.md                # Create: Aşama 1 — kategori arama prompt'u (~300 token)
│   └── extract.md               # Create: Aşama 2 — reçete çıkarma prompt'u (~400 token)
├── lib/
│   ├── pipeline.js              # Create: 3 aşamalı pipeline orchestrator
│   ├── claude-runner.js         # Create: Claude CLI spawn + stream parse helper
│   └── renderer.js              # Create: JSON → HTML render (LLM yok)
├── prompts/system.md            # Keep: sadece learn.sh ve scout.sh (CLI) için
├── templates/report.html        # Keep: renderer.js bu şablonu kullanır
├── public/index.html            # Modify: ilerleme UI (8/8 kategori, 16/16 reçete)
└── scout.sh                     # Modify: pipeline'ı CLI'dan da çağırabilir
```

---

### Task 1: Claude Runner Helper — `lib/claude-runner.js`

**Files:**
- Create: `lib/claude-runner.js`

Tek bir Claude CLI çağrısını yöneten helper. Prompt gönderir, JSON sonuç döndürür.

- [ ] **Step 1: Modülü oluştur**

```javascript
// lib/claude-runner.js
const { spawn } = require('child_process');

/**
 * Claude CLI'ı çalıştır, JSON sonuç döndür.
 * @param {object} opts
 * @param {string} opts.prompt - Gönderilecek prompt
 * @param {string} opts.model - 'sonnet' | 'haiku'
 * @param {string[]} opts.tools - İzin verilen tool'lar ['WebSearch', 'WebFetch']
 * @param {number} opts.budget - Max USD bütçe
 * @param {string} opts.cwd - Çalışma dizini
 * @param {function} opts.onEvent - Her stream event'i için callback (opsiyonel)
 * @returns {{ promise: Promise<{success, result, cost, duration}>, abort: function }}
 */
function runClaude(opts) {
  var proc;

  var promise = new Promise(function(resolve, reject) {
    var args = [
      '-p', opts.prompt,
      '--model', opts.model || 'sonnet',
      '--output-format', 'stream-json',
      '--verbose',
      '--allowedTools', (opts.tools || ['WebSearch', 'WebFetch']).join(','),
      '--max-budget-usd', String(opts.budget || 0.5)
    ];

    proc = spawn('claude', args, {
      cwd: opts.cwd || process.cwd(),
      env: Object.assign({}, process.env),
      stdio: ['ignore', 'pipe', 'pipe']
    });

    var buffer = '';
    var lastResult = null;

    proc.stdout.on('data', function(chunk) {
      buffer += chunk.toString();
      var lines = buffer.split('\n');
      buffer = lines.pop();

      for (var i = 0; i < lines.length; i++) {
        var line = lines[i].trim();
        if (!line) continue;
        try {
          var event = JSON.parse(line);

          // Callback for streaming events
          if (opts.onEvent) opts.onEvent(event);

          // Capture result
          if (event.type === 'result') {
            lastResult = {
              success: event.subtype === 'success' && !event.is_error,
              result: event.result || '',
              cost: event.total_cost_usd || 0,
              duration: event.duration_ms || 0
            };
          }
        } catch(e) {}
      }
    });

    proc.stderr.on('data', function(chunk) {
      // Ignore stderr — hooks output goes here
    });

    proc.on('error', function(err) {
      reject(new Error('Claude başlatılamadı: ' + err.message));
    });

    proc.on('close', function(code) {
      // Process remaining buffer
      if (buffer.trim()) {
        try {
          var event = JSON.parse(buffer.trim());
          if (event.type === 'result') {
            lastResult = {
              success: event.subtype === 'success' && !event.is_error,
              result: event.result || '',
              cost: event.total_cost_usd || 0,
              duration: event.duration_ms || 0
            };
          }
        } catch(e) {}
      }

      if (lastResult) {
        resolve(lastResult);
      } else {
        reject(new Error('Claude çıktı vermeden sonlandı (exit: ' + code + ')'));
      }
    });

  });

  return {
    promise: promise,
    abort: function() { if (proc) proc.kill('SIGTERM'); }
  };
}

module.exports = { runClaude };
```

- [ ] **Step 2: `lib/` dizinini oluştur**

```bash
mkdir -p /Users/sertanacikgoz/Developer/recete-agent/lib
```

- [ ] **Step 3: Dosyayı yaz ve test et**

```bash
node -e "
var { runClaude } = require('./lib/claude-runner');
runClaude({
  prompt: 'Sadece {\"test\": true} JSON döndür, başka bir şey yazma.',
  model: 'haiku',
  tools: [],
  budget: 0.05
}).then(function(r) {
  console.log('Success:', r.success);
  console.log('Result:', r.result.substring(0, 100));
  console.log('Cost:', r.cost);
}).catch(function(e) {
  console.log('Error:', e.message);
});
"
```

Expected: Success: true, Result: {"test": true} benzeri çıktı

---

### Task 2: Arama Prompt'u — `prompts/search.md`

**Files:**
- Create: `prompts/search.md`

Kategori başına ~300 token'lık küçük prompt. Sonnet'e gider.

- [ ] **Step 1: Prompt'u oluştur**

```markdown
Sen bir pastacılık reçete araştırmacısısın.

## Görev
{{KATEGORI}} kategorisinde TAM 2 haute pâtisserie reçetesi bul.

## Kategori
{{KATEGORI_ACIKLAMA}}

## Arama Kuralları
- Farklı dillerde ara (Fransızca, İngilizce, Japonca)
- Her aramaya şu siteleri hariç tut: -allrecipes -food.com -marmiton -tasty -delish -pinterest -cuisineaz -750g -bbc
- Sabit sorgu kullanma, yaratıcı ara

## YASAK Kaynaklar
allrecipes.com, food.com, tasty.co, delish.com, marmiton.org, cuisineaz.com, 750g.com, food network, bbc good food, Pinterest

## İSTENEN Kaynaklar
Bireysel pastacı blogları, Michelin/ödüllü şef siteleri, profesyonel pastacılık siteleri, niş bloglar

## Kalite Filtresi
- "Evde yapım", "kolay", "5 malzemeli" reçeteleri ELEME
- En az 2 teknik bileşen içermeli
- Haute pâtisserie seviyesi

{{TERCIHLER}}

## Çıktı Formatı
SADECE JSON döndür, başka bir şey yazma:
```json
[
  {
    "ad_tr": "Türkçe ad",
    "ad_orijinal": "Orijinal ad",
    "url": "https://...",
    "kaynak_adi": "Şef/Blog adı",
    "neden": "2-3 cümle neden seçildi"
  },
  {
    "ad_tr": "...",
    "ad_orijinal": "...",
    "url": "...",
    "kaynak_adi": "...",
    "neden": "..."
  }
]
```
```

---

### Task 3: Çıkarma Prompt'u — `prompts/extract.md`

**Files:**
- Create: `prompts/extract.md`

URL'den reçete detayı çıkaran ~400 token'lık prompt. Haiku'ya gider.

- [ ] **Step 1: Prompt'u oluştur**

```markdown
Aşağıdaki URL'deki reçeteden yapılandırılmış veri çıkar.

## URL
{{URL}}

## Reçete Bilgisi
Ad: {{AD_TR}} ({{AD_ORIJINAL}})
Kaynak: {{KAYNAK_ADI}}

## Çıkaracağın Veriler
SADECE JSON döndür:
```json
{
  "ad_tr": "Türkçe ad",
  "ad_orijinal": "Orijinal ad",
  "url": "reçete URL'si",
  "kaynak_adi": "kaynak adı",
  "neden": "neden seçildi",
  "zorluk": 3,
  "malzemeler": ["malzeme 1", "malzeme 2", "malzeme 3"],
  "bilesenler": ["dacquoise", "crémeux", "glaçage miroir"],
  "teknik_not": "1-2 cümle teknik detay",
  "karmasiklik": 4
}
```

## Kurallar
- zorluk: 1-5 (yıldız)
- karmasiklik: 1-5 (1=basit cookie, 5=çok katmanlı entremet)
- bilesenler: Fransızca teknik terimler (mousse, crémeux, dacquoise, sablé, glaçage miroir, insert, croustillant, ganache montée, pralin, feuilletage, namelaka, praliné, streusel, pâte sucrée vb.)
- malzemeler: Türkçe, ana malzemeler (max 8)
- teknik_not: Türkçe, teknik terimler orijinal kalabilir
- Reçete adını ve açıklamaları Türkçeye çevir
```

---

### Task 4: JSON → HTML Renderer — `lib/renderer.js`

**Files:**
- Create: `lib/renderer.js`

LLM kullanmadan JSON reçete verisini HTML şablonuna render eder.

- [ ] **Step 1: Renderer modülünü oluştur**

```javascript
// lib/renderer.js
var fs = require('fs');
var path = require('path');

var TEMPLATE_PATH = path.join(__dirname, '..', 'templates', 'report.html');

var CATEGORIES = [
  { id: 'viennoiserie', name: 'Viennoiserie' },
  { id: 'tart-tartolet', name: 'Tart & Tartolet' },
  { id: 'entremets-mousse', name: 'Entremets & Mousse' },
  { id: 'petit-gateau', name: 'Petit Gâteau' },
  { id: 'cikolata', name: 'Çikolata' },
  { id: 'trend', name: 'Trend' },
  { id: 'uluslararasi', name: 'Uluslararası' },
  { id: 'sandvic', name: 'Sandviç' }
];

/**
 * Reçete JSON verilerini HTML'e render et.
 * @param {object} opts
 * @param {string} opts.date - Tarih (YYYY-MM-DD)
 * @param {object} opts.recipes - { "viennoiserie": [{...}, {...}], "tart-tartolet": [...], ... }
 * @param {object[]} opts.sources - [{ name, type, note, url }]
 * @returns {string} Tam HTML
 */
function renderHTML(opts) {
  var template = fs.readFileSync(TEMPLATE_PATH, 'utf-8');

  // Template'i parçala: <style> ... </style> ve <script> ... </script> blokları
  var styleMatch = template.match(/<style>([\s\S]*?)<\/style>/);
  var scriptMatch = template.match(/<script>([\s\S]*?)<\/script>/);

  var css = styleMatch ? styleMatch[1] : '';
  var js = scriptMatch ? scriptMatch[1] : '';

  var sourceCount = 0;
  var allSources = [];

  // Kategori HTML'lerini oluştur
  var categoriesHTML = '';
  var cardId = 1;

  CATEGORIES.forEach(function(cat) {
    var recipes = opts.recipes[cat.id] || [];
    categoriesHTML += '<section class="category" id="' + cat.id + '">\n';
    categoriesHTML += '  <h2>' + escapeHTML(cat.name) + '</h2>\n';
    categoriesHTML += '  <div class="card-grid">\n';

    recipes.forEach(function(r) {
      categoriesHTML += renderCard(r, cardId, cat.id);
      cardId++;

      // Kaynakları topla
      if (r.kaynak_adi && allSources.indexOf(r.kaynak_adi) === -1) {
        allSources.push(r.kaynak_adi);
        sourceCount++;
      }
    });

    categoriesHTML += '  </div>\n';
    categoriesHTML += '</section>\n\n';
  });

  // Footer — kaynaklar tablosu
  var sourcesHTML = '';
  if (opts.sources && opts.sources.length) {
    opts.sources.forEach(function(s) {
      sourcesHTML += '<tr><td>' + (s.url ? '<a href="' + escapeHTML(s.url) + '" target="_blank" rel="noopener">' + escapeHTML(s.name) + '</a>' : escapeHTML(s.name)) + '</td>';
      sourcesHTML += '<td>' + escapeHTML(s.type || '') + '</td>';
      sourcesHTML += '<td>' + escapeHTML(s.note || '') + '</td></tr>\n';
    });
  }

  // Tam HTML oluştur
  var html = '<!DOCTYPE html>\n';
  html += '<html lang="tr" data-theme="light">\n';
  html += '<head>\n';
  html += '  <meta charset="UTF-8">\n';
  html += '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n';
  html += '  <title>Reçete Scout — ' + opts.date + '</title>\n';
  html += '  <style>' + css + '</style>\n';
  html += '</head>\n';
  html += '<body>\n';
  html += '  <header>\n';
  html += '    <div class="header-top">\n';
  html += '      <h1>Reçete Scout</h1>\n';
  html += '      <div class="header-actions">\n';
  html += '        <button type="button" onclick="toggleTheme()" class="theme-toggle" title="Tema Değiştir">🌓</button>\n';
  html += '        <button type="button" onclick="exportScores()" class="export-btn">Puanları Dışa Aktar</button>\n';
  html += '      </div>\n';
  html += '    </div>\n';
  html += '    <p class="date">' + opts.date + '</p>\n';
  html += '    <p class="stats">Taranan kaynak: ' + sourceCount + ' | Toplam reçete: ' + (cardId - 1) + '</p>\n';
  html += '  </header>\n\n';
  html += '  <main>\n';
  html += categoriesHTML;
  html += '  </main>\n\n';
  html += '  <footer>\n';
  html += '    <h2>Keşfedilen Kaynaklar</h2>\n';
  html += '    <table>\n';
  html += '      <thead><tr><th>Kaynak</th><th>Tür</th><th>Not</th></tr></thead>\n';
  html += '      <tbody>\n' + sourcesHTML + '      </tbody>\n';
  html += '    </table>\n';
  html += '  </footer>\n\n';
  html += '  <script>' + js + '</script>\n';
  html += '</body>\n</html>';

  // {{TARIH}} placeholder'larını değiştir
  html = html.replace(/\{\{TARIH\}\}/g, opts.date);
  html = html.replace(/\{\{KAYNAK_SAYISI\}\}/g, String(sourceCount));

  return html;
}

function renderCard(recipe, id, category) {
  var r = recipe;
  var stars = '';
  for (var i = 0; i < 5; i++) {
    stars += i < (r.zorluk || 3) ? '⭐' : '';
  }

  var components = '';
  if (r.bilesenler && r.bilesenler.length) {
    r.bilesenler.forEach(function(b) {
      components += '      <span class="component-tag">' + escapeHTML(b) + '</span>\n';
    });
  }

  var ingredients = '';
  if (r.malzemeler && r.malzemeler.length) {
    r.malzemeler.forEach(function(m) {
      ingredients += '        <li>' + escapeHTML(m) + '</li>\n';
    });
  }

  var html = '';
  html += '    <article class="recipe-card" data-id="' + id + '" data-category="' + category + '">\n';
  html += '      <div class="recipe-info">\n';
  html += '        <h3>\n';
  html += '          <span class="recipe-name-tr">' + escapeHTML(r.ad_tr || '') + '</span>\n';
  html += '          <span class="recipe-name-original">' + escapeHTML(r.ad_orijinal || '') + '</span>\n';
  html += '        </h3>\n';
  html += '        <a href="' + escapeHTML(r.url || '#') + '" target="_blank" rel="noopener" class="source">Kaynak: ' + escapeHTML(r.kaynak_adi || '') + '</a>\n';
  html += '        <div class="difficulty">Zorluk: ' + stars + '</div>\n';
  html += '        <p class="why-selected">' + escapeHTML(r.neden || '') + '</p>\n';
  html += '        <div class="ingredients">\n';
  html += '          <strong>Ana malzemeler:</strong>\n';
  html += '          <ul>\n' + ingredients + '          </ul>\n';
  html += '        </div>\n';
  html += '        <div class="components">\n';
  html += '          <strong>Bileşenler:</strong>\n' + components;
  html += '        </div>\n';
  html += '        <p class="tech-note">' + escapeHTML(r.teknik_not || '') + '</p>\n';
  html += '        <div class="complexity" data-score="' + (r.karmasiklik || 3) + '">Karmaşıklık: <span class="complexity-bar"></span> ' + (r.karmasiklik || 3) + '/5</div>\n';
  html += '      </div>\n';
  html += '      <div class="scoring-form">\n';
  html += '        <div class="stars"><label>Puan:</label>';
  for (var s = 1; s <= 5; s++) {
    html += '<button type="button" class="star" data-value="' + s + '">★</button>';
  }
  html += '</div>\n';
  html += '        <div class="tags"><label>Etiketler:</label>';
  var tags = ['teknik','yaratici','klasik','sunum','uygulanabilir','trend','ilham','mevsimsel'];
  var tagLabels = { yaratici: 'yaratıcı' };
  tags.forEach(function(t) {
    html += '<button type="button" class="tag-btn" data-tag="' + t + '">' + (tagLabels[t] || t) + '</button>';
  });
  html += '</div>\n';
  html += '        <textarea class="comment" placeholder="Yorum (opsiyonel)..." rows="2"></textarea>\n';
  html += '      </div>\n';
  html += '    </article>\n';

  return html;
}

function escapeHTML(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

module.exports = { renderHTML, CATEGORIES };
```

- [ ] **Step 2: Test et**

```bash
node -e "
var { renderHTML } = require('./lib/renderer');
var html = renderHTML({
  date: '2026-03-26',
  recipes: {
    'viennoiserie': [
      { ad_tr: 'Test Kruvasan', ad_orijinal: 'Test Croissant', url: 'https://test.com', kaynak_adi: 'Test Blog', zorluk: 4, karmasiklik: 3, malzemeler: ['un', 'tereyağı'], bilesenler: ['feuilletage', 'laminage'], teknik_not: 'Test not', neden: 'Test neden' }
    ]
  },
  sources: []
});
console.log('HTML length:', html.length);
console.log('Has recipe card:', html.includes('recipe-card'));
console.log('Has data-score:', html.includes('data-score'));
"
```

---

### Task 5: Pipeline Orchestrator — `lib/pipeline.js`

**Files:**
- Create: `lib/pipeline.js`

3 aşamayı koordine eden ana modül.

- [ ] **Step 1: Pipeline modülünü oluştur**

```javascript
// lib/pipeline.js
var fs = require('fs');
var path = require('path');
var { runClaude } = require('./claude-runner');
var { renderHTML, CATEGORIES } = require('./renderer');

var PROMPTS_DIR = path.join(__dirname, '..', 'prompts');

var CATEGORY_DETAILS = {
  'viennoiserie': 'Kruvasan, brioche, pain au chocolat, danish, kouign-amann',
  'tart-tartolet': 'Tart, tartolet, galette, crostata',
  'entremets-mousse': 'Mousse pasta, bavarian, charlotte, çok katmanlı pasta',
  'petit-gateau': 'Cookie, financier, madeleine, canelé, sablé, macaron',
  'cikolata': 'Bonbon, truffle, tablette, çikolatalı tatlılar, ganache, pralin',
  'trend': 'Sosyal medyada popüler, viral, yeni çıkan tatlılar',
  'uluslararasi': 'Fransa dışı: Japon, Kore, İtalyan, İskandinav, Güney Amerika',
  'sandvic': 'Kruvasan sandviç, focaccia, baguette, brioche sandviç, panini — tuzlu ürünler'
};

/**
 * Tam pipeline'ı çalıştır.
 * @param {object} opts
 * @param {function} opts.onProgress - İlerleme callback: (phase, detail)
 * @param {string} opts.preferences - Tercih profili JSON string
 * @param {string} opts.outputDir - HTML çıktı dizini
 * @param {string} opts.date - Tarih YYYY-MM-DD
 * @returns {Promise<{html: string, totalCost: number, totalDuration: number}>}
 */
async function runPipeline(opts) {
  var date = opts.date || new Date().toISOString().slice(0, 10);
  var onProgress = opts.onProgress || function() {};
  var preferences = opts.preferences || '';
  var totalCost = 0;
  var startTime = Date.now();
  var activeAborts = []; // Tüm aktif process'lerin abort handle'ları

  // Dışarıdan abort edilebilir
  runPipeline._currentAborts = activeAborts;

  // ─── AŞAMA 1: Paralel Arama (8 x Sonnet) ─────────────────
  onProgress('search-start', { total: CATEGORIES.length });

  var searchPromptTemplate = fs.readFileSync(path.join(PROMPTS_DIR, 'search.md'), 'utf-8');
  var prefsSection = preferences
    ? '## Tercih Profili\nKullanıcının tercihleri:\n' + preferences.substring(0, 2000)
    : '';

  var searchPromises = CATEGORIES.map(function(cat) {
    var prompt = searchPromptTemplate
      .replace(/\{\{KATEGORI\}\}/g, cat.name)
      .replace(/\{\{KATEGORI_ACIKLAMA\}\}/g, CATEGORY_DETAILS[cat.id] || cat.name)
      .replace(/\{\{TERCIHLER\}\}/g, prefsSection);

    var run = runClaude({
      prompt: prompt,
      model: 'sonnet',
      tools: ['WebSearch', 'WebFetch'],
      budget: 0.50
    });
    activeAborts.push(run.abort);

    return run.promise.then(function(result) {
      onProgress('search-done', { category: cat.name, categoryId: cat.id });
      totalCost += result.cost;

      // JSON parse et
      try {
        var text = result.result.trim();
        // JSON bloğunu bul (bazen markdown code block içinde olabiliyor)
        var jsonMatch = text.match(/\[[\s\S]*\]/);
        if (jsonMatch) return { categoryId: cat.id, recipes: JSON.parse(jsonMatch[0]) };
      } catch(e) {}

      onProgress('search-error', { category: cat.name, error: 'JSON parse hatası' });
      return { categoryId: cat.id, recipes: [] };
    }).catch(function(err) {
      onProgress('search-error', { category: cat.name, error: err.message });
      return { categoryId: cat.id, recipes: [] };
    });
  });

  var searchResults = await Promise.all(searchPromises);
  onProgress('search-complete', { found: searchResults.reduce(function(sum, r) { return sum + r.recipes.length; }, 0) });

  // ─── AŞAMA 2: Paralel Çıkarma (16 x Haiku) ───────────────
  var extractPromptTemplate = fs.readFileSync(path.join(PROMPTS_DIR, 'extract.md'), 'utf-8');
  var extractTasks = [];

  searchResults.forEach(function(sr) {
    sr.recipes.forEach(function(recipe) {
      extractTasks.push({
        categoryId: sr.categoryId,
        recipe: recipe
      });
    });
  });

  activeAborts.length = 0; // Arama abort'larını temizle
  onProgress('extract-start', { total: extractTasks.length });

  var extractPromises = extractTasks.map(function(task) {
    var prompt = extractPromptTemplate
      .replace(/\{\{URL\}\}/g, task.recipe.url || '')
      .replace(/\{\{AD_TR\}\}/g, task.recipe.ad_tr || '')
      .replace(/\{\{AD_ORIJINAL\}\}/g, task.recipe.ad_orijinal || '')
      .replace(/\{\{KAYNAK_ADI\}\}/g, task.recipe.kaynak_adi || '');

    var run = runClaude({
      prompt: prompt,
      model: 'haiku',
      tools: ['WebFetch'],
      budget: 0.10
    });
    activeAborts.push(run.abort);

    return run.promise.then(function(result) {
      onProgress('extract-done', { recipe: task.recipe.ad_tr, categoryId: task.categoryId });
      totalCost += result.cost;

      try {
        var text = result.result.trim();
        var jsonMatch = text.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          var data = JSON.parse(jsonMatch[0]);
          // Arama aşamasından gelen bilgileri ekle (eğer extract'ta eksikse)
          data.neden = data.neden || task.recipe.neden;
          data.url = data.url || task.recipe.url;
          data.kaynak_adi = data.kaynak_adi || task.recipe.kaynak_adi;
          data.ad_tr = data.ad_tr || task.recipe.ad_tr;
          data.ad_orijinal = data.ad_orijinal || task.recipe.ad_orijinal;
          return { categoryId: task.categoryId, data: data };
        }
      } catch(e) {}

      // Fallback: arama verisini kullan
      onProgress('extract-error', { recipe: task.recipe.ad_tr, error: 'JSON parse hatası' });
      return {
        categoryId: task.categoryId,
        data: {
          ad_tr: task.recipe.ad_tr,
          ad_orijinal: task.recipe.ad_orijinal,
          url: task.recipe.url,
          kaynak_adi: task.recipe.kaynak_adi,
          neden: task.recipe.neden,
          zorluk: 3,
          malzemeler: [],
          bilesenler: [],
          teknik_not: '',
          karmasiklik: 3
        }
      };
    }).catch(function(err) {
      onProgress('extract-error', { recipe: task.recipe.ad_tr, error: err.message });
      return {
        categoryId: task.categoryId,
        data: {
          ad_tr: task.recipe.ad_tr, ad_orijinal: task.recipe.ad_orijinal,
          url: task.recipe.url, kaynak_adi: task.recipe.kaynak_adi,
          neden: task.recipe.neden, zorluk: 3, malzemeler: [], bilesenler: [],
          teknik_not: '', karmasiklik: 3
        }
      };
    });
  });

  var extractResults = await Promise.all(extractPromises);
  onProgress('extract-complete', { extracted: extractResults.length });

  // ─── AŞAMA 3: Render (LLM yok) ────────────────────────────
  onProgress('render-start', {});

  // Reçeteleri kategoriye göre grupla
  var recipesByCategory = {};
  CATEGORIES.forEach(function(cat) { recipesByCategory[cat.id] = []; });
  extractResults.forEach(function(er) {
    if (recipesByCategory[er.categoryId]) {
      recipesByCategory[er.categoryId].push(er.data);
    }
  });

  // Kaynakları topla
  var sourceMap = {};
  extractResults.forEach(function(er) {
    var name = er.data.kaynak_adi;
    if (name && !sourceMap[name]) {
      sourceMap[name] = { name: name, url: er.data.url, type: 'Blog/Site', note: '' };
    }
  });
  var sources = Object.values(sourceMap);

  // HTML render
  var html = renderHTML({
    date: date,
    recipes: recipesByCategory,
    sources: sources
  });

  // Dosyaya yaz
  var outputDir = opts.outputDir || path.join(require('os').homedir(), 'recettes');
  fs.mkdirSync(outputDir, { recursive: true });
  var outputPath = path.join(outputDir, date + '.html');
  fs.writeFileSync(outputPath, html, 'utf-8');

  var totalDuration = Date.now() - startTime;
  onProgress('complete', { cost: totalCost, duration: totalDuration, file: outputPath, recipeCount: extractResults.length });

  return { html: html, totalCost: totalCost, totalDuration: totalDuration };
}

module.exports = { runPipeline };
```

---

### Task 6: Server — handleScout Pipeline'a Geçiş

**Files:**
- Modify: `server.js`

Mevcut `handleScout` fonksiyonunu pipeline'a yönlendir.

- [ ] **Step 1: Pipeline import'u ekle**

`server.js`'in en üstüne, require'ların yanına ekle:

```javascript
var { runPipeline } = require('./lib/pipeline');
```

- [ ] **Step 2: handleScout'u yeniden yaz**

Mevcut `handleScout` fonksiyonunu (satır ~232-358) tamamen değiştir:

```javascript
function handleScout(ws) {
  if (activeProcesses.has(ws)) {
    sendJSON(ws, { type: 'error', message: 'Zaten çalışan bir işlem var.' });
    return;
  }

  var date = new Date().toISOString().slice(0, 10);

  // Read preferences
  var preferences = '';
  var prefsPath = path.join(SCRIPT_DIR, 'data', 'preferences.json');
  try { preferences = fs.readFileSync(prefsPath, 'utf-8'); } catch(e) {}

  sendJSON(ws, { type: 'status', status: 'started', date });

  // Track as active — kill method aborts all child processes
  var pipelineHandle = {
    killed: false,
    kill: function() {
      this.killed = true;
      // Tüm aktif Claude process'lerini öldür
      var aborts = runPipeline._currentAborts || [];
      aborts.forEach(function(abort) { abort(); });
    }
  };
  activeProcesses.set(ws, pipelineHandle);

  runPipeline({
    date: date,
    preferences: preferences,
    outputDir: RECETTES_DIR,
    onProgress: function(phase, detail) {
      if (pipelineHandle.killed) return;
      sendJSON(ws, { type: 'pipeline-progress', phase: phase, detail: detail });
    }
  }).then(function(result) {
    activeProcesses.delete(ws);
    sendJSON(ws, {
      type: 'result',
      success: true,
      duration: result.totalDuration,
      cost: result.totalCost
    });
    sendJSON(ws, {
      type: 'status',
      status: 'completed',
      date: date
    });
  }).catch(function(err) {
    activeProcesses.delete(ws);
    sendJSON(ws, { type: 'error', message: 'Pipeline hatası: ' + err.message });
    sendJSON(ws, { type: 'status', status: 'error' });
  });
}
```

- [ ] **Step 3: handleStop'u güncelle**

Pipeline tek bir process değil, birden fazla process olabilir. Basit bir `killed` flag'i yeterli:

Mevcut `handleStop` zaten SIGTERM gönderiyor ama pipeline'da child process'ler `runClaude` içinde. Şimdilik `pipelineActive.killed = true` flag'ini kullanarak progress callback'leri durdurmak yeterli.

---

### Task 7: Dashboard UI — Pipeline İlerleme Göstergesi

**Files:**
- Modify: `public/index.html`

Yeni `pipeline-progress` mesaj tipini handle et. Kategori bazlı ilerleme göster.

- [ ] **Step 1: CSS ekle — ilerleme çubukları**

```css
/* === Pipeline Progress === */
.pipeline-progress {
  max-width: 1200px;
  margin: 1rem auto;
  padding: 0 1rem;
}

.progress-phase {
  margin-bottom: 1rem;
}

.progress-phase h3 {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.progress-bar-container {
  background: var(--border);
  border-radius: 999px;
  height: 8px;
  overflow: hidden;
  margin-bottom: 0.3rem;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.3s ease;
  background: linear-gradient(90deg, #22c55e, #3b82f6);
}

.progress-items {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.progress-item {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  background: var(--bg-tag);
  color: var(--text-secondary);
  transition: all 0.3s;
}

.progress-item.done {
  background: #22c55e;
  color: white;
}

.progress-item.error {
  background: #ef4444;
  color: white;
}
```

- [ ] **Step 2: Pipeline progress HTML container**

Stream panel'den sonra, recipes container'dan önce ekle:

```html
<section id="pipeline-progress" style="display:none">
  <div class="pipeline-progress">
    <div class="progress-phase" id="phase-search">
      <h3>🔍 Aşama 1: Kategori Araması <span id="search-count">0/8</span></h3>
      <div class="progress-bar-container"><div class="progress-bar-fill" id="search-bar" style="width:0%"></div></div>
      <div class="progress-items" id="search-items"></div>
    </div>
    <div class="progress-phase" id="phase-extract" style="display:none">
      <h3>📄 Aşama 2: Reçete Detayları <span id="extract-count">0/0</span></h3>
      <div class="progress-bar-container"><div class="progress-bar-fill" id="extract-bar" style="width:0%"></div></div>
      <div class="progress-items" id="extract-items"></div>
    </div>
    <div class="progress-phase" id="phase-render" style="display:none">
      <h3>✨ Aşama 3: HTML Oluşturuluyor...</h3>
    </div>
  </div>
</section>
```

- [ ] **Step 3: Pipeline progress handler JS**

```javascript
var pipelineState = { searchTotal: 8, searchDone: 0, extractTotal: 0, extractDone: 0 };

function handlePipelineProgress(msg) {
  var panel = document.getElementById('pipeline-progress');
  panel.style.display = 'block';

  switch (msg.phase) {
    case 'search-start':
      pipelineState.searchTotal = msg.detail.total;
      pipelineState.searchDone = 0;
      // Kategori pill'lerini oluştur
      var items = document.getElementById('search-items');
      items.innerHTML = '';
      var cats = ['Viennoiserie','Tart','Entremets','Petit Gâteau','Çikolata','Trend','Uluslararası','Sandviç'];
      cats.forEach(function(c) {
        var span = document.createElement('span');
        span.className = 'progress-item';
        span.textContent = c;
        span.id = 'search-' + c.toLowerCase().replace(/[^a-z]/g, '');
        items.appendChild(span);
      });
      break;

    case 'search-done':
      pipelineState.searchDone++;
      document.getElementById('search-count').textContent = pipelineState.searchDone + '/' + pipelineState.searchTotal;
      document.getElementById('search-bar').style.width = (pipelineState.searchDone / pipelineState.searchTotal * 100) + '%';
      // Pill'i yeşil yap
      appendStreamLog('✅ ' + msg.detail.category + ' — reçeteler bulundu', 'tool');
      break;

    case 'search-error':
      appendStreamLog('❌ ' + msg.detail.category + ' — ' + msg.detail.error, 'error');
      pipelineState.searchDone++;
      document.getElementById('search-count').textContent = pipelineState.searchDone + '/' + pipelineState.searchTotal;
      document.getElementById('search-bar').style.width = (pipelineState.searchDone / pipelineState.searchTotal * 100) + '%';
      break;

    case 'search-complete':
      appendStreamLog('🔍 Arama tamamlandı — ' + msg.detail.found + ' reçete bulundu', 'info');
      break;

    case 'extract-start':
      pipelineState.extractTotal = msg.detail.total;
      pipelineState.extractDone = 0;
      document.getElementById('phase-extract').style.display = 'block';
      document.getElementById('extract-count').textContent = '0/' + msg.detail.total;
      break;

    case 'extract-done':
      pipelineState.extractDone++;
      document.getElementById('extract-count').textContent = pipelineState.extractDone + '/' + pipelineState.extractTotal;
      document.getElementById('extract-bar').style.width = (pipelineState.extractDone / pipelineState.extractTotal * 100) + '%';
      appendStreamLog('📄 ' + msg.detail.recipe + ' detayları çıkarıldı', 'tool');
      break;

    case 'extract-error':
      pipelineState.extractDone++;
      document.getElementById('extract-count').textContent = pipelineState.extractDone + '/' + pipelineState.extractTotal;
      document.getElementById('extract-bar').style.width = (pipelineState.extractDone / pipelineState.extractTotal * 100) + '%';
      appendStreamLog('⚠️ ' + msg.detail.recipe + ' — fallback kullanıldı', 'warn');
      break;

    case 'extract-complete':
      appendStreamLog('📄 Çıkarma tamamlandı — ' + msg.detail.extracted + ' reçete', 'info');
      break;

    case 'render-start':
      document.getElementById('phase-render').style.display = 'block';
      appendStreamLog('✨ HTML render ediliyor...', 'info');
      break;

    case 'complete':
      panel.style.display = 'none';
      var sec = (msg.detail.duration / 1000).toFixed(1);
      var cost = msg.detail.cost.toFixed(4);
      appendStreamLog('🎉 Tamamlandı — ' + msg.detail.recipeCount + ' reçete, ' + sec + 's, $' + cost, 'info');
      break;
  }
}
```

- [ ] **Step 4: handleMessage'a pipeline-progress ekle**

```javascript
case 'pipeline-progress': handlePipelineProgress(msg); break;
```

- [ ] **Step 5: startScout'ta pipeline progress panelini sıfırla**

`startScout` fonksiyonuna ekle:

```javascript
document.getElementById('pipeline-progress').style.display = 'none';
document.getElementById('search-bar').style.width = '0%';
document.getElementById('extract-bar').style.width = '0%';
document.getElementById('phase-extract').style.display = 'none';
document.getElementById('phase-render').style.display = 'none';
document.getElementById('search-items').innerHTML = '';
```

---

### Task 8: scout.sh — Pipeline Uyumu (Opsiyonel)

**Files:**
- Modify: `scout.sh`

CLI/cron kullanımı için scout.sh'ı da pipeline'a yönlendir.

- [ ] **Step 1: scout.sh'ı Node.js üzerinden çalıştır**

```bash
#!/bin/bash
# Reçete Scout Agent — Her gün 8 kategoriden 16 reçete keşfeder (paralel pipeline)
#
# Kullanım:
#   ./scout.sh
#
# Çıktı: ~/recettes/YYYY-MM-DD.html

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATE=$(date +%Y-%m-%d)

echo "📅 $DATE — Reçete Scout başlıyor (paralel pipeline)..."

node -e "
var { runPipeline } = require('$SCRIPT_DIR/lib/pipeline');
runPipeline({
  date: '$DATE',
  outputDir: require('os').homedir() + '/recettes',
  preferences: (function() { try { return require('fs').readFileSync('$SCRIPT_DIR/data/preferences.json', 'utf-8'); } catch(e) { return ''; } })(),
  onProgress: function(phase, detail) {
    if (phase === 'search-done') console.log('🔍 ' + detail.category + ' bulundu');
    if (phase === 'extract-done') console.log('📄 ' + detail.recipe + ' çıkarıldı');
    if (phase === 'complete') console.log('✅ Tamamlandı — ' + detail.recipeCount + ' reçete, ' + (detail.duration/1000).toFixed(1) + 's, \$' + detail.cost.toFixed(4));
  }
}).then(function() { process.exit(0); }).catch(function(e) { console.error('❌ Hata:', e.message); process.exit(1); });
"
```

---

## Notlar

- Mevcut tek-agent yaklaşımı (server.js'deki eski handleScout) tamamen kaldırılıyor
- `prompts/system.md` korunuyor — sadece learn.sh ve referans olarak kullanılır
- `templates/report.html` korunuyor — renderer.js CSS/JS'ini buradan alır
- 8 Sonnet arama + 16 Haiku çıkarma = 24 paralel Claude çağrısı
- Tahmini maliyet: ~$0.30-0.50 (eski: ~$2.70)
- Tahmini süre: ~2-3 dakika (eski: ~10 dakika)
- Rate limiting riski: 16 paralel Haiku spawn'u rate limit'e çarpabilir. Gerekirse concurrency limiter eklenebilir.
- `toolAccumulator` ve `parseClaudeEvent` kodu server.js'te kalıyor — handleLearn için hala kullanılabilir

## Review Düzeltmeleri

1. **C1**: `runClaude` artık `{ promise, abort }` döndürüyor. Pipeline tüm abort handle'ları topluyor. `handleStop` ve `ws.on('close')` abort'ları çağırabiliyor.
2. **C3**: Duplicate `extract-start` kaldırıldı — sadece gerçek total ile bir kez emit ediliyor.
3. **I7**: `pipelineHandle` artık `.kill()` method'u olan bir obje — `ws.on('close')` handler crash etmez.
