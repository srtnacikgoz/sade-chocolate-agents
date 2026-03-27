#!/bin/bash
# learn.sh — Puanlardan ogrenme cikar, preferences.json guncelle
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCORES_DIR="$HOME/recettes/scores"
PREFS_FILE="$SCRIPT_DIR/data/preferences.json"

mkdir -p "$SCRIPT_DIR/data"
mkdir -p "$SCORES_DIR"

# Check for score files (they are named *-scores.json)
SCORE_COUNT=$(find "$SCORES_DIR" -name "*-scores.json" -type f | wc -l | tr -d ' ')
if [ "$SCORE_COUNT" -eq 0 ]; then
  echo "Henuz puanlanmis dosya yok. Once HTML raporlari puanlayip export edin."
  exit 0
fi

echo "📊 Puanlar analiz ediliyor..."
echo "📁 Puan dosyalari: $SCORE_COUNT adet"

# Combine all score files
COMBINED=$(cat "$SCORES_DIR"/*-scores.json | jq -s '.')

# Read favorites if exists
FAVORITES_FILE="$SCRIPT_DIR/data/favorites.json"
if [ -f "$FAVORITES_FILE" ]; then
  FAVORITES=$(cat "$FAVORITES_FILE")
  echo "⭐ Favoriler yüklendi: $(echo "$FAVORITES" | jq 'length') adet"
else
  FAVORITES="[]"
fi

claude -p "
Sen bir ogrenme motorusun. Asagidaki puanlama verilerinden ve favori recetelerden kullanicinin tercih profilini cikar.

## Puanlama Verileri
$COMBINED

## Favori Receteler (kullanicinin ozellikle begendigi ve sakladigi)
$FAVORITES
NOT: Favori receteler kullanicinin EN cok begendigi recetelerdir. Bunlarin bilesen ve kaynak oruntulerine EKSTRA agirlik ver.

## Cikar ve JSON olarak yaz:

1. **stil_profili**: Yuksek puanli (4-5) recetelerin ortak ozellikleri
   - tercih_edilen_bilesenler: En cok begenilen bilesen kombinasyonlari
   - tercih_edilen_teksturler: Begenilen tekstur kontrastlari
   - tercih_edilen_lezzet_aileleri: Begenilen lezzet profilleri
   - karmasiklik_tercihi: Ortalama begenilen karmasiklik skoru

2. **kaynak_kalite_haritasi**: Her kaynagin ortalama puani
   - yuksek_kalite: 4+ ortalama alan kaynaklar
   - dusuk_kalite: 2.5 alti ortalama alan kaynaklar
   - BU BOLUM checkbox kaynakli engellemelerden AYRI olmali

3. **bilesen_tercihleri**: Yuksek puanli recetelerde sik gecen bilesenler ve kombinasyonlar

4. **kacinilacaklar**: Dusuk puanli (1-2) recetelerin ortak ozellikleri

5. **tag_analizi**: Hangi tag'ler yuksek puanla birlikte geliyor (or: 'teknik' tag'i olan receteler ortalama 4.2 puan)

6. **kullanici_yorumlari_ozet**: Yorumlardan cikarilan anahtar bilgiler

7. **favori_analizi**: Favori recetelerden cikarilan oruntu
   - ortak_bilesenler: Favorilerde en sik gecen bilesenler
   - ortak_teknikler: Favorilerdeki teknik yaklasimlar
   - kaynak_profili: Favorilerin geldigi kaynaklar
   - benzer_ara: Bu favorilere benzer recete bulmak icin arama onerileri

8. **kaynak_engel_listesi**: Checkbox ile isaretlenen sorunlu kaynaklari domain bazinda cikar
   - erisim_sorunlu: `kaynakDurumu.erisimHatasi = true` olan domainler
   - kullanma_listesi: `kaynakDurumu.kullanma = true` olan domainler
   - Her kayit su alanlari icersin: `kaynak`, `neden`, `isaretlenme_sayisi`
   - `kaynak` alani domain olsun (or: `example.com`)
   - Ayni domain birden fazla recetede isaretlendiyse tek kayitta topla
   - Iki liste birbirinden AYRI tutulmali
   - Bu liste kaynak puanlamasindan bagimsiz, dogrudan bloklama sinyali olarak ele alinmali

JSON formatinda $PREFS_FILE dosyasina yaz. SADECE gecerli JSON yaz, markdown code block kullanma.
" \
  --allowedTools "Read,Write" \
  --max-budget-usd 1

# Validation: check file was created and is valid JSON
if [ ! -f "$PREFS_FILE" ]; then
  echo "❌ HATA: preferences.json olusturulamadi."
  exit 1
fi

if ! jq empty "$PREFS_FILE" 2>/dev/null; then
  echo "❌ HATA: preferences.json gecersiz JSON. Dosya siliniyor, tekrar deneyin."
  rm -f "$PREFS_FILE"
  exit 1
fi

echo "✅ Tercih profili guncellendi: $PREFS_FILE"
echo "📊 Ozet:"
jq '.stil_profili.karmasiklik_tercihi // "henuz veri yok"' "$PREFS_FILE"
