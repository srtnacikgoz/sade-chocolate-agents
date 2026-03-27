# Reçete Scout Agent

Haute pâtisserie reçete keşif ajanı. Her gün 8 kategoriden 16 profesyonel reçete bulur,
HTML rapor üretir, kullanıcı puanlarından öğrenir.

## Web Dashboard (Önerilen)

```bash
npm install   # ilk seferde
npm start     # http://localhost:3000
```

Dashboard'dan:
- **URL'den Çek** — Tek bir reçete URL'sini Türkçe profesyonel reçete sayfasına dönüştürür
- **Reçete Getir** — Agent'ı çalıştırır, canlı ilerlemeyi izlersiniz
- **Puanlama** — Reçeteleri yıldız + etiket + yorum ile puanlayın
- **Puanları Kaydet** — Otomatik olarak `~/recettes/scores/` klasörüne kaydeder
- **Öğren** — Puanlardan tercih profili oluşturur

Tek reçete çıktıları `~/recettes/single/` klasörüne yazılır ve dashboard içinde iframe önizleme olarak gösterilir.

## CLI Kullanım (alternatif)

```bash
./scout.sh     # Günlük keşif
./learn.sh     # Puanları öğrenme motoruna aktar
```

## Akış

1. Agent 8 kategoriden 16 reçete bulur → `~/recettes/YYYY-MM-DD.html`
2. Reçeteleri puanla (yıldız + etiket + yorum)
3. Puanları kaydet → `~/recettes/scores/`
4. `./learn.sh` veya "Öğren" butonu → tercih profili üretir (`data/preferences.json`)
5. Sonraki çalışmada agent öğrenilmiş tercihlerini kullanır

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
