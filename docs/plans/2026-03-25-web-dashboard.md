# Recipe Scout Web Dashboard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tüm agent işlemlerini (keşif, puanlama, öğrenme) tek bir web sayfasından canlı streaming ile yönetmek.

**Architecture:** Node.js sunucu `claude` CLI'ı `--output-format stream-json` ile spawn eder, stdout'u WebSocket üzerinden tarayıcıya canlı akıtır. Tek sayfa dashboard: kontrol paneli + canlı akış log'u + reçete kartları + puanlama + tercih profili. `scout.sh` ve `learn.sh` cron/CLI kullanımı için korunur.

**Tech Stack:** Node.js (built-in `http`, `fs`, `path`, `child_process`), `ws` (tek bağımlılık), vanilla HTML/CSS/JS

---

## Dosya Yapısı

```
recete-agent/
├── server.js              # Create: HTTP + WebSocket sunucu
├── package.json           # Create: ws bağımlılığı
├── public/
│   └── index.html         # Create: tek sayfa dashboard
├── prompts/system.md      # Unchanged
├── templates/report.html  # Unchanged (referans şablon)
├── scout.sh               # Unchanged (CLI/cron kullanımı)
├── learn.sh               # Unchanged (CLI/cron kullanımı)
├── data/                  # Unchanged
└── README.md              # Modify: web dashboard kullanımı ekle
```

---

### Task 1: Node.js Proje Kurulumu

**Files:**
- Create: `package.json`

- [ ] **Step 1: package.json oluştur**

```json
{
  "name": "recete-scout",
  "version": "2.0.0",
  "description": "Reçete Scout Agent — Web Dashboard",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "node server.js"
  },
  "dependencies": {
    "ws": "^8.18.0"
  }
}
```

- [ ] **Step 2: Bağımlılıkları yükle**

```bash
cd /Users/sertanacikgoz/Developer/recete-agent
npm install
```

Expected: `node_modules/` oluşur, `package-lock.json` oluşur.

- [ ] **Step 3: .gitignore oluştur**

Create: `/Users/sertanacikgoz/Developer/recete-agent/.gitignore`

```
node_modules/
```

---

### Task 2: WebSocket Sunucu — `server.js`

**Files:**
- Create: `server.js`

Sunucu iki iş yapar:
1. `public/` dizininden statik dosya servisi (HTTP)
2. WebSocket üzerinden agent komutları (scout, learn, save-scores, get-preferences)

- [ ] **Step 1: HTTP statik dosya sunucusu**

```javascript
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const PUBLIC_DIR = path.join(__dirname, 'public');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.svg': 'image/svg+xml'
};

const server = http.createServer((req, res) => {
  let filePath = path.join(PUBLIC_DIR, req.url === '/' ? 'index.html' : req.url);
  const ext = path.extname(filePath);
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';

  // Path traversal koruması
  const resolved = path.resolve(filePath);
  if (!resolved.startsWith(PUBLIC_DIR)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
  });
});

server.listen(PORT, () => {
  console.log(`🚀 Reçete Scout Dashboard: http://localhost:${PORT}`);
});
```

- [ ] **Step 2: WebSocket entegrasyonu**

```javascript
const { WebSocketServer } = require('ws');
const { spawn } = require('child_process');

const wss = new WebSocketServer({ server });

// Track active child process per connection
const activeProcesses = new Map();

wss.on('connection', (ws) => {
  console.log('Client connected');

  ws.on('message', (raw) => {
    let msg;
    try {
      msg = JSON.parse(raw);
    } catch {
      ws.send(JSON.stringify({ type: 'error', message: 'Invalid JSON' }));
      return;
    }

    switch (msg.type) {
      case 'scout':
        handleScout(ws);
        break;
      case 'learn':
        handleLearn(ws);
        break;
      case 'save-scores':
        handleSaveScores(ws, msg.data);
        break;
      case 'get-preferences':
        handleGetPreferences(ws);
        break;
      case 'get-result':
        handleGetResult(ws, msg.date);
        break;
      case 'stop':
        handleStop(ws);
        break;
    }
  });

  ws.on('close', () => {
    // Kill any active process for this connection
    const proc = activeProcesses.get(ws);
    if (proc) {
      proc.kill('SIGTERM');
      activeProcesses.delete(ws);
    }
  });
});
```

- [ ] **Step 3: Scout handler — Claude CLI streaming**

Bu fonksiyon `scout.sh`'ın yaptığını yapar ama streaming ile:

```javascript
const SCRIPT_DIR = __dirname;
const RECETTES_DIR = path.join(require('os').homedir(), 'recettes');

function handleScout(ws) {
  // Prevent concurrent runs
  if (activeProcesses.has(ws)) {
    ws.send(JSON.stringify({ type: 'error', message: 'Zaten bir işlem çalışıyor.' }));
    return;
  }

  const date = new Date().toISOString().split('T')[0];
  const outputDir = RECETTES_DIR;
  const scoresDir = path.join(outputDir, 'scores');
  const prefsFile = path.join(SCRIPT_DIR, 'data', 'preferences.json');
  const systemPrompt = fs.readFileSync(path.join(SCRIPT_DIR, 'prompts', 'system.md'), 'utf8');
  const template = fs.readFileSync(path.join(SCRIPT_DIR, 'templates', 'report.html'), 'utf8');

  // Ensure directories exist
  fs.mkdirSync(outputDir, { recursive: true });
  fs.mkdirSync(scoresDir, { recursive: true });

  // Read preferences
  let preferences = 'Henüz tercih verisi yok. Kendi en iyi yargını kullan.';
  try {
    preferences = fs.readFileSync(prefsFile, 'utf8');
  } catch {}

  // Build the full prompt (same as scout.sh)
  const fullPrompt = `${systemPrompt}

## Tercih Profili (Öğrenilen)

${preferences}

## HTML Şablon (bu yapıyı AYNEN takip et, sadece içerik kısımlarını doldur)

${template}

## Çıktı
Bugünün tarihi: ${date}
Sonucu ${date}.html dosyasına yaz (mevcut dizine).
HTML şablonundaki placeholder'ları gerçek reçete verileriyle doldur.
CSS ve JavaScript kodunu AYNEN koru, değiştirme.
{{TARIH}} placeholder'larını ${date} ile değiştir.`;

  ws.send(JSON.stringify({ type: 'status', status: 'started', date }));

  const child = spawn('claude', [
    '-p', fullPrompt,
    '--output-format', 'stream-json',
    '--verbose',
    '--bare',
    '--allowedTools', 'WebSearch,WebFetch,Read,Write',
    '--max-budget-usd', '5'
  ], {
    cwd: outputDir,
    env: { ...process.env }
  });

  activeProcesses.set(ws, child);

  let buffer = '';

  child.stdout.on('data', (chunk) => {
    buffer += chunk.toString();
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Keep incomplete line in buffer

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const event = JSON.parse(line);
        const parsed = parseClaudeEvent(event);
        if (parsed) {
          ws.send(JSON.stringify(parsed));
        }
      } catch {}
    }
  });

  child.stderr.on('data', (chunk) => {
    // stderr'i de log olarak gönder
    ws.send(JSON.stringify({ type: 'log', level: 'warn', message: chunk.toString() }));
  });

  child.on('close', (code) => {
    activeProcesses.delete(ws);
    ws.send(JSON.stringify({
      type: 'status',
      status: code === 0 ? 'completed' : 'error',
      date,
      outputFile: path.join(outputDir, `${date}.html`)
    }));
  });
}
```

- [ ] **Step 4: Claude stream event parser**

Claude CLI stream-json çıktısını kullanıcı dostu mesajlara dönüştür:

```javascript
// Track tool use accumulation for streaming
const toolAccumulator = {};

function parseClaudeEvent(event) {
  switch (event.type) {
    case 'system':
      if (event.subtype === 'init') {
        return { type: 'log', level: 'info', message: 'Agent başlatıldı' };
      }
      return null;

    // Streaming events — these carry the actual live data
    case 'content_block_start':
      if (event.content_block && event.content_block.type === 'tool_use') {
        // Tool use başladı — tool adını hemen göster
        const toolName = event.content_block.name;
        const index = event.index;
        toolAccumulator[index] = { name: toolName, inputJson: '' };
        return {
          type: 'tool',
          tool: toolName,
          message: `🔧 ${toolName} çalışıyor...`,
          detail: ''
        };
      }
      return null;

    case 'content_block_delta':
      if (event.delta) {
        // Text streaming — canlı metin parçaları
        if (event.delta.type === 'text_delta') {
          return { type: 'assistant-text', text: event.delta.text };
        }
        // Tool input streaming — JSON parçalarını biriktir
        if (event.delta.type === 'input_json_delta') {
          const index = event.index;
          if (toolAccumulator[index]) {
            toolAccumulator[index].inputJson += event.delta.partial_json;
          }
          return null; // Parça parça göstermeye gerek yok
        }
      }
      return null;

    case 'content_block_stop':
      // Tool use tamamlandı — biriken JSON'dan detay çıkar
      const index = event.index;
      if (toolAccumulator[index]) {
        const tool = toolAccumulator[index];
        let input = {};
        try { input = JSON.parse(tool.inputJson); } catch {}
        delete toolAccumulator[index];
        return parseToolUse({ name: tool.name, input });
      }
      return null;

    // Final summary events
    case 'assistant':
      // Bu sadece tamamlanmış mesaj — streaming zaten content_block_delta ile geldi
      return null;

    case 'result':
      return {
        type: 'result',
        success: event.subtype === 'success',
        duration: event.duration_ms,
        cost: event.total_cost_usd
      };

    default:
      return null;
  }
}

function parseToolUse(block) {
  const toolName = block.name;
  const input = block.input || {};

  switch (toolName) {
    case 'WebSearch':
      return {
        type: 'tool',
        tool: 'search',
        message: `🔍 Arıyor: ${input.query || ''}`,
        detail: input.query
      };
    case 'WebFetch':
      return {
        type: 'tool',
        tool: 'fetch',
        message: `📄 Kaynak okunuyor: ${input.url || ''}`,
        detail: input.url
      };
    case 'Write':
      return {
        type: 'tool',
        tool: 'write',
        message: `✍️ Dosya yazılıyor: ${input.file_path || ''}`,
        detail: input.file_path
      };
    case 'Read':
      return {
        type: 'tool',
        tool: 'read',
        message: `📖 Dosya okunuyor: ${input.file_path || ''}`,
        detail: input.file_path
      };
    default:
      return {
        type: 'tool',
        tool: toolName,
        message: `🔧 ${toolName}`,
        detail: JSON.stringify(input).substring(0, 200)
      };
  }
}
```

- [ ] **Step 5: Learn handler**

```javascript
function handleLearn(ws) {
  if (activeProcesses.has(ws)) {
    ws.send(JSON.stringify({ type: 'error', message: 'Zaten bir işlem çalışıyor.' }));
    return;
  }

  ws.send(JSON.stringify({ type: 'status', status: 'learning-started' }));

  const child = spawn('bash', [path.join(SCRIPT_DIR, 'learn.sh')], {
    cwd: SCRIPT_DIR,
    env: { ...process.env }
  });

  activeProcesses.set(ws, child);

  child.stdout.on('data', (chunk) => {
    ws.send(JSON.stringify({ type: 'log', level: 'info', message: chunk.toString() }));
  });

  child.stderr.on('data', (chunk) => {
    ws.send(JSON.stringify({ type: 'log', level: 'warn', message: chunk.toString() }));
  });

  child.on('close', (code) => {
    activeProcesses.delete(ws);
    ws.send(JSON.stringify({
      type: 'status',
      status: code === 0 ? 'learning-completed' : 'learning-error'
    }));
    // Preferences güncellenmiş olabilir, gönder
    if (code === 0) handleGetPreferences(ws);
  });
}
```

- [ ] **Step 6: Score save / preferences read / result read handlers**

```javascript
function handleSaveScores(ws, data) {
  if (!data || !data.tarih || !/^\d{4}-\d{2}-\d{2}$/.test(data.tarih)) {
    ws.send(JSON.stringify({ type: 'error', message: 'Geçersiz puan verisi veya tarih formatı.' }));
    return;
  }

  const scoresDir = path.join(RECETTES_DIR, 'scores');
  fs.mkdirSync(scoresDir, { recursive: true });

  const filePath = path.join(scoresDir, `${data.tarih}-scores.json`);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');

  ws.send(JSON.stringify({
    type: 'status',
    status: 'scores-saved',
    file: filePath
  }));
}

function handleGetPreferences(ws) {
  const prefsFile = path.join(SCRIPT_DIR, 'data', 'preferences.json');
  try {
    const prefs = JSON.parse(fs.readFileSync(prefsFile, 'utf8'));
    ws.send(JSON.stringify({ type: 'preferences', data: prefs }));
  } catch {
    ws.send(JSON.stringify({ type: 'preferences', data: null }));
  }
}

function handleGetResult(ws, date) {
  if (!date) date = new Date().toISOString().split('T')[0];
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    ws.send(JSON.stringify({ type: 'error', message: 'Geçersiz tarih formatı.' }));
    return;
  }
  const filePath = path.join(RECETTES_DIR, `${date}.html`);

  try {
    const html = fs.readFileSync(filePath, 'utf8');
    ws.send(JSON.stringify({ type: 'result-html', date, html }));
  } catch {
    ws.send(JSON.stringify({ type: 'error', message: `${date}.html bulunamadı.` }));
  }
}

function handleStop(ws) {
  const proc = activeProcesses.get(ws);
  if (proc) {
    proc.kill('SIGTERM');
    activeProcesses.delete(ws);
    ws.send(JSON.stringify({ type: 'status', status: 'stopped' }));
  }
}
```

- [ ] **Step 7: server.js'i birleştir ve doğrula**

Tüm parçaları tek `server.js` dosyasında birleştir. Çalıştır:
```bash
node server.js
# Expected: 🚀 Reçete Scout Dashboard: http://localhost:3000
# Ctrl+C ile kapat
```

---

### Task 3: Dashboard UI — `public/index.html`

**Files:**
- Create: `public/index.html`

Tek sayfa, 4 ana bölüm: Kontrol + Canlı Akış + Reçete Kartları + Tercih Profili

- [ ] **Step 1: HTML iskeleti**

```html
<!DOCTYPE html>
<html lang="tr" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reçete Scout — Dashboard</title>
</head>
<body>
  <!-- 1. Header / Kontrol Paneli -->
  <header id="control-panel">
    <div class="header-top">
      <h1>Reçete Scout</h1>
      <div class="header-actions">
        <button type="button" id="btn-scout" onclick="startScout()">Reçete Getir</button>
        <button type="button" id="btn-learn" onclick="startLearn()">Öğren</button>
        <button type="button" id="btn-stop" onclick="stopAgent()" style="display:none">Durdur</button>
        <button type="button" id="btn-save" onclick="saveScores()" disabled>Puanları Kaydet</button>
        <button type="button" onclick="toggleTheme()" class="theme-toggle" title="Tema Değiştir">🌓</button>
      </div>
    </div>
    <div class="status-bar" id="status-bar">
      <span class="status-dot" id="status-dot"></span>
      <span id="status-text">Hazır</span>
      <span id="status-detail"></span>
    </div>
  </header>

  <!-- 2. Canlı Akış Paneli -->
  <section id="stream-panel" class="collapsed">
    <div class="stream-header" onclick="toggleStreamPanel()">
      <h2>Canlı Akış</h2>
      <span class="toggle-arrow">▼</span>
    </div>
    <div class="stream-content">
      <div id="stream-log"></div>
    </div>
  </section>

  <!-- 3. Reçete Kartları -->
  <main id="recipes-container">
    <p class="empty-state" id="empty-state">
      Henüz reçete yok. "Reçete Getir" butonuna tıklayarak başlayın.
    </p>
    <!-- Reçete kartları dinamik olarak buraya eklenir -->
  </main>

  <!-- 4. Tercih Profili -->
  <section id="preferences-panel">
    <h2>Tercih Profili</h2>
    <div id="preferences-content">
      <p class="empty-state">Henüz tercih profili oluşturulmamış.</p>
    </div>
  </section>

  <style>/* inline CSS */</style>
  <script>/* inline JS */</script>
</body>
</html>
```

- [ ] **Step 2: CSS tasarımı**

Gereksinimler:
- Aynı design system (report.html ile uyumlu CSS custom properties)
- Sticky header: kontrol paneli + status bar
- Stream panel: açılır/kapanır (default collapsed), max-height ile scroll
- Stream log: terminal tarzı, koyu arka plan, monospace font
  - Tool mesajları renkli ikonlarla (🔍 mavi, 📄 yeşil, ✍️ turuncu)
  - Yeni mesajlar alta eklenir, otomatik scroll
- Reçete kartları: report.html'deki card tasarımıyla aynı grid layout
- Puanlama formu: aynı stars/tags/comment tasarımı
- Tercih profili: JSON ağacı veya formatlı tablo
- Status bar animasyonu: çalışırken pulse, idle'da sabit
- Dark mode desteği
- Responsive (mobile-first)
- Butonlar: scout=yeşil, learn=mavi, save=turuncu, çalışırken disabled+spinner

- [ ] **Step 3: WebSocket bağlantısı ve mesaj yönetimi**

```javascript
// === WebSocket Connection ===
let ws;
let reconnectTimer;

function connect() {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  ws = new WebSocket(`${protocol}//${location.host}`);

  ws.onopen = () => {
    updateStatus('connected', 'Bağlandı');
    // Sayfa açıldığında mevcut tercihleri yükle
    ws.send(JSON.stringify({ type: 'get-preferences' }));
    // Bugünkü sonuç varsa yükle
    ws.send(JSON.stringify({ type: 'get-result', date: getTodayDate() }));
  };

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    handleMessage(msg);
  };

  ws.onclose = () => {
    updateStatus('disconnected', 'Bağlantı koptu');
    reconnectTimer = setTimeout(connect, 3000);
  };

  ws.onerror = () => {
    ws.close();
  };
}

function handleMessage(msg) {
  switch (msg.type) {
    case 'status':
      handleStatusMessage(msg);
      break;
    case 'tool':
      appendStreamLog(msg.message, 'tool');
      break;
    case 'assistant-text':
      appendStreamLog(msg.text, 'assistant');
      break;
    case 'log':
      appendStreamLog(msg.message, msg.level);
      break;
    case 'result':
      handleResult(msg);
      break;
    case 'result-html':
      renderRecipes(msg.html, msg.date);
      break;
    case 'preferences':
      renderPreferences(msg.data);
      break;
    case 'error':
      appendStreamLog(msg.message, 'error');
      break;
  }
}

function getTodayDate() {
  return new Date().toISOString().split('T')[0];
}
```

- [ ] **Step 4: Scout / Learn / Stop kontrolleri**

```javascript
function startScout() {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;

  // UI durumunu güncelle
  setButtonsRunning(true);
  clearStreamLog();
  expandStreamPanel();
  updateStatus('running', 'Reçete arıyor...');

  ws.send(JSON.stringify({ type: 'scout' }));
}

function startLearn() {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;

  setButtonsRunning(true);
  clearStreamLog();
  expandStreamPanel();
  updateStatus('running', 'Öğreniyor...');

  ws.send(JSON.stringify({ type: 'learn' }));
}

function stopAgent() {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  ws.send(JSON.stringify({ type: 'stop' }));
}

function handleStatusMessage(msg) {
  switch (msg.status) {
    case 'started':
      updateStatus('running', `Keşif başladı — ${msg.date}`);
      break;
    case 'completed':
      updateStatus('success', 'Tamamlandı!');
      setButtonsRunning(false);
      // Sonuçları yükle
      ws.send(JSON.stringify({ type: 'get-result', date: msg.date || getTodayDate() }));
      break;
    case 'error':
      updateStatus('error', 'Hata oluştu');
      setButtonsRunning(false);
      break;
    case 'learning-started':
      updateStatus('running', 'Tercihler analiz ediliyor...');
      break;
    case 'learning-completed':
      updateStatus('success', 'Öğrenme tamamlandı!');
      setButtonsRunning(false);
      break;
    case 'learning-error':
      updateStatus('error', 'Öğrenme hatası');
      setButtonsRunning(false);
      break;
    case 'scores-saved':
      updateStatus('success', 'Puanlar kaydedildi!');
      appendStreamLog(`Puanlar kaydedildi: ${msg.file}`, 'info');
      break;
    case 'stopped':
      updateStatus('idle', 'Durduruldu');
      setButtonsRunning(false);
      break;
  }
}

function handleResult(msg) {
  const duration = msg.duration ? `${(msg.duration / 1000).toFixed(1)}s` : 'bilinmiyor';
  const cost = msg.cost != null ? `$${msg.cost.toFixed(4)}` : 'bilinmiyor';
  appendStreamLog(`Tamamlandı — Süre: ${duration}, Maliyet: ${cost}`, 'info');
}

function setButtonsRunning(running) {
  document.getElementById('btn-scout').disabled = running;
  document.getElementById('btn-learn').disabled = running;
  document.getElementById('btn-stop').style.display = running ? 'inline-block' : 'none';
  if (running) {
    document.getElementById('btn-scout').textContent = 'Çalışıyor...';
  } else {
    document.getElementById('btn-scout').textContent = 'Reçete Getir';
  }
}
```

- [ ] **Step 5: Stream log paneli**

```javascript
const MAX_LOG_ENTRIES = 500;

function appendStreamLog(message, level) {
  const log = document.getElementById('stream-log');
  const entry = document.createElement('div');
  entry.className = `log-entry log-${level}`;

  const time = new Date().toLocaleTimeString('tr-TR');
  entry.innerHTML = `<span class="log-time">${time}</span> ${escapeHtml(message)}`;

  log.appendChild(entry);

  // Limit log entries
  while (log.children.length > MAX_LOG_ENTRIES) {
    log.removeChild(log.firstChild);
  }

  // Auto-scroll
  log.scrollTop = log.scrollHeight;
}

function clearStreamLog() {
  document.getElementById('stream-log').innerHTML = '';
}

function toggleStreamPanel() {
  document.getElementById('stream-panel').classList.toggle('collapsed');
}

function expandStreamPanel() {
  document.getElementById('stream-panel').classList.remove('collapsed');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
```

- [ ] **Step 6: Reçete kartlarını render etme**

Agent HTML çıktısını alıp dashboard'a reçete kartlarını enjekte et:

```javascript
function renderRecipes(html, date) {
  const container = document.getElementById('recipes-container');
  const emptyState = document.getElementById('empty-state');

  // Parse agent HTML to extract recipe cards
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');
  const cards = doc.querySelectorAll('.recipe-card');

  if (cards.length === 0) {
    emptyState.textContent = 'HTML parse edilemedi veya reçete kartı bulunamadı.';
    return;
  }

  // Kategori bölümlerini de al
  const categories = doc.querySelectorAll('.category');

  // Mevcut içeriği temizle
  container.innerHTML = '';

  // Kategori bölümlerini kopyala
  categories.forEach(cat => {
    const section = document.createElement('section');
    section.className = 'category';
    section.id = cat.id;

    const heading = cat.querySelector('h2');
    if (heading) {
      const h2 = document.createElement('h2');
      h2.textContent = heading.textContent;
      section.appendChild(h2);
    }

    const grid = document.createElement('div');
    grid.className = 'card-grid';

    // Bu kategorideki kartları bul
    const catCards = cat.querySelectorAll('.recipe-card');
    catCards.forEach(card => {
      const cloned = card.cloneNode(true);
      // Puanlama formunu yeniden oluştur (event listeners için)
      addScoringForm(cloned);
      grid.appendChild(cloned);
    });

    section.appendChild(grid);
    container.appendChild(section);
  });

  // Complexity barlarını render et
  renderComplexityBars();

  // Mevcut puanları localStorage'dan yükle
  loadScoresFromStorage(date);

  // Puanla ve Kaydet butonunu etkinleştir
  document.getElementById('btn-save').disabled = false;

  // Tarih bilgisini sakla
  container.dataset.date = date;

  updateStatus('idle', `${date} — ${cards.length} reçete yüklendi`);
}

function addScoringForm(card) {
  // Eğer varolan scoring-form varsa sil (agent HTML'den gelmiş olabilir)
  const existingForm = card.querySelector('.scoring-form');
  if (existingForm) existingForm.remove();

  const form = document.createElement('div');
  form.className = 'scoring-form';

  form.innerHTML = `
    <div class="stars">
      <label>Puan:</label>
      ${[1,2,3,4,5].map(v => `<button type="button" class="star" data-value="${v}">★</button>`).join('')}
    </div>
    <div class="tags">
      <label>Etiketler:</label>
      ${['teknik','yaratici','klasik','sunum','uygulanabilir','trend','ilham','mevsimsel'].map(t =>
        `<button type="button" class="tag-btn" data-tag="${t}">${t === 'yaratici' ? 'yaratıcı' : t}</button>`
      ).join('')}
    </div>
    <textarea class="comment" placeholder="Yorum (opsiyonel)..." rows="2"></textarea>
  `;

  card.appendChild(form);

  // Attach event listeners
  attachScoringEvents(card);
}
```

- [ ] **Step 7: Puanlama mantığı (scoring)**

report.html'deki mantığın aynısı, ama WebSocket üzerinden kaydetme ekli:

```javascript
let scores = {};
let currentDate = '';

function attachScoringEvents(card) {
  const id = card.dataset.id;

  // Stars
  card.querySelectorAll('.star').forEach(star => {
    star.addEventListener('click', () => {
      const value = parseInt(star.dataset.value);
      scores[id] = scores[id] || {};
      scores[id].puan = value;
      updateStarUI(card, value);
      saveScoresToStorage();
    });
  });

  // Tags
  card.querySelectorAll('.tag-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tag = btn.dataset.tag;
      scores[id] = scores[id] || {};
      scores[id].tags = scores[id].tags || [];
      const idx = scores[id].tags.indexOf(tag);
      if (idx > -1) scores[id].tags.splice(idx, 1);
      else scores[id].tags.push(tag);
      btn.classList.toggle('selected');
      saveScoresToStorage();
    });
  });

  // Comment
  const textarea = card.querySelector('.comment');
  let saveTimer;
  textarea.addEventListener('input', () => {
    scores[id] = scores[id] || {};
    scores[id].yorum = textarea.value;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(saveScoresToStorage, 400);
  });
}

function updateStarUI(card, value) {
  card.querySelectorAll('.star').forEach(star => {
    const v = parseInt(star.dataset.value);
    star.classList.toggle('filled', v <= value);
  });
}

function saveScoresToStorage() {
  const date = document.getElementById('recipes-container').dataset.date || getTodayDate();
  localStorage.setItem(`dashboard-scores-${date}`, JSON.stringify(scores));
}

function loadScoresFromStorage(date) {
  const saved = localStorage.getItem(`dashboard-scores-${date}`);
  if (!saved) { scores = {}; return; }
  try {
    scores = JSON.parse(saved);
  } catch { scores = {}; return; }

  // Restore UI
  Object.entries(scores).forEach(([id, data]) => {
    const card = document.querySelector(`.recipe-card[data-id="${id}"]`);
    if (!card) return;
    if (data.puan) updateStarUI(card, data.puan);
    if (data.tags) {
      data.tags.forEach(tag => {
        const btn = card.querySelector(`.tag-btn[data-tag="${tag}"]`);
        if (btn) btn.classList.add('selected');
      });
    }
    if (data.yorum) {
      const textarea = card.querySelector('.comment');
      if (textarea) textarea.value = data.yorum;
    }
  });
  currentDate = date;
}

// Puanları sunucuya kaydet
function saveScores() {
  const date = document.getElementById('recipes-container').dataset.date || getTodayDate();

  // Her reçetenin meta bilgisini dahil et
  const exportData = {
    tarih: date,
    puanlamaTarihi: new Date().toISOString(),
    receteler: {}
  };

  document.querySelectorAll('.recipe-card').forEach(card => {
    const id = card.dataset.id;
    const category = card.dataset.category;
    const nameEl = card.querySelector('.recipe-name-tr');
    const sourceEl = card.querySelector('.source');
    const components = [...card.querySelectorAll('.component-tag')].map(t => t.textContent);
    const complexityEl = card.querySelector('.complexity');
    const complexity = complexityEl ? (parseInt(complexityEl.dataset.score) || 0) : 0;

    exportData.receteler[id] = {
      ad: nameEl ? nameEl.textContent : '',
      kategori: category,
      kaynak: sourceEl ? sourceEl.href : '',
      bilesenler: components,
      karmasiklik: complexity,
      ...(scores[id] || {})
    };
  });

  ws.send(JSON.stringify({ type: 'save-scores', data: exportData }));
}
```

- [ ] **Step 8: Tercih profili render**

```javascript
function renderPreferences(data) {
  const container = document.getElementById('preferences-content');

  if (!data) {
    container.innerHTML = '<p class="empty-state">Henüz tercih profili oluşturulmamış. Reçeteleri puanlayıp "Öğren" butonuna tıklayın.</p>';
    return;
  }

  let html = '';

  // Stil profili
  if (data.stil_profili) {
    html += '<div class="pref-section"><h3>Stil Profili</h3>';
    const sp = data.stil_profili;
    if (sp.tercih_edilen_bilesenler) {
      html += `<p><strong>Tercih Edilen Bileşenler:</strong> ${formatValue(sp.tercih_edilen_bilesenler)}</p>`;
    }
    if (sp.tercih_edilen_teksturler) {
      html += `<p><strong>Tekstür Kontrastları:</strong> ${formatValue(sp.tercih_edilen_teksturler)}</p>`;
    }
    if (sp.tercih_edilen_lezzet_aileleri) {
      html += `<p><strong>Lezzet Aileleri:</strong> ${formatValue(sp.tercih_edilen_lezzet_aileleri)}</p>`;
    }
    if (sp.karmasiklik_tercihi) {
      html += `<p><strong>Karmaşıklık Tercihi:</strong> ${sp.karmasiklik_tercihi}/5</p>`;
    }
    html += '</div>';
  }

  // Kaynak kalite haritası
  if (data.kaynak_kalite_haritasi) {
    html += '<div class="pref-section"><h3>Kaynak Kalitesi</h3>';
    const kk = data.kaynak_kalite_haritasi;
    if (kk.yuksek_kalite && kk.yuksek_kalite.length) {
      html += `<p><strong>Yüksek Kalite:</strong> ${formatValue(kk.yuksek_kalite)}</p>`;
    }
    if (kk.dusuk_kalite && kk.dusuk_kalite.length) {
      html += `<p><strong>Düşük Kalite:</strong> ${formatValue(kk.dusuk_kalite)}</p>`;
    }
    html += '</div>';
  }

  // Tag analizi
  if (data.tag_analizi) {
    html += '<div class="pref-section"><h3>Tag Analizi</h3>';
    html += `<p>${formatValue(data.tag_analizi)}</p></div>`;
  }

  container.innerHTML = html || '<p class="empty-state">Tercih verisi boş.</p>';
}

function formatValue(val) {
  if (Array.isArray(val)) return val.join(', ');
  if (typeof val === 'object') return JSON.stringify(val, null, 2);
  return String(val);
}
```

- [ ] **Step 9: Utility fonksiyonları ve init**

```javascript
// Status bar
function updateStatus(state, text, detail) {
  const dot = document.getElementById('status-dot');
  const textEl = document.getElementById('status-text');
  const detailEl = document.getElementById('status-detail');

  dot.className = `status-dot status-${state}`;
  textEl.textContent = text;
  if (detail) detailEl.textContent = detail;
}

// Theme
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
}

// Complexity bars (aynı mantık report.html'den)
function renderComplexityBars() {
  document.querySelectorAll('.complexity').forEach(el => {
    const score = parseInt(el.dataset.score) || 0;
    const barEl = el.querySelector('.complexity-bar');
    if (!barEl) return;
    barEl.innerHTML = '';
    for (let i = 1; i <= 5; i++) {
      const block = document.createElement('span');
      block.className = 'block' + (i <= score ? ' filled' : '');
      barEl.appendChild(block);
    }
  });
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  // Theme
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) document.documentElement.setAttribute('data-theme', savedTheme);

  // Connect WebSocket
  connect();
});
```

- [ ] **Step 10: Tüm parçaları birleştirip `public/index.html`'i yaz**

Tüm CSS inline `<style>` tag'inde, tüm JS inline `<script>` tag'inde.
CSS, `templates/report.html` ile aynı custom properties kullanmalı (tutarlılık).
Reçete kartı stili report.html'den alınmalı (copy-paste, aynı sınıf adları).

- [ ] **Step 11: Tarayıcıda doğrula**

```bash
cd /Users/sertanacikgoz/Developer/recete-agent
node server.js &
# http://localhost:3000 aç
```

Kontrol listesi:
- [ ] Sayfa yükleniyor, header ve butonlar görünüyor
- [ ] WebSocket bağlantısı kuruluyor (status: "Bağlandı")
- [ ] Dark mode toggle çalışıyor
- [ ] Stream panel açılıp kapanıyor
- [ ] "Reçete Getir"e basınca butonlar disabled oluyor
- [ ] Canlı akış mesajları görünüyor (tool kullanımı, metin)
- [ ] Tamamlandığında reçete kartları render ediliyor
- [ ] Puanlama (yıldız, tag, yorum) çalışıyor
- [ ] "Puanları Kaydet" sunucuya JSON gönderiyor
- [ ] "Öğren" butonuna basınca learn.sh çalışıyor
- [ ] Tercih profili render ediliyor
- [ ] Mobile responsive

---

### Task 4: README Güncellemesi

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Web Dashboard bölümü ekle**

README'ye ekle:

```markdown
## Web Dashboard

```bash
# Sunucuyu başlat
npm start

# Tarayıcıda aç
open http://localhost:3000
```

Dashboard'dan yapabilecekleriniz:
- **Reçete Getir** — Agent'ı çalıştırır, canlı ilerlemeyi izlersiniz
- **Puanlama** — Reçeteleri yıldız + etiket + yorum ile puanlayın
- **Puanları Kaydet** — Puanları otomatik olarak `~/recettes/scores/` klasörüne kaydeder
- **Öğren** — Puanlardan tercih profili oluşturur
- **Tercih Profili** — Öğrenilmiş tercihleri görüntüler

### Kurulum

```bash
cd /Users/sertanacikgoz/Developer/recete-agent
npm install
npm start
```
```

---

## Notlar

- `scout.sh` ve `learn.sh` değişmiyor — CLI/cron kullanımı aynen devam eder
- `server.js` aynı mantığı kullanır ama streaming ekler
- Dashboard puanları doğrudan sunucuya kaydeder — manuel JSON taşıma gereksiz
- WebSocket reconnect: bağlantı koparsa 3 saniye sonra otomatik yeniden bağlanır
- `learn.sh` kendi içinde Claude CLI çağırır (streaming olmadan) — dashboard sadece bash çıktısını gösterir
- Prompt boyutu: system prompt + HTML template (~55KB) spawn argv ile geçirilir — macOS ARG_MAX (262KB) limiti dahilinde

## Review Düzeltmeleri

1. **C1**: `complexity-block` → `block` (report.html ile uyum)
2. **C2**: `recipe-grid` → `card-grid` (report.html ile uyum)
3. **C3**: `content_block_delta`, `content_block_start`, `content_block_stop` event handling eklendi — canlı streaming artık çalışır
4. **I4**: Tool use streaming: `content_block_start`'ta tool adı gösterilir, `content_block_stop`'ta detay eklenir
5. **I6-I7**: Tarih parametrelerine `/^\d{4}-\d{2}-\d{2}$/` regex validasyonu eklendi
6. **I8**: Static file server'a path traversal koruması eklendi (`resolved.startsWith(PUBLIC_DIR)`)
7. **I9**: `.gitignore` dosya yolu belirtildi
8. **I10**: `msg.cost.toFixed()` null safety eklendi
9. **S12**: "Durdur" butonu eklendi, çalışırken görünür
