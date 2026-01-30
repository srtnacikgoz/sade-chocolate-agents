#!/usr/bin/env python3
"""
The Perfectionist - UX Denetim Agent'i calistirma scripti.

Kullanim:
    python scripts/run_perfectionist.py                      # Interaktif mod
    python scripts/run_perfectionist.py --dry-run            # Syntax kontrolu
    python scripts/run_perfectionist.py --content "metin"    # Direkt icerik denetimi
    python scripts/run_perfectionist.py --file input.txt     # Dosyadan icerik
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
    print("THE PERFECTIONIST - UX Denetim Agent'i (DRY RUN)")
    print("=" * 60)
    print("\n[?] Import kontrolu...\n")

    try:
        from sade_agents.agents.perfectionist import PerfectionistAgent
        print("  [+] PerfectionistAgent import edildi")

        from sade_agents.skills import denetle, stil_kilavuzu_yukle, onaylanmis_ornekler_yukle
        print("  [+] Perfectionist skills import edildi")

        from sade_agents.models import AuditResult, AUDIT_CRITERIA_BY_TYPE
        print("  [+] AuditResult modeli import edildi")

        from sade_agents.config import get_settings
        print("  [+] Config import edildi")

        # Agent olusturma testi
        agent = PerfectionistAgent()
        print(f"\n  [+] Agent olusturuldu: {agent.role}")
        print(f"      - Department: {agent.department}")
        print(f"      - Autonomy: {agent.autonomy_level}")
        print(f"      - Tools: {[t.name for t in agent.tools]}")

        # Skill testleri (CrewAI tool'lari .run() ile cagrilir)
        print("\n[?] Skill testleri...\n")

        # stil_kilavuzu_yukle testi
        import json
        guide = stil_kilavuzu_yukle.run()
        guide_data = json.loads(guide)
        if "error" not in guide_data:
            print(f"  [+] stil_kilavuzu_yukle() calisti")
            print(f"      Yuklenentler: {list(guide_data.keys())}")
        else:
            print(f"  [!] stil_kilavuzu_yukle() uyari: {guide_data.get('error')}")

        # onaylanmis_ornekler_yukle testi
        ornekler = onaylanmis_ornekler_yukle.run(icerik_turu="metin")
        ornekler_data = json.loads(ornekler)
        print(f"  [+] onaylanmis_ornekler_yukle('metin') calisti")
        print(f"      Ornek sayisi: {ornekler_data.get('ornek_sayisi', 0)}")

        # denetle testi (sadece prompt uretimi)
        test_content = "Beklenmedik. Cikolatanin hikayesi."
        prompt = denetle.run(
            icerik=test_content,
            icerik_turu="metin",
            kaynak_agent="narrator"
        )
        print(f"  [+] denetle() calisti")
        print(f"      Prompt uzunlugu: {len(prompt)} karakter")

        # AuditResult model testi
        audit = AuditResult(
            content_type="metin",
            source_agent="narrator",
            overall_score=85,
            tone_score=90,
            vocabulary_score=80,
            structure_score=85,
            verdict="onay",
            issues=[],
            suggestions=[],
            summary_tr="Test basarili"
        )
        print(f"  [+] AuditResult modeli calisti")
        print(f"      Verdict: {audit.verdict}")

        # Kriterler kontrolu
        print(f"\n  [+] AUDIT_CRITERIA_BY_TYPE: {len(AUDIT_CRITERIA_BY_TYPE)} agent tipi")
        for agent_type, criteria in AUDIT_CRITERIA_BY_TYPE.items():
            print(f"      - {agent_type}: threshold={criteria['threshold']}")

        # API key kontrolu
        if check_api_key():
            print("\n  [+] OPENAI_API_KEY mevcut")
        else:
            print("\n  [!] OPENAI_API_KEY eksik veya gecersiz")
            print("      -> .env.example'dan .env olusturun")

        print("\n" + "=" * 60)
        print("[OK] DRY RUN BASARILI - Tum importlar ve syntax dogru")
        print("=" * 60)

    except ImportError as e:
        print(f"  [X] Import hatasi: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  [X] Hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_audit(content: str, content_type: str = "metin", source_agent: str = "narrator") -> None:
    """Icerik denetimi calistir."""
    print("=" * 60)
    print("THE PERFECTIONIST - UX Denetim Agent'i")
    print("=" * 60)

    if not check_api_key():
        print("\n[X] HATA: OPENAI_API_KEY gerekli!")
        print("\nCozum:")
        print("  1. cp .env.example .env")
        print("  2. .env dosyasina API key'inizi ekleyin")
        sys.exit(1)

    try:
        from crewai import Crew, Task

        from sade_agents.agents.perfectionist import PerfectionistAgent
        from sade_agents.config import get_settings

        settings = get_settings()
        print(f"\n[i] Ayarlar:")
        print(f"    Model: {settings.openai_model_name}")
        print(f"    Icerik turu: {content_type}")
        print(f"    Kaynak agent: {source_agent}")

        # Icerik onizleme
        preview = content[:100] + "..." if len(content) > 100 else content
        print(f"\n[i] Icerik onizleme:")
        print(f"    {preview}")

        # Agent olustur
        perfectionist = PerfectionistAgent()
        print(f"\n[*] Agent: {perfectionist.role}")
        print(f"    Department: {perfectionist.department}")
        print(f"    Autonomy: {perfectionist.autonomy_level}")

        # Task tanimla
        task = Task(
            description=f"""
Asagidaki icerigi "Sessiz Luks" marka sesine gore denetle.

## DENETLENECEK ICERIK
```
{content}
```

## METADATA
- Icerik Turu: {content_type}
- Kaynak Agent: {source_agent}

## GOREVLER
1. Oncelikle `stil_kilavuzu_yukle` ile marka stil kilavuzunu incele
2. `onaylanmis_ornekler_yukle` ile '{content_type}' icin benchmark ornekleri al
3. `denetle` skill'i ile icerigi degerlendir
4. Sonuclari AuditResult JSON formatinda sun

## ONEMLI
- Tum geri bildirimler TURKCE olmali
- Her sorun icin somut alternatif oner
- Override politikasi: Sadece tavsiye ver, son karar kullanicinin
            """,
            expected_output="""
AuditResult JSON formatinda denetim sonucu:
- overall_score (0-100)
- verdict (onay/revizyon_gerekli/red)
- issues (Turkce sorun listesi)
- suggestions (Turkce oneri listesi)
- summary_tr (2-3 cumlelik ozet)
            """,
            agent=perfectionist,
        )

        # Crew olustur ve calistir
        crew = Crew(
            agents=[perfectionist],
            tasks=[task],
            verbose=True,
        )

        print("\n" + "-" * 60)
        print("[>] Denetim basliyor...")
        print("-" * 60 + "\n")

        result = crew.kickoff()

        print("\n" + "=" * 60)
        print("[*] DENETIM SONUCU")
        print("=" * 60)
        print(result)

        print("\n" + "-" * 60)
        print("[!] HATIRLATMA: Bu sonuc TAVSIYE niteligindedir.")
        print("    Kullanici isterse icerigi oldugu gibi kullanabilir.")
        print("-" * 60)

    except ImportError as e:
        print(f"\n[X] Import hatasi: {e}")
        print("CrewAI kurulu mu? pip install crewai")
        sys.exit(1)
    except Exception as e:
        print(f"\n[X] Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="The Perfectionist - Sade Chocolate UX Denetim Agent'i"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Sadece import ve syntax kontrolu yap, API cagirisi yapma"
    )
    parser.add_argument(
        "--content",
        type=str,
        help="Denetlenecek icerik (direkt metin)"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Denetlenecek icerik dosyasi"
    )
    parser.add_argument(
        "--type",
        type=str,
        default="metin",
        choices=["metin", "fiyat_analizi", "trend_raporu", "recete", "gorsel_prompt"],
        help="Icerik turu (default: metin)"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="narrator",
        choices=["narrator", "pricing", "growth", "alchemist", "curator"],
        help="Kaynak agent (default: narrator)"
    )

    args = parser.parse_args()

    if args.dry_run:
        dry_run()
    elif args.content:
        run_audit(args.content, args.type, args.source)
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[X] Dosya bulunamadi: {args.file}")
            sys.exit(1)
        content = file_path.read_text(encoding="utf-8")
        run_audit(content, args.type, args.source)
    else:
        # Interaktif mod
        print("=" * 60)
        print("THE PERFECTIONIST - Interaktif Mod")
        print("=" * 60)
        print("\nDenetlenecek icerigi girin (bos satir ile bitirin):")
        print("-" * 40)

        lines = []
        while True:
            try:
                line = input()
                if line == "":
                    break
                lines.append(line)
            except EOFError:
                break

        if not lines:
            print("\n[!] Icerik girilmedi. Cikiliyor.")
            sys.exit(0)

        content = "\n".join(lines)
        run_audit(content, args.type, args.source)


if __name__ == "__main__":
    main()
