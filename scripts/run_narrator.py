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

        print("  ✓ SadeAgent import edildi")
        print("  ✓ NarratorAgent import edildi")
        print("  ✓ Config modülü import edildi")

        # Agent oluştur (API çağrısı olmadan)
        agent = NarratorAgent()
        print(f"  ✓ NarratorAgent oluşturuldu")
        print(f"    → Rol: {agent.role}")
        print(f"    → Departman: {agent.department}")
        print(f"    → Otonomi: {agent.autonomy_level}")

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
    print("=" * 40)

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

        # Marka tanıtım görevi
        print("\n📋 Görev tanımlanıyor...")
        task = Task(
            description="""
Sade Chocolate için kısa bir marka tanıtım cümlesi yaz.

Kurallar:
- "Sessiz Lüks" tonunda ol
- Maksimum 2-3 cümle
- Emoji kullanma
- "Hemen Al", "Kaçırma" gibi ifadeler yasak
- Sofistike ve understated ol

Örnek ton: "Bazı tatlar anlatılmaz, sadece hissedilir."
            """,
            expected_output="Sade Chocolate için 2-3 cümlelik sofistike marka tanıtımı",
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

        print("\n" + "=" * 40)
        print("✅ The Narrator Çıktısı:")
        print("-" * 40)
        print(result)
        print("=" * 40)
        print("\n🎉 The Narrator başarıyla çalıştı!")

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
