# Referans Görseller

Bu klasöre **1-6 adet** örnek etiket görseli ekleyin.

## Amaç

Bu görseller Gemini API'ye stil referansı olarak gönderilecek. AI, bu görsellerden esinlenerek Sade Chocolate için yeni etiketler üretecek.

## Format Gereksinimleri

- **Format:** PNG veya JPG
- **Çözünürlük:** Minimum 1024x1024, ideal 2048x2732 (3:4 aspect ratio)
- **Kalite:** Yüksek çözünürlük - detaylar net görünmeli
- **İçerik:** Çikolata etiketleri veya premium ürün paketleri

## Stil Kriterleri

İdeal referans görselleri:

### ✓ İyi Örnekler
- Vakko Chocolate etiketleri (Sessiz Lüks)
- Butterfly Chocolate packaging (Minimalist elegance)
- Godiva premium koleksiyonlar
- Aesop ürün etiketleri (Tipografi ve düzen)
- Diptyque mum etiketleri (Simplicity)
- Kinfolk/Monocle editöryel görseller (Estetik)

### ✗ Kaçınılacak Örnekler
- Parlak, renkli, shouty tasarımlar
- Discount/indirim görünümlü paketler
- Çok işlemeli, karmaşık tasarımlar
- Emoji veya cartoon elementler içeren
- Trend-focused (kısa ömürlü) tasarımlar

## Kullanım

Gemini API'ye gönderilirken:
1. Görseller base64 encode edilecek
2. Prompt ile birlikte "reference style" olarak sunulacak
3. AI bu görsellerin aesthetic'ini analiz edecek
4. Yeni etiketler bu stile uygun üretilecek

## Dosya Adlandırma

Açıklayıcı isimler kullanın:
- `vakko_bitter_label.png`
- `butterfly_minimalist_cream.jpg`
- `godiva_gold_accent.png`

## Güncellemeler

Referans görselleri değiştirdiğinizde:
1. Eski görselleri `archive/` alt klasörüne taşıyın
2. Yeni görselleri ekleyin
3. `style_config.json` dosyasındaki `competitors_visual_reference` listesini güncelleyin

---

**Not:** Bu klasör boş bırakılabilir. Gemini API referans görseller olmadan da çalışır, ancak stil tutarlılığı için 2-3 güçlü referans kullanılması önerilir.
