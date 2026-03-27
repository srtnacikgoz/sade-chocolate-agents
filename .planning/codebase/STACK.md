# Technology Stack - Sade Chocolate Agents

## Languages & Runtime

**Use Python 3.11+**

- **Version**: Python 3.11, 3.12 supported (from `pyproject.toml`)
- **Location**: `pyproject.toml` line 10
- **Package Name**: `sade-agents` v0.1.0

Primary language for the entire codebase. No TypeScript, JavaScript, or multi-language setup detected.

## Frameworks

### Core AI/Agent Framework

**Use CrewAI** (>=0.86.0)
- Multi-agent orchestration framework
- Agent definition and task management
- Tool/skill binding and execution
- **Import Pattern** (from `src/sade_agents/agents/base.py` line 11):
  ```python
  from crewai import Agent
  ```
- **Usage Example** (`scripts/run_alchemist.py` line 100):
  ```python
  from crewai import Crew, Task

  crew = Crew(
      agents=[agent],
      tasks=[task],
      verbose=True,
  )
  result = crew.kickoff()
  ```

### LLM Provider

**Use OpenAI API (GPT-4o-mini by default)**
- Managed through CrewAI's integration
- API Key required: `OPENAI_API_KEY` environment variable
- Default model: `gpt-4o-mini` (overridable via `OPENAI_MODEL_NAME`)
- **Config Location**: `src/sade_agents/config/settings.py` lines 23-27

## Key Dependencies

### Direct Dependencies

From `pyproject.toml` lines 23-27:

```toml
dependencies = [
    "crewai>=0.86.0",
    "python-dotenv>=1.0.0",
    "pydantic-settings>=2.0.0",
]
```

| Package | Version | Purpose |
|---------|---------|---------|
| **crewai** | >=0.86.0 | Multi-agent AI framework, tool system, task orchestration |
| **python-dotenv** | >=1.0.0 | Load `.env` environment variables for API keys |
| **pydantic-settings** | >=2.0.0 | Type-safe configuration management from env vars |

### Development Dependencies

From `pyproject.toml` lines 30-34:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "ruff>=0.1",
]
```

| Package | Purpose |
|---------|---------|
| **pytest** | Unit testing framework |
| **pytest-cov** | Code coverage reporting |
| **ruff** | Fast Python linter and formatter |

### Transitive Dependencies

CrewAI brings:
- **langchain** ecosystem (LLM integrations)
- **pydantic** v2 (data validation)
- Additional async/networking libraries

## Configuration Files

### Primary Config

**`src/sade_agents/config/settings.py`**
- Type-safe settings using Pydantic v2
- **Class**: `Settings` (inherits `BaseSettings`)
- **Configuration Method**: Environment variables + `.env` file
- **Key Fields**:
  - `openai_api_key: str` (required)
  - `openai_model_name: str = "gpt-4o-mini"` (optional, default GPT-4o-mini)
- **Validation**: `validate_api_key()` method checks for valid API key
- **Pattern Used**:
  ```python
  from pydantic_settings import BaseSettings, SettingsConfigDict

  class Settings(BaseSettings):
      model_config = SettingsConfigDict(
          env_file=".env",
          env_file_encoding="utf-8",
          extra="ignore",
      )
  ```

### Environment Configuration

**`.env.example`**
Template for environment setup:
```
OPENAI_API_KEY=
OPENAI_MODEL_NAME=gpt-4o-mini
```

**`.env`** (runtime, not in repo)
- Load at runtime via `python-dotenv`
- Must contain `OPENAI_API_KEY`
- Loaded in `scripts/run_alchemist.py` line 32

### Build Configuration

**`pyproject.toml`**
- Build system: `hatchling`
- Build backend: `hatchling.build`
- Wheel packages: `src/sade_agents` (line 37)
- Linting config: `[tool.ruff]` section (lines 39-44)
- Testing config: `[tool.pytest.ini_options]` section (lines 46-48)

## Build & Dev Tools

### Build System

**Use Hatchling** (lines 2-3)
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Package management: Poetry/pip with PEP 517 compliance

### Code Quality

**Ruff Linter** (`tool.ruff` section)
- Line length: 100 characters
- Target Python version: 3.11
- Enabled rule categories:
  - `E` (pycodestyle errors)
  - `F` (Pyflakes)
  - `I` (isort - import sorting)
  - `N` (pep8-naming)
  - `W` (pycodestyle warnings)

**Configuration** (lines 39-44):
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
```

### Testing

**Pytest** (`tool.pytest.ini_options` section)
- Test discovery: `tests/` directory
- Python path: `src/` (for absolute imports)
- **Run Command**: `pytest tests`

**Configuration** (lines 46-48):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

### Project Structure

```
src/sade_agents/
  ├── agents/
  │   ├── base.py           # SadeAgent base class (CrewAI.Agent)
  │   ├── alchemist.py      # AlchemistAgent (flavor/recipe)
  │   ├── growth_hacker.py  # GrowthHackerAgent (trends/growth)
  │   ├── narrator.py       # NarratorAgent (brand voice)
  │   ├── pricing_analyst.py # PricingAnalystAgent (competitive pricing)
  │   └── test_agent.py     # Test/demo agent
  ├── skills/
  │   ├── alchemist_skills.py    # lezzet_pisileri tool
  │   ├── growth_skills.py       # sosyal_nabiz tool
  │   ├── narrator_skills.py     # hikayelestir tool
  │   ├── pricing_skills.py      # fiyat_kontrol tool
  │   └── __init__.py            # Exports all tools
  └── config/
      ├── settings.py  # Pydantic BaseSettings config
      └── __init__.py

scripts/
  ├── run_alchemist.py
  ├── run_growth_hacker.py
  ├── run_narrator.py
  ├── run_pricing_analyst.py
  └── run_test_agent.py
```

### Script Execution Pattern

**Location**: `scripts/run_alchemist.py` (representative example)

Standard pattern for all agent runner scripts:

1. **Path Setup** (lines 18-20):
   ```python
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root / "src"))
   ```

2. **API Key Validation** (lines 23-35):
   - Check `.env` existence
   - Load via `dotenv.load_dotenv()`
   - Validate `OPENAI_API_KEY` environment variable

3. **Dry-run Mode** (lines 38-82):
   - Test imports without API calls
   - Useful for CI/CD validation

4. **Agent Execution** (lines 85-168):
   - Import agent class
   - Create agent instance
   - Define task with `Task()` class
   - Execute with `Crew().kickoff()`
   - Handle exceptions gracefully

## Summary Table

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Language** | Python | 3.11+ | Primary runtime |
| **AI Framework** | CrewAI | >=0.86.0 | Agent orchestration |
| **LLM Provider** | OpenAI API | (gpt-4o-mini) | LLM backend |
| **Config Management** | Pydantic Settings | >=2.0.0 | Type-safe env config |
| **Environment** | python-dotenv | >=1.0.0 | `.env` loading |
| **Build System** | Hatchling | - | Package build |
| **Linter** | Ruff | >=0.1 | Code quality |
| **Testing** | Pytest | >=8.0 | Unit tests |
| **Package Manager** | pip/Poetry | - | Dependency management |

All integrations are managed through Python imports and environment configuration. No Docker, Kubernetes, or containerization detected in current stack.
