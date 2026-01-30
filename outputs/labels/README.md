# Üretilen Etiketler

Bu klasörde Gemini API tarafından oluşturulan etiket görselleri saklanır.

## Klasör Yapısı

```
outputs/labels/
├── [urun-adi]/
│   ├── v1/
│   │   ├── sade_[sku]_v1_[timestamp].png
│   │   ├── sade_[sku]_v1_alt1_[timestamp].png
│   │   └── sade_[sku]_v1_alt2_[timestamp].png
│   ├── v2/
│   │   └── sade_[sku]_v2_[timestamp].png
│   └── final/
│       └── sade_[sku]_final.png
├── bitter70/
├── sutlu50/
└── findikli60/
```

## Dosya Adlandırma

Format: `sade_[product_sku]_v[N]_[timestamp].png`

Örnekler:
- `sade_bitter70_v1_20260130.png` - İlk versiyon
- `sade_bitter70_v2_20260201.png` - İkinci iterasyon
- `sade_bitter70_final.png` - Onaylanmış final tasarım

## Versiyon Yönetimi

- **v1, v2, v3...** - AI iterasyonları, farklı prompt denemeleri
- **alt1, alt2** - Aynı prompttan farklı varyasyonlar
- **final/** - Onaylanmış, production-ready tasarımlar

## Metadata

Her etiket için metadata JSON dosyası:

```json
{
  "product_sku": "bitter70",
  "version": 1,
  "timestamp": "2026-01-30T12:00:00Z",
  "gemini_model": "gemini-2.0-flash-exp",
  "prompt": "[kullanılan tam prompt]",
  "reference_images": ["vakko_label.png"],
  "thinking_used": true,
  "generation_time_ms": 3500,
  "approved": false,
  "approval_notes": ""
}
```

Dosya adı: `sade_[sku]_v[N]_metadata.json`

## Kalite Kontrol

Her üretilen etiket için checklist:

- [ ] Text okunaklı mı? (kontrast yeterli)
- [ ] Brand colors kullanılmış mı?
- [ ] Quiet luxury estetik mevcut mu?
- [ ] Beyaz alan %30+ mı?
- [ ] Font weights doğru mu? (bold yok)
- [ ] 3:4 aspect ratio korunmuş mu?
- [ ] 300 DPI çözünürlük var mı?

## Print-Ready Export

Final tasarımlar için:
1. PNG'yi AI/PDF formatına dönüştür (Adobe Illustrator)
2. CMYK color mode'a geçir
3. Bleed area ekle (+3mm her kenarda)
4. `final/print-ready/` klasörüne kaydet

## Yedekleme

Her ürün klasörü için:
- v1-v3: Geçici - üretim sonrası silinebilir
- final/: Kalıcı - git'e commit edilmeli
- final/print-ready/: Kalıcı - ayrı backup tavsiye edilir

---

**Not:** Bu klasör başlangıçta boştür. İlk etiket üretimi sonrası dolmaya başlayacak.
