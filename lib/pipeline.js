'use strict';

// lib/pipeline.js — Reçete Scout paralel pipeline
// runPipeline({ date, preferences, outputDir, onProgress })
//   → { promise: Promise<{ totalDuration, totalCost }>, abort: Function }

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const SCRIPT_DIR = path.resolve(__dirname, '..');

const CATEGORIES = [
  { id: 'viennoiserie',     ad: 'Viennoiserie',      aciklama: 'Kruvasan, brioche, pain au chocolat, danish, kouign-amann' },
  { id: 'tart-tartolet',   ad: 'Tart & Tartolet',   aciklama: 'Tart, tartolet, galette, crostata' },
  { id: 'entremets-mousse',ad: 'Entremets & Mousse', aciklama: 'Mousse pasta, bavarian, charlotte, çok katmanlı pasta' },
  { id: 'petit-gateau',    ad: 'Petit Gâteau',       aciklama: 'Cookie, financier, madeleine, canelé, sablé, macaron' },
  { id: 'cikolata',        ad: 'Çikolata',           aciklama: 'Bonbon, truffle, tablette, çikolatalı tatlılar, ganache, pralin' },
  { id: 'trend',           ad: 'Trend',              aciklama: 'Sosyal medyada popüler, viral, yeni çıkan tatlılar' },
  { id: 'uluslararasi',    ad: 'Uluslararası',       aciklama: 'Fransa dışı: Japon, Kore, İtalyan, İskandinav, Güney Amerika' },
  { id: 'sandvic',         ad: 'Sandviç',            aciklama: 'Kruvasan sandviç, focaccia, baguette, brioche sandviç, panini — tuzlu ürünler' },
];

const CATEGORY_NAMES = {
  'viennoiserie':     'Viennoiserie',
  'tart-tartolet':    'Tart & Tartolet',
  'entremets-mousse': 'Entremets & Mousse',
  'petit-gateau':     'Petit Gâteau',
  'cikolata':         'Çikolata',
  'trend':            'Trend',
  'uluslararasi':     'Uluslararası',
  'sandvic':          'Sandviç',
};

function runPipeline({ date, preferences, outputDir, onProgress }) {
  const abortController = { aborted: false };
  const activeProcs = new Set();
  let totalCost = 0;
  const startTime = Date.now();

  function spawnClaude(prompt, opts) {
    return new Promise((resolve, reject) => {
      if (abortController.aborted) { reject(new Error('Aborted')); return; }

      const args = [
        '-p', prompt,
        '--output-format', 'json',
        '--allowedTools', opts.allowedTools || 'WebSearch,WebFetch',
        '--max-budget-usd', String(opts.maxBudget || 1),
      ];

      const proc = spawn('claude', args, {
        cwd: opts.cwd || SCRIPT_DIR,
        env: { ...process.env },
        stdio: ['ignore', 'pipe', 'pipe'],
        detached: true,
      });

      activeProcs.add(proc);

      let stdout = '';
      proc.stdout.on('data', d => { stdout += d.toString(); });
      proc.stderr.on('data', () => {});

      proc.on('close', code => {
        activeProcs.delete(proc);
        if (abortController.aborted) { reject(new Error('Aborted')); return; }
        if (code !== 0) { reject(new Error(`claude exit ${code}`)); return; }
        try {
          const parsed = JSON.parse(stdout.trim());
          if (parsed.total_cost_usd) totalCost += parsed.total_cost_usd;
          resolve(parsed.result || '');
        } catch {
          resolve(stdout.trim());
        }
      });

      proc.on('error', err => { activeProcs.delete(proc); reject(err); });
    });
  }

  function abort() {
    abortController.aborted = true;
    for (const proc of activeProcs) {
      try { process.kill(-proc.pid, 'SIGTERM'); } catch (_) {}
      try { proc.kill('SIGTERM'); } catch (_) {}
    }
  }

  const promise = (async () => {
    const searchTemplate = fs.readFileSync(path.join(SCRIPT_DIR, 'prompts', 'search.md'), 'utf-8');
    const extractTemplate = fs.readFileSync(path.join(SCRIPT_DIR, 'prompts', 'extract.md'), 'utf-8');
    const reportTemplate = fs.readFileSync(path.join(SCRIPT_DIR, 'templates', 'report.html'), 'utf-8');

    const tercihlerBlok = preferences
      ? `## Engellenen Kaynaklar (Tercih Profili)\n\n${preferences}`
      : '';

    // ── Phase 1: Search ─────────────────────────────────────────────────────
    onProgress('search-start', { total: CATEGORIES.length });

    const searchSettled = await Promise.allSettled(
      CATEGORIES.map(async cat => {
        const prompt = searchTemplate
          .replace('{{KATEGORI}}', cat.ad)
          .replace('{{KATEGORI_ACIKLAMA}}', cat.aciklama)
          .replace('{{TERCIHLER}}', tercihlerBlok);

        try {
          const raw = await spawnClaude(prompt, { allowedTools: 'WebSearch,WebFetch', maxBudget: 0.5 });
          const match = String(raw).match(/\[[\s\S]*?\]/);
          const recipes = match ? JSON.parse(match[0]) : [];
          recipes.forEach(r => { r._catId = cat.id; r._catAd = cat.ad; });
          onProgress('search-done', { category: cat.ad });
          return recipes;
        } catch (err) {
          onProgress('search-error', { category: cat.ad, error: err.message });
          return [];
        }
      })
    );

    const allRecipes = searchSettled.flatMap(r => r.status === 'fulfilled' ? r.value : []);
    onProgress('search-complete', { found: allRecipes.length });

    if (abortController.aborted) throw new Error('Aborted');

    // ── Phase 2: Extract ─────────────────────────────────────────────────────
    onProgress('extract-start', { total: allRecipes.length });

    const extractSettled = await Promise.allSettled(
      allRecipes.map(async recipe => {
        const prompt = extractTemplate
          .replace('{{URL}}', recipe.url || '')
          .replace('{{AD_TR}}', recipe.ad_tr || '')
          .replace('{{AD_ORIJINAL}}', recipe.ad_orijinal || '')
          .replace('{{KAYNAK_ADI}}', recipe.kaynak_adi || '');

        try {
          const raw = await spawnClaude(prompt, { allowedTools: 'WebFetch', maxBudget: 0.3 });
          const match = String(raw).match(/\{[\s\S]*?\}/);
          const data = match ? JSON.parse(match[0]) : {};
          data._catId = recipe._catId;
          data._catAd = recipe._catAd;
          if (!data.ad_tr) { data.ad_tr = recipe.ad_tr; data.ad_orijinal = recipe.ad_orijinal; data.url = recipe.url; data.kaynak_adi = recipe.kaynak_adi; data.neden = recipe.neden; }
          onProgress('extract-done', { recipe: data.ad_tr || recipe.ad_tr });
          return data;
        } catch {
          onProgress('extract-error', { recipe: recipe.ad_tr || '?' });
          return { ...recipe, zorluk: 3, malzemeler: [], bilesenler: [], teknik_not: '', karmasiklik: 3, _catId: recipe._catId, _catAd: recipe._catAd };
        }
      })
    );

    const extracted = extractSettled.map(r => r.status === 'fulfilled' ? r.value : null).filter(Boolean);

    if (abortController.aborted) throw new Error('Aborted');

    // ── Phase 3: Render ──────────────────────────────────────────────────────
    onProgress('render-start', {});

    const html = renderHTML(reportTemplate, date, extracted);
    fs.mkdirSync(outputDir, { recursive: true });
    fs.writeFileSync(path.join(outputDir, `${date}.html`), html, 'utf-8');

    const elapsed = Date.now() - startTime;
    onProgress('complete', { recipeCount: extracted.length, duration: elapsed, cost: totalCost });

    return { totalDuration: elapsed, totalCost };
  })();

  return { promise, abort };
}

// ── HTML Renderer ────────────────────────────────────────────────────────────

const SCORING_FORM = `          <div class="scoring-form">
            <div class="stars">
              <label>Puan:</label>
              <button type="button" class="star" data-value="1">&#9733;</button>
              <button type="button" class="star" data-value="2">&#9733;</button>
              <button type="button" class="star" data-value="3">&#9733;</button>
              <button type="button" class="star" data-value="4">&#9733;</button>
              <button type="button" class="star" data-value="5">&#9733;</button>
            </div>
            <div class="tags">
              <label>Etiketler:</label>
              <button type="button" class="tag-btn" data-tag="teknik">teknik</button>
              <button type="button" class="tag-btn" data-tag="yaratici">yaratıcı</button>
              <button type="button" class="tag-btn" data-tag="klasik">klasik</button>
              <button type="button" class="tag-btn" data-tag="sunum">sunum</button>
              <button type="button" class="tag-btn" data-tag="uygulanabilir">uygulanabilir</button>
              <button type="button" class="tag-btn" data-tag="trend">trend</button>
              <button type="button" class="tag-btn" data-tag="ilham">ilham</button>
              <button type="button" class="tag-btn" data-tag="mevsimsel">mevsimsel</button>
            </div>
            <textarea class="comment" placeholder="Yorum (opsiyonel)..." rows="2"></textarea>
          </div>`;

function e(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function stars(n) {
  return '⭐'.repeat(Math.min(5, Math.max(1, n || 3)));
}

function recipeCard(recipe, id) {
  const catId = recipe._catId || 'viennoiserie';
  const zorluk = Math.min(5, Math.max(1, recipe.zorluk || 3));
  const karmasiklik = Math.min(5, Math.max(1, recipe.karmasiklik || 3));
  const malzemeler = (recipe.malzemeler || []).slice(0, 8).map(m => `                <li>${e(m)}</li>`).join('\n');
  const bilesenler = (recipe.bilesenler || []).map(b => `              <span class="component-tag">${e(b)}</span>`).join('\n');

  return `        <article class="recipe-card" data-id="${id}" data-category="${e(catId)}">
          <div class="recipe-info">
            <h3>
              <span class="recipe-name-tr">${e(recipe.ad_tr)}</span>
              <span class="recipe-name-original">${e(recipe.ad_orijinal)}</span>
            </h3>
            <a href="${e(recipe.url || '#')}" target="_blank" rel="noopener" class="source">Kaynak: ${e(recipe.kaynak_adi)}</a>
            <div class="difficulty">Zorluk: ${stars(zorluk)}</div>
            <p class="why-selected">${e(recipe.neden)}</p>
            <div class="ingredients">
              <strong>Ana malzemeler:</strong>
              <ul>
${malzemeler}
              </ul>
            </div>
            <div class="components">
              <strong>Bileşenler:</strong>
              ${bilesenler}
            </div>
            <p class="tech-note">${e(recipe.teknik_not)}</p>
            <div class="complexity" data-score="${karmasiklik}">Karmaşıklık: <span class="complexity-bar"></span> ${karmasiklik}/5</div>
          </div>
${SCORING_FORM}
        </article>`;
}

function renderHTML(template, date, recipes) {
  const d = new Date(date + 'T12:00:00');
  const months = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'];
  const displayDate = `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`;

  // Group recipes by category
  const byCategory = {};
  recipes.forEach(r => {
    const cid = r._catId || 'viennoiserie';
    if (!byCategory[cid]) byCategory[cid] = [];
    byCategory[cid].push(r);
  });

  // Build recipe sections HTML
  let recipeId = 0;
  const sectionsHTML = CATEGORIES.map(cat => {
    const catRecipes = byCategory[cat.id] || [];
    if (!catRecipes.length) return '';
    const cardsHTML = catRecipes.map(r => recipeCard(r, ++recipeId)).join('\n\n');
    return `    <!-- ==================== ${CATEGORY_NAMES[cat.id]} ==================== -->
    <section class="category" id="${cat.id}">
      <h2>${CATEGORY_NAMES[cat.id]}</h2>
      <div class="card-grid">

${cardsHTML}

      </div>
    </section>`;
  }).filter(Boolean).join('\n\n');

  // Build sources table rows
  const sources = [...new Set(recipes.map(r => ({ ad: r.kaynak_adi, url: r.url })).filter(r => r.ad))];
  const sourcesHTML = sources.map(s =>
    `        <tr>\n          <td><a href="${e(s.url || '#')}" target="_blank" rel="noopener">${e(s.ad)}</a></td>\n          <td>Blog/Şef</td>\n          <td></td>\n        </tr>`
  ).join('\n');

  // Extract static wrapper from template (header section up to <main>, and from </main> onwards)
  const mainStart = template.indexOf('<main>');
  const mainEnd = template.indexOf('</main>');

  let header = mainStart > -1 ? template.slice(0, mainStart) : '';
  let footer = mainEnd > -1 ? template.slice(mainEnd + '</main>'.length) : '';

  // Replace placeholders in header/footer
  header = header
    .replace(/\{\{TARIH\}\}/g, displayDate)
    .replace(/\{\{KAYNAK_SAYISI\}\}/g, String(sources.length));

  // Replace sources table placeholders in footer
  const tbodyStart = footer.indexOf('<tbody>');
  const tbodyEnd = footer.indexOf('</tbody>');
  if (tbodyStart > -1 && tbodyEnd > -1) {
    footer = footer.slice(0, tbodyStart + '<tbody>'.length) + '\n' + sourcesHTML + '\n      ' + footer.slice(tbodyEnd);
  }

  // Replace remaining {{...}} placeholders in footer (TARIH in JS)
  footer = footer.replace(/\{\{TARIH\}\}/g, date);

  return `${header}<main>\n\n${sectionsHTML}\n\n  </main>${footer}`;
}

module.exports = { runPipeline };
