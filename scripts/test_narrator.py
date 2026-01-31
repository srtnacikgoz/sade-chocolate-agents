
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from crewai import Crew, Task, Process
from sade_agents.agents import NarratorAgent

def main():
    print("🎭 Testing The Narrator Agent...")
    print("="*50)

    try:
        # Instantiate Agent
        narrator = NarratorAgent()
        print(f"Agent: {narrator.role}")
        print(f"Goal: {narrator.goal}")

        # Define Task using the magic word context
        task = Task(
            description="""
            /hikayelestir
            
            Ürün: Ruby Çikolata Tablet
            Gramaj: 85g 
            Özellikler: Doğal pembe, mayhoş tat, dördüncü tür çikolata.

            Bana 'Sessiz Lüks' tonunda 3 parça içerik üret:
            1. Etiket Hikayesi
            2. Instagram Caption
            3. Kutu İçi Not
            """,
            expected_output="3 parça 'Sessiz Lüks' metni (Etiket, Instagram, Not)",
            agent=narrator
        )

        # Create Crew
        crew = Crew(
            agents=[narrator],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )

        # Run
        result = crew.kickoff()
        
        print("\n" + "="*50)
        print("✅ RESULT:")
        print("="*50)
        print(result)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
