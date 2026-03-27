# Sade Chocolate Agents - Directory Structure & File Location Guide

## Directory Tree

```
sade-chocolate-agents/
├── src/                              # Main source code (Python package)
│   └── sade_agents/                  # Package root
│       ├── __init__.py               # Package metadata (__version__)
│       │
│       ├── agents/                   # Agent implementations
│       │   ├── __init__.py           # Exports all agent classes
│       │   ├── base.py               # SadeAgent base class (core abstraction)
│       │   ├── narrator.py           # The Narrator Agent (marketing/content)
│       │   ├── alchemist.py          # The Alchemist Agent (product/flavor)
│       │   ├── pricing_analyst.py    # The Pricing Analyst Agent (finance)
│       │   ├── growth_hacker.py      # The Growth Hacker Agent (marketing/trends)
│       │   └── test_agent.py         # Test/demo agent
│       │
│       ├── skills/                   # Tool/skill implementations
│       │   ├── __init__.py           # Exports all skill functions
│       │   ├── narrator_skills.py    # hikayelestir() - content generation
│       │   ├── alchemist_skills.py   # lezzet_pisileri() - flavor database
│       │   ├── pricing_skills.py     # fiyat_kontrol() - pricing data
│       │   └── growth_skills.py      # sosyal_nabiz() - trend monitoring
│       │
│       └── config/                   # Configuration management
│           ├── __init__.py           # Exports Settings, get_settings()
│           └── settings.py           # Pydantic Settings class + loader
│
├── scripts/                          # Executable entry points
│   ├── run_narrator.py               # Run The Narrator Agent
│   ├── run_alchemist.py              # Run The Alchemist Agent
│   ├── run_pricing_analyst.py        # Run The Pricing Analyst Agent
│   ├── run_growth_hacker.py          # Run The Growth Hacker Agent
│   └── run_test_agent.py             # Run Test Agent
│
├── tests/                            # Test suite (pytest)
│   ├── __init__.py
│   ├── finance/                      # Finance agent tests
│   ├── marketing/                    # Marketing agent tests
│   ├── operations/                   # Operations tests
│   └── product/                      # Product agent tests
│
├── .planning/                        # Planning & documentation
│   ├── codebase/                     # This directory
│   │   ├── ARCHITECTURE.md           # Architecture patterns
│   │   └── STRUCTURE.md              # This file
│   ├── phases/                       # Phase-based implementation roadmap
│   │   ├── 01-temel-altyapi/
│   │   ├── 02-the-narrator/
│   │   ├── 03-the-pricing-analyst/
│   │   ├── 04-the-growth-hacker/
│   │   └── 05-the-alchemist/
│   └── ...
│
├── skills/                           # Domain-specific skill documentation
│   ├── finance/                      # Financial analysis capabilities
│   ├── marketing/                    # Marketing & brand strategy
│   ├── operations/                   # Operational capabilities
│   └── product/                      # Product development
│
├── architecture/                     # Architecture documentation & diagrams
├── legal/                            # Legal documents
├── marketing/                        # Marketing materials
├── operations/                       # Operations documentation
├── product/                          # Product specifications
├── research/                         # Research findings
│
├── pyproject.toml                    # Project metadata & dependencies
├── README.md                         # Project overview
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
└── .env                              # Local environment (not in repo)
```

---

## Key Locations - Where to Find What

### Agent Code
| What | Where |
|------|-------|
| Base agent class | `src/sade_agents/agents/base.py` |
| Narrator implementation | `src/sade_agents/agents/narrator.py` |
| Alchemist implementation | `src/sade_agents/agents/alchemist.py` |
| Pricing Analyst implementation | `src/sade_agents/agents/pricing_analyst.py` |
| Growth Hacker implementation | `src/sade_agents/agents/growth_hacker.py` |
| Agent exports | `src/sade_agents/agents/__init__.py` |

### Tools/Skills
| What | Where |
|------|-------|
| Narrator skill (storytelling) | `src/sade_agents/skills/narrator_skills.py` → `hikayelestir()` |
| Alchemist skill (flavor) | `src/sade_agents/skills/alchemist_skills.py` → `lezzet_pisileri()` |
| Pricing skill (price tracking) | `src/sade_agents/skills/pricing_skills.py` → `fiyat_kontrol()` |
| Growth skill (trends) | `src/sade_agents/skills/growth_skills.py` → `sosyal_nabiz()` |
| Skill exports | `src/sade_agents/skills/__init__.py` |

### Configuration
| What | Where |
|------|-------|
| Settings class | `src/sade_agents/config/settings.py` |
| get_settings() function | `src/sade_agents/config/settings.py` |
| Config exports | `src/sade_agents/config/__init__.py` |
| Environment template | `.env.example` |
| Local environment (secrets) | `.env` (NOT in git) |

### Execution Scripts
| What | Where |
|------|-------|
| Narrator runner | `scripts/run_narrator.py` |
| Alchemist runner | `scripts/run_alchemist.py` |
| Pricing Analyst runner | `scripts/run_pricing_analyst.py` |
| Growth Hacker runner | `scripts/run_growth_hacker.py` |
| Test runner | `scripts/run_test_agent.py` |

### Package Info
| What | Where |
|------|-------|
| Version & metadata | `src/sade_agents/__init__.py` |
| Dependencies | `pyproject.toml` |
| Project metadata | `pyproject.toml` |

### Tests
| What | Where |
|------|-------|
| Test configuration (pytest) | `pyproject.toml` (testpaths, pythonpath) |
| Finance tests | `tests/finance/` |
| Marketing tests | `tests/marketing/` |
| Product tests | `tests/product/` |
| Operations tests | `tests/operations/` |

---

## File Naming Conventions

### Python Files

#### Agents
- **Pattern:** `snake_case_agent.py` (e.g., `narrator.py`, `alchemist.py`)
- **Base class:** `base.py`
- **Rule:** One agent per file
- **Exports:** `__all__ = ["ClassName"]` at end of file

#### Skills
- **Pattern:** `{domain}_skills.py` (e.g., `narrator_skills.py`, `alchemist_skills.py`)
- **Rule:** Related skills grouped by domain
- **Tool decorator:** `@tool` from `crewai.tools`
- **Exports:** `__all__ = ["skill_name", ...]` at end of file

#### Config
- **Pattern:** `settings.py` (standard configuration file name)
- **Rule:** Single configuration module per domain
- **Exports:** `__all__ = ["Settings", "get_settings"]`

#### Scripts
- **Pattern:** `run_{agent_name}.py` (e.g., `run_narrator.py`)
- **Rule:** One script per agent
- **Shebang:** `#!/usr/bin/env python3`
- **Main guard:** `if __name__ == "__main__": main()`

### Docstring Style

All files follow Google-style docstrings with Turkish comments:

```python
"""
Sade Chocolate - {Component Name}.

Turkish description of component purpose.
"""

def function_name(param1: str, param2: int) -> str:
    """
    Short description in English.

    Longer explanation if needed.

    Args:
        param1: Description
        param2: Description

    Returns:
        Description

    Raises:
        ExceptionType: When this happens
    """
```

---

## Naming Conventions

### Agents
- **Class name:** `{Specialty}Agent` (e.g., `NarratorAgent`, `AlchemistAgent`)
- **Inherited from:** `SadeAgent`
- **Module location:** `src/sade_agents/agents/{specialty_name_lowercase}.py`

### Skills/Tools
- **Function name:** Turkish concept name (e.g., `hikayelestir`, `lezzet_pisileri`, `sosyal_nabiz`)
- **Decorator:** `@tool` (CrewAI)
- **Parameters:** Snake case (e.g., `malzeme`, `urun_adi`)
- **Returns:** `str` (Markdown formatted with embedded prompts)

### Variables
- **Agent instances:** `{lowercase_agent_name}_agent` (e.g., `narrator_agent`, `alchemist_agent`)
- **Task variables:** `{task_name}_task` (e.g., `storytelling_task`, `flavor_task`)
- **Config variable:** `settings` (from `get_settings()`)

### Constants
- **Database constants:** `UPPERCASE_WITH_UNDERSCORES` (e.g., `LEZZET_ESLESTIRMELERI`, `MEVSIMSEL_MALZEMELER`)
- **Location:** Top of module, after imports

---

## Where to Add New Code

### Adding a New Agent

**Steps:**

1. Create new agent file: `src/sade_agents/agents/{agent_name}.py`
2. Implement agent class inheriting from `SadeAgent`:

```python
"""
Sade Chocolate - {Your Agent Name}.

Description of agent purpose.
"""

from sade_agents.agents.base import SadeAgent
from sade_agents.skills import relevant_skill

class YourAgent(SadeAgent):
    """Your agent docstring with responsibilities."""

    def __init__(self) -> None:
        super().__init__(
            role="Role Title",
            goal="Agent goal statement",
            tools=[relevant_skill],
            backstory="""
Your agent backstory and expertise description.
            """,
            department="marketing",  # or finance, operations, product
            autonomy_level="autonomous",  # or supervised, mixed
            verbose=True,
        )
```

3. Add export to `src/sade_agents/agents/__init__.py`:
```python
from sade_agents.agents.your_agent import YourAgent

__all__: list[str] = [
    # ... existing
    "YourAgent",
]
```

4. Create runner script: `scripts/run_your_agent.py` (copy from existing runner, modify agent import and task)

5. Add tests in: `tests/{department}/test_your_agent.py`

### Adding a New Skill/Tool

**Steps:**

1. Create new skill file: `src/sade_agents/skills/{domain}_skills.py`
2. Implement tool function with `@tool` decorator:

```python
"""
Sade Agents - {Domain} Skills.

Descriptions of available skills.
"""

from crewai.tools import tool

# Database/constants at module level
SKILL_DATA = {
    "key1": {"data": "value"},
}

@tool
def your_skill_name(param1: str, param2: str = "default") -> str:
    """
    Short description of what skill does.

    Longer explanation including data retrieval strategy and output format.

    Args:
        param1: Parameter description
        param2: Parameter description

    Returns:
        Markdown-formatted output with analysis prompt template

    Kullanım:
        your_skill_name("input1")
    """
    # 1. Retrieve/format data
    data_output = _format_data(param1)

    # 2. Create analysis prompt template
    analysis_prompt = """

---

## ANALYSIS INSTRUCTIONS

Instructions for agent to analyze the data above...
    """

    # 3. Return combined output
    return data_output + analysis_prompt


def _format_data(param: str) -> str:
    """Helper: Format raw data into Markdown table."""
    # Implementation here
    pass


__all__ = ["your_skill_name"]
```

3. Add export to `src/sade_agents/skills/__init__.py`:
```python
from sade_agents.skills.your_domain import your_skill_name

__all__: list[str] = [
    # ... existing
    "your_skill_name",
]
```

4. Attach skill to appropriate agent in agent's `__init__`:
```python
tools=[your_skill_name]
```

### Adding Tests

**Location:** `tests/{department}/test_{component}.py`

**Pattern:**
```python
import pytest
from sade_agents.agents import YourAgent
from sade_agents.skills import your_skill


def test_agent_creation():
    """Test agent can be instantiated."""
    agent = YourAgent()
    assert agent.role == "Expected Role"
    assert agent.department == "marketing"


def test_skill_output():
    """Test skill returns proper format."""
    result = your_skill("test_input")
    assert isinstance(result, str)
    assert "expected_content" in result
```

### Modifying Configuration

**File:** `src/sade_agents/config/settings.py`

**Steps:**

1. Add new setting field to `Settings` class:
```python
class Settings(BaseSettings):
    openai_api_key: str
    your_new_setting: str = "default_value"  # Add here
```

2. Update `.env.example`:
```bash
OPENAI_API_KEY=your-api-key-here
YOUR_NEW_SETTING=value_here
```

3. Use in code:
```python
settings = get_settings()
value = settings.your_new_setting
```

### Adding Database/Mock Data

**Location:** Top of skill module file (after imports)

**Pattern:**
```python
YOUR_DATABASE = {
    "category1": {
        "item1": {"property": "value"},
    },
}

def _helper_format_data(key: str) -> str:
    """Helper to format database into output."""
    # Format YOUR_DATABASE[key]
    pass
```

**Usage in tool:**
```python
@tool
def your_tool(query: str) -> str:
    """Tool that uses database."""
    formatted = _helper_format_data(query)
    return formatted + analysis_template
```

---

## Import Patterns

### Correct Imports (Use These)

```python
# Agents
from sade_agents.agents import NarratorAgent, AlchemistAgent
from sade_agents.agents.base import SadeAgent

# Skills
from sade_agents.skills import hikayelestir, lezzet_pisileri

# Config
from sade_agents.config import Settings, get_settings

# CrewAI
from crewai import Agent, Crew, Task
from crewai.tools import tool

# External
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
```

### Avoid These Patterns

```python
# DON'T: Direct file imports
from sade_agents.agents.narrator import NarratorAgent  # Use __init__.py exports instead

# DON'T: Circular imports
# If skill imports agent that uses skill -> circular dependency

# DON'T: External dependencies not in pyproject.toml
import some_unregistered_package  # Add to pyproject.toml first
```

---

## Environment Variables

### .env File Location
`/c/dev/sade-chocolate-agents/.env` (local, NOT in git)

### Required Variables
```bash
OPENAI_API_KEY=your-api-key-here
```

### Optional Variables
```bash
OPENAI_MODEL_NAME=gpt-4o-mini  # Default if not set
```

### How Loaded
1. Script calls `check_api_key()` from `dotenv`
2. Loads `.env` file if exists
3. `Settings` class reads from environment
4. Validates with `get_settings()`

---

## Testing Structure

### Test Organization
- By department: `tests/{department}/test_{component}.py`
- Departments: `finance`, `marketing`, `operations`, `product`

### Running Tests
```bash
pytest tests/                    # All tests
pytest tests/marketing/          # Marketing tests only
pytest tests/ -v                 # Verbose output
pytest tests/ --cov              # With coverage
```

### Pytest Configuration
Located in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

---

## Build & Package Information

### Package Definition
- **Name:** `sade-agents`
- **Path:** `src/sade_agents/`
- **Version:** `0.1.0` (in `src/sade_agents/__init__.py`)
- **Build system:** Hatchling

### Dependencies (from pyproject.toml)
- `crewai>=0.86.0` - Multi-agent framework
- `python-dotenv>=1.0.0` - Environment loading
- `pydantic-settings>=2.0.0` - Configuration management

### Installing Package
```bash
pip install -e ".[dev]"  # Editable install with dev dependencies
```

### Package Structure
```python
src/sade_agents/
├── __init__.py          # Package entry point (defines __version__)
├── agents/__init__.py   # Agent exports
├── skills/__init__.py   # Skill exports
└── config/__init__.py   # Config exports
```

---

## Quick Reference

| Need | File |
|------|------|
| Add agent | Create `src/sade_agents/agents/{name}.py` → Update `agents/__init__.py` → Create `scripts/run_{name}.py` |
| Add skill | Create `src/sade_agents/skills/{domain}_skills.py` → Update `skills/__init__.py` → Use in agent |
| Add config | Update `src/sade_agents/config/settings.py` → Update `.env.example` |
| Add test | Create `tests/{department}/test_{name}.py` |
| Database | Add constant in skill module (e.g., `FLAVOR_DATA = {...}`) |
| Entry point | Create script in `scripts/run_{agent}.py` |
| Version | Update `src/sade_agents/__init__.py` and `pyproject.toml` |

---

## Special Notes

### Brand Voice Enforcement
- **Narrator:** See `backstory` in `narrator.py` for "Sessiz Lüks" guidelines
- **All agents:** Inherit from `SadeAgent` to access `brand_voice` attribute
- **Tool prompts:** Embed brand constraints in returned prompt templates

### Autonomy Levels
- **Autonomous:** Agent makes decisions independently (Alchemist, Growth Hacker)
- **Supervised:** Agent recommends, human decides (Narrator for critical content, Pricing Analyst)
- **Mixed:** Context-dependent (new agents default to this)

### Mock Data Strategy
- Databases are Python dictionaries at module level (`FLAVOR_DATA = {...}`)
- Helper functions format databases for output (`_format_{component}`)
- Tools receive and parse database → return formatted + prompt
- Production: Replace mock dict with API calls in helper functions

### Error Handling Pattern
```python
@tool
def my_tool(param: str) -> str:
    """Tool documentation."""
    if param not in VALID_OPTIONS:
        valid = ", ".join(VALID_OPTIONS)
        return f"Invalid {param}. Valid options: {valid}"

    # Process normally
```
