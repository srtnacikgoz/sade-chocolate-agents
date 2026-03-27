# Phase 6: The Curator - Research

**Researched:** 2026-01-30
**Domain:** AI görsel üretimi (Gemini 3 Pro), Figma entegrasyonu, ürün etiket tasarımı
**Confidence:** MEDIUM

## Summary

Phase 6: The Curator, Gemini 3 Pro Image API kullanarak ürün etiket tasarımı yapan bir CrewAI agent'ıdır. Araştırma, Gemini API'nin güçlü metin render yetenekleri, varyasyon tabanlı üretim workflow'u ve Figma REST API entegrasyonu üzerine odaklandı.

**Gemini 3 Pro Image** (alias "Nano Banana Pro"), profesyonel asset üretimi için optimize edilmiş, gelişmiş text rendering yetenekleri (etiket, menü, infografik için okunaklı, stilize metin) ve 14 adete kadar referans görsel (6 obje + 5 insan + stil referansları) desteği sunan state-of-the-art bir modeldir. Python SDK (`google-genai`) ile tam entegrasyon, 1K/2K/4K çözünürlük desteği ve conversational editing özellikleri sunar.

**Figma entegrasyonu** iki temel yaklaşımla mümkündür: (1) Template export yaklaşımı - Figma'da template oluştur, export et, referans görsel olarak kullan; (2) REST API yaklaşımı - Programmatik export ve versiyon kontrolü için Figma REST API kullan. İkinci yaklaşım daha fazla esneklik sağlar ancak daha karmaşıktır.

**Style consistency**, referans görseller (style guide dosyası), detaylı prompt engineering ("quiet luxury" estetik tanımlaması) ve iterative refinement (varyasyon üretip seçme) ile sağlanır. Gemini'nin multi-turn chat yetenekleri, seçilen varyasyonun üzerinde ince ayarlar yapmaya olanak tanır.

**Primary recommendation:** Gemini 3 Pro Image API + referans görsel tabanlı style transfer kullan. Figma'yı template tasarımı ve initial export için kullan (manuel veya REST API ile), ardından Gemini'ye referans olarak ver. CrewAI agent'ı supervised (her zaman onay) modda çalıştır, varyasyonları yerel klasöre kaydet, kullanıcı onayından sonra final versiyonu PNG/SVG/PDF formatlarında export et.

## Standard Stack

Görsel tasarım agent'ları için kurulu stack:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| google-genai | Latest (2026) | Gemini API Python SDK | Google'ın resmi SDK'sı, Gemini 3 Pro Image erişimi, conversational editing |
| crewai | Latest | Agent orchestration | Mevcut projede kullanılıyor, supervised workflow desteği |
| Pillow (PIL) | 12.1.0+ | Image manipulation | Python'da endüstri standardı, format dönüşümleri, boyutlandırma |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| requests | 2.31.0+ | HTTP requests (Figma API) | Figma REST API entegrasyonu için |
| cairosvg | 2.7.0+ | SVG → PNG/PDF conversion | SVG export gerektiğinde |
| reportlab | 4.0.0+ | PDF generation/manipulation | PDF formatı için gelişmiş işlemler |
| python-dotenv | 1.0.0+ | Environment variables | API key yönetimi |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Gemini 3 Pro | DALL-E 3 | DALL-E text rendering daha zayıf, maliyet daha yüksek ($0.040 vs $0.039), kullanıcı zaten Gemini API erişimine sahip |
| Figma REST API | Manual export | REST API otomasyonu sağlar ama ek komplekslik getirir; v1 için manual export yeterli olabilir |
| Pillow | OpenCV | OpenCV daha güçlü ama etiket tasarımı için overkill, Pillow yeterli ve daha basit |

**Installation:**
```bash
pip install google-genai crewai pillow requests cairosvg reportlab python-dotenv
```

## Architecture Patterns

### Recommended Project Structure
```
src/sade_agents/agents/
├── curator.py                 # The Curator agent (SadeAgent subclass)
├── tools/
│   ├── gemini_image_tool.py   # Gemini image generation tool
│   ├── figma_export_tool.py   # (Optional) Figma REST API tool
│   └── image_format_tool.py   # Format conversion tool (PNG/SVG/PDF)
outputs/
├── labels/                    # Etiket çıktıları
│   ├── [product-name]/
│   │   ├── v1/                # Versiyonlar
│   │   │   ├── variation-1.png
│   │   │   ├── variation-2.png
│   │   │   └── ...
│   │   └── approved/          # Onaylanmış final versiyonlar
│   │       ├── final.png
│   │       ├── final.svg
│   │       └── final.pdf
style_guide/
├── brand_colors.json          # Renk paleti
├── typography.json            # Font bilgileri
├── reference_images/          # Referans görseller (style transfer için)
│   ├── label_example_1.png
│   └── label_example_2.png
```

### Pattern 1: Variation-Based Generation Workflow
**What:** Önce 3-4 varyasyon üret, kullanıcıya sun, seçileni geliştir
**When to use:** Supervised autonomy (her zaman onay) workflow'larında
**Example:**
```python
# Source: AI workflow best practices 2026
class CuratorAgent(SadeAgent):
    def generate_label_variations(self, product_info: dict, num_variations: int = 3):
        """Ürün bilgisinden etiket varyasyonları üret"""
        variations = []

        for i in range(num_variations):
            # Gemini'ye prompt gönder (aynı prompt, farklı sonuçlar)
            prompt = self._build_label_prompt(product_info)
            image = self.gemini_tool.generate_image(
                prompt=prompt,
                aspect_ratio="3:4",  # Etiket oranı
                image_size="2K",
                style_references=self._load_style_references()
            )
            variations.append(image)

        return variations

    def refine_selected_variation(self, selected_image, refinement_instructions: str):
        """Seçilen varyasyonu iyileştir (conversational editing)"""
        refined = self.gemini_tool.edit_image(
            input_image=selected_image,
            prompt=refinement_instructions,
            preserve_aspect_ratio=True
        )
        return refined
```

### Pattern 2: Style Guide Reference System
**What:** Style guide dosyalarını referans görsel olarak Gemini'ye ver
**When to use:** Brand consistency sağlamak için tüm generasyonlarda
**Example:**
```python
# Source: Gemini API image generation docs
def _load_style_references(self):
    """Style guide referanslarını yükle"""
    references = []

    # Brand color reference
    if os.path.exists("style_guide/reference_images/color_palette.png"):
        references.append({
            "type": "style",
            "path": "style_guide/reference_images/color_palette.png"
        })

    # Example label references (up to 6 object images)
    for ref in glob("style_guide/reference_images/label_example_*.png")[:6]:
        references.append({
            "type": "object",
            "path": ref
        })

    return references

def _build_label_prompt(self, product_info: dict):
    """Ürün bilgisinden prompt oluştur"""
    # Narrative, descriptive approach (Gemini best practice)
    prompt = f"""
    Create a premium product label for a quiet luxury chocolate brand named Sade.

    Product: {product_info['name']} - {product_info['flavor']}
    Text to render: "{product_info['label_text']}" (max 25 characters)

    Design aesthetic: Understated elegance in the style of Monocle and Kinfolk magazines.
    Use a minimalist layout with a neutral color palette (beige, soft grays, muted earth tones).
    Typography should be clean, serif or elegant sans-serif, with excellent legibility.
    The design should feel timeless, sophisticated, and whisper luxury rather than shout it.

    Include the reference images for visual style consistency.
    Render the text clearly with proper spacing and alignment for print-ready output.
    """
    return prompt
```

### Pattern 3: Supervised Workflow with Human Approval
**What:** Agent varyasyonları üretir, kullanıcı seçer, agent refinement yapar
**When to use:** Supervised autonomy level (her zaman onay)
**Example:**
```python
# Source: Human-in-the-loop AI workflows 2026
class CuratorTask:
    def execute(self):
        # 1. Generate variations
        variations = agent.generate_label_variations(product_info)

        # 2. Save and display to user
        variation_paths = []
        for i, var in enumerate(variations):
            path = f"outputs/labels/{product_name}/v1/variation-{i+1}.png"
            var.save(path)
            variation_paths.append(path)

        # 3. Request human approval (pause workflow)
        print(f"Generated {len(variations)} variations at:")
        for path in variation_paths:
            print(f"  - {path}")

        selected_index = int(input("Select variation (1-3): ")) - 1
        refinement_notes = input("Any refinements? (or press Enter to approve): ")

        # 4. Apply refinements if needed
        selected_image = variations[selected_index]
        if refinement_notes:
            final_image = agent.refine_selected_variation(selected_image, refinement_notes)
        else:
            final_image = selected_image

        # 5. Export to all formats
        agent.export_final_label(final_image, product_name)
```

### Pattern 4: Format Export Pipeline
**What:** Final görseli PNG, SVG, PDF formatlarında export et
**When to use:** Onay sonrası, son aşama
**Example:**
```python
# Source: Python Pillow and CairoSVG documentation
def export_final_label(self, image, product_name: str):
    """Final etiketi tüm formatlarda export et"""
    base_path = f"outputs/labels/{product_name}/approved"
    os.makedirs(base_path, exist_ok=True)

    # PNG (direct save)
    png_path = f"{base_path}/final.png"
    image.save(png_path, "PNG", dpi=(300, 300))

    # SVG conversion (if needed - note: AI generates raster, this is for workflow)
    # For true vector, would need to use Figma export or vectorization tool

    # PDF (using Pillow)
    pdf_path = f"{base_path}/final.pdf"
    image.save(pdf_path, "PDF", resolution=300.0)

    print(f"Exported to: {png_path}, {pdf_path}")
```

### Anti-Patterns to Avoid
- **Keyword-only prompts:** Gemini güçlü dil anlayışına sahip, keyword dizisi yerine narrative prompt kullan
- **Vague style descriptions:** "Luxury" yerine "Understated elegance with neutral palette, serif typography, Monocle magazine aesthetic" gibi detaylı tanımla
- **Ignoring text limits:** 25 karakterden fazla metin render kalitesini düşürür
- **No reference images:** Style consistency için mutlaka referans görseller kullan
- **First-output acceptance:** İlk üretimi kabul etme, varyasyon üret ve en iyisini seç
- **Manual format conversion:** Format conversion'ı automate et, manuel işlem hataya açık

## Don't Hand-Roll

Basit görünen ama mevcut çözümü olan problemler:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Image generation | Custom diffusion model | Gemini 3 Pro Image API | Text rendering zor, training maliyetli, Gemini zaten optimize |
| Format conversion | Custom PIL scripts | CairoSVG + Pillow | SVG conversion edge case'leri çok, test edilmiş kütüphaneler kullan |
| Style consistency | Custom style transfer model | Gemini reference images (up to 14) | Built-in özellik, training gerektirmez |
| Figma export | Web scraping | Figma REST API | API resmi, güvenilir, rate limit yönetimi var |
| Human approval workflow | Custom CLI/GUI | Prefect/LangChain HITL patterns | Type-safe input, approval tracking, audit trail |
| Prompt templates | String concatenation | Jinja2/Template engines | Version control, multi-language, maintainability |

**Key insight:** AI görsel üretimi artık commoditized bir hizmet. Kendi modelini train etme, mevcut API'leri kullan. Farklılaşma prompt engineering, style guide implementation ve workflow design'da.

## Common Pitfalls

### Pitfall 1: Vague or Keyword-Based Prompts
**What goes wrong:** "luxury chocolate label, gold, elegant" gibi keyword-only prompt'lar generic, tutarsız sonuçlar verir
**Why it happens:** GPT-3 döneminden kalma alışkanlık, Gemini'nin dil anlayışı çok daha güçlü
**How to avoid:** Narrative, descriptive paragraph kullan. "Create a product label in the style of..." yaklaşımı
**Warning signs:** Her seferinde çok farklı stil, istenen estetik yansımıyor

### Pitfall 2: Text Rendering Overload
**What goes wrong:** 25+ karakter metin render edilmeye çalışılınca metinler okunamaz, hatalı oluyor
**Why it happens:** AI modelleri text rendering'de hala limitation'lar yaşıyor
**How to avoid:** Label text'i 25 karakter veya daha kısa tut. Uzun metinler için Figma template + overlay yaklaşımı kullan
**Warning signs:** Üretilen görsellerde metinler bulanık, harfler yanlış

### Pitfall 3: No Style Reference Images
**What goes wrong:** Her üretimde farklı stil, brand consistency yok
**Why it happens:** Prompt'a güvenip referans görsel vermeyi unutma
**How to avoid:** Her generation'da style_guide/reference_images/ altındaki görselleri mutlaka referans olarak ver
**Warning signs:** Aynı prompt farklı tasarım tarzları üretiyor

### Pitfall 4: Accepting First Output
**What goes wrong:** İlk üretim nadiren ideal, ama kullanıcı "yeterince iyi" deyip geçiyor
**Why it happens:** Varyasyon üretmek zaman alıyor gibi görünür
**How to avoid:** Workflow'a 3-4 varyasyon üretimi built-in yap, kullanıcı en iyisini seçsin
**Warning signs:** Kullanıcı "daha iyi olabilirdi" diyor ama revize istemiyor

### Pitfall 5: Ignoring Conversational Editing
**What goes wrong:** Küçük değişiklikler için sıfırdan generate ediliyor, context kayboluyor
**Why it happens:** Gemini'nin multi-turn chat yetenekleri bilinmiyor
**How to avoid:** Refinement için conversational editing kullan: "Change text color to darker gray", "Move logo 10px down"
**Warning signs:** Her küçük değişiklik için tamamen yeni generation, tutarsız sonuçlar

### Pitfall 6: Manual Format Conversion
**What goes wrong:** Her seferinde manuel olarak PNG'den PDF'e convert ediliyor, hatalar oluyor
**Why it happens:** Automation yapılmamış
**How to avoid:** Export pipeline'ı automate et, tek tıkla tüm formatlar üretilsin
**Warning signs:** "PDF'i unuttum" gibi sorunlar, manuel işlem basamakları

### Pitfall 7: API Key Management
**What goes wrong:** API key'ler code'a hardcode ediliyor veya git'e push ediliyor
**Why it happens:** Hızlıca test için hardcode ediliyor, sonra unutuluyor
**How to avoid:** `.env` dosyası + `python-dotenv` kullan, `.gitignore`'a ekle
**Warning signs:** API key exposure, security risk

### Pitfall 8: No Rate Limiting
**What goes wrong:** Çok hızlı request gönderilince API rate limit hatası
**Why it happens:** Varyasyon üretiminde parallel request'ler yapılıyor
**How to avoid:** Sequential generation veya rate limiting (exponential backoff) implement et
**Warning signs:** "429 Too Many Requests" hatası

### Pitfall 9: Insufficient Resolution
**What goes wrong:** 1K resolution print'e yetmiyor, etiketler bulanık basılıyor
**Why it happens:** Daha hızlı/ucuz diye 1K seçiliyor
**How to avoid:** Print için minimum 2K, ideali 4K kullan (maliyet: 2K=$0.134, 4K=$0.24)
**Warning signs:** Print edilen etiketlerde kalite düşük

### Pitfall 10: Figma Dependency Overload
**What goes wrong:** Her değişiklik için Figma'ya gidip manuel export yapılıyor
**Why it happens:** REST API kompleks görünüyor, manuel "daha hızlı" gibi
**How to avoid:** v1 için manuel yeterli AMA export process'i dokümante et, v2'de automate etmeyi planla
**Warning signs:** "Figma export unutuldu", bottleneck oluşuyor

## Code Examples

Verified patterns from official sources:

### Gemini Image Generation (Basic)
```python
# Source: https://ai.google.dev/gemini-api/docs/image-generation
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="""
    Create a premium chocolate product label for Sade brand.
    Text: "Antep Fıstıklı 50g"
    Style: Quiet luxury aesthetic with neutral palette, elegant serif typography.
    Layout: Minimalist, centered composition, ample white space.
    """,
    config=types.GenerateContentConfig(
        response_modalities=['Text', 'Image'],
        image_config=types.ImageConfig(
            aspect_ratio="3:4",
            image_size="2K"
        )
    )
)

# Extract and save image
for part in response.parts:
    if image := part.as_image():
        image.save("label_output.png")
```

### Gemini with Style Reference Images
```python
# Source: https://ai.google.dev/gemini-api/docs/image-generation
def generate_with_style_references(prompt: str, reference_paths: list[str]):
    """Style reference'ları kullanarak generate et"""

    # Load reference images
    reference_images = []
    for path in reference_paths:
        with open(path, 'rb') as f:
            reference_images.append({
                'mime_type': 'image/png',
                'data': f.read()
            })

    # Generate with references
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[
            {"text": prompt},
            *reference_images  # Up to 14 references
        ],
        config=types.GenerateContentConfig(
            response_modalities=['Image'],
            image_config=types.ImageConfig(
                aspect_ratio="3:4",
                image_size="2K"
            )
        )
    )

    return response.parts[0].as_image()
```

### Conversational Editing (Refinement)
```python
# Source: https://ai.google.dev/gemini-api/docs/image-generation
def refine_label_design(original_image_path: str, refinement_prompt: str):
    """Mevcut tasarımı conversational editing ile iyileştir"""

    # Load original image
    with open(original_image_path, 'rb') as f:
        original_data = f.read()

    # Edit conversationally
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",  # Faster for edits
        contents=[
            {
                'mime_type': 'image/png',
                'data': original_data
            },
            {
                "text": f"{refinement_prompt}. Preserve the input aspect ratio."
            }
        ],
        config=types.GenerateContentConfig(
            response_modalities=['Image']
        )
    )

    return response.parts[0].as_image()
```

### Figma REST API Export
```python
# Source: https://developers.figma.com/docs/rest-api/
import requests

def export_figma_template(file_key: str, node_id: str, format: str = "PNG"):
    """Figma file'dan template export et"""

    headers = {
        "X-Figma-Token": os.getenv("FIGMA_ACCESS_TOKEN")
    }

    # Get export URL
    url = f"https://api.figma.com/v1/images/{file_key}"
    params = {
        "ids": node_id,
        "format": format.lower(),
        "scale": 2  # 2x for high-res
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    # Download image
    image_url = data['images'][node_id]
    image_response = requests.get(image_url)

    return image_response.content
```

### Format Export Pipeline
```python
# Source: https://pillow.readthedocs.io/en/stable/
from PIL import Image
import cairosvg

def export_all_formats(image: Image.Image, base_path: str):
    """PNG, SVG, PDF formatlarında export et"""

    # PNG (high-res for print)
    png_path = f"{base_path}.png"
    image.save(png_path, "PNG", dpi=(300, 300), optimize=True)

    # PDF (for print houses)
    pdf_path = f"{base_path}.pdf"
    # Convert to RGB if needed (PDF doesn't support RGBA well)
    if image.mode == 'RGBA':
        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
        rgb_image.paste(image, mask=image.split()[3])
        rgb_image.save(pdf_path, "PDF", resolution=300.0)
    else:
        image.save(pdf_path, "PDF", resolution=300.0)

    # SVG (note: rasterized, for true vector use Figma export)
    # AI generates raster, so this is PNG wrapped in SVG
    svg_path = f"{base_path}.svg"
    # Save PNG temporarily
    temp_png = f"{base_path}_temp.png"
    image.save(temp_png, "PNG")
    # Note: cairosvg converts SVG->PNG, not PNG->SVG
    # For true SVG, export from Figma or use vectorization tool

    return {
        "png": png_path,
        "pdf": pdf_path
    }
```

### CrewAI Tool Integration
```python
# Source: https://docs.crewai.com/en/learn/dalle-image-generation
from crewai import Agent, Task
from crewai.tools import BaseTool

class GeminiImageTool(BaseTool):
    name: str = "Generate Product Label"
    description: str = "Generates product label design using Gemini 3 Pro Image API"

    def _run(self, product_info: dict) -> str:
        """Generate label and return path"""
        prompt = self._build_prompt(product_info)
        image = generate_with_style_references(
            prompt,
            reference_paths=glob("style_guide/reference_images/*.png")
        )

        # Save
        output_path = f"outputs/labels/{product_info['name']}/generated.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        image.save(output_path)

        return output_path

# Agent definition
curator_agent = Agent(
    role="Visual Design Curator",
    goal="Create premium product label designs",
    tools=[GeminiImageTool()],
    backstory="Expert in quiet luxury aesthetics...",
    allow_delegation=False
)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| DALL-E 2/3 | Gemini 3 Pro Image | Q4 2025 | Daha iyi text rendering, daha ucuz ($0.039 vs $0.040), referans görsel desteği |
| Stable Diffusion (self-host) | API-based services | 2024-2025 | Infrastructure cost yok, sürekli improvement, text rendering daha iyi |
| Keyword prompts | Narrative prompts | 2024-2025 | Gemini gibi models dil anlayışı çok gelişti, narrative daha iyi sonuç |
| Single-shot generation | Variation + selection | 2025-2026 | Workflow pattern olarak standard haline geldi |
| Manual human approval | HITL frameworks (Prefect, LangChain) | 2025-2026 | Type-safe, audit trail, scalable |
| Manual Figma export | REST API automation | Ongoing | v1'de manual OK, v2'de automate edilmeli |

**Deprecated/outdated:**
- **DALL-E 2**: Text rendering zayıf, Gemini 3 Pro superiyor
- **Midjourney API**: Resmi API yok, Discord bot unreliable
- **Stable Diffusion v1.5**: Text rendering çok zayıf, yeni modeller (SDXL, FLUX) daha iyi ama Gemini hala önde
- **PIL-only workflows**: Format conversion için CairoSVG gibi specialized tools kullan

## Open Questions

Things that couldn't be fully resolved:

1. **True Vector (SVG) Output from AI**
   - What we know: Gemini (ve diğer AI modeller) raster görsel üretir, vector değil
   - What's unclear: True vector SVG için en pratik yol nedir? (a) Figma template + AI-generated raster overlay, (b) Vectorization tool (Vectorizer.AI), (c) AI'yı sadece concept için kullan, Figma'da finalize et
   - Recommendation: v1 için (c) yaklaşımı - AI concept/variation üretir, kullanıcı Figma'da finalize eder. v2'de automation için (a) veya (b) explore edilebilir

2. **Gemini 3 Pro Image Availability**
   - What we know: `gemini-3-pro-image-preview` preview phase'de (Ocak 2026)
   - What's unclear: Production availability tarihi, pricing stability, rate limits
   - Recommendation: Preview API kullanarak başla, production'da `gemini-2.5-flash-image` fallback planı yap (daha hızlı, ucuz, ama text rendering biraz daha zayıf)

3. **Figma Template Complexity**
   - What we know: Figma REST API file export destekliyor
   - What's unclear: Template'lerin ne kadar complex olması gerekiyor? AI kendisi tasarım yaparken Figma template'i ne için kullanılacak?
   - Recommendation: Figma'yı (1) style guide reference görselleri oluşturmak için, (2) final approval sonrası vector format'a çevirmek için kullan. AI'ın generation phase'inde Figma'ya dependency olmasın

4. **Multi-Language Text Rendering**
   - What we know: Gemini Türkçe text render edebilir
   - What's unclear: Special karakterler (ı, ş, ğ, ü, ç) render kalitesi nasıl?
   - Recommendation: Style guide oluştururken Türkçe karakterli örnekler ekle, test et. Sorun varsa text overlay stratejisine geç

5. **Print Production Requirements**
   - What we know: 2K/4K resolution, PDF format, 300 DPI standard
   - What's unclear: Sade'nin print house'ı başka requirement'lar isteyebilir mi? (CMYK color space, bleed, etc.)
   - Recommendation: Phase planning sırasında print house requirements'ları sor, gerekirse export pipeline'ı buna göre customize et

## Sources

### Primary (HIGH confidence)
- [Gemini API Image Generation Docs](https://ai.google.dev/gemini-api/docs/image-generation) - Official documentation
- [Gemini 2.5 Flash Image Prompting Guide](https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/) - Official best practices
- [Figma REST API Introduction](https://developers.figma.com/docs/rest-api/) - API documentation
- [Python Pillow Documentation](https://pillow.readthedocs.io/en/stable/) - Official docs
- [CrewAI Image Generation Guide](https://docs.crewai.com/en/learn/dalle-image-generation) - DALL-E örneği ama pattern Gemini'ye uygulanabilir

### Secondary (MEDIUM confidence)
- [AI Image Generation Complete Guide 2026](https://wavespeed.ai/blog/posts/complete-guide-ai-image-apis-2026/) - API comparison, verification: multiple sources agree
- [Human-in-the-Loop AI Agents Python](https://medium.com/@ged1182/building-human-in-the-loop-ai-agents-in-python-nextjs-3ab362d3fcc1) - Workflow patterns
- [Quiet Luxury Design Aesthetic 2026](https://luxurycolumnist.com/quiet-luxury-trends-lifestyle-guide/) - Design principles
- [AI Image Generation Mistakes 2026](https://www.godofprompt.ai/blog/10-ai-image-generation-mistakes-99percent-of-people-make-and-how-to-fix-them) - Common pitfalls

### Tertiary (LOW confidence - needs validation)
- WebSearch results on Figma API Python integration - no official Python SDK found, REST API + requests library standard approach
- WebSearch on product label AI automation - emerging domain, limited established patterns
- Style consistency implementation - various approaches, no single standard yet

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Google-genai, CrewAI, Pillow well-documented and stable
- Architecture: MEDIUM - Workflow patterns emerging but not yet standardized for AI visual design agents
- Pitfalls: MEDIUM - Based on general AI image generation best practices, verified with official Gemini docs, but specific to product labels is less documented

**Research date:** 2026-01-30
**Valid until:** 7 days (fast-moving domain - AI image generation evolving rapidly)

**Key findings summary:**
1. Gemini 3 Pro Image superior text rendering capability için ideal seçim
2. Variation-based workflow + supervised approval standard pattern
3. Style consistency için reference images (up to 14) kritik
4. Narrative prompting > keyword prompts (Gemini'nin güçlü dil anlayışı)
5. Format export pipeline automate edilmeli (PNG/PDF minimum)
6. Figma entegrasyonu v1'de optional (manual export OK), v2'de REST API ile automate edilebilir
7. True vector SVG için AI generation yeterli değil, Figma post-processing gerekli

**Next steps for planner:**
- Style guide oluşturma task'ı öncelikli (referans görseller olmadan generation kalitesi düşük)
- Gemini API key ve quota verify et
- Print house requirements'ları netleştir (CMYK, bleed, color profile)
- Test product ile end-to-end workflow validate et
