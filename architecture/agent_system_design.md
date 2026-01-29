# Sade Chocolate - Ajan Mimarisi ve Rol Dağılımı
*Dijital İşgücü Tasarımı*

## 0. The Chief Architect (Baş Mimar)
Bu planın kendisini tasarlayan, "Büyük Resmi" gören ajandır.
- **Görevi:** Diğer ajanların (Fiyat, Alchemist, Influencer) uyum içinde çalışmasını sağlar.
- **Çıktısı:** Aşağıdaki teknik yol haritası ve sistem tasarımı.
- **Beslenme Kaynağı:** **GitHub**. (Yeni çıkan AI ajan kütüphanelerini, otonom pazarlama scriptlerini [Örn: AutoGPT, BabyAGI] takip eder ve sistemi sürekli günceller).

### Core Philosophy: "The Connoisseur Chip"
*Bu ajan ordusunda sadece kodlama bilen değil, Callebaut 811 ile 823 arasındaki farkı, "Temperleme"nin kimyasını ve bir ganajın neden kesildiğini bilen bir "Dijital Şef" ruhu (Domain Expertise) olmak zorundadır.*

---

## 1. Ajan Kadrosu (The Agent Roster)

### 🕵️‍♂️ The Pricing Analyst (Fiyat İstihbaratı)
*Duygusuz, sadece matematik.*
- **Girdiler:** Vakko/Butterfly Fiyatları + **Google Maps/Trustpilot Yorumları** (Rakiplerin 1 yıldızlı yorumları = Bizim fırsatlarımız).
- **İşlem:** Fiyatları "TL/Gram" cinsine çevirir. Rakip şikayetlerini ("Kargo erimiş geldi") analiz ederek operasyonel risk primi ekler.
- **Çıktı:** "Rakipler ortalama 5.2 TL/gr satıyor. Ancak 'Erimiş Paket' şikayetleri %20 artmış. Biz 'Erimeme Garantisi' ile 6.0 TL/gr satabiliriz."

### 🚀 The Growth Hacker (Büyüme Korsanı)
*Fırsatçı ve veri odaklı.*
- **Girdiler:** Google Trends + **LinkedIn (Kurumsal Av)**.
- **İşlem:** "Antalya Hediye" aramasında hacim arttığını veya LinkedIn'de "İK Direktörleri"nin "Yılbaşı Hediyesi" aradığını fark eder.
- **Çıktı:** "Acil 'Kurumsal Hediye Kataloğu' reklamı çıkmalıyız."

### 🤝 The Influencer Hunter (PR Uzmanı)
*Seçici, nazik ve diplomatik.*
- **Girdiler:** Instagram hashtagleri (#Gurme, #Lüks), Profil analizleri (LLM).
- **İşlem:** Uygun profilleri bulur, "Teaser Mesajı"nı taslak olarak hazırlar.
- **Çıktı:** "Bu hafta 5 potansiyel işbirliği adayı buldum. Onaylarsanız iletişime geçeceğim."

### 👨‍🍳 The Alchemist (Flavor & Trend Architect)
*Sadece trend avcısı değil, aynı zamanda Baş Şefin Dijital İkizi.*
- **Persona:** Pierre Hermé'nin vizyonuna, Amaury Guichon'un tekniğine sahip.
- **Girdiler:** 
    - **Reddit (`r/chocolate`, `r/AskCulinary`):** Profesyonellerin dedikoduları ve teknik tartışmalar.
    - **Pinterest:** Lüks ambalaj ve görsel sunum trendleri.
    - **X (Twitter):** *"Şu an viral olan ne?"* sorusunun cevabı. (Örn: "Dubai Çikolatası" çılgınlığı önce TikTok'ta başlar, X'te tartışılır, Instagram'a düşer).
    - **Michelin Menüleri:** Global şeflerin kullandığı yeni malzemeler.
- **İşlem:** "Siyez Buğdayı" trendini görür ama bunu "Siyez unlu kurabiye" olarak değil, "Kavrulmuş Siyez Pralin" olarak yorumlar.
- **Çıktı:** "Şefim, Madagaskar vanilyası klişe oldu. Tahiti vanilyası ve Tonka Fasulyesi eşleşmesi öneriyorum."

### 🧐 The Perfectionist (UX & Brand Auditor)
*Bizim en acımasız eleştirmenimiz. "Sade" ismine leke sürdürmez.*
- **Persona:** Obsesif bir Sanat Yönetmeni ve QA (Kalite Kontrol) Mühendisi.
- **Görevi:** `sadechocolate.com`'u 7/24 tarar. Kendini müşteri yerine koyar.
- **Girdiler:** 
    - **Site Performansı:** PageSpeed, Broken Link Checker.
    - **Rakip Benchmarking:** "Vakko'nun sepet sayfası 2 adımda bitiyor, bizimki neden 4 adım?"
    - **Görsel Kontrol:** "Bu ürün fotoğrafı karanlık çıkmış, marka kimliğine uymuyor."
- **Çıktı:** "Mobil anasayfada 'Satın Al' butonu 3 piksel kaymış. Kabul edilemez. Hemen düzeltilmeli."

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
