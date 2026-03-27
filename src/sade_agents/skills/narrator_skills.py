"""
Sade Agents - The Narrator Skills.

The Narrator agent'ın kullandığı skill'ler.
"Sessiz Lüks" tonunda içerik üretimi yetenekleri.
"""

from crewai.tools import tool


@tool
def hikayelestir(urun_adi: str, urun_gramaji: str, urun_icerik: str) -> str:
    """
    Ürün bilgilerinden "Sessiz Lüks" tonunda hikaye içerikleri üretir.

    Bu tool 3 farklı içerik tipi üretmek için kullanılır:
    1. Etiket Hikayesi - ürün arkasında veya menüde yer alacak kısa metin
    2. Instagram Caption - sofistike sosyal medya postu
    3. Kutu İçi Not - hediye kartı için samimi ama premium not

    Args:
        urun_adi: Ürün adı (örn: "Ruby Çikolata Tablet")
        urun_gramaji: Gramaj bilgisi (örn: "85g")
        urun_icerik: Ürün içeriği/özellikleri (örn: "Doğal pembe renk, mayhoş tat")

    Returns:
        Üç bölümlü içerik: Etiket Hikayesi, Instagram Caption, Kutu İçi Not

    Kullanım:
        hikayelestir("Ruby Tablet", "85g", "Doğal pembe, mayhoş tat, 4. tür çikolata")
    """
    # Bu fonksiyon bir prompt template'i olarak çalışır
    # Agent bu tool'u çağırdığında, LLM parametreleri kullanarak içerik üretir
    prompt_template = f"""
Aşağıdaki ürün için "Sessiz Lüks" tonunda 3 farklı içerik üret:

**Ürün Bilgileri:**
- Ürün Adı: {urun_adi}
- Gramaj: {urun_gramaji}
- İçerik/Özellikler: {urun_icerik}

---

## YAZIM KURALLARI (KESİNLİKLE UYULMALI)

### YASAK İfadeler (KULLANMA):
- "Hemen Al!", "Kaçırma!", "Şok Fiyat!", "İnanılmaz fırsat!"
- "Son şans!", "Sınırlı stok!", "Acele edin!"
- Çoklu ünlem işaretleri (!!)
- Emoji kullanımı
- Abartılı sıfatlar: "muhteşem", "harika", "enfes", "süper"

### TERCİH EDİLEN İfadeler:
- "Beklenmedik", "Kendiliğinden", "Keşfetmeye davet"
- "Fark edenler için", "Bilen bilir", "Sessizce"
- Tek ünlem veya hiç ünlem
- Kısa, öz cümleler

### TON:
- Monocle/Kinfolk dergisi editörü gibi
- Sofistike ama gösterişsiz
- Hikaye anlat, satış yapma
- Merak uyandır, zorla değil

---

## ÜRETİLECEK İÇERİKLER:

### 1. Etiket Hikayesi
Ürün arkasında veya menüde yer alacak metin.
- Kısa bir başlık (2-4 kelime)
- 2-3 cümlelik açıklama
- Ürün bilgisi satırı

### 2. Instagram Caption
Sofistike sosyal medya postu.
- Tek kelimelik açılış (örn: "Beklenmedik.")
- 2-3 cümle hikaye
- Ürün tanımı
- 3-4 hashtag (küçük harf, Türkçe karakter yok)

### 3. Kutu İçi Not
Hediye kartı için samimi ama premium not.
- Tırnak içinde kısa bir cümle
- Altında "- Afiyetle." imzası

---

Şimdi bu 3 içeriği "Sessiz Lüks" tonunda üret.
"""
    return prompt_template


__all__ = ["hikayelestir"]
