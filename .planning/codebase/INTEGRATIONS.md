# External Integrations - Sade Chocolate Agents

## External APIs

### OpenAI GPT API

**Primary LLM Provider**

- **Service**: OpenAI API (GPT-4o-mini / GPT-4 Turbo)
- **Authentication**: API Key (`OPENAI_API_KEY`)
- **Configuration**:
  - Location: `src/sade_agents/config/settings.py` lines 24, 27
  - Default Model: `gpt-4o-mini` (configurable via `OPENAI_MODEL_NAME`)
  - Field: `openai_api_key: str` (required, validated)
  - Method: Environment variable or `.env` file

- **Usage Pattern**:
  ```python
  # From src/sade_agents/config/settings.py
  class Settings(BaseSettings):
      openai_api_key: str  # Required - will fail if missing
      openai_model_name: str = "gpt-4o-mini"  # Optional default
  ```

- **Integration Method**:
  - CrewAI automatically uses OpenAI API for all LLM calls
  - API key injected through environment at runtime
  - No explicit API calls in application code (handled by CrewAI)

- **Setup Instructions**:
  ```bash
  # From .env.example
  OPENAI_API_KEY=your-api-key-here
  OPENAI_MODEL_NAME=gpt-4o-mini  # Optional
  ```

- **Validation** (`src/sade_agents/config/settings.py` lines 29-31):
  ```python
  def validate_api_key(self) -> bool:
      """API key'in ayarlanip ayarlanmadigini kontrol eder."""
      return bool(self.openai_api_key and self.openai_api_key != "your-api-key-here")
  ```

### Social Media & Market Intelligence APIs (Planned)

**Currently Mock Data, Future Integration Points**

Location: `src/sade_agents/skills/growth_skills.py` lines 11-99

**Mock Data Providers** (replace with real APIs):

#### Twitter/X API
- **Current**: Mock hashtag data (`x_twitter` in `TREND_VERILERI`)
- **Data Tracked**: Hashtags, mentions, sentiment, trend direction
- **Integration Point**: `sosyal_nabiz()` tool, platform="x_twitter"
- **Example Mock Data** (lines 13-44):
  ```python
  "x_twitter": [
      {
          "hashtag": "#artisanchocolate",
          "mentions": 2400,
          "sentiment": "pozitif",
          "trend": "yukselis",
      },
  ]
  ```
- **Future API**: Twitter API v2 (Academic Research or Premium tier)
- **Required**: Twitter API credentials

#### Instagram API
- **Current**: Mock trend data
- **Data Tracked**: Visual trends, engagement metrics, segment targeting
- **Integration Point**: `sosyal_nabiz()` tool, platform="instagram"
- **Mock Structure** (lines 45-51):
  ```python
  "instagram": [
      {"trend": "Minimalist ambalaj", "engagement": "yuksek", "segment": "luks"},
  ]
  ```
- **Future API**: Instagram Graph API (Meta Business API)
- **Required**: Meta app credentials, business account

#### Reddit API
- **Current**: Mock subreddit data
- **Data Tracked**: Subreddit discussions, upvotes, sentiment
- **Integration Point**: `sosyal_nabiz()` tool, platform="reddit"
- **Mock Data** (lines 52-71):
  ```python
  "reddit": [
      {
          "subreddit": "r/chocolate",
          "topic": "Turkish chocolate brands",
          "upvotes": 156,
          "sentiment": "merakli",
      },
  ]
  ```
- **Future API**: Reddit API (PRAW library or REST API)
- **Required**: Reddit API credentials

### Market Signal APIs (Planned)

- **Current**: Hardcoded market data in `pazar_sinyalleri`
- **Tracked Signals** (lines 72-98):
  - New retail locations (Zorlu Center, Nişantaşı, Bebek)
  - Competitor launches
  - Location trends
  - Seasonal opportunities
- **Data Points**: Signal type, priority level, description
- **Future Integration**: Real estate databases, competitor monitoring services

## Databases

**Currently: None**

### Planned/Future Requirements

Based on agent architecture and use cases, likely database integrations:

#### For Flavor/Recipe Data
- **Location**: `src/sade_agents/skills/alchemist_skills.py` lines 14-96
- **Current Storage**: In-memory Python dictionaries
- **Data Stored**:
  - `LEZZET_ESLESTIRMELERI`: Flavor pairings by chocolate type
  - `MEVSIMSEL_MALZEMELER`: Seasonal ingredients calendar
  - `CIKOLATA_BILGISI`: Technical chocolate specifications
- **Recommendation**: NoSQL (MongoDB) or PostgreSQL for flexible schema
- **Schema**: Chocolate types, flavor profiles, seasonal mappings

#### For Pricing Analytics
- **Location**: `src/sade_agents/skills/pricing_skills.py`
- **Current Storage**: Mock/hardcoded (not yet implemented)
- **Data to Store**:
  - Competitor pricing history
  - Sade product costs
  - Margin tracking
  - Price change events
- **Recommendation**: Time-series database (InfluxDB) or PostgreSQL
- **Access Pattern**: Historical trend analysis, competitive intelligence

#### For Social Sentiment Tracking
- **Location**: `src/sade_agents/skills/growth_skills.py`
- **Current Storage**: Mock data
- **Data to Store**:
  - Social media mentions
  - Sentiment scores
  - Trend velocity
  - Engagement metrics
- **Recommendation**: Time-series DB for metrics + PostgreSQL for references
- **Access Pattern**: Real-time monitoring, historical comparisons

## Auth Providers

### OpenAI Authentication

**Type**: API Key-based authentication

**Configuration**:
- **Field**: `OPENAI_API_KEY` environment variable
- **Set in**: `.env` file (line 2 of `.env.example`)
- **Validation**: Checked by `Settings.validate_api_key()` method
- **Error Handling** (from `scripts/run_alchemist.py` lines 91-97):
  ```python
  if not check_api_key():
      print("\n❌ HATA: OPENAI_API_KEY gerekli!")
      print("\nÇözüm:")
      print("  1. cp .env.example .env")
      print("  2. .env dosyasına API key'inizi ekleyin")
      print("  3. Bu scripti tekrar çalıştırın")
      sys.exit(1)
  ```

### Future Auth Requirements

For planned integrations:

| Service | Auth Type | Credentials |
|---------|-----------|-------------|
| Twitter/X API | OAuth 2.0 | API Key + Secret, Bearer Token |
| Instagram/Meta Graph | OAuth 2.0 | App ID, App Secret, Access Token |
| Reddit API | OAuth 2.0 | Client ID, Client Secret |
| Competitor APIs | Varies | Likely API keys or web scraping |

## Third-party Services

### Language Model Service (OpenAI)

**Service Type**: SaaS LLM API

**Capabilities Used**:
- Text generation (agent responses)
- Tool/function calling (agent actions)
- Multi-turn conversations

**CrewAI Integration** (from agent implementations):

**Example from `src/sade_agents/agents/alchemist.py` lines 29-82**:
- Agent initialized with CrewAI's Agent class
- CrewAI automatically routes agent queries to OpenAI
- Tasks defined in `scripts/run_alchemist.py` (lines 117-145)
- Execution via `Crew().kickoff()`

**Agent Tool System (CrewAI)**

Tools are Python functions decorated with `@tool` that agents can invoke:

#### Lezzet Pisileri (Flavor Tool)

**Location**: `src/sade_agents/skills/alchemist_skills.py` lines 172-255

**Function Signature**:
```python
@tool
def lezzet_pisileri(malzeme: str = "bitter_cikolata", mod: str = "eslestir") -> str:
```

**Modes**:
- `"eslestir"`: Flavor pairings for chocolate type
- `"mevsim"`: Current month's seasonal ingredients
- `"bilgi"`: Technical chocolate specifications
- `"tumu"`: All data combined

**Data Source**: In-memory dictionaries (future: database)

#### Sosyal Nabız (Social Pulse Tool)

**Location**: `src/sade_agents/skills/growth_skills.py` lines 199-285

**Function Signature**:
```python
@tool
def sosyal_nabiz(platform: str = "tumu") -> str:
```

**Platforms**:
- `"x_twitter"`: Twitter hashtag trends
- `"instagram"`: Instagram content trends
- `"reddit"`: Reddit discussions
- `"pazar"`: Market signals
- `"tumu"`: All platforms

**Data Source**: Mock data (future: Twitter API, Instagram API, Reddit API)

#### Hikayelestir (Storytelling Tool)

**Location**: `src/sade_agents/skills/narrator_skills.py` lines 11-93

**Function Signature**:
```python
@tool
def hikayelestir(urun_adi: str, urun_gramaji: str, urun_icerik: str) -> str:
```

**Produces**:
1. Label story (for packaging)
2. Instagram caption (social media)
3. Gift box note (personalization)

**Returns**: Prompt template for LLM to generate "Quiet Luxury" brand-voice content

#### Fiyat Kontrol (Pricing Tool)

**Location**: `src/sade_agents/skills/pricing_skills.py` (not yet fully shown)

**Purpose**: Competitive pricing analysis

**Not Yet Implemented**: Placeholder tool definition

### CrewAI Framework Service

**Service Type**: Open-source framework (local execution)

**Provides**:
- Agent orchestration
- Task scheduling
- Tool binding and execution
- LLM integration layer
- Multi-agent coordination

**Import Pattern** (used across all agents):
```python
from crewai import Agent, Crew, Task
```

**Execution Flow**:
1. Define agents (inheriting `SadeAgent`)
2. Define tasks with descriptions
3. Create `Crew` with agents + tasks
4. Call `crew.kickoff()` to execute
5. CrewAI handles LLM routing and tool calls

## Integration Architecture Diagram

```
┌─────────────────────────────────────────────┐
│  Sade Agents Application                    │
│  (Python + CrewAI)                          │
└──────────────┬──────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
    ┌───▼────┐    ┌──▼────────────┐
    │ OpenAI │    │ Mock Data      │
    │  API   │    │ (Future APIs)  │
    └───┬────┘    └──┬─────────────┘
        │            │
    ┌───▼────────────▼──┐
    │  CrewAI Framework │
    │  (Agent System)   │
    └───┬────────────┬──┘
        │            │
    ┌───▼──────┐ ┌──▼──────────┐
    │  Agents  │ │  Tools      │
    │ (4 types)│ │ (4 skills)  │
    └──────────┘ └─────────────┘

Agents:
- AlchemistAgent (flavor/recipe)
- GrowthHackerAgent (trends/growth)
- NarratorAgent (brand voice)
- PricingAnalystAgent (competitive pricing)

Tools:
- lezzet_pisileri (flavor pairings)
- sosyal_nabiz (social trends)
- hikayelestir (storytelling)
- fiyat_kontrol (pricing analysis)
```

## Configuration for Integrations

### Environment Setup

**File**: `.env` (copy from `.env.example`)

**Required Variables**:
```bash
# OpenAI API (required for any agent execution)
OPENAI_API_KEY=your-key-here

# Optional configuration
OPENAI_MODEL_NAME=gpt-4o-mini
```

**Load Process**:
1. Application starts (`scripts/run_alchemist.py`)
2. `check_api_key()` loads `.env` via `dotenv.load_dotenv()`
3. `Settings` class validates `OPENAI_API_KEY`
4. If invalid, script exits with helpful error message

### Runtime Configuration

**Location**: `src/sade_agents/config/__init__.py`

**Export Pattern**:
```python
from sade_agents.config.settings import Settings, get_settings

# Usage:
settings = get_settings()
# settings.openai_api_key available for CrewAI
# settings.openai_model_name defaults to "gpt-4o-mini"
```

## Integration Testing Patterns

### Dry-Run Mode

**Purpose**: Validate integrations without API calls

**Execution** (from `scripts/run_alchemist.py` lines 38-82):
```bash
python scripts/run_alchemist.py --dry-run
```

**Tests**:
- Import all modules
- Instantiate all agents
- Verify tools are attached
- Check API key configuration
- No actual LLM calls

### Full Execution

**Execution** (standard run):
```bash
python scripts/run_alchemist.py
```

**What Happens**:
1. Validates API key
2. Creates agent
3. Defines task with description
4. Executes through CrewAI
5. LLM (OpenAI) called to process task
6. Agent uses tools as needed
7. Returns structured output

## Future Integration Roadmap

### Phase 1: Real Competitor Pricing (High Priority)
- Scrape Vakko, Butterfly, Marie Antoinette websites
- Parse product prices and weights
- Store in time-series database
- Enable PricingAnalystAgent full functionality

### Phase 2: Social Media Monitoring (High Priority)
- Twitter API v2: Track #cikolata, #artisanchocolate hashtags
- Instagram Graph API: Monitor competitor posts + engagement
- Reddit API: Track r/chocolate discussions
- Enable GrowthHackerAgent real-time insights

### Phase 3: Data Persistence (Medium Priority)
- PostgreSQL for pricing history + competitor data
- MongoDB for flexible flavor/recipe data
- InfluxDB for time-series sentiment/engagement
- Implement data refresh schedule

### Phase 4: Advanced Analytics (Medium Priority)
- Sentiment analysis API integration
- Price elasticity modeling
- Flavor trend prediction
- Competitive positioning visualization

### Phase 5: External Services (Low Priority)
- Email/SMS notifications for price alerts
- Slack integration for agent reports
- Analytics dashboards
- API endpoint for external consumption

## Summary

**Current State**:
- Fully integrated with OpenAI GPT API (required)
- Mock data for social/market intelligence (placeholders)
- No database persistence
- No auth services beyond OpenAI API key

**Integration Points**:
- **OpenAI**: Required, fully functional
- **Social APIs**: Stubbed, ready for real integration
- **Pricing Data**: Hardcoded, ready for web scraping
- **Persistence**: In-memory only, design ready for DB

**Next Steps**:
1. Implement real competitor price scraping
2. Add Twitter/Instagram/Reddit API connections
3. Set up PostgreSQL for historical data
4. Add real-time monitoring and alerts
