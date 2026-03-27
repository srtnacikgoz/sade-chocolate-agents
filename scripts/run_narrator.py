#!/usr/bin/env python3
"""
Sade Chocolate - The Narrator Agent Çalıştırma Scripti.

Kullanım:
    python scripts/run_narrator.py           # Agent'ı çalıştır
    python scripts/run_narrator.py --dry-run # Sadece syntax kontrolü

Gereksinimler:
    - .env dosyası (OPENAI_API_KEY ile)
    - veya OPENAI_API_KEY ortam değişkeni
"""

import argparse
import sys
from pathlib import Path

# Proje root'unu Python path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def check_api_key() -> bool:
    """API key'in mevcut olup olmadığını kontrol eder."""
    import os

    from dotenv import load_dotenv

    # .env varsa yükle
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)

    api_key = os.getenv("OPENAI_API_KEY", "")
    return bool(api_key and api_key != "your-api-key-here")


def dry_run() -> None:
    """Syntax ve import kontrolü yapar (API çağrısı olmadan)."""
    print("🔍 Dry run: Import ve syntax kontrolü...")

    try:
        from sade_agents.agents.base import SadeAgent
        from sade_agents.agents.narrator import NarratorAgent
        from sade_agents.config import get_settings
        from sade_agents.skills import hikayelestir

        print("  ✓ SadeAgent import edildi")
        print("  ✓ NarratorAgent import edildi")
        print("  ✓ Config modülü import edildi")
        print("  ✓ hikayelestir skill import edildi")

        # Agent oluştur (API çağrısı olmadan)
        agent = NarratorAgent()
        print(f"  ✓ NarratorAgent oluşturuldu")
        print(f"    → Rol: {agent.role}")
        print(f"    → Departman: {agent.department}")
        print(f"    → Otonomi: {agent.autonomy_level}")

        # Tools kontrolü
        if agent.tools:
            print(f"  ✓ Tools: {len(agent.tools)} adet")
            for tool in agent.tools:
                print(f"    → {tool.name}")
        else:
            print("  ⚠ Agent'ta tool yok")

        # API key kontrolü
        if check_api_key():
            print("  ✓ OPENAI_API_KEY mevcut")
        else:
            print("  ⚠ OPENAI_API_KEY eksik veya geçersiz")
            print("    → .env.example'dan .env oluşturun")

        print("\n✓ Dry run başarılı - tüm importlar çalışıyor")

    except ImportError as e:
        print(f"  ✗ Import hatası: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  ✗ Beklenmeyen hata: {e}")
        sys.exit(1)


def run_agent() -> None:
    """The Narrator agent'ı çalıştırır."""
    print("🍫 Sade Chocolate - The Narrator")
    print("=" * 50)

    # API key kontrolü
    if not check_api_key():
        print("\n❌ HATA: OPENAI_API_KEY gerekli!")
        print("\nÇözüm:")
        print("  1. cp .env.example .env")
        print("  2. .env dosyasına API key'inizi ekleyin")
        print("  3. Bu scripti tekrar çalıştırın")
        sys.exit(1)

    try:
        from crewai import Crew, Task

        from sade_agents.agents.narrator import NarratorAgent

        # Agent oluştur
        print("\n📦 Agent oluşturuluyor...")
        agent = NarratorAgent()
        print(f"  → Rol: {agent.role}")
        print(f"  → Departman: {agent.department}")
        print(f"  → Otonomi: {agent.autonomy_level}")
        if agent.tools:
            print(f"  → Tools: {[t.name for t in agent.tools]}")

        # Hikaye oluşturma görevi (hikayelestir tool kullanarak)
        print("\n📋 Görev: 85g Ruby Çikolata için hikaye oluştur")
        print("-" * 50)

        task = Task(
            description="""
85g Ruby Çikolata Tablet için ürün hikayeleri oluştur.

Ürün Bilgileri:
- Ürün Adı: Ruby Çikolata Tablet
- Gramaj: 85g
- İçerik/Özellikler: Doğal pembe renk, mayhoş tat, dördüncü tür çikolata, Ruby kakao çekirdeği

'hikayelestir' tool'unu kullanarak 3 farklı içerik üret:
1. Etiket Hikayesi - ürün arkasına
2. Instagram Caption - sosyal medya postu
3. Kutu İçi Not - hediye kartı

Kurallar:
- "Sessiz Lüks" tonunda ol
- Emoji kullanma
- "Hemen Al", "Kaçırma", "Şok Fiyat" gibi ifadeler YASAK
- Sofistike ve understated ol
- Monocle/Kinfolk dergisi editörü gibi konuş
            """,
            expected_output="""3 bölümlü içerik:
1. Etiket Hikayesi (başlık + 2-3 cümle + gramaj)
2. Instagram Caption (tek kelime açılış + hikaye + hashtagler)
3. Kutu İçi Not (tırnak içinde cümle + imza)""",
            agent=agent,
        )

        # Crew oluştur ve çalıştır
        print("\n🚀 Çalıştırılıyor...\n")
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True,
        )

        result = crew.kickoff()

        print("\n" + "=" * 50)
        print("✅ The Narrator - /hikayelestir Çıktısı")
        print("=" * 50)
        print()
        print(result)
        print()
        print("=" * 50)
        print("🎉 The Narrator başarıyla çalıştı!")

    except Exception as e:
        print(f"\n❌ Hata: {e}")
        sys.exit(1)


def main() -> None:
    """Ana fonksiyon."""
    parser = argparse.ArgumentParser(
        description="Sade Chocolate - The Narrator Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python scripts/run_narrator.py           # Agent'ı çalıştır
  python scripts/run_narrator.py --dry-run # Sadece syntax kontrolü
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Sadece import/syntax kontrolü yap, API çağrısı yapma",
    )

    args = parser.parse_args()

    if args.dry_run:
        dry_run()
    else:
        run_agent()


if __name__ == "__main__":
    main()
