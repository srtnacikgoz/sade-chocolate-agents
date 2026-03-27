#!/usr/bin/env python3
"""
The Curator - Gorsel Tasarim Agent'i calistirma scripti.

Kullanim:
    python scripts/run_curator.py                    # Tam calisma
    python scripts/run_curator.py --dry-run          # Syntax kontrolu
    python scripts/run_curator.py --product "Ruby"   # Belirli urun
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def check_api_key() -> bool:
    """API key kontrolu."""
    import os

    # .env varsa yukle (dotenv opsiyonel)
    try:
        from dotenv import load_dotenv
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
    except ImportError:
        pass  # dotenv kurulu degil, ortam degiskenlerini kullan

    key = os.getenv("OPENAI_API_KEY")
    return bool(key and key != "your-api-key-here")


def dry_run() -> None:
    """Dry run - sadece import ve syntax kontrolu."""
    print("=" * 60)
    print("THE CURATOR - Gorsel Tasarim Agent'i (DRY RUN)")
    print("=" * 60)
    print("\n🔍 Import kontrolu...\n")

    try:
        from sade_agents.agents.curator import CuratorAgent
        print("  ✓ CuratorAgent import edildi")

        from sade_agents.skills import gorsel_tasarla
        print("  ✓ gorsel_tasarla skill import edildi")

        from sade_agents.config import get_settings
        print("  ✓ Config import edildi")

        # Agent olusturma testi
        agent = CuratorAgent()
        print(f"  ✓ Agent olusturuldu: {agent.role}")
        print(f"    - Department: {agent.department}")
        print(f"    - Autonomy: {agent.autonomy_level}")
        print(f"    - Tools: {[t.name for t in agent.tools]}")

        # Skill testi (CrewAI tool'lari .run() ile cagrilir)
        print("\n🎨 Skill testi...\n")
        bilgi = gorsel_tasarla.run(
            urun_adi="Test Urun",
            urun_gramaj="50g",
            urun_aciklama="test aciklama",
            mod="bilgi"
        )
        print("  ✓ gorsel_tasarla(mod='bilgi') calisti")
        print(f"    Cikti uzunlugu: {len(bilgi)} karakter")

        prompt = gorsel_tasarla.run(
            urun_adi="Test Urun",
            urun_gramaj="50g",
            urun_aciklama="test aciklama",
            mod="prompt"
        )
        print("  ✓ gorsel_tasarla(mod='prompt') calisti")
        print(f"    Prompt uzunlugu: {len(prompt)} karakter")

        # API key kontrolu
        if check_api_key():
            print("\n  ✓ OPENAI_API_KEY mevcut")
        else:
            print("\n  ⚠ OPENAI_API_KEY eksik veya gecersiz")
            print("    → .env.example'dan .env olusturun")

        print("\n" + "=" * 60)
        print("✅ DRY RUN BASARILI - Tum importlar ve syntax dogru")
        print("=" * 60)

    except ImportError as e:
        print(f"  ✗ Import hatasi: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  ✗ Hata: {e}")
        sys.exit(1)


def run_agent(product_name: str = "Bitter Orange", product_weight: str = "85g") -> None:
    """Agent'i calistir."""
    print("=" * 60)
    print("THE CURATOR - Gorsel Tasarim Agent'i")
    print("=" * 60)

    if not check_api_key():
        print("\n❌ HATA: OPENAI_API_KEY gerekli!")
        print("\nCozum:")
        print("  1. cp .env.example .env")
        print("  2. .env dosyasina API key'inizi ekleyin")
        sys.exit(1)

    try:
        from crewai import Crew, Task

        from sade_agents.agents.curator import CuratorAgent
        from sade_agents.config import get_settings

        settings = get_settings()
        print(f"\n📋 Ayarlar:")
        print(f"   Model: {settings.openai_model_name}")
        print(f"   Urun: {product_name} ({product_weight})")

        # Agent olustur
        curator = CuratorAgent()
        print(f"\n🎨 Agent: {curator.role}")
        print(f"   Department: {curator.department}")
        print(f"   Autonomy: {curator.autonomy_level}")

        # Task tanimla - varyasyon promptlari olusturma
        task = Task(
            description=f"""
Sade Chocolate icin "{product_name}" ({product_weight}) urunune etiket tasarimi yap.

1. Oncelikle `gorsel_tasarla` skill'ini "bilgi" moduyla cagirarak stil kilavuzunu incele.

2. Ardindan `gorsel_tasarla` skill'ini "varyasyon_prompt" moduyla cagirarak
   3 farkli tasarim varyasyonu icin Gemini promptlari olustur.

3. Her varyasyonun temel ozelliklerini ve farklilaşan yonlerini acikla.

4. Kullaniciya hangi varyasyonu tercih ettigini sor.

NOT: Bu gorev sadece prompt olusturma asamasi. Gercek gorsel uretim
Gemini API entegrasyonu ile ayri bir workflow'da yapilacak.
            """,
            expected_output="""
Markdown formatinda cikti:
1. Stil Kilavuzu Ozeti
2. 3 Varyasyon Promptu (Gemini-ready)
3. Her varyasyonun kisa aciklamasi
4. Kullaniciya secim sorusu
            """,
            agent=curator,
        )

        # Crew olustur ve calistir
        crew = Crew(
            agents=[curator],
            tasks=[task],
            verbose=True,
        )

        print("\n" + "-" * 60)
        print("🚀 Gorev basliyor...")
        print("-" * 60 + "\n")

        result = crew.kickoff()

        print("\n" + "=" * 60)
        print("📋 SONUC")
        print("=" * 60)
        print(result)

    except ImportError as e:
        print(f"\n❌ Import hatasi: {e}")
        print("CrewAI kurulu mu? pip install crewai")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="The Curator - Sade Chocolate Gorsel Tasarim Agent'i"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Sadece import ve syntax kontrolu yap, API cagirisi yapma"
    )
    parser.add_argument(
        "--product",
        type=str,
        default="Bitter Orange",
        help="Tasarlanacak urun adi (default: Bitter Orange)"
    )
    parser.add_argument(
        "--weight",
        type=str,
        default="85g",
        help="Urun gramaji (default: 85g)"
    )

    args = parser.parse_args()

    if args.dry_run:
        dry_run()
    else:
        run_agent(args.product, args.weight)


if __name__ == "__main__":
    main()
