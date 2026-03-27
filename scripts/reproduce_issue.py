
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from sade_agents.crews.product_launch_crew import ProductLaunchCrew

def main():
    print("🚀 Testing ProductLaunchCrew inputs...")
    
    # Inputs mimicking web/pages/product_launch.py
    inputs = {
        "flavor_concept": "Test Flavor",
        "target_audience": "Test Audience",
        "price_range_min": 100.0,
        "price_range_max": 200.0,
        "price_range": (100.0, 200.0), # Intentionally adding a tuple to test sanitization
        "include_audit": False
    }

    try:
        crew = ProductLaunchCrew()
        print("Crew initialized.")
        
        # This calls the wrapper kickoff which filters inputs
        result = crew.kickoff(inputs)
        print("✅ Success! Result:", result)
        
    except Exception as e:
        print("❌ Error:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
