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
var preferences = '';
try { preferences = require('fs').readFileSync('$SCRIPT_DIR/data/preferences.json', 'utf-8'); } catch(e) {}

runPipeline({
  date: '$DATE',
  outputDir: require('os').homedir() + '/recettes',
  preferences: preferences,
  onProgress: function(phase, detail) {
    if (phase === 'search-start')    console.log('🔍 Arama başlıyor — ' + detail.total + ' kategori...');
    if (phase === 'search-done')     console.log('  ✅ ' + detail.category + ' bulundu');
    if (phase === 'search-error')    console.log('  ❌ ' + detail.category + ' — ' + detail.error);
    if (phase === 'search-complete') console.log('🔍 Arama tamamlandı — ' + detail.found + ' reçete');
    if (phase === 'extract-start')   console.log('📄 Çıkarma başlıyor — ' + detail.total + ' reçete...');
    if (phase === 'extract-done')    console.log('  📄 ' + detail.recipe + ' çıkarıldı');
    if (phase === 'extract-error')   console.log('  ⚠️  ' + detail.recipe + ' — fallback');
    if (phase === 'render-start')    console.log('✨ HTML render ediliyor...');
    if (phase === 'complete')        console.log('✅ Tamamlandı — ' + detail.recipeCount + ' reçete, ' + (detail.duration/1000).toFixed(1) + 's, \$' + detail.cost.toFixed(4));
  }
}).then(function(r) {
  process.exit(0);
}).catch(function(e) {
  console.error('❌ Hata:', e.message);
  process.exit(1);
});
"
