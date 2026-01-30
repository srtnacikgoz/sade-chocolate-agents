#!/usr/bin/env python3
"""
Sade Chocolate - The Alchemist Agent Çalıştırma Scripti.

Kullanım:
    python scripts/run_alchemist.py           # Agent'ı çalıştır
    python scripts/run_alchemist.py --dry-run # Sadece syntax kontrolü

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
        from sade_agents.agents.alchemist import AlchemistAgent
        from sade_agents.agents.base import SadeAgent
        from sade_agents.config import get_settings
        from sade_agents.skills import lezzet_pisileri

        print("  ✓ SadeAgent import edildi")
        print("  ✓ AlchemistAgent import edildi")
        print("  ✓ Config modülü import edildi")
        print("  ✓ lezzet_pisileri skill import edildi")

        # Agent oluştur (API çağrısı olmadan)
        agent = AlchemistAgent()
        print("  ✓ AlchemistAgent oluşturuldu")
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
    """The Alchemist agent'ı çalıştırır."""
    print("🧪 Sade Chocolate - The Alchemist")
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

        from sade_agents.agents.alchemist import AlchemistAgent

        # Agent oluştur
        print("\n📦 Agent oluşturuluyor...")
        agent = AlchemistAgent()
        print(f"  → Rol: {agent.role}")
        print(f"  → Departman: {agent.department}")
        print(f"  → Otonomi: {agent.autonomy_level}")
        if agent.tools:
            print(f"  → Tools: {[t.name for t in agent.tools]}")

        # Lezzet önerisi görevi
        print("\n📋 Görev: Yeni bitter çikolata ürünü için lezzet önerileri")
        print("-" * 50)

        task = Task(
            description="""
Yeni bir premium bitter çikolata ürünü için lezzet kombinasyonu öner.

1. Önce 'lezzet_pisileri' tool'unu kullanarak:
   - Bitter çikolata eşleştirmelerini çek (mod: eslestir)
   - Bu ayın mevsimsel malzemelerini kontrol et (mod: mevsim)
   - Çikolata teknik bilgilerini gözden geçir (mod: bilgi)

2. Analiz yap:
   - Klasik vs cesur kombinasyonlar
   - Mevsimsel uygunluk
   - Hedef segment (premium hediye kutusu)

3. Öneri hazırla:
   - 2-3 farklı lezzet kombinasyonu
   - Her biri için "neden çalışır" açıklaması
   - Couverture seçimi (Callebaut 811 veya Valrhona Guanaja)
   - "Sessiz Lüks" markasına uygun isim önerileri

Flavor Architect perspektifinden, bilimsel ama erişilebilir bir rapor hazırla.
            """,
            expected_output="""Lezzet önerisi raporu:
1. Çikolata bazı ve teknik detaylar
2. 2-3 lezzet kombinasyonu (malzemeler + neden çalışır)
3. Mevsimsel uyumluluk değerlendirmesi
4. Ürün konsepti ve isim önerileri""",
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
        print("✅ The Alchemist - Lezzet Önerisi Çıktısı")
        print("=" * 50)
        print()
        print(result)
        print()
        print("=" * 50)
        print("🧪 The Alchemist başarıyla çalıştı!")

    except Exception as e:
        print(f"\n❌ Hata: {e}")
        sys.exit(1)


def main() -> None:
    """Ana fonksiyon."""
    parser = argparse.ArgumentParser(
        description="Sade Chocolate - The Alchemist Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python scripts/run_alchemist.py           # Agent'ı çalıştır
  python scripts/run_alchemist.py --dry-run # Sadece syntax kontrolü
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
