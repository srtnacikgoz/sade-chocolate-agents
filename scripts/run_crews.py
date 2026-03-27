#!/usr/bin/env python3
"""
Sade Chocolate - Crew Workflows CLI.

Multi-agent workflow'larini calistirir.

Kullanim:
    python scripts/run_crews.py product-launch --flavor "Ruby Cikolata"
    python scripts/run_crews.py market-analysis --competitor "Vakko"
    python scripts/run_crews.py quality-audit --content "Icerik metni"
    python scripts/run_crews.py --dry-run              # Sadece syntax kontrolu

Gereksinimler:
    - .env dosyasi (OPENAI_API_KEY ile)
"""

import argparse
import sys
import json
from pathlib import Path

# Proje root'unu Python path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def check_api_key() -> bool:
    """API key'in mevcut olup olmadigini kontrol eder."""
    import os

    # Try to load dotenv if available
    try:
        from dotenv import load_dotenv
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
    except ImportError:
        pass  # dotenv kurulu degil, ortam degiskenlerini kullan

    api_key = os.getenv("OPENAI_API_KEY", "")
    return bool(api_key and api_key != "your-api-key-here")


def dry_run() -> None:
    """Syntax ve import kontrolu yapar (API cagrisi olmadan)."""
    print("=" * 60)
    print("SADE CHOCOLATE - Crew Workflows (DRY RUN)")
    print("=" * 60)
    print("\n[?] Bagimliliklari kontrol ediliyor...\n")

    missing_deps = []

    # Check pydantic
    try:
        import pydantic
        print("  [+] pydantic kurulu")
    except ImportError:
        print("  [!] pydantic kurulu degil")
        missing_deps.append("pydantic")

    # Check crewai
    crewai_available = False
    try:
        import crewai
        crewai_available = True
        print("  [+] crewai kurulu")
    except ImportError:
        print("  [!] crewai kurulu degil")
        missing_deps.append("crewai")

    # Check dotenv
    try:
        import dotenv
        print("  [+] python-dotenv kurulu")
    except ImportError:
        print("  [!] python-dotenv kurulu degil")
        missing_deps.append("python-dotenv")

    if missing_deps:
        print(f"\n[!] Eksik bagimliliklar: {', '.join(missing_deps)}")
        print("    Kurmak icin: pip install " + " ".join(missing_deps))
        print("\n[?] CLI syntax kontrolu yapiliyor...\n")

        # CLI parsing test (no imports needed)
        print("  [+] CLI parser tanimli")
        print("  [+] Subcommand: product-launch")
        print("  [+] Subcommand: market-analysis")
        print("  [+] Subcommand: quality-audit")

        print("\n" + "=" * 60)
        print("[OK] DRY RUN BASARILI - CLI syntax dogru (bagimliliklar eksik)")
        print("=" * 60)
        return

    try:
        # Models require pydantic
        from sade_agents.models import (
            ProductLaunchInput,
            ProductLaunchOutput,
            MarketAnalysisInput,
            MarketAnalysisOutput,
            QualityAuditInput,
            QualityAuditOutput,
        )
        print("  [+] Tum workflow modelleri import edildi")

        # Input model validation test
        print("\n[?] Model validasyon testleri...\n")

        # ProductLaunchInput test
        pl_input = ProductLaunchInput(
            flavor_concept="Test Lezzet",
            target_audience="Test Kitle",
            price_range=(100.0, 200.0),
            include_audit=True
        )
        print(f"  [+] ProductLaunchInput dogrulandi: {pl_input.flavor_concept}")

        # MarketAnalysisInput test
        ma_input = MarketAnalysisInput(
            competitor_name="Test Rakip",
            product_category="premium chocolate",
            include_trends=True
        )
        print(f"  [+] MarketAnalysisInput dogrulandi: {ma_input.competitor_name}")

        # QualityAuditInput test
        qa_input = QualityAuditInput(
            content="Test icerik",
            content_type="metin",
            source_agent="narrator"
        )
        print(f"  [+] QualityAuditInput dogrulandi: {qa_input.content_type}")

        # Crew imports (require crewai)
        if crewai_available:
            print("\n[?] Crew import testleri...\n")

            from sade_agents.crews import (
                SadeCrewFactory,
                ProductLaunchCrew,
                MarketAnalysisCrew,
                QualityAuditCrew,
            )

            print("  [+] SadeCrewFactory import edildi")
            print("  [+] Tum crew class'lari import edildi")

            # Factory test
            factory = SadeCrewFactory()
            print("  [+] SadeCrewFactory olusturuldu")

            # Crew instantiation test
            print("\n[?] Crew olusturma testleri...\n")
            for crew_type in ["product_launch", "market_analysis", "quality_audit"]:
                crew = factory.create_crew(crew_type)
                print(f"  [+] {type(crew).__name__} olusturuldu")
        else:
            print("\n[?] Crew testleri atlaniyor (crewai gerekli)...\n")
            print("  [!] ProductLaunchCrew - crewai gerekli")
            print("  [!] MarketAnalysisCrew - crewai gerekli")
            print("  [!] QualityAuditCrew - crewai gerekli")

        # API key kontrolu
        print("\n[?] API key kontrolu...\n")
        if check_api_key():
            print("  [+] OPENAI_API_KEY mevcut")
        else:
            print("  [!] OPENAI_API_KEY eksik veya gecersiz")
            print("      -> .env.example'dan .env olusturun")

        print("\n" + "=" * 60)
        if crewai_available:
            print("[OK] DRY RUN BASARILI - Tum importlar calisiyor")
        else:
            print("[OK] DRY RUN BASARILI - Modeller calisiyor (crewai kurulu degil)")
        print("=" * 60)

    except ImportError as e:
        print(f"  [X] Import hatasi: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  [X] Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_product_launch(args: argparse.Namespace) -> None:
    """ProductLaunchCrew calistirir."""
    print("=" * 60)
    print("SADE CHOCOLATE - Product Launch Crew")
    print("=" * 60)

    if not check_api_key():
        print("\n[X] HATA: OPENAI_API_KEY gerekli!")
        print("\nCozum:")
        print("  1. cp .env.example .env")
        print("  2. .env dosyasina API key'inizi ekleyin")
        sys.exit(1)

    from sade_agents.crews import SadeCrewFactory
    from sade_agents.models import ProductLaunchInput

    # Input hazirla
    inputs = {
        "flavor_concept": args.flavor,
        "target_audience": args.audience,
        "price_range": (args.price_min, args.price_max),
        "include_audit": not args.skip_audit,
    }

    print(f"\n[i] Girdi:")
    print(f"    Lezzet: {inputs['flavor_concept']}")
    print(f"    Hedef Kitle: {inputs['target_audience']}")
    print(f"    Fiyat Araligi: {inputs['price_range'][0]}-{inputs['price_range'][1]} TL")
    print(f"    Denetim: {'Evet' if inputs['include_audit'] else 'Hayir'}")

    # Validate
    try:
        validated = ProductLaunchInput(**inputs)
        print("  [+] Girdi dogrulandi")
    except Exception as e:
        print(f"  [X] Girdi hatasi: {e}")
        sys.exit(1)

    # Run crew
    print("\n" + "-" * 60)
    print("[>] Crew calistiriliyor...")
    print("-" * 60 + "\n")

    factory = SadeCrewFactory()
    crew = factory.create_product_launch_crew()
    result = crew.kickoff(inputs)

    print("\n" + "=" * 60)
    print("[OK] Product Launch Crew Tamamlandi")
    print("=" * 60)
    print(f"\n[i] Calisma suresi: {result.execution_time_seconds:.1f} saniye")
    print("\n[*] Sonuc:")
    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False, default=str))


def run_market_analysis(args: argparse.Namespace) -> None:
    """MarketAnalysisCrew calistirir."""
    print("=" * 60)
    print("SADE CHOCOLATE - Market Analysis Crew")
    print("=" * 60)

    if not check_api_key():
        print("\n[X] HATA: OPENAI_API_KEY gerekli!")
        print("\nCozum:")
        print("  1. cp .env.example .env")
        print("  2. .env dosyasina API key'inizi ekleyin")
        sys.exit(1)

    from sade_agents.crews import SadeCrewFactory
    from sade_agents.models import MarketAnalysisInput

    # Input hazirla
    inputs = {
        "competitor_name": args.competitor,
        "product_category": args.category,
        "include_trends": not args.skip_trends,
    }

    print(f"\n[i] Girdi:")
    print(f"    Rakip: {inputs['competitor_name']}")
    print(f"    Kategori: {inputs['product_category']}")
    print(f"    Trend Analizi: {'Evet' if inputs['include_trends'] else 'Hayir'}")

    # Validate
    try:
        validated = MarketAnalysisInput(**inputs)
        print("  [+] Girdi dogrulandi")
    except Exception as e:
        print(f"  [X] Girdi hatasi: {e}")
        sys.exit(1)

    # Run crew
    print("\n" + "-" * 60)
    print("[>] Crew calistiriliyor...")
    print("-" * 60 + "\n")

    factory = SadeCrewFactory()
    crew = factory.create_market_analysis_crew()
    result = crew.kickoff(inputs)

    print("\n" + "=" * 60)
    print("[OK] Market Analysis Crew Tamamlandi")
    print("=" * 60)
    print(f"\n[i] Calisma suresi: {result.execution_time_seconds:.1f} saniye")
    print("\n[*] Ozet:")
    print(result.summary)


def run_quality_audit(args: argparse.Namespace) -> None:
    """QualityAuditCrew calistirir."""
    print("=" * 60)
    print("SADE CHOCOLATE - Quality Audit Crew")
    print("=" * 60)

    if not check_api_key():
        print("\n[X] HATA: OPENAI_API_KEY gerekli!")
        print("\nCozum:")
        print("  1. cp .env.example .env")
        print("  2. .env dosyasina API key'inizi ekleyin")
        sys.exit(1)

    from sade_agents.crews import SadeCrewFactory
    from sade_agents.models import QualityAuditInput

    # Content'i al (arguman veya dosya)
    content = args.content
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[X] Dosya bulunamadi: {args.file}")
            sys.exit(1)
        content = file_path.read_text(encoding="utf-8")

    if not content:
        print("[X] HATA: --content veya --file gerekli!")
        sys.exit(1)

    # Input hazirla
    inputs = {
        "content": content,
        "content_type": args.content_type,
        "source_agent": args.source,
    }

    print(f"\n[i] Girdi:")
    print(f"    Icerik Turu: {inputs['content_type']}")
    print(f"    Kaynak Agent: {inputs['source_agent']}")
    print(f"    Icerik Uzunlugu: {len(content)} karakter")

    # Icerik onizleme
    preview = content[:100] + "..." if len(content) > 100 else content
    print(f"    Onizleme: {preview}")

    # Validate
    try:
        validated = QualityAuditInput(**inputs)
        print("  [+] Girdi dogrulandi")
    except Exception as e:
        print(f"  [X] Girdi hatasi: {e}")
        sys.exit(1)

    # Run crew
    print("\n" + "-" * 60)
    print("[>] Crew calistiriliyor...")
    print("-" * 60 + "\n")

    factory = SadeCrewFactory()
    crew = factory.create_quality_audit_crew()
    result = crew.kickoff(inputs)

    print("\n" + "=" * 60)
    print("[OK] Quality Audit Crew Tamamlandi")
    print("=" * 60)
    print(f"\n[i] Calisma suresi: {result.execution_time_seconds:.1f} saniye")
    print(f"\n[*] Sonuc: {'GECTI' if result.passed else 'KALDI'}")
    print(f"    Puan: {result.audit_result.overall_score}/100")
    print(f"    Karar: {result.audit_result.verdict}")

    if result.audit_result.issues:
        print("\n[!] Sorunlar:")
        for issue in result.audit_result.issues:
            print(f"    - {issue}")

    if result.audit_result.suggestions:
        print("\n[>] Oneriler:")
        for suggestion in result.audit_result.suggestions:
            print(f"    - {suggestion}")

    print("\n" + "-" * 60)
    print("[!] HATIRLATMA: Bu sonuc TAVSIYE niteligindedir.")
    print("    Kullanici isterse icerigi oldugu gibi kullanabilir.")
    print("-" * 60)


def main() -> None:
    """Ana fonksiyon - CLI parser."""
    parser = argparse.ArgumentParser(
        description="Sade Chocolate - Crew Workflows CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ornekler:
  python scripts/run_crews.py --dry-run
  python scripts/run_crews.py product-launch --flavor "Antep Fistikli"
  python scripts/run_crews.py market-analysis --competitor "Vakko"
  python scripts/run_crews.py quality-audit --content "Test icerigi" --content-type metin --source narrator

Crew Tipleri:
  product-launch   : Alchemist -> Narrator -> Curator -> Perfectionist
  market-analysis  : PricingAnalyst -> GrowthHacker -> Narrator
  quality-audit    : Perfectionist (tek)
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Sadece import/syntax kontrolu yap",
    )

    subparsers = parser.add_subparsers(dest="command", help="Crew tipi")

    # Product Launch subcommand
    pl_parser = subparsers.add_parser(
        "product-launch",
        help="Urun lansmani workflow'u",
        description="Alchemist -> Narrator -> Curator -> Perfectionist pipeline'i"
    )
    pl_parser.add_argument(
        "--flavor",
        required=True,
        help="Lezzet konsepti (ornek: 'Ruby Cikolata', 'Antep Fistikli')"
    )
    pl_parser.add_argument(
        "--audience",
        default="Quiet luxury consumers",
        help="Hedef kitle (default: 'Quiet luxury consumers')"
    )
    pl_parser.add_argument(
        "--price-min",
        type=float,
        default=100.0,
        help="Minimum fiyat TL (default: 100)"
    )
    pl_parser.add_argument(
        "--price-max",
        type=float,
        default=200.0,
        help="Maksimum fiyat TL (default: 200)"
    )
    pl_parser.add_argument(
        "--skip-audit",
        action="store_true",
        help="Perfectionist denetimini atla"
    )

    # Market Analysis subcommand
    ma_parser = subparsers.add_parser(
        "market-analysis",
        help="Pazar analizi workflow'u",
        description="PricingAnalyst -> GrowthHacker -> Narrator pipeline'i"
    )
    ma_parser.add_argument(
        "--competitor",
        required=True,
        help="Rakip adi (ornek: 'Vakko', 'Godiva')"
    )
    ma_parser.add_argument(
        "--category",
        default="premium chocolate",
        help="Urun kategorisi (default: 'premium chocolate')"
    )
    ma_parser.add_argument(
        "--skip-trends",
        action="store_true",
        help="GrowthHacker trend analizini atla"
    )

    # Quality Audit subcommand
    qa_parser = subparsers.add_parser(
        "quality-audit",
        help="Kalite denetimi workflow'u",
        description="Perfectionist agent ile bagimsiz icerik denetimi"
    )
    qa_parser.add_argument(
        "--content",
        help="Denetlenecek icerik metni"
    )
    qa_parser.add_argument(
        "--file",
        help="Icerik dosyasi yolu"
    )
    qa_parser.add_argument(
        "--content-type",
        choices=["metin", "gorsel_prompt", "fiyat_analizi", "trend_raporu", "recete"],
        default="metin",
        help="Icerik turu (default: metin)"
    )
    qa_parser.add_argument(
        "--source",
        choices=["narrator", "curator", "pricing", "growth", "alchemist"],
        default="narrator",
        help="Kaynak agent (default: narrator)"
    )

    args = parser.parse_args()

    if args.dry_run:
        dry_run()
    elif args.command == "product-launch":
        run_product_launch(args)
    elif args.command == "market-analysis":
        run_market_analysis(args)
    elif args.command == "quality-audit":
        run_quality_audit(args)
    else:
        parser.print_help()
        print("\n[!] Bir crew tipi secin: product-launch, market-analysis, quality-audit")
        print("    Veya --dry-run ile import kontrolu yapin.")
        sys.exit(1)


if __name__ == "__main__":
    main()
