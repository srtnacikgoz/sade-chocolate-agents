# Codebase Conventions & Patterns

## Code Style

### Python Version & Standards
- **Target Version:** Python 3.11+ (specified in `pyproject.toml`)
- **Line Length:** 100 characters (configured in `tool.ruff`)
- **Linter:** Ruff with E, F, I, N, W rules enabled

Example from `src/sade_agents/config/settings.py`:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Type-safe configuration class."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
```

### Code Organization
- **Imports:** Organize in standard order: stdlib, third-party, local
  - Example: `src/sade_agents/agents/alchemist.py` shows correct organization
- **Type Hints:** Use comprehensive type hints on function signatures and class attributes
- **Docstrings:** Use module-level docstrings in Turkish with English context
- **Module Exports:** Include `__all__` list at end of modules

Example from `src/sade_agents/agents/base.py`:
```python
"""
Sade Chocolate - Temel Agent Base Class.

"The Connoisseur Chip" felsefesi:
Sadece kod değil, çikolata craft'ını bilen dijital şef ruhu.
"""

import logging
from typing import Literal

from crewai import Agent

__all__ = ["SadeAgent"]
```

## Naming Conventions

### Files & Directories
- **Module Files:** Use snake_case: `alchemist.py`, `growth_hacker.py`, `pricing_analyst.py`
- **Skill Files:** Use snake_case with descriptive names: `alchemist_skills.py`, `growth_skills.py`
- **Script Files:** Use snake_case with `run_` prefix: `run_alchemist.py`, `run_narrator.py`
- **Package Directories:** Use snake_case: `agents/`, `skills/`, `config/`

### Python Identifiers

#### Classes
Use PascalCase with descriptive names:
```python
# Agents - from src/sade_agents/agents/
class SadeAgent(Agent)
class AlchemistAgent(SadeAgent)
class GrowthHackerAgent(SadeAgent)
class PricingAnalystAgent(SadeAgent)
class NarratorAgent(SadeAgent)
```

#### Functions & Methods
Use snake_case:
```python
# From src/sade_agents/skills/alchemist_skills.py
def _get_ay_adi() -> str:
    """Private helper function."""

def _format_eslestirmeler(cikolata_tipi: str) -> str:
    """Format flavor pairings."""

@tool
def lezzet_pisileri(malzeme: str = "bitter_cikolata", mod: str = "eslestir") -> str:
    """Tool function using snake_case."""
```

#### Variables
Use snake_case for all variables:
```python
# From src/sade_agents/skills/alchemist_skills.py
LEZZET_ESLESTIRMELERI = {  # Constants: UPPER_SNAKE_CASE
    "bitter_cikolata": {...}
}

brand_voice: str = "sessiz_luks"  # Instance attributes: snake_case
autonomy_level: Literal["autonomous", "supervised", "mixed"] = "mixed"
```

### Language Conventions
- **Turkish with English Context:** All docstrings and comments in Turkish with domain terms explained
- **Comments:** Explain "why" not "what"; code should be self-documenting
- **Function Parameter Names:** Use Turkish descriptive names where appropriate
  - `malzeme` (ingredient), `cikolata_tipi` (chocolate type), `rakip` (competitor), `platform` (platform)

## Common Patterns

### Agent Architecture Pattern
All agents inherit from `SadeAgent` base class with consistent structure:

```python
# From src/sade_agents/agents/alchemist.py
class AlchemistAgent(SadeAgent):
    """Agent docstring in Turkish."""

    def __init__(self) -> None:
        """Initialize agent with super().__init__() and keyword args."""
        super().__init__(
            role="The Alchemist - Flavor Architect",
            goal="Clear goal in Turkish",
            tools=[skill_name],
            backstory="""Detailed persona and instructions.""",
            department="product",  # finance|marketing|operations|product
            autonomy_level="autonomous",  # autonomous|supervised|mixed
            verbose=True,
        )
```

### Skill/Tool Pattern
Tools are defined using CrewAI's `@tool` decorator:

```python
# From src/sade_agents/skills/alchemist_skills.py
@tool
def lezzet_pisileri(malzeme: str = "bitter_cikolata", mod: str = "eslestir") -> str:
    """
    Comprehensive docstring explaining:
    - What the tool does
    - Args with detailed descriptions
    - Return value description
    - Usage examples
    """
    sections = []  # Build output as list

    # Process logic
    if mod == "eslestir":
        sections.append(_format_eslestirmeler(malzeme))
    # ... more cases

    # Add prompt template for agent analysis
    analiz_template = """
    ## 🎯 AGENT INSTRUCTIONS
    ...
    """
    sections.append(analiz_template)

    return "\n".join(sections)  # Join with newlines for readability
```

### Configuration Pattern
Use Pydantic Settings for configuration:

```python
# From src/sade_agents/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Configuration loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Define required and optional settings with type hints
    openai_api_key: str
    openai_model_name: str = "gpt-4o-mini"

    def validate_api_key(self) -> bool:
        """Validate configuration."""
        return bool(self.openai_api_key and self.openai_api_key != "your-api-key-here")

def get_settings() -> Settings:
    """Factory function to load settings."""
    return Settings()
```

### Script Entry Point Pattern
Scripts follow consistent initialization pattern:

```python
# From scripts/run_alchemist.py
import argparse
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def dry_run() -> None:
    """Dry run for syntax checking."""
    print("🔍 Dry run: Import validation...")
    # Test imports without API calls

def run_agent() -> None:
    """Run the actual agent."""
    # Main execution with error handling

def main() -> None:
    """Entry point with argument parsing."""
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument("--dry-run", action="store_true", help="...")
    args = parser.parse_args()

    if args.dry_run:
        dry_run()
    else:
        run_agent()

if __name__ == "__main__":
    main()
```

### Data Structure Pattern
Use dictionaries for lookup tables and structured data:

```python
# From src/sade_agents/skills/alchemist_skills.py
LEZZET_ESLESTIRMELERI = {
    "bitter_cikolata": {
        "klasik": ["portakal", "nane", "kahve", "fındık", "badem"],
        "cesur": ["lavanta", "biberiye", "acı biber", "zeytinyağı", "deniz tuzu"],
        "meyveli": ["ahududu", "vişne", "çilek", "muz", "incir"],
    },
    "sutlu_cikolata": {...},
}

MEVSIMSEL_MALZEMELER = {
    "ocak": ["kestane", "hurma", "portakal", "greyfurt", "nar"],
    "subat": [...],
}
```

### Error Handling Pattern
Validate inputs and return user-friendly error messages:

```python
# From src/sade_agents/skills/alchemist_skills.py
def _format_eslestirmeler(cikolata_tipi: str) -> str:
    """Format flavor pairings."""
    if cikolata_tipi not in LEZZET_ESLESTIRMELERI:
        valid = ", ".join(LEZZET_ESLESTIRMELERI.keys())
        return f"Bilinmeyen çikolata tipi: {cikolata_tipi}. Geçerli: {valid}"
    # ... normal processing
```

Also from `scripts/run_alchemist.py`:
```python
def run_agent() -> None:
    """Run agent with comprehensive error checking."""
    if not check_api_key():
        print("\n❌ HATA: OPENAI_API_KEY gerekli!")
        print("\nÇözüm:")
        print("  1. cp .env.example .env")
        print("  2. .env dosyasına API key'inizi ekleyin")
        sys.exit(1)

    try:
        # Main logic
    except ImportError as e:
        print(f"  ✗ Import hatası: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  ✗ Beklenmeyen hata: {e}")
        sys.exit(1)
```

## Error Handling

### Validation Pattern
Input validation with informative error messages:
- Check for required parameters
- Validate against known sets of values
- Return descriptive error messages in Turkish with valid options listed

### Exception Handling
Use try-except for external operations:
- API calls (OpenAI)
- File operations (.env loading)
- Import operations

Example from `scripts/run_alchemist.py`:
```python
try:
    from sade_agents.agents.alchemist import AlchemistAgent
    from sade_agents.config import get_settings
except ImportError as e:
    print(f"✗ Import hatası: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Beklenmeyen hata: {e}")
    sys.exit(1)
```

### Logging Pattern
Use Python's logging module for debug information:

```python
# From src/sade_agents/agents/base.py
import logging
from logging import getLogger

logger = logging.getLogger(__name__)

class SadeAgent(Agent):
    def __init__(self, ...):
        logger.debug(
            "SadeAgent oluşturuldu: %s (department=%s, autonomy=%s)",
            kwargs.get("role", "Unknown"),
            department,
            autonomy_level,
        )

    def log_action(self, action: str, details: str = "") -> None:
        """Log agent actions."""
        logger.info(
            "[%s] %s: %s %s",
            self.department.upper(),
            getattr(self, "role", "Agent"),
            action,
            details,
        )
```

## Import Organization

### Standard Order
1. **Standard Library:** `import logging`, `from typing import Literal`, `from pathlib import Path`
2. **Third-Party:** `from crewai import Agent`, `from pydantic_settings import BaseSettings`
3. **Local/Relative:** `from sade_agents.agents.base import SadeAgent`, `from sade_agents.skills import lezzet_pisileri`

### Import Examples
```python
# From src/sade_agents/agents/alchemist.py
from sade_agents.agents.base import SadeAgent
from sade_agents.skills import lezzet_pisileri

# From src/sade_agents/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

# From src/sade_agents/agents/base.py
import logging
from typing import Literal

from crewai import Agent

# From scripts/run_alchemist.py
import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv
```

### Module/Skill Imports
Always import tools and skills explicitly:
```python
from sade_agents.skills import lezzet_pisileri, sosyal_nabiz, fiyat_kontrol, hikayelestir

# Then use in agent
tools=[lezzet_pisileri]
```
