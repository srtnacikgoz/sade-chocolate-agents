#!/usr/bin/env python3
"""
Sade Chocolate - Agent Command Center (Dispatcher) 🍫✨

Kullanım:
    python sade.py /sihirli_kelime [parametreler]

Örnekler:
    python sade.py /hikayelestir "Ruby Tablet" "85g" "Pembe, mayhoş"
    python sade.py /fiyat_kontrol vakko
    python sade.py /etiket_tasarla "Dark Chocolate" "Yoğun, isli"
    python sade.py /gundem
    python sade.py /urun_lansmani "Antep Fıstıklı" "150-200"

"""

import sys
import argparse
from typing import List

# Add src to path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from crewai import Crew, Task, Process

# Import Skills & Agents
from sade_agents.skills.narrator_skills import hikayelestir
from sade_agents.skills.pricing_skills import fiyat_kontrol
from sade_agents.skills.product_skills import etiket_tasarla, lezzet_pisileri
from sade_agents.skills.marketing_skills import gundem_analizi

# Import Crews
from sade_agents.crews.product_launch_crew import ProductLaunchCrew


def run_single_skill(skill_func, **kwargs):
    """Tekil bir skill'i (Tool) calistirir."""
    print(f"\n✨ Sade Agent Skill Çalıştırılıyor: {skill_func.name}")
    print("="*50)
    try:
        # CrewAI Tool objesi ise .run() ile calistir
        result = skill_func.run(**kwargs)
        print(result)
        return result
    except Exception as e:
        print(f"❌ Hata: {e}")
        return str(e)

def run_narrator_flow(product: str, gramaj: str, details: str):
    """Narrator Agent'i calistirir (LLM ile)."""
    from sade_agents.agents import NarratorAgent
    
    print(f"\n🎭 The Narrator Sahneye Çıkıyor: {product}")
    print("="*50)
    
    agent = NarratorAgent()
    task = Task(
        description=f"""
        /hikayelestir
        Urun: {product}
        Gramaj: {gramaj}
        Ozellikler: {details}
        
        Sessiz Luks tonunda 3 parca icerik uret (Etiket, Instagram, Not).
        """,
        expected_output="3 parca Sessiz Luks metni",
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task], verbose=True)
    result = crew.kickoff()
    
    print("\n✅ The Narrator Çıktısı:")
    print("="*50)
    print(result)

def run_product_launch(concept: str, price_range: str):
    """Product Launch Crew'u calistirir."""
    print(f"\n🚀 Ürün Lansman Ekibi Toplanıyor: {concept}")
    print("="*50)
    
    try:
        min_p, max_p = map(float, price_range.split("-"))
    except:
        min_p, max_p = 100.0, 200.0
        
    inputs = {
        "flavor_concept": concept,
        "target_audience": "Quiet Luxury Lovers",
        "price_range_min": min_p,
        "price_range_max": max_p,
        "include_audit": True
    }
    
    crew = ProductLaunchCrew()
    # verify fix of tuple error :)
    result = crew.kickoff(inputs)
    
    print("\n✅ Lansman Dosyası Hazır:")
    print("="*50)
    print(result)


def dispatch(args: List[str]):
    if not args:
        print(__doc__)
        return

    command = args[0]
    params = args[1:]

    # 1. /hikayelestir (The Narrator)
    if command == "/hikayelestir":
        if len(params) < 3:
            print("⚠️ Kullanım: /hikayelestir <urun> <gramaj> <detay>")
            return
        run_narrator_flow(params[0], params[1], params[2])

    # 2. /fiyat_kontrol (Pricing Analyst)
    elif command == "/fiyat_kontrol":
        rakip = params[0] if params else "tumu"
        run_single_skill(fiyat_kontrol, rakip=rakip)

    # 3. /etiket_tasarla (The Curator - Skill only)
    elif command == "/etiket_tasarla":
        if len(params) < 2:
            print("⚠️ Kullanım: /etiket_tasarla <urun> <konsept>")
            return
        run_single_skill(etiket_tasarla, urun_adi=params[0], konsept=params[1])

    # 4. /gundem (Growth Hacker - Skill only)
    elif command == "/gundem" or command == "/gundem_analizi":
        odak = params[0] if params else "genel"
        run_single_skill(gundem_analizi, odak=odak)
        
    # 5. /lezzet_pisileri (The Alchemist - Skill only)
    elif command == "/lezzet_pisileri":
        mevsim = params[0] if params else "kis"
        run_single_skill(lezzet_pisileri, mevsim=mevsim)

    # 6. /urun_lansmani (Full Crew)
    elif command == "/urun_lansmani":
         if len(params) < 2:
            print("⚠️ Kullanım: /urun_lansmani <konsept> <fiyat_araligi_min-max>")
            return
         run_product_launch(params[0], params[1])

    else:
        print(f"❌ Tanımsız sihirli kelime: {command}")
        print(__doc__)

if __name__ == "__main__":
    dispatch(sys.argv[1:])
