# Sade Chocolate Agents - Architecture Documentation

## Pattern

**Multi-Agent System with Specialized Skill Distribution**

This codebase implements a **Specialized Agents with Tools Pattern** using CrewAI framework, where:
- Each agent represents a distinct business function (marketing, finance, product, operations)
- Agents collaborate through a central orchestration layer
- Each agent is equipped with domain-specific tools/skills for task execution
- No traditional layering (MVC/3-tier); instead: Agent-Skill-Tool vertical slicing

The architecture follows **Domain-Driven Design (DDD)** principles where each agent owns its domain expertise.

---

## Layers & Responsibilities

### Layer 1: Configuration & Foundation
**Location:** `src/sade_agents/config/`

- **`settings.py`** - Pydantic-based configuration management
  - Loads environment variables from `.env` file
  - Manages OpenAI API credentials and model selection
  - Validates API key availability
  - Function: `get_settings()` returns singleton Settings object

### Layer 2: Agent Base & Framework
**Location:** `src/sade_agents/agents/`

- **`base.py` - SadeAgent Class**
  - Custom CrewAI Agent subclass
  - Adds Sade-specific attributes:
    - `brand_voice` - Ensures "Sessiz Lüks" (Quiet Luxury) brand consistency
    - `department` - Categorizes agents (marketing, finance, operations, product)
    - `autonomy_level` - Controls decision authority (autonomous, supervised, mixed)
  - Provides `log_action()` method for consistent logging
  - **Principle:** All specialized agents inherit from this to maintain brand voice and operational consistency

### Layer 3: Specialized Agents
**Location:** `src/sade_agents/agents/`

Each agent is a specialized expert with defined role, goal, backstory, and tools:

1. **The Narrator Agent** (`narrator.py`)
   - **Role:** Brand voice custodian and content creator
   - **Department:** Marketing
   - **Autonomy:** Supervised
   - **Skills:** `hikayelestir` (storytelling)
   - **Outputs:** Product stories, Instagram captions, packaging notes
   - **Brand Constraint:** Enforces "Sessiz Lüks" writing guidelines
   - **Tools:** None directly available (LLM-driven content generation)

2. **The Alchemist Agent** (`alchemist.py`)
   - **Role:** Flavor architect and recipe designer
   - **Department:** Product
   - **Autonomy:** Autonomous
   - **Skills:** `lezzet_pisileri` (flavor pairings, seasonal ingredients, chocolate knowledge)
   - **Outputs:** Flavor recommendations, seasonal reports, recipe concepts
   - **Expertise:** Chocolate science, ganache chemistry, tempering, flavor pairing theory
   - **Tools:** Flavor database, seasonal ingredient calendar, chocolate technical specs

3. **The Pricing Analyst Agent** (`pricing_analyst.py`)
   - **Role:** Competitive intelligence and pricing strategist
   - **Department:** Finance
   - **Autonomy:** Supervised (requires human approval for price changes)
   - **Skills:** `fiyat_kontrol` (price monitoring and TL/gram analysis)
   - **Outputs:** Competitor reports, TL/gram comparisons, margin analysis
   - **Competitors Tracked:** Vakko, Butterfly, Marie Antoinette, Baylan, Divan
   - **Tools:** Competitor pricing database, margin calculations

4. **The Growth Hacker Agent** (`growth_hacker.py`)
   - **Role:** Trend scout and growth strategist
   - **Department:** Marketing
   - **Autonomy:** Autonomous
   - **Skills:** `sosyal_nabiz` (social media and market pulse)
   - **Outputs:** Daily trend reports, opportunity analysis, competitor alerts
   - **Platforms Monitored:** X (Twitter), Instagram, Reddit, market signals
   - **Tools:** Trend database, sentiment analysis templates

### Layer 4: Skills & Tools
**Location:** `src/sade_agents/skills/`

Skills are CrewAI `@tool` decorated functions that provide structured data and analysis templates:

- **`alchemist_skills.py`**
  - `lezzet_pisileri(malzeme, mod)` - Multi-mode flavor database
    - Modes: `eslestir` (pairings), `mevsim` (seasonal), `bilgi` (technical), `tumu` (all)
    - Returns: Markdown tables + analysis prompts

- **`narrator_skills.py`**
  - `hikayelestir(urun_adi, urun_gramaji, urun_icerik)` - Content generation template
    - Generates: Product story, Instagram caption, gift box note
    - Enforces: No emojis, no urgency language, sophisticated tone

- **`pricing_skills.py`**
  - `fiyat_kontrol(rakip)` - Competitor pricing analysis
    - Modes: Individual competitor or `tumu` (all)
    - Returns: Price tables + TL/gram normalization + analysis prompts

- **`growth_skills.py`**
  - `sosyal_nabiz(platform)` - Trend aggregation
    - Modes: `x_twitter`, `instagram`, `reddit`, `pazar`, `tumu`
    - Returns: Trend tables + sentiment analysis + actionable prompts

**Design Pattern:** Tools primarily return **structured data + prompt templates**, allowing agents (LLM) to perform analysis with consistent context.

### Layer 5: Orchestration & Execution
**Location:** `scripts/`

Entry point scripts for individual agent execution:
- `run_narrator.py` - Brand content creation
- `run_alchemist.py` - Product flavor development
- `run_pricing_analyst.py` - Market analysis
- `run_growth_hacker.py` - Trend tracking
- `run_test_agent.py` - Testing framework

**Features:**
- `.env` configuration loading
- Dry-run mode for syntax validation (no API calls)
- Structured task definitions with expected outputs
- CrewAI Crew orchestration (single or multi-agent)

---

## Data Flow

### 1. Agent Execution Flow

```
Script Entry Point
    ↓
Load Configuration (.env) via settings.py
    ↓
Initialize Agent (inherits from SadeAgent)
    ├─ Load role/goal/backstory
    ├─ Attach tools/skills
    └─ Set department & autonomy level
    ↓
Define Task(s) with detailed description
    ├─ Problem statement
    ├─ Tool usage instructions
    └─ Expected output format
    ↓
Create Crew (single or multi-agent orchestration)
    ↓
Execute crew.kickoff()
    ├─ Agent processes task description
    ├─ Agent selects appropriate tool(s)
    ├─ Tool returns structured data + prompt
    ├─ Agent (LLM) analyzes/synthesizes
    └─ Agent produces final output
    ↓
Return structured result to user
```

### 2. Tool Usage Pattern

```
Agent (LLM) identifies task type
    ↓
Agent calls appropriate tool: tool_name(arg1, arg2)
    ↓
Tool function:
    ├─ Retrieves database/mock data
    ├─ Formats as Markdown table/structure
    ├─ Appends analysis prompt template
    └─ Returns string with context
    ↓
Agent receives formatted data + implicit instructions
    ↓
Agent (LLM) performs semantic analysis/synthesis
    ↓
Agent generates final output (respecting brand/guidelines)
```

### 3. Example: Product Story Generation

```
hikayelestir("Ruby Tablet", "85g", "Doğal pembe renk, mayhoş tat")
    ├─ Creates prompt template with Narrator's brand guidelines
    ├─ Specifies 3 outputs: Tag story, Instagram caption, Gift note
    ├─ Lists forbidden words (emojis, urgency language)
    ├─ Lists preferred tone markers (sophisticated, understated)
    └─ Returns template to agent

Agent (LLM) receives template
    ├─ Generates 3 content pieces
    ├─ Respects "Sessiz Lüks" constraints
    └─ Outputs final content
```

### 4. Example: Flavor Recommendation

```
lezzet_pisileri("bitter_cikolata", "eslestir")
    ├─ Returns Classic/Bold/Fruity pairings for dark chocolate
    ├─ Appends seasonal ingredient calendar for current month
    ├─ Appends chocolate technical specs (tempering, couverture info)
    └─ Returns structured data + analysis instructions

Agent (LLM) receives data
    ├─ Selects 2-3 combinations
    ├─ Explains flavor science
    ├─ Suggests Callebaut/Valrhona couverture choice
    ├─ Proposes product names aligned with brand
    └─ Outputs flavor recommendation report
```

---

## Key Abstractions

### 1. **SadeAgent Base Class**
- **Purpose:** Ensure all agents maintain brand voice, departmental clarity, and operational consistency
- **Key Methods:**
  - `__init__()` - Initializes with Sade-specific attributes
  - `log_action(action, details)` - Department-prefixed logging
- **Key Attributes:**
  - `brand_voice` - Default "sessiz_luks"
  - `department` - Enum: marketing, finance, operations, product
  - `autonomy_level` - Enum: autonomous, supervised, mixed

### 2. **Tool Pattern**
- **Purpose:** Provide agents with structured data + implicit instructions
- **Structure:**
  - Database/data retrieval
  - Markdown formatting for readability
  - Embedded prompt templates for LLM guidance
- **Benefit:** Separates data logic from reasoning logic

### 3. **Crew Orchestration**
- **Purpose:** Enable multi-agent workflows and dependency management
- **Components:**
  - `agents` - List of collaborating agents
  - `tasks` - Ordered task definitions with dependencies
  - `verbose` - Detailed execution logging

### 4. **Task Definition**
- **Purpose:** Provide agents with precise context and expected outputs
- **Components:**
  - `description` - Problem statement + tool usage guide
  - `expected_output` - Structured output format specification
  - `agent` - Assigned agent
  - (Optional) `depends_on` - Task dependencies for chaining

### 5. **Brand Voice Enforcement**
- **Mechanism:** Embedded in agent backstories and tool prompt templates
- **Examples:**
  - Narrator: "Sessiz Lüks" guidelines with forbidden words
  - Pricing Analyst: Human approval requirement for decisions
  - Alchemist: Chocolate science + flavor pairing framework
  - Growth Hacker: Opportunity prioritization matrix

---

## Entry Points

### Command-Line Scripts

**1. `scripts/run_narrator.py`**
```bash
python scripts/run_narrator.py           # Full run with API calls
python scripts/run_narrator.py --dry-run # Syntax check only
```
- Creates NarratorAgent
- Defines content generation task
- Executes crew.kickoff()

**2. `scripts/run_alchemist.py`**
```bash
python scripts/run_alchemist.py
python scripts/run_alchemist.py --dry-run
```
- Creates AlchemistAgent
- Defines flavor recommendation task
- Uses `lezzet_pisileri` tool with multiple modes

**3. `scripts/run_pricing_analyst.py`**
- Creates PricingAnalystAgent
- Defines market analysis task
- Uses `fiyat_kontrol` tool for competitor comparison

**4. `scripts/run_growth_hacker.py`**
- Creates GrowthHackerAgent
- Defines trend analysis task
- Uses `sosyal_nabiz` tool for multi-platform monitoring

**5. `scripts/run_test_agent.py`**
- Testing/demonstration agent
- Used for framework validation

### Configuration Entry Point

**`src/sade_agents/config/settings.py`**
- Function: `get_settings()` - Loads `.env` file, validates OpenAI API key
- Used by: All scripts before creating agents

### Module Imports

```python
# By package
from sade_agents import __version__

# By agent
from sade_agents.agents import (
    SadeAgent,
    NarratorAgent,
    AlchemistAgent,
    PricingAnalystAgent,
    GrowthHackerAgent,
)

# By skill
from sade_agents.skills import (
    hikayelestir,
    lezzet_pisileri,
    fiyat_kontrol,
    sosyal_nabiz,
)

# By config
from sade_agents.config import Settings, get_settings
```

---

## Execution Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Script Entry Point                         │
│              (run_narrator.py, etc.)                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │  Load .env Config   │
        │ (settings.py)       │
        └────────┬────────────┘
                 │
                 ▼
        ┌─────────────────────────────────────────┐
        │  Initialize Specialized Agent            │
        │  (Narrator, Alchemist, etc.)            │
        │  └─ Inherits from SadeAgent             │
        │  └─ Gets role, goal, backstory         │
        │  └─ Gets tools/skills attached         │
        └─────────┬──────────────────────────────┘
                  │
                  ▼
        ┌──────────────────────────────┐
        │  Define Task(s)              │
        │  ├─ Description              │
        │  ├─ Expected output format   │
        │  └─ Tool usage guide         │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │  Create Crew                 │
        │  ├─ agents=[...]             │
        │  ├─ tasks=[...]              │
        │  └─ verbose=True             │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌────────────────────────────────────────┐
        │  crew.kickoff()                        │
        │  ├─ Agent reads task description       │
        │  ├─ Agent decides tool usage           │
        │  ├─ Calls tool(args)                   │
        │  └─ Tool returns data + prompt         │
        └────────┬───────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────────┐
        │  Agent (LLM) Processing                │
        │  ├─ Receives tool output               │
        │  ├─ Analyzes/synthesizes               │
        │  ├─ Respects brand voice constraints   │
        │  └─ Generates output                   │
        └────────┬───────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────────┐
        │  Return Result to User/Caller          │
        │  ├─ Structured output                  │
        │  ├─ Follows expected_output format     │
        │  └─ Respects autonomy_level            │
        └────────────────────────────────────────┘
```

---

## Technology Stack

- **Framework:** CrewAI 0.86.0+
- **LLM:** OpenAI (GPT-4O Mini default)
- **Configuration:** Pydantic-settings 2.0+
- **Language:** Python 3.11+
- **Build Tool:** Hatchling
- **Testing:** Pytest 8.0+
- **Linting:** Ruff

---

## Design Principles

1. **Separation of Concerns** - Each agent has distinct domain responsibility
2. **Brand Voice Consistency** - All agents enforce "Sessiz Lüks" guidelines through base class and backstories
3. **Supervised Autonomy** - Critical decisions (pricing) require human approval; creative decisions are autonomous
4. **Data-Driven Insights** - Tools provide structured data enabling LLM analysis
5. **Scalability** - New agents/skills added by extending SadeAgent and creating tools
6. **Modularity** - Skills are independent, database-driven functions
7. **Human-in-the-Loop** - Supervised agents generate recommendations, not final decisions
