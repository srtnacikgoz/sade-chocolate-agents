#!/usr/bin/env python3
"""
Sade Chocolate - The Growth Hacker Agent Çalıştırma Scripti.

Kullanım:
    python scripts/run_growth_hacker.py           # Agent'ı çalıştır
    python scripts/run_growth_hacker.py --dry-run # Sadece syntax kontrolü

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
        from sade_agents.agents.growth_hacker import GrowthHackerAgent
        from sade_agents.config import get_settings
        from sade_agents.skills import sosyal_nabiz

        print("  ✓ SadeAgent import edildi")
        print("  ✓ GrowthHackerAgent import edildi")
        print("  ✓ Config modülü import edildi")
        print("  ✓ sosyal_nabiz skill import edildi")

        # Agent oluştur (API çağrısı olmadan)
        agent = GrowthHackerAgent()
        print(f"  ✓ GrowthHackerAgent oluşturuldu")
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
    """The Growth Hacker agent'ı çalıştırır."""
    print("📈 Sade Chocolate - The Growth Hacker")
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

        from sade_agents.agents.growth_hacker import GrowthHackerAgent

        # Agent oluştur
        print("\n📦 Agent oluşturuluyor...")
        agent = GrowthHackerAgent()
        print(f"  → Rol: {agent.role}")
        print(f"  → Departman: {agent.department}")
        print(f"  → Otonomi: {agent.autonomy_level}")
        if agent.tools:
            print(f"  → Tools: {[t.name for t in agent.tools]}")

        # Trend analizi görevi
        print("\n📋 Görev: Son 24 saatin trend raporu")
        print("-" * 50)

        task = Task(
            description="""
Son 24 saatin sosyal medya ve pazar trend raporunu hazırla.

1. Önce 'sosyal_nabiz' tool'unu kullanarak tüm platformların verilerini çek.
   - X (Twitter) hashtag'leri
   - Instagram trendleri
   - Reddit konuşmaları
   - Pazar sinyalleri

2. Verileri analiz et:
   - En çok konuşulan konular neler?
   - Yükselen trendler hangileri?
   - Sade için fırsatlar var mı?

3. Aksiyon önerileri hazırla:
   - Hemen değerlendirilmesi gereken fırsatlar
   - Takipte tutulması gereken trendler
   - Rakip hareketlerine dikkat

Trend scout perspektifinden, data-driven ama sezgisel bir rapor hazırla.
            """,
            expected_output="""Günlük trend raporu:
1. Platform bazlı trend özeti
2. Sade için fırsat analizi (yüksek/orta/düşük öncelik)
3. Rakip istihbaratı
4. Aksiyon önerileri (ne, neden, ne zaman)""",
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
        print("✅ The Growth Hacker - Trend Raporu Çıktısı")
        print("=" * 50)
        print()
        print(result)
        print()
        print("=" * 50)
        print("📈 The Growth Hacker başarıyla çalıştı!")

    except Exception as e:
        print(f"\n❌ Hata: {e}")
        sys.exit(1)


def main() -> None:
    """Ana fonksiyon."""
    parser = argparse.ArgumentParser(
        description="Sade Chocolate - The Growth Hacker Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python scripts/run_growth_hacker.py           # Agent'ı çalıştır
  python scripts/run_growth_hacker.py --dry-run # Sadece syntax kontrolü
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
