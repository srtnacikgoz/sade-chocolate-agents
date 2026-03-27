
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from sade_agents.skills.marketing_skills import gundem_analizi

def main():
    print("📈 Testing Marketing Skills...")
    print("="*50)

    print("\n1. Gündem Analizi (Genel):")
    # Using .run() because it is a CrewAI Tool
    print(gundem_analizi.run())

    print("\n2. Gündem Analizi (Ruby):")
    print(gundem_analizi.run(odak="ruby"))

if __name__ == "__main__":
    main()
