// server.js — Reçete Scout Agent WebSocket Server
// Serves static files from public/ and handles WebSocket commands
// for live-streaming Claude CLI output to the browser.

const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { WebSocketServer } = require('ws');
const { runPipeline } = require('./lib/pipeline');

// ─── Constants ───────────────────────────────────────────────────────────────

const PORT = 3000;
const PUBLIC_DIR = path.resolve(__dirname, 'public');
const SCRIPT_DIR = __dirname;
const HOME_DIR = process.env.HOME || process.env.USERPROFILE;
const RECETTES_DIR = path.join(HOME_DIR, 'recettes');
const SINGLE_RECIPES_DIR = path.join(RECETTES_DIR, 'single');

// ─── MIME Types ──────────────────────────────────────────────────────────────

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png':  'image/png',
  '.svg':  'image/svg+xml',
};

// ─── HTTP Server ─────────────────────────────────────────────────────────────

const server = http.createServer((req, res) => {
  // Only allow GET and HEAD
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.writeHead(405, { 'Content-Type': 'text/plain' });
    res.end('Method Not Allowed');
    return;
  }

  let urlPath = req.url.split('?')[0]; // strip query string
  if (urlPath === '/') urlPath = '/index.html';

  // Serve generated single recipe pages from ~/recettes/single/
  if (urlPath.startsWith('/recipes/')) {
    const recipeFile = path.basename(urlPath); // basename prevents traversal
    if (!recipeFile || recipeFile === '.') {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Not Found');
      return;
    }
    const recipePath = path.join(SINGLE_RECIPES_DIR, recipeFile);
    fs.readFile(recipePath, (err, data) => {
      if (err) {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Recipe not found');
        return;
      }
      res.writeHead(200, {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'no-store, no-cache, must-revalidate',
      });
      res.end(data);
    });
    return;
  }

  const filePath = path.join(PUBLIC_DIR, urlPath);

  // Path traversal protection
  if (!filePath.startsWith(PUBLIC_DIR)) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('Forbidden');
    return;
  }

  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, data) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
      } else {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Internal Server Error');
      }
      return;
    }
    res.writeHead(200, {
      'Content-Type': contentType,
      'Cache-Control': 'no-store, no-cache, must-revalidate',
    });
    res.end(data);
  });
});

// ─── WebSocket Server ────────────────────────────────────────────────────────

const wss = new WebSocketServer({ server });

// Track active child processes per WebSocket connection
const activeProcesses = new Map();

wss.on('connection', (ws) => {
  console.log('[WS] Client connected');

  ws.on('message', (raw) => {
    let msg;
    try {
      msg = JSON.parse(raw);
    } catch {
      sendJSON(ws, { type: 'error', message: 'Invalid JSON' });
      return;
    }

    const command = msg.type || msg.command;
    const data = msg.data || msg.date;
    console.log(`[WS] Command: ${command}, Raw: ${JSON.stringify(msg).substring(0, 200)}`);

    switch (command) {
      case 'scout':
        handleScout(ws);
        break;
      case 'learn':
        handleLearn(ws);
        break;
      case 'fetch-recipe':
        handleFetchRecipe(ws, data);
        break;
      case 'save-scores':
        handleSaveScores(ws, data);
        break;
      case 'get-preferences':
        handleGetPreferences(ws);
        break;
      case 'get-result':
        handleGetResult(ws, data);
        break;
      case 'get-single-result':
        handleGetSingleResult(ws, data);
        break;
      case 'stop':
        handleStop(ws);
        break;
      case 'add-favorite':
        handleAddFavorite(ws, data);
        break;
      case 'remove-favorite':
        handleRemoveFavorite(ws, data);
        break;
      case 'get-favorites':
        handleGetFavorites(ws);
        break;
      default:
        sendJSON(ws, { type: 'error', message: `Unknown command: ${command}` });
    }
  });

  ws.on('close', () => {
    console.log('[WS] Client disconnected');
    const handle = activeProcesses.get(ws);
    if (handle) {
      // Pipeline handle (.kill method, no .pid) vs legacy process (.pid)
      if (typeof handle.kill === 'function' && !handle.pid) {
        handle.kill();
      } else {
        killProcessTree(handle);
      }
      activeProcesses.delete(ws);
    }
  });
});

// ─── Helper: Send JSON ──────────────────────────────────────────────────────

function sendJSON(ws, obj) {
  if (ws.readyState === ws.OPEN) {
    ws.send(JSON.stringify(obj));
  }
}

function slugify(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/^https?:\/\//, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80) || 'recipe';
}

function buildRecipeJob(url) {
  const slug = slugify(url);
  const stamp = new Date().toISOString().replace(/[:.]/g, '-').toLowerCase();
  const key = `${stamp}-${slug}`;
  return {
    key,
    fileName: `${key}.html`,
    outputPath: path.join(SINGLE_RECIPES_DIR, `${key}.html`),
  };
}

function extractBlockedDomains(preferencesRaw) {
  try {
    const prefs = JSON.parse(preferencesRaw);
    const blocked = prefs.kaynak_engel_listesi || {};
    const accessList = Array.isArray(blocked.erisim_sorunlu) ? blocked.erisim_sorunlu : [];
    const avoidList = Array.isArray(blocked.kullanma_listesi) ? blocked.kullanma_listesi : [];

    function readDomain(entry) {
      if (!entry) return '';
      if (typeof entry === 'string') return entry;
      if (typeof entry.kaynak === 'string') return entry.kaynak;
      return '';
    }

    const accessDomains = accessList.map(readDomain).filter(Boolean);
    const avoidDomains = avoidList.map(readDomain).filter(Boolean);
    const allDomains = Array.from(new Set(accessDomains.concat(avoidDomains)));

    return {
      accessDomains,
      avoidDomains,
      allDomains,
    };
  } catch {
    return {
      accessDomains: [],
      avoidDomains: [],
      allDomains: [],
    };
  }
}

// ─── Claude Event Parser (Step 4) ──────────────────────────────────────────

const toolAccumulator = {};

function parseClaudeEvent(event) {
  switch (event.type) {
    case 'system':
      if (event.subtype === 'init') {
        return { type: 'log', level: 'info', message: 'Agent başlatıldı' };
      }
      return null;

    case 'content_block_start':
      if (event.content_block && event.content_block.type === 'tool_use') {
        const toolName = event.content_block.name;
        const index = event.index;
        toolAccumulator[index] = { name: toolName, inputJson: '' };
        return { type: 'tool', tool: toolName, message: `🔧 ${toolName} çalışıyor...`, detail: '' };
      }
      return null;

    case 'content_block_delta':
      if (event.delta) {
        if (event.delta.type === 'text_delta') {
          return { type: 'assistant-text', text: event.delta.text };
        }
        if (event.delta.type === 'input_json_delta') {
          const index = event.index;
          if (toolAccumulator[index]) {
            toolAccumulator[index].inputJson += event.delta.partial_json;
          }
          return null;
        }
      }
      return null;

    case 'content_block_stop': {
      const index = event.index;
      if (toolAccumulator[index]) {
        const tool = toolAccumulator[index];
        let input = {};
        try { input = JSON.parse(tool.inputJson); } catch {}
        delete toolAccumulator[index];
        return parseToolUse({ name: tool.name, input });
      }
      return null;
    }

    case 'assistant':
      return null; // Already streamed via content_block_delta

    case 'result':
      return {
        type: 'result',
        success: event.subtype === 'success' && event.is_error !== true,
        isError: event.is_error === true,
        duration: event.duration_ms,
        cost: event.total_cost_usd,
        message: event.result || '',
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
      return { type: 'tool', tool: 'search', message: `🔍 Arıyor: ${input.query || ''}`, detail: input.query };
    case 'WebFetch':
      return { type: 'tool', tool: 'fetch', message: `📄 Kaynak okunuyor: ${input.url || ''}`, detail: input.url };
    case 'Write':
      return { type: 'tool', tool: 'write', message: `✍️ Dosya yazılıyor: ${input.file_path || ''}`, detail: input.file_path };
    case 'Read':
      return { type: 'tool', tool: 'read', message: `📖 Dosya okunuyor: ${input.file_path || ''}`, detail: input.file_path };
    default:
      return { type: 'tool', tool: toolName, message: `🔧 ${toolName}`, detail: JSON.stringify(input).substring(0, 200) };
  }
}

// ─── Scout Handler — Paralel Pipeline ───────────────────────────────────────

function handleScout(ws) {
  if (activeProcesses.has(ws)) {
    sendJSON(ws, { type: 'error', message: 'Zaten çalışan bir işlem var. Önce durdurun.' });
    return;
  }

  const date = new Date().toISOString().slice(0, 10);

  // Read preferences (optional)
  let preferences = '';
  const prefsPath = path.join(SCRIPT_DIR, 'data', 'preferences.json');
  try { preferences = fs.readFileSync(prefsPath, 'utf-8'); } catch (_) {}

  // Ensure output directories exist
  fs.mkdirSync(RECETTES_DIR, { recursive: true });
  fs.mkdirSync(path.join(RECETTES_DIR, 'scores'), { recursive: true });

  sendJSON(ws, { type: 'status', status: 'started', date });

  // Pipeline handle — kill() aborts all active Claude child processes
  const pipeline = runPipeline({
    date: date,
    preferences: preferences,
    outputDir: RECETTES_DIR,
    onProgress: function(phase, detail) {
      if (pipelineHandle.killed) return;
      sendJSON(ws, { type: 'pipeline-progress', phase: phase, detail: detail });
    }
  });

  const pipelineHandle = {
    killed: false,
    kill: function() {
      this.killed = true;
      pipeline.abort();
    }
  };
  activeProcesses.set(ws, pipelineHandle);

  pipeline.promise.then(function(result) {
    activeProcesses.delete(ws);
    if (pipelineHandle.killed) return; // Stop'tan sonra completed gönderme
    sendJSON(ws, { type: 'result', success: true, duration: result.totalDuration, cost: result.totalCost });
    sendJSON(ws, { type: 'status', status: 'completed', date: date });
  }).catch(function(err) {
    activeProcesses.delete(ws);
    if (pipelineHandle.killed) return; // Stop'tan sonra hata gönderme
    sendJSON(ws, { type: 'error', message: 'Pipeline hatası: ' + err.message });
    sendJSON(ws, { type: 'status', status: 'error' });
  });
}

// ─── Learn Handler (Step 5) ─────────────────────────────────────────────────

function handleLearn(ws) {
  if (activeProcesses.has(ws)) {
    sendJSON(ws, { type: 'error', message: 'Zaten çalışan bir işlem var. Önce durdurun.' });
    return;
  }

  const learnScript = path.join(SCRIPT_DIR, 'learn.sh');

  if (!fs.existsSync(learnScript)) {
    sendJSON(ws, { type: 'error', message: 'learn.sh bulunamadı.' });
    return;
  }

  sendJSON(ws, { type: 'status', status: 'learning-started', message: 'Öğrenme başlatılıyor...' });

  const proc = spawn('bash', [learnScript], {
    cwd: SCRIPT_DIR,
    env: { ...process.env },
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: true,
  });

  activeProcesses.set(ws, proc);

  proc.stdout.on('data', (chunk) => {
    const text = chunk.toString().trim();
    if (text) {
      sendJSON(ws, { type: 'log', level: 'info', message: text });
    }
  });

  proc.stderr.on('data', (chunk) => {
    const text = chunk.toString().trim();
    if (text) {
      sendJSON(ws, { type: 'log', level: 'warn', message: text });
    }
  });

  proc.on('close', (code) => {
    activeProcesses.delete(ws);

    if (code === 0) {
      sendJSON(ws, { type: 'status', status: 'learning-completed', message: 'Öğrenme tamamlandı.' });
      // Send updated preferences
      handleGetPreferences(ws);
    } else {
      sendJSON(ws, { type: 'status', status: 'learning-error', message: `Öğrenme hata ile sonlandı (exit code: ${code})` });
    }
  });

  proc.on('error', (err) => {
    activeProcesses.delete(ws);
    sendJSON(ws, { type: 'error', message: `learn.sh başlatılamadı: ${err.message}` });
  });
}

// ─── Single Recipe Fetch Handler ────────────────────────────────────────────

function handleFetchRecipe(ws, data) {
  if (activeProcesses.has(ws)) {
    sendJSON(ws, { type: 'error', message: 'Zaten çalışan bir işlem var. Önce durdurun.' });
    return;
  }

  const url = typeof data === 'string' ? data.trim() : (data && typeof data.url === 'string' ? data.url.trim() : '');
  if (!url) {
    sendJSON(ws, { type: 'error', message: 'URL gerekli.' });
    return;
  }

  let parsedUrl;
  try {
    parsedUrl = new URL(url);
  } catch {
    sendJSON(ws, { type: 'error', message: 'Geçerli bir URL girin.' });
    return;
  }

  if (!/^https?:$/.test(parsedUrl.protocol)) {
    sendJSON(ws, { type: 'error', message: 'Sadece http/https URL desteklenir.' });
    return;
  }

  let systemPrompt;
  let template;
  try {
    systemPrompt = fs.readFileSync(path.join(SCRIPT_DIR, 'prompts', 'recipe-fetch.md'), 'utf-8');
    template = fs.readFileSync(path.join(SCRIPT_DIR, 'templates', 'recipe.html'), 'utf-8');
  } catch (err) {
    sendJSON(ws, { type: 'error', message: `Recipe prompt/template okunamadı: ${err.message}` });
    return;
  }

  fs.mkdirSync(SINGLE_RECIPES_DIR, { recursive: true });

  const job = buildRecipeJob(parsedUrl.toString());
  const fullPrompt = `${systemPrompt}

## Kaynak URL
${parsedUrl.toString()}

## HTML Şablonu
${template}

## Placeholder Doldurma Talimatı
- Tüm placeholder alanlarını gerçek veriyle değiştir.
- '{{STIL_TAGLERI}}' için birden fazla <span class="chip">...</span> üret.
- '{{MALZEMELER_HTML}}' için her bileşen grubunu <div class="malzeme-grup"> bloğu olarak yaz.
- '{{ADIMLAR_HTML}}' için her adımı <div class="adim"> bloğu olarak yaz; kısa teknik notları <p class="adim-not"> ile adım içine, kritik uyarıları <div class="puf-noktasi"> olarak adımlar arasına ekle.
- Bilgi yoksa alanı boş bırakma; kısa bir "Kaynakta belirtilmemiştir." notu yaz.

## Çıktı
- Sonucu sadece ${job.fileName} dosyasına yaz.
- Çalışma dizini zaten hedef klasördür.
- Önce URL'yi WebFetch ile oku, sonra HTML dosyasını Write ile oluştur.
- Nihai çıktı tam HTML dosyası olmalı. Markdown veya JSON üretme.`;

  sendJSON(ws, {
    type: 'status',
    status: 'single-started',
    key: job.key,
    url: parsedUrl.toString(),
    message: 'Tek reçete çekimi başlatılıyor.',
  });

  const proc = spawn('claude', [
    '-p', fullPrompt,
    '--output-format', 'stream-json',
    '--verbose',
    '--allowedTools', 'WebFetch,Read,Write',
    '--max-budget-usd', '2',
  ], {
    cwd: SINGLE_RECIPES_DIR,
    env: { ...process.env },
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: true,
  });

  activeProcesses.set(ws, proc);

  let stdoutBuffer = '';

  proc.stdout.on('data', (chunk) => {
    stdoutBuffer += chunk.toString();
    const lines = stdoutBuffer.split('\n');
    stdoutBuffer = lines.pop();

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;

      let event;
      try {
        event = JSON.parse(trimmed);
      } catch {
        sendJSON(ws, { type: 'log', level: 'debug', message: trimmed });
        continue;
      }

      const parsed = parseClaudeEvent(event);
      if (parsed) sendJSON(ws, parsed);
    }
  });

  proc.stderr.on('data', (chunk) => {
    const text = chunk.toString().trim();
    if (text) {
      sendJSON(ws, { type: 'log', level: 'warn', message: text });
    }
  });

  proc.on('close', (code) => {
    activeProcesses.delete(ws);

    if (stdoutBuffer.trim()) {
      try {
        const event = JSON.parse(stdoutBuffer.trim());
        const parsed = parseClaudeEvent(event);
        if (parsed) sendJSON(ws, parsed);
      } catch {
        // ignore
      }
    }

    if (code === 0 && fs.existsSync(job.outputPath)) {
      sendJSON(ws, {
        type: 'status',
        status: 'single-completed',
        key: job.key,
        fileName: job.fileName,
        recipeUrl: `/recipes/${job.fileName}`,
        url: parsedUrl.toString(),
        message: 'Tek reçete sayfası hazır.',
      });
    } else {
      sendJSON(ws, {
        type: 'status',
        status: 'error',
        key: job.key,
        message: fs.existsSync(job.outputPath)
          ? `Tek reçete işlemi hata ile sonlandı (exit code: ${code})`
          : 'Tek reçete HTML dosyası üretilemedi.',
      });
    }
  });

  proc.on('error', (err) => {
    activeProcesses.delete(ws);
    sendJSON(ws, { type: 'error', message: `Claude başlatılamadı: ${err.message}` });
  });
}

// ─── Save Scores Handler (Step 6) ───────────────────────────────────────────

function handleSaveScores(ws, data) {
  if (!data || !data.tarih) {
    sendJSON(ws, { type: 'error', message: 'tarih alanı gerekli.' });
    return;
  }

  if (!/^\d{4}-\d{2}-\d{2}$/.test(data.tarih)) {
    sendJSON(ws, { type: 'error', message: 'Geçersiz tarih formatı. YYYY-MM-DD olmalı.' });
    return;
  }

  const scoresDir = path.join(RECETTES_DIR, 'scores');
  fs.mkdirSync(scoresDir, { recursive: true });

  const filePath = path.join(scoresDir, `${data.tarih}-scores.json`);

  try {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
    sendJSON(ws, { type: 'status', status: 'scores-saved', message: `Puanlar kaydedildi: ${data.tarih}` });
  } catch (err) {
    sendJSON(ws, { type: 'error', message: `Puanlar kaydedilemedi: ${err.message}` });
  }
}

// ─── Get Preferences Handler (Step 6) ───────────────────────────────────────

function handleGetPreferences(ws) {
  const prefsPath = path.join(SCRIPT_DIR, 'data', 'preferences.json');

  try {
    const raw = fs.readFileSync(prefsPath, 'utf-8');
    const data = JSON.parse(raw);
    sendJSON(ws, { type: 'preferences', data });
  } catch {
    sendJSON(ws, { type: 'preferences', data: null });
  }
}

// ─── Get Result Handler (Step 6) ────────────────────────────────────────────

function handleGetResult(ws, data) {
  const date = typeof data === 'string' ? data : (data && data.date);

  if (!date || !/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    sendJSON(ws, { type: 'error', message: 'Geçersiz tarih formatı. YYYY-MM-DD olmalı.' });
    return;
  }

  const filePath = path.join(RECETTES_DIR, `${date}.html`);

  try {
    const html = fs.readFileSync(filePath, 'utf-8');
    sendJSON(ws, { type: 'result-html', date, html });
  } catch (err) {
    if (err.code === 'ENOENT') {
      sendJSON(ws, { type: 'no-result', date });
    } else {
      sendJSON(ws, { type: 'error', message: `Dosya okunamadı: ${err.message}` });
    }
  }
}

function handleGetSingleResult(ws, data) {
  const key = typeof data === 'string' ? data : (data && data.key);
  if (!key || !/^[a-z0-9-]+$/.test(key)) {
    sendJSON(ws, { type: 'error', message: 'Geçersiz reçete anahtarı.' });
    return;
  }

  const filePath = path.join(SINGLE_RECIPES_DIR, `${key}.html`);

  try {
    const html = fs.readFileSync(filePath, 'utf-8');
    sendJSON(ws, { type: 'single-result-html', key, html });
  } catch (err) {
    if (err.code === 'ENOENT') {
      sendJSON(ws, { type: 'error', message: 'Reçete çıktısı bulunamadı.' });
    } else {
      sendJSON(ws, { type: 'error', message: `Dosya okunamadı: ${err.message}` });
    }
  }
}

// ─── Stop Handler (Step 6) ──────────────────────────────────────────────────

function killProcessTree(proc) {
  try {
    // Kill the entire process group (negative PID)
    process.kill(-proc.pid, 'SIGTERM');
  } catch (e) {
    // Process group may already be dead, try killing just the process
    try { proc.kill('SIGTERM'); } catch (_) {}
  }
  // Force kill after 2 seconds if still alive
  setTimeout(() => {
    try {
      process.kill(-proc.pid, 'SIGKILL');
    } catch (_) {}
    try {
      proc.kill('SIGKILL');
    } catch (_) {}
  }, 2000);
}

function handleStop(ws) {
  const handle = activeProcesses.get(ws);
  if (handle) {
    // Pipeline handle (has .kill method) or legacy process (has .pid)
    if (typeof handle.kill === 'function' && !handle.pid) {
      handle.kill();
    } else {
      killProcessTree(handle);
    }
    activeProcesses.delete(ws);
    sendJSON(ws, { type: 'status', status: 'stopped', message: 'İşlem durduruldu.' });
  } else {
    sendJSON(ws, { type: 'status', status: 'stopped', message: 'Çalışan işlem yok.' });
  }
}

// ─── Favorites Handlers ─────────────────────────────────────────────────────

const FAVORITES_FILE = path.join(SCRIPT_DIR, 'data', 'favorites.json');

function readFavorites() {
  try {
    return JSON.parse(fs.readFileSync(FAVORITES_FILE, 'utf-8'));
  } catch {
    return [];
  }
}

function writeFavorites(favorites) {
  fs.mkdirSync(path.join(SCRIPT_DIR, 'data'), { recursive: true });
  fs.writeFileSync(FAVORITES_FILE, JSON.stringify(favorites, null, 2), 'utf-8');
}

function handleAddFavorite(ws, data) {
  if (!data || !data.ad) {
    sendJSON(ws, { type: 'error', message: 'Geçersiz reçete verisi.' });
    return;
  }

  const favorites = readFavorites();

  // Aynı reçeteyi tekrar eklemeyi engelle (ad + kaynak ile kontrol)
  const exists = favorites.some(function(f) {
    return f.ad === data.ad && f.kaynak === data.kaynak;
  });

  if (exists) {
    sendJSON(ws, { type: 'status', status: 'favorite-exists', message: 'Bu reçete zaten favorilerde.' });
    return;
  }

  data.eklenmeTarihi = new Date().toISOString();
  favorites.push(data);
  writeFavorites(favorites);

  sendJSON(ws, { type: 'favorites', data: favorites });
  sendJSON(ws, { type: 'status', status: 'favorite-added', message: data.ad + ' favorilere eklendi.' });
}

function handleRemoveFavorite(ws, data) {
  if (!data || (!data.ad && !data.index)) {
    sendJSON(ws, { type: 'error', message: 'Geçersiz silme verisi.' });
    return;
  }

  const favorites = readFavorites();
  let removed;

  if (typeof data.index === 'number') {
    removed = favorites.splice(data.index, 1)[0];
  } else {
    const idx = favorites.findIndex(function(f) {
      return f.ad === data.ad && f.kaynak === data.kaynak;
    });
    if (idx > -1) removed = favorites.splice(idx, 1)[0];
  }

  if (removed) {
    writeFavorites(favorites);
    sendJSON(ws, { type: 'favorites', data: favorites });
    sendJSON(ws, { type: 'status', status: 'favorite-removed', message: removed.ad + ' favorilerden çıkarıldı.' });
  } else {
    sendJSON(ws, { type: 'error', message: 'Reçete favorilerde bulunamadı.' });
  }
}

function handleGetFavorites(ws) {
  sendJSON(ws, { type: 'favorites', data: readFavorites() });
}

// ─── Start Server ────────────────────────────────────────────────────────────

server.listen(PORT, () => {
  console.log(`Reçete Scout Server — http://localhost:${PORT}`);
  console.log(`WebSocket — ws://localhost:${PORT}`);
  console.log(`Static files — ${PUBLIC_DIR}`);
  console.log(`Recettes dir — ${RECETTES_DIR}`);
});
