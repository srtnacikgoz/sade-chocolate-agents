#!/usr/bin/env python3
"""
Sade Chocolate - The Pricing Analyst Agent Çalıştırma Scripti.

Kullanım:
    python scripts/run_pricing_analyst.py           # Agent'ı çalıştır
    python scripts/run_pricing_analyst.py --dry-run # Sadece syntax kontrolü

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
        from sade_agents.agents.pricing_analyst import PricingAnalystAgent
        from sade_agents.config import get_settings
        from sade_agents.skills import fiyat_kontrol

        print("  ✓ SadeAgent import edildi")
        print("  ✓ PricingAnalystAgent import edildi")
        print("  ✓ Config modülü import edildi")
        print("  ✓ fiyat_kontrol skill import edildi")

        # Agent oluştur (API çağrısı olmadan)
        agent = PricingAnalystAgent()
        print(f"  ✓ PricingAnalystAgent oluşturuldu")
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
    """The Pricing Analyst agent'ı çalıştırır."""
    print("📊 Sade Chocolate - The Pricing Analyst")
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

        from sade_agents.agents.pricing_analyst import PricingAnalystAgent

        # Agent oluştur
        print("\n📦 Agent oluşturuluyor...")
        agent = PricingAnalystAgent()
        print(f"  → Rol: {agent.role}")
        print(f"  → Departman: {agent.department}")
        print(f"  → Otonomi: {agent.autonomy_level}")
        if agent.tools:
            print(f"  → Tools: {[t.name for t in agent.tools]}")

        # Fiyat analizi görevi
        print("\n📋 Görev: Rakip fiyat analizi ve Sade için öneri")
        print("-" * 50)

        task = Task(
            description="""
Rakip çikolata markalarının fiyatlarını analiz et ve Sade için fiyat stratejisi öner.

1. Önce 'fiyat_kontrol' tool'unu kullanarak tüm rakiplerin fiyatlarını çek.
   - Vakko, Butterfly, Divan, Baylan, Marie Antoinette

2. TL/gram bazında karşılaştırma yap:
   - En pahalı rakip kim?
   - En ucuz rakip kim?
   - Pazar ortalaması nedir?

3. Sade için öneriler hazırla:
   - Sade'nin hedefi: 4.50-5.50 TL/gram arası premium segment
   - Vakko ile doğrudan rekabet
   - Marka primi: 1.5x

Analitik ve veri odaklı bir rapor hazırla.
            """,
            expected_output="""Rekabet istihbaratı raporu:
1. Rakip fiyat tablosu (TL/gram bazında)
2. Pazar segmentasyonu (Premium/Orta/Ekonomik)
3. Sade için fiyat önerisi ve gerekçe
4. Dikkat edilecek sinyaller""",
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
        print("✅ The Pricing Analyst - Rekabet Analizi Çıktısı")
        print("=" * 50)
        print()
        print(result)
        print()
        print("=" * 50)
        print("📊 The Pricing Analyst başarıyla çalıştı!")

    except Exception as e:
        print(f"\n❌ Hata: {e}")
        sys.exit(1)


def main() -> None:
    """Ana fonksiyon."""
    parser = argparse.ArgumentParser(
        description="Sade Chocolate - The Pricing Analyst Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python scripts/run_pricing_analyst.py           # Agent'ı çalıştır
  python scripts/run_pricing_analyst.py --dry-run # Sadece syntax kontrolü
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
