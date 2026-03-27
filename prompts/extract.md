Aşağıdaki URL'deki reçeteden yapılandırılmış veri çıkar.

## URL
{{URL}}

## Reçete Bilgisi
Ad: {{AD_TR}} ({{AD_ORIJINAL}})
Kaynak: {{KAYNAK_ADI}}

## Çıkaracağın Veriler
SADECE JSON döndür, başka hiçbir şey yazma:
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
