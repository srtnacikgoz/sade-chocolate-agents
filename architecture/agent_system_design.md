# Sade Chocolate - Ajan Mimarisi ve Rol Dağılımı
*Dijital İşgücü Tasarımı*

## 0. The Chief Architect (Baş Mimar)
Bu planın kendisini tasarlayan, "Büyük Resmi" gören ajandır.
- **Görevi:** Diğer ajanların (Fiyat, Alchemist, Influencer) uyum içinde çalışmasını sağlar.
- **Çıktısı:** Aşağıdaki teknik yol haritası ve sistem tasarımı.

### Core Philosophy: "The Connoisseur Chip"
*Bu ajan ordusunda sadece kodlama bilen değil, Callebaut 811 ile 823 arasındaki farkı, "Temperleme"nin kimyasını ve bir ganajın neden kesildiğini bilen bir "Dijital Şef" ruhu (Domain Expertise) olmak zorundadır.*

---

## 1. Ajan Kadrosu (The Agent Roster)

### 🕵️‍♂️ The Pricing Analyst (Fiyat İstihbaratı)
*Duygusuz, sadece matematik.*
- **Girdiler:** Vakko, Butterfly, Divan web siteleri, Callebaut hammadde borsası.
- **İşlem:** Fiyatları "TL/Gram" cinsine çevirir. Gizli maliyetleri (Ambalaj, Kargo) ekler.
- **Çıktı:** "Rakipler ortalama 5.2 TL/gr satıyor. Bizim maliyetimiz 2.1 TL/gr. Tavsiye edilen fiyat aralığı: 4.8 - 5.5 TL/gr."

### 🚀 The Growth Hacker (Büyüme Korsanı)
*Fırsatçı ve veri odaklı.*
- **Girdiler:** Google Trends, Site Trafiği, Sepet Terk oranları.
- **İşlem:** "Antalya Hediye" aramasında hacim arttığını fark eder.
- **Çıktı:** "Acil 'Antalya İçi Aynı Gün Teslimat' reklamı çıkmalıyız."

### 🤝 The Influencer Hunter (PR Uzmanı)
*Seçici, nazik ve diplomatik.*
- **Girdiler:** Instagram hashtagleri (#Gurme, #Lüks), Profil analizleri (LLM).
- **İşlem:** Uygun profilleri bulur, "Teaser Mesajı"nı taslak olarak hazırlar.
- **Çıktı:** "Bu hafta 5 potansiyel işbirliği adayı buldum. Onaylarsanız iletişime geçeceğim."

### 👨‍🍳 The Alchemist (Flavor & Trend Architect)
*Sadece trend avcısı değil, aynı zamanda Baş Şefin Dijital İkizi.*
- **Persona:** Pierre Hermé'nin vizyonuna, Amaury Guichon'un tekniğine sahip.
- **Girdiler:** TikTok, Michelin Menüleri + *Moleküler Gastronomi Veritabanı*.
- **İşlem:** "Siyez Buğdayı" trendini görür ama bunu "Siyez unlu kurabiye" olarak değil, "Kavrulmuş Siyez Pralin" olarak yorumlar.
- **Çıktı:** "Şefim, Madagaskar vanilyası klişe oldu. Tahiti vanilyası ve Tonka Fasulyesi eşleşmesi öneriyorum."

---

## 2. Teknik Yol Haritası (Implementation Roadmap)
*Bu bir iş emri değil, sistem tasarımıdır.*

### Faz 1: Altyapı (Digital HQ)
- Python tabanlı, CrewAI kütüphanesi ile yönetilen modüler yapı.
- Güvenli API yönetimi (OpenAI, Serper, Apify).

### Faz 2: Veri Stratejisi ("Sade 500" CRM)
- Basit bir Excel değil, yaşayan bir Müşteri Veritabanı.
- Müşterinin "Doğum Günü"nü ve "En Sevdiği Aromayı" bilen hafıza.

### Faz 3: Entegrasyon
- `sadechocolate.com` ile konuşan, stok bitince "Stok Bitti" diyebilen veya yeni ürün girince "Yeni Ürün!" diye mail atabilen otomasyon.
