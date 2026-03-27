
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from sade_agents.skills.pricing_skills import fiyat_kontrol, maliyet_analizi

def main():
    print("💰 Testing Pricing Skills...")
    print("="*50)

    print("\n1. Fiyat Kontrol (Tümü):")
    print(fiyat_kontrol.run())

    print("\n2. Fiyat Kontrol (Vakko):")
    print(fiyat_kontrol.run(rakip="vakko"))

    print("\n3. Maliyet Analizi (Ruby Tablet 85g):")
    print(maliyet_analizi.run(urun_tipi="ruby_tablet", gramaj=85))

    print("\n4. Maliyet Analizi (Fıstık Bar 100g):")
    print(maliyet_analizi.run(urun_tipi="fistikli_bar", gramaj=100))

if __name__ == "__main__":
    main()
