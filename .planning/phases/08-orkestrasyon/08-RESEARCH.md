# Phase 8: Orkestrasyon - Research

**Researched:** 2026-01-30
**Domain:** CrewAI Multi-Agent Orchestration, Inter-Agent Communication, Workflow Coordination
**Confidence:** MEDIUM

## Summary

Phase 8: Orkestrasyon implements a "Chief Architect" orchestration layer that coordinates the 6 specialist agents (Narrator, Pricing Analyst, Growth Hacker, Alchemist, Curator, Perfectionist) to work together on complex multi-step workflows. This research investigated CrewAI's orchestration patterns, process types, and best practices for coordinating mixed-autonomy agents.

CrewAI provides two primary orchestration approaches: **Sequential Process** (linear task execution where each task's output becomes the next task's input) and **Hierarchical Process** (manager-led coordination with dynamic task delegation). For Sade's use case with 6 independent specialists and a quality control agent, a **hybrid approach** is recommended: Sequential process for standard workflows with task context passing, plus optional Hierarchical process for complex campaigns requiring dynamic coordination.

The research revealed that **Flows** (deterministic, event-driven orchestration) and **Crews** (autonomous multi-agent collaboration) serve different purposes and can be combined. Flows provide the structural backbone with precise control over execution paths, while Crews enable agent autonomy within those flows. Production systems benefit from this "deterministic backbone + agentic steps" pattern.

**Primary recommendation:** Use CrewAI Sequential Process with task context for standard workflows, implement shared memory/state for cross-agent communication, create reusable Crew compositions for common scenarios (e.g., "New Product Launch Crew" = Alchemist + Narrator + Curator + Perfectionist), and reserve Hierarchical Process for complex multi-stage campaigns requiring dynamic delegation.

## Standard Stack

The established libraries/tools for CrewAI multi-agent orchestration:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| crewai | >=0.86.0 | Multi-agent orchestration framework | Already in use, native support for sequential/hierarchical processes, memory sharing, task context |
| pydantic | >=2.0.0 | Structured data models for inputs/outputs | Already in use, type-safe inter-agent communication, validation |
| python-dotenv | >=1.0.0 | Environment configuration | Already in use, API key management |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| instructor | ^1.0 | Structured LLM outputs with Pydantic | If additional structured output validation needed beyond CrewAI's built-in support |
| langfuse | latest | Observability, tracing, debugging | Production monitoring to trace multi-agent workflows and identify bottlenecks |
| crewai[tools] | latest | Extended tool integrations | If integrating with external services (Slack, webhooks) for notifications |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Sequential Process | Hierarchical Process | Hierarchical adds manager overhead but enables dynamic delegation; use only when complexity demands it |
| CrewAI Crews | CrewAI Flows | Flows are deterministic (no agent autonomy), Crews are autonomous; hybrid approach is optimal |
| Task context passing | Shared memory/database | Task context is simpler for linear flows; shared state needed for complex branching |
| Single monolithic crew | Multiple specialized crews | Specialized crews are more maintainable and testable; compose as needed |

**Installation:**
```bash
# Core dependencies already in pyproject.toml
# Optional additions:
pip install langfuse  # For observability
pip install instructor  # For enhanced structured outputs
```

## Architecture Patterns

### Recommended Project Structure
```
src/sade_agents/
├── agents/
│   ├── base.py                     # SadeAgent (existing)
│   ├── narrator.py                 # Individual agents (existing)
│   ├── pricing_analyst.py
│   ├── growth_hacker.py
│   ├── alchemist.py
│   ├── curator.py
│   └── perfectionist.py
├── crews/
│   ├── __init__.py
│   ├── base_crew.py                # Base crew composition utilities
│   ├── product_launch_crew.py     # Alchemist + Narrator + Curator + Perfectionist
│   ├── market_analysis_crew.py    # Pricing + Growth + Narrator
│   └── quality_audit_crew.py      # All agents + Perfectionist validation
├── workflows/
│   ├── __init__.py
│   ├── sequential_workflow.py     # Standard sequential orchestration
│   └── hierarchical_workflow.py   # (Optional) Manager-led complex workflows
├── models/
│   ├── workflow_input.py          # Pydantic models for workflow inputs
│   └── workflow_output.py         # Structured outputs across agents
└── config/
    └── crew_configs.py            # Crew composition definitions
```

### Pattern 1: Task Context Passing (Sequential Workflow)

**What:** Tasks depend on previous task outputs using the `context` attribute, creating a dependency graph.

**When to use:** Linear workflows where output of one agent informs the next (e.g., Alchemist creates recipe → Narrator writes story → Curator designs label).

**Source:** [CrewAI Tasks Documentation](https://docs.crewai.com/en/concepts/tasks)

**Example:**
```python
from crewai import Agent, Task, Crew, Process

# Define tasks with context dependencies
recipe_task = Task(
    description="Create a new chocolate flavor profile with Antep pistachio",
    expected_output="Recipe with ingredients, process steps, and flavor notes",
    agent=alchemist_agent,
    async_execution=False  # Must complete before dependent tasks
)

story_task = Task(
    description="Write a 'Quiet Luxury' product story for the new flavor",
    expected_output="2-3 paragraph story, Instagram caption, and box insert note",
    agent=narrator_agent,
    context=[recipe_task]  # Waits for recipe_task to complete, uses its output
)

label_task = Task(
    description="Design product label visual using the recipe and story",
    expected_output="3 label design variations in PNG format",
    agent=curator_agent,
    context=[recipe_task, story_task]  # Uses outputs from both tasks
)

audit_task = Task(
    description="Audit all outputs for brand consistency",
    expected_output="AuditResult JSON with scores and recommendations",
    agent=perfectionist_agent,
    context=[story_task, label_task]  # Reviews final outputs
)

# Sequential crew composition
product_launch_crew = Crew(
    agents=[alchemist_agent, narrator_agent, curator_agent, perfectionist_agent],
    tasks=[recipe_task, story_task, label_task, audit_task],
    process=Process.sequential,  # Tasks execute in order
    verbose=True
)

# Execute workflow
result = product_launch_crew.kickoff(inputs={"flavor_concept": "Antep Pistachio"})
```

### Pattern 2: Specialized Crew Compositions

**What:** Pre-configured crews for common workflows, composed from specialist agents.

**When to use:** Reusable workflows that combine specific agents (e.g., "Market Analysis" always uses Pricing + Growth + Narrator).

**Source:** [CrewAI Best Practices 2026](https://docs.crewai.com/en/guides/agents/crafting-effective-agents)

**Example:**
```python
# File: src/sade_agents/crews/product_launch_crew.py
from crewai import Crew, Process
from sade_agents.agents import AlchemistAgent, NarratorAgent, CuratorAgent, PerfectionistAgent
from sade_agents.models import ProductLaunchInput, ProductLaunchOutput
from typing import Dict, Any


class ProductLaunchCrew:
    """
    Product launch workflow crew.

    Orchestrates: Alchemist → Narrator → Curator → Perfectionist
    Use case: New flavor development, recipe + story + visual + audit
    """

    def __init__(self):
        """Initialize agents for product launch."""
        self.alchemist = AlchemistAgent()
        self.narrator = NarratorAgent()
        self.curator = CuratorAgent()
        self.perfectionist = PerfectionistAgent()

    def create_tasks(self, inputs: ProductLaunchInput) -> list:
        """Create task chain with context dependencies."""
        from crewai import Task

        recipe_task = Task(
            description=f"Create chocolate recipe for: {inputs.flavor_concept}",
            expected_output="Recipe JSON with ingredients, process, tasting notes",
            agent=self.alchemist
        )

        story_task = Task(
            description="Write product story, caption, and box note",
            expected_output="ProductStory JSON (story, caption, note)",
            agent=self.narrator,
            context=[recipe_task]
        )

        label_task = Task(
            description="Design label visuals (3 variations)",
            expected_output="List of image file paths",
            agent=self.curator,
            context=[recipe_task, story_task]
        )

        audit_task = Task(
            description="Audit story and label for brand consistency",
            expected_output="AuditResult JSON",
            agent=self.perfectionist,
            context=[story_task, label_task]
        )

        return [recipe_task, story_task, label_task, audit_task]

    def kickoff(self, inputs: Dict[str, Any]) -> ProductLaunchOutput:
        """Execute product launch workflow."""
        validated_inputs = ProductLaunchInput(**inputs)

        tasks = self.create_tasks(validated_inputs)

        crew = Crew(
            agents=[self.alchemist, self.narrator, self.curator, self.perfectionist],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff(inputs=inputs)

        # Parse and validate output
        return ProductLaunchOutput.parse_from_result(result)
```

### Pattern 3: Hierarchical Process with Custom Manager

**What:** A manager agent coordinates task delegation to specialist agents based on capabilities and availability.

**When to use:** Complex, non-linear workflows where tasks need dynamic allocation (e.g., multi-channel campaign with conditional branches).

**Source:** [CrewAI Hierarchical Process](https://docs.crewai.com/how-to/hierarchical-process)

**Example:**
```python
from crewai import Agent, Crew, Process

# Define specialist agents (already exist)
specialists = [
    narrator_agent,
    pricing_analyst_agent,
    growth_hacker_agent,
    alchemist_agent,
    curator_agent,
    perfectionist_agent
]

# Option 1: Auto-generated manager with manager_llm
campaign_crew = Crew(
    agents=specialists,
    tasks=campaign_tasks,  # Manager will allocate these dynamically
    process=Process.hierarchical,
    manager_llm="gpt-4o",  # Manager uses this model for decisions
    verbose=True
)

# Option 2: Custom manager agent (more control)
chief_architect = Agent(
    role="Chief Architect - Campaign Coordinator",
    goal="Coordinate specialist agents to deliver cohesive marketing campaigns",
    backstory="""
    You are the Chief Architect of Sade Chocolate's AI team.
    You understand each specialist's strengths:
    - Alchemist: Recipe and flavor expertise
    - Narrator: Brand voice and storytelling
    - Curator: Visual design and aesthetics
    - Pricing Analyst: Market intelligence and pricing
    - Growth Hacker: Trend identification and opportunities
    - Perfectionist: Quality control and brand consistency

    Your job is to delegate tasks to the right specialists, ensure
    outputs pass through Perfectionist review, and coordinate handoffs.
    """,
    allow_delegation=True,  # Critical: manager must be able to delegate
    verbose=True
)

campaign_crew = Crew(
    agents=specialists,
    tasks=campaign_tasks,
    process=Process.hierarchical,
    manager_agent=chief_architect,  # Use custom manager instead of auto-generated
    verbose=True
)
```

### Pattern 4: Human-in-the-Loop Approval Workflow

**What:** Pause workflow for human approval before proceeding, especially for supervised agents (Narrator, Curator, Perfectionist).

**When to use:** Tasks requiring human judgment (pricing decisions, content approval, design selection).

**Source:** [CrewAI HITL Workflows](https://docs.crewai.com/en/learn/human-in-the-loop)

**Example:**
```python
# Option 1: CLI-based approval (for local development)
def execute_with_approval(crew: Crew, inputs: dict):
    """Execute crew with manual approval gates."""
    result = crew.kickoff(inputs=inputs)

    # Pause for approval
    print("\n=== APPROVAL REQUIRED ===")
    print(f"Result: {result}")
    approval = input("Approve? (yes/no): ").lower()

    if approval == "yes":
        return result
    else:
        refinement = input("Refinement instructions: ")
        # Re-run with refinement context
        inputs["refinement_notes"] = refinement
        return crew.kickoff(inputs=inputs)

# Option 2: Webhook-based approval (for production/async)
# Using CrewAI's resume endpoint pattern
kickoff_response = requests.post(
    f"{CREW_API_URL}/kickoff",
    headers={"Authorization": f"Bearer {API_TOKEN}"},
    json={
        "inputs": {"topic": "New Ruby Chocolate Launch"},
        "humanInputWebhook": {
            "url": "https://your-app.com/webhooks/approval",
            "authentication": {
                "strategy": "bearer",
                "token": "webhook-secret"
            }
        }
    }
)

# Later, resume after human feedback
resume_response = requests.post(
    f"{CREW_API_URL}/resume",
    headers={"Authorization": f"Bearer {API_TOKEN}"},
    json={
        "execution_id": execution_id,
        "task_id": task_id,
        "human_feedback": "Approved with minor refinements: soften the call-to-action",
        "is_approve": True
    }
)
```

### Pattern 5: Mixed Autonomy Orchestration

**What:** Different agents have different autonomy levels; orchestrator respects supervision requirements.

**When to use:** Sade's mixed autonomy model (PricingAnalyst supervised, GrowthHacker autonomous, etc.).

**Source:** Project context + [CrewAI Flows](https://www.crewai.com/crewai-flows)

**Example:**
```python
from sade_agents.agents.base import SadeAgent

def create_supervised_task(agent: SadeAgent, task_config: dict):
    """Create task with autonomy-appropriate settings."""
    task = Task(**task_config, agent=agent)

    # Add approval gate for supervised agents
    if agent.autonomy_level == "supervised":
        task.callback = require_approval_callback

    return task

def require_approval_callback(task_output):
    """Callback for supervised task approval."""
    print(f"\n[{task_output.agent.role}] Requires approval:")
    print(task_output.raw)

    approved = input("Approve? (y/n): ").lower() == 'y'

    if not approved:
        feedback = input("Feedback for revision: ")
        # Trigger re-execution with feedback
        raise TaskRevisionRequested(feedback)

    return task_output

# Example crew with mixed autonomy
analysis_crew = Crew(
    agents=[
        pricing_analyst_agent,  # autonomy_level="supervised"
        growth_hacker_agent,    # autonomy_level="autonomous"
        narrator_agent          # autonomy_level="supervised"
    ],
    tasks=[
        create_supervised_task(pricing_analyst_agent, pricing_task_config),
        Task(**growth_task_config, agent=growth_hacker_agent),  # No approval needed
        create_supervised_task(narrator_agent, story_task_config)
    ],
    process=Process.sequential
)
```

### Anti-Patterns to Avoid

- **God Crew:** Don't create one massive crew with all 6 agents for every task. Compose specialized crews for specific workflows.

- **Task Bloat:** Avoid vague mega-tasks like "Create complete marketing campaign." Break into specific tasks with clear inputs/outputs/acceptance criteria.

- **Ignoring Task Context:** Don't manually pass data between tasks when CrewAI's `context` attribute handles it automatically.

- **Over-Hierarchical:** Don't use Hierarchical Process when Sequential suffices. Manager overhead adds latency and cost; use only when dynamic delegation is needed.

- **Silent Failures:** Always set `verbose=True` during development to trace agent decisions. Remove in production but add structured logging.

- **No Structured Outputs:** Don't rely on unstructured text returns. Use Pydantic models with `expected_output` defined clearly.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Task dependency management | Manual output passing | CrewAI `context` attribute | Automatic context propagation, handles async/parallel tasks, built-in error handling |
| Inter-agent communication | Custom message queue | CrewAI shared memory + task context | Framework handles state, memory persistence, context passing |
| Workflow state management | Custom state machine | CrewAI Flows (if deterministic) or Crew context | Event-driven flows with branching, state management, error recovery |
| Human approval gates | Custom CLI/webhooks | CrewAI HITL webhook pattern | Standardized pause/resume, multiple auth strategies, webhook integration |
| Manager/coordinator logic | Custom delegation code | CrewAI Hierarchical Process | LLM-powered intelligent delegation, capability matching, task allocation |
| Observability/tracing | Print/log statements | LangFuse or CrewAI built-in telemetry | Execution traces, agent decision tracking, performance metrics, debugging |

**Key insight:** CrewAI is purpose-built for multi-agent orchestration. Custom orchestration logic is rarely needed unless you have truly unique requirements outside CrewAI's process types. The framework handles 90% of coordination complexity.

## Common Pitfalls

### Pitfall 1: Position Bias in Manager Delegation

**What goes wrong:** In Hierarchical Process, manager agent consistently delegates to the first agent in the list regardless of suitability.

**Why it happens:** LLM attention mechanism favors early inputs; agent list order influences delegation decisions (~40% bias).

**How to avoid:**
- Randomize agent order in the agents list between runs
- OR use Sequential Process with explicit task assignments (no delegation needed)
- OR provide manager with clear capability descriptions in agent backstories

**Warning signs:** Same agent always gets first task, regardless of task type.

**Source:** [LLM-as-Judge Position Bias](https://labelyourdata.com/articles/llm-as-a-judge)

### Pitfall 2: Task Context Misuse

**What goes wrong:** Tasks don't receive expected context from previous tasks; outputs are missing or incomplete.

**Why it happens:** Forgetting to set `context=[prev_task]` or setting `async_execution=True` on a dependency.

**How to avoid:**
- Always set `async_execution=False` (or omit it, default is False) for tasks that have dependents
- Explicitly list all prerequisite tasks in `context=[task1, task2]`
- Use `expected_output` to document what context the task needs

**Warning signs:** Agent says "I don't have the information to complete this task."

**Source:** [CrewAI Tasks Documentation](https://docs.crewai.com/en/concepts/tasks)

### Pitfall 3: Over-Complexity with Hierarchical Process

**What goes wrong:** Hierarchical Process adds latency, cost, and unpredictability without clear benefits.

**Why it happens:** Assumption that "manager = better" without evaluating whether dynamic delegation is needed.

**How to avoid:**
- Start with Sequential Process for all workflows
- Only migrate to Hierarchical if you observe genuine need for dynamic task allocation
- Use Hierarchical sparingly, not as default

**Warning signs:** Manager makes poor delegation decisions, or always delegates in same order (making it no better than Sequential).

**Source:** [Sequential vs Hierarchical Decision Guide](https://help.crewai.com/ware-are-the-key-differences-between-hierarchical-and-sequential-processes-in-crewai)

### Pitfall 4: Ignoring Autonomy Levels

**What goes wrong:** Autonomous agents get approval gates (annoying interruptions), or supervised agents run without review (risky).

**Why it happens:** Orchestration doesn't respect `autonomy_level` attribute from SadeAgent.

**How to avoid:**
- Check `agent.autonomy_level` when creating tasks
- Add approval callbacks only for `supervised` or `mixed` agents
- Document which agents require supervision in crew docstrings

**Warning signs:** User frustrated by constant approvals for GrowthHacker reports, or pricing changes applied without review.

**Source:** Project context (mixed autonomy model)

### Pitfall 5: No Structured Input/Output Models

**What goes wrong:** Crew inputs are loose dictionaries, outputs are unstructured text, parsing fails downstream.

**Why it happens:** Skipping Pydantic model definition to "move fast."

**How to avoid:**
- Define Pydantic models for workflow inputs (e.g., `ProductLaunchInput`)
- Define models for expected outputs (e.g., `ProductLaunchOutput`)
- Validate inputs before crew kickoff, parse outputs after completion

**Warning signs:** Runtime errors from missing keys, type mismatches, downstream tasks failing to parse outputs.

**Source:** [Pydantic LLM Intro](https://pydantic.dev/articles/llm-intro)

### Pitfall 6: Tool Overreach

**What goes wrong:** Agents have access to tools they don't need, leading to confusion or misuse.

**Why it happens:** Giving all agents all tools by default instead of least-privilege principle.

**How to avoid:**
- Only attach tools an agent truly needs (e.g., Narrator doesn't need `gorsel_tasarla`)
- Review agent `tools=[]` list carefully during crew composition
- Keep tools deterministic and well-documented

**Warning signs:** Agent tries to use wrong tool, or tool calls fail because agent lacks context to use them properly.

**Source:** [CrewAI Common Pitfalls 2026](https://ondrej-popelka.medium.com/crewai-practical-lessons-learned-b696baa67242)

### Pitfall 7: Insufficient Debugging Visibility

**What goes wrong:** Workflow fails mid-execution, no visibility into which agent/task failed or why.

**Why it happens:** Running with `verbose=False` or no structured logging.

**How to avoid:**
- Always use `verbose=True` during development
- Add structured logging for production (LangFuse or similar)
- Implement error handling with informative messages

**Warning signs:** "Something went wrong" errors with no stack trace or agent decision log.

**Source:** [CrewAI Observability Best Practices](https://medium.com/@takafumi.endo/crewai-scaling-human-centric-ai-agents-in-production-a023e0be7af9)

### Pitfall 8: No Workflow Testing Strategy

**What goes wrong:** Workflows break in production; untested edge cases cause failures.

**Why it happens:** Only testing individual agents, not full crew compositions.

**How to avoid:**
- Write integration tests for each specialized crew
- Test with representative inputs (real product data)
- Mock expensive operations (Gemini API calls) in tests

**Warning signs:** Individual agents work fine, but crew workflows fail mysteriously.

**Source:** Software engineering best practices

## Code Examples

Verified patterns from official sources:

### Basic Sequential Crew with Task Context

```python
# Source: https://docs.crewai.com/en/concepts/tasks
from crewai import Agent, Task, Crew, Process

# Create agents (using existing SadeAgent instances)
from sade_agents.agents import AlchemistAgent, NarratorAgent

alchemist = AlchemistAgent()
narrator = NarratorAgent()

# Define tasks with context dependencies
recipe_task = Task(
    description="Create a pistachio chocolate recipe",
    expected_output="Recipe JSON with ingredients and process",
    agent=alchemist
)

story_task = Task(
    description="Write a product story based on the recipe",
    expected_output="Story text and Instagram caption",
    agent=narrator,
    context=[recipe_task]  # Waits for recipe_task, uses its output
)

# Create crew
flavor_development_crew = Crew(
    agents=[alchemist, narrator],
    tasks=[recipe_task, story_task],
    process=Process.sequential,
    verbose=True
)

# Execute
result = flavor_development_crew.kickoff(
    inputs={"flavor_concept": "Antep Fıstıklı"}
)
print(result)
```

### Kickoff with Structured Inputs

```python
# Source: https://docs.crewai.com/en/enterprise/guides/kickoff-crew
from pydantic import BaseModel, Field
from crewai import Crew

class ProductLaunchInput(BaseModel):
    """Structured input for product launch workflow."""

    flavor_concept: str = Field(description="Flavor concept description")
    target_audience: str = Field(description="Target customer segment")
    price_range: tuple[float, float] = Field(description="Min and max price")

    class Config:
        json_schema_extra = {
            "example": {
                "flavor_concept": "Ruby Chocolate with Rose",
                "target_audience": "Affluent millennials",
                "price_range": (120, 180)
            }
        }

# Validate inputs before kickoff
inputs = ProductLaunchInput(
    flavor_concept="Antep Fıstıklı",
    target_audience="Quiet luxury consumers",
    price_range=(150, 200)
)

result = product_launch_crew.kickoff(inputs=inputs.model_dump())
```

### Async Kickoff for Multiple Inputs

```python
# Source: https://docs.crewai.com/en/enterprise/guides/kickoff-crew
# Use case: Analyze multiple competitor products simultaneously

competitor_inputs = [
    {"competitor": "Vakko", "product": "Bitter 70%"},
    {"competitor": "Butterfly", "product": "Sütlü Fıstıklı"},
    {"competitor": "Godiva", "product": "Dark Chocolate Truffle"}
]

# Async kickoff for each
async_results = market_analysis_crew.kickoff_for_each_async(
    inputs=competitor_inputs
)

# Results are returned as they complete
for result in async_results:
    print(f"Competitor Analysis: {result}")
```

### Custom Manager Agent for Hierarchical Process

```python
# Source: https://docs.crewai.com/how-to/custom-manager-agent
from crewai import Agent, Crew, Process

# Define custom manager agent
chief_architect = Agent(
    role="Chief Architect",
    goal="Coordinate specialist agents to deliver cohesive campaigns",
    backstory="""
    You are Sade Chocolate's Chief Architect, coordinating 6 specialist agents:

    1. Alchemist - Recipe and flavor expertise (use for: flavor development, ingredient selection)
    2. Narrator - Brand storytelling (use for: product stories, captions, messaging)
    3. Curator - Visual design (use for: label design, visual assets)
    4. Pricing Analyst - Market intelligence (use for: competitor pricing, price recommendations)
    5. Growth Hacker - Trend identification (use for: market opportunities, growth strategies)
    6. Perfectionist - Quality control (use for: final review, brand consistency audit)

    WORKFLOW:
    - Product development: Alchemist → Narrator → Curator → Perfectionist
    - Market analysis: Pricing Analyst → Growth Hacker → Narrator
    - Campaign review: All agents → Perfectionist (final gate)

    Your job is to delegate tasks to the right specialists and ensure quality control.
    """,
    allow_delegation=True,  # CRITICAL: Manager must be able to delegate
    verbose=True
)

# Create hierarchical crew with custom manager
campaign_crew = Crew(
    agents=[alchemist, narrator, curator, pricing_analyst, growth_hacker, perfectionist],
    tasks=campaign_tasks,
    process=Process.hierarchical,
    manager_agent=chief_architect,  # Use custom manager
    verbose=True
)

result = campaign_crew.kickoff(inputs={"campaign_goal": "Launch Ruby Chocolate Line"})
```

### Human-in-the-Loop with Webhooks

```python
# Source: https://docs.crewai.com/en/learn/human-in-the-loop
import requests
import os

CREW_API_URL = os.getenv("CREW_API_URL")
API_TOKEN = os.getenv("CREW_API_TOKEN")

# Kickoff with HITL webhook
response = requests.post(
    f"{CREW_API_URL}/kickoff",
    headers={
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    },
    json={
        "inputs": {"product": "Antep Fıstıklı 50g"},
        "humanInputWebhook": {
            "url": "https://sade-admin.com/webhooks/approval",
            "authentication": {
                "strategy": "bearer",
                "token": os.getenv("WEBHOOK_SECRET")
            }
        }
    }
)

kickoff_data = response.json()
execution_id = kickoff_data["kickoff_id"]

# Later, after human reviews and approves...
resume_response = requests.post(
    f"{CREW_API_URL}/resume",
    headers={
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    },
    json={
        "execution_id": execution_id,
        "task_id": "label_design_task",
        "human_feedback": "Approved. Please make logo 10% smaller.",
        "is_approve": True
    }
)
```

### Specialized Crew Factory Pattern

```python
# Source: Project architecture + CrewAI best practices
from typing import List
from crewai import Crew, Process, Agent, Task

class SadeCrewFactory:
    """Factory for creating specialized crew compositions."""

    def __init__(self):
        """Initialize all available agents."""
        from sade_agents.agents import (
            AlchemistAgent,
            NarratorAgent,
            CuratorAgent,
            PricingAnalystAgent,
            GrowthHackerAgent,
            PerfectionistAgent
        )

        self.alchemist = AlchemistAgent()
        self.narrator = NarratorAgent()
        self.curator = CuratorAgent()
        self.pricing = PricingAnalystAgent()
        self.growth = GrowthHackerAgent()
        self.perfectionist = PerfectionistAgent()

    def create_product_launch_crew(self) -> Crew:
        """
        Product launch workflow.

        Pipeline: Alchemist → Narrator → Curator → Perfectionist
        Use case: New flavor development from recipe to approved label
        """
        agents = [self.alchemist, self.narrator, self.curator, self.perfectionist]
        tasks = self._create_product_launch_tasks()

        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )

    def create_market_analysis_crew(self) -> Crew:
        """
        Market analysis workflow.

        Pipeline: Pricing Analyst → Growth Hacker → Narrator
        Use case: Competitor intelligence and market opportunity reports
        """
        agents = [self.pricing, self.growth, self.narrator]
        tasks = self._create_market_analysis_tasks()

        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )

    def create_quality_audit_crew(self) -> Crew:
        """
        Quality audit workflow.

        Pipeline: All agents → Perfectionist review
        Use case: Full campaign review before launch
        """
        # All agents participate, Perfectionist reviews all outputs
        agents = [
            self.alchemist,
            self.narrator,
            self.curator,
            self.pricing,
            self.growth,
            self.perfectionist
        ]
        tasks = self._create_quality_audit_tasks()

        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )

    def _create_product_launch_tasks(self) -> List[Task]:
        """Define task chain for product launch."""
        # Implementation details...
        pass

    def _create_market_analysis_tasks(self) -> List[Task]:
        """Define task chain for market analysis."""
        # Implementation details...
        pass

    def _create_quality_audit_tasks(self) -> List[Task]:
        """Define task chain for quality audit."""
        # Implementation details...
        pass

# Usage
factory = SadeCrewFactory()
launch_crew = factory.create_product_launch_crew()
result = launch_crew.kickoff(inputs={"flavor": "Ruby Chocolate"})
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single mega-crew | Specialized crew compositions | 2025-2026 | Better maintainability, testability, reusability |
| Manual task chaining | CrewAI task context | 2024-2025 | Automatic dependency resolution, parallel execution support |
| Custom orchestration | CrewAI Flows + Crews hybrid | 2025-2026 | Deterministic backbone + agentic flexibility |
| Print-based debugging | Structured observability (LangFuse) | 2025-2026 | Production-ready tracing, performance metrics |
| Keyword delegation | LLM-powered manager | 2024-2025 | Intelligent task allocation based on capabilities |
| Sequential-only | Sequential + Hierarchical options | 2023-2024 | Choose right pattern for workflow complexity |

**Deprecated/outdated:**
- **Monolithic crews:** Don't use one crew for all workflows; compose specialized crews
- **Manual context passing:** Task `context` attribute is standard; manual passing is anti-pattern
- **Hierarchical-first:** Sequential is default and preferred; hierarchical only when needed
- **Unstructured I/O:** Pydantic models are now standard for inputs/outputs

## Open Questions

Things that couldn't be fully resolved:

1. **Crew State Persistence**
   - What we know: CrewAI supports memory, but long-running state persistence is unclear
   - What's unclear: How to persist crew state between sessions (e.g., save mid-workflow, resume later)?
   - Recommendation: For v1, run workflows to completion in single session. For v2, investigate CrewAI Flows state management or external state store (Redis/SQLite)

2. **Error Handling and Retries**
   - What we know: Individual agents can fail; CrewAI has some built-in error handling
   - What's unclear: Best practices for crew-level error recovery (retry failed tasks, rollback, etc.)
   - Recommendation: Implement try-catch around crew.kickoff(), log failures, manual retry for v1. Explore CrewAI's error handling hooks for v2

3. **Performance at Scale**
   - What we know: CrewAI powers "millions of daily executions" in production
   - What's unclear: Performance characteristics for Sade's specific workflows (6 agents, mixed autonomy)
   - Recommendation: Benchmark Product Launch Crew end-to-end, measure latency/cost. Optimize bottleneck tasks (likely Curator image generation)

4. **Hierarchical Process Stability**
   - What we know: Hierarchical process has recent bug reports (delegation type errors, wrong agent selection)
   - What's unclear: Is Hierarchical production-ready, or still experimental in CrewAI 0.86+?
   - Recommendation: Start with Sequential Process. Only migrate to Hierarchical after validating stability with simple test crews

5. **Multi-Language Support**
   - What we know: All Sade agents use Turkish (backstories, outputs, feedback)
   - What's unclear: Does CrewAI's manager agent handle non-English agent coordination well?
   - Recommendation: Test with custom Turkish manager agent backstory. Monitor for language mixing issues

6. **Approval Gate Integration**
   - What we know: HITL webhooks exist for enterprise/API usage
   - What's unclear: Best pattern for local CLI-based approval (Sade's current execution mode)?
   - Recommendation: Implement simple CLI approval callback pattern (see Pattern 4). Migrate to webhooks if deploying as service

## Sources

### Primary (HIGH confidence)
- [CrewAI Documentation](https://docs.crewai.com/) - Official documentation for Crews, Tasks, Processes
- [CrewAI Hierarchical Process](https://docs.crewai.com/how-to/hierarchical-process) - Manager agent setup
- [CrewAI Tasks Documentation](https://docs.crewai.com/en/concepts/tasks) - Task context and dependencies
- [CrewAI HITL Workflows](https://docs.crewai.com/en/learn/human-in-the-loop) - Human approval patterns
- [CrewAI Flows](https://www.crewai.com/crewai-flows) - Deterministic orchestration with Flows

### Secondary (MEDIUM confidence)
- [Sequential vs Hierarchical Guide](https://help.crewai.com/ware-are-the-key-differences-between-hierarchical-and-sequential-processes-in-crewai) - Process selection criteria
- [CrewAI Best Practices 2026](https://docs.crewai.com/en/guides/agents/crafting-effective-agents) - Agent and task design patterns
- [LLM-as-Judge Position Bias](https://labelyourdata.com/articles/llm-as-a-judge) - Manager delegation pitfalls
- [CrewAI Practical Lessons](https://ondrej-popelka.medium.com/crewai-practical-lessons-learned-b696baa67242) - Common pitfalls and mistakes
- [Agentic Systems with CrewAI](https://blog.crewai.com/agentic-systems-with-crewai/) - Architecture patterns (Flows + Crews)

### Tertiary (LOW confidence - needs validation)
- [Multi-Agent Design Patterns](https://www.infoq.com/news/2026/01/multi-agent-design-patterns/) - Generator-Critic and other patterns (Google research)
- Community forum discussions on Hierarchical Process bugs - anecdotal, needs testing
- CrewAI examples repository - good for code samples but not all production-ready

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - CrewAI already in use, well-documented features
- Architecture: MEDIUM - Sequential/Hierarchical patterns documented, but Sade-specific crew compositions need validation
- Pitfalls: MEDIUM - Based on official docs + community experience, but some are inferred from general LLM pitfalls

**Research date:** 2026-01-30
**Valid until:** 30 days (stable domain - CrewAI orchestration patterns are mature)

**Key findings summary:**
1. Sequential Process with task context is recommended default for Sade workflows
2. Specialized crew compositions (ProductLaunchCrew, MarketAnalysisCrew) improve reusability
3. Hierarchical Process optional, only for complex non-linear workflows (reserve for v2)
4. Task context attribute handles inter-agent communication automatically
5. Human-in-the-loop approval needed for supervised agents (Narrator, Curator, Perfectionist)
6. Pydantic models critical for structured inputs/outputs across crews
7. Hybrid Flows + Crews pattern emerging as production best practice (deterministic backbone + agentic steps)

**Next steps for planner:**
- Define ProductLaunchInput/Output Pydantic models (workflow I/O contracts)
- Implement SadeCrewFactory with 3 initial crew compositions (Product Launch, Market Analysis, Quality Audit)
- Create sequential workflow orchestration with task context
- Add CLI-based approval gates for supervised agents
- Test end-to-end Product Launch Crew with real data
- Defer Hierarchical Process to Phase 9 (validate need first)
