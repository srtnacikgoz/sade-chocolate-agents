
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from sade_agents.skills.product_skills import etiket_tasarla, lezzet_pisileri

def main():
    print("🎨 Testing Product Design Skills...")
    print("="*50)

    print("\n1. Etiket Tasarımı (Ruby Tablet):")
    # Using .run() because it is a CrewAI Tool
    print(etiket_tasarla.run(urun_adi="Ruby Tablet 85g", konsept="Dogal pembe, mayhos, 4. tur cikolata"))

    print("\n2. Etiket Tasarımı (Dark Chocolate):")
    print(etiket_tasarla.run(urun_adi="Single Origin Dark 70%", konsept="Yogun kakao, isli notalar"))

    print("\n3. Lezzet Pişileri (Kış):")
    print(lezzet_pisileri.run(mevsim="kis"))

if __name__ == "__main__":
    main()
