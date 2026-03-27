# Sade Chocolate Agents

## What This Is

AI-powered business operations agents for Sade Chocolate — a Turkish premium chocolate brand. Multi-agent system covering marketing, finance, operations, and product departments with 6 specialized agents (Narrator, Pricing Analyst, Growth Hacker, Alchemist, Curator, Perfectionist) orchestrated through CrewAI workflows.

## Core Value

Every output sounds authentically Sade — consistent brand voice across all departments and touchpoints.

## Current State (v1.0 Shipped)

**Tech Stack:** Python 3.11+ / CrewAI / Gemini 2.0 Flash / Pydantic
**LOC:** 5,125 Python
**Agents:** 6 specialized agents with skills
**Crews:** 3 workflow compositions (ProductLaunch, MarketAnalysis, QualityAudit)

## Requirements

### Validated

- ✓ Agent architecture designed — v1.0 (7 specialized agents defined)
- ✓ Skills/Tools model established — v1.0 (Brain & Muscle separation)
- ✓ Department capability manifests — v1.0 (Finance, Marketing, Operations, Product)
- ✓ Brand strategy documentation — v1.0 (voice, positioning, pricing)
- ✓ Core agent framework (Python + CrewAI) — v1.0
- ✓ The Narrator agent (brand voice guardian) — v1.0
- ✓ The Pricing Analyst agent (competitive intelligence) — v1.0
- ✓ The Growth Hacker agent (trends and opportunities) — v1.0
- ✓ The Alchemist agent (flavor trends and recipes) — v1.0
- ✓ The Curator agent (visual/label design with Gemini) — v1.0
- ✓ The Perfectionist agent (UX and brand auditing) — v1.0
- ✓ Skills/tools implementation for each department — v1.0
- ✓ Inter-agent orchestration (SadeCrewFactory) — v1.0
- ✓ Agents integrated into daily workflow (CLI + docs) — v1.0

### Active

- [ ] Real web scraping for competitor prices
- [ ] Social media API integrations (trends)
- [ ] Test coverage improvement
- [ ] Error handling hardening

### Out of Scope

- Customer-facing chat — v1 is internal operations only, not customer service
- External payment API integrations — human approval required for any money movement
- sadechocolate.com integration — v2+ per roadmap, not v1
- Automated financial transactions — human approval required

## Context

**Brand Identity:**
- "Sessiz Luks" (Quiet Luxury) philosophy — sophisticated, understated, never shouty
- Premium positioning competing with Vakko, Butterfly in Turkish market
- The Narrator agent embodies Monocle/Kinfolk editorial voice

**Technical Foundation:**
- CrewAI for multi-agent orchestration
- Gemini 2.0 Flash for visual generation (Curator)
- LLM-as-Judge pattern for quality control (Perfectionist)
- Mock data approach — real APIs to be added in v1.1

**Agent Philosophy:**
- "Connoisseur Chip" — agents understand chocolate craft, not just code
- Domain expertise embedded in agent prompts and decision-making

## Constraints

- **Brand voice**: All agent outputs must pass The Narrator's "Sade voice" filter
- **Autonomy levels**: Mixed — some tasks autonomous, others require human approval

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python + CrewAI stack | Modular agent framework, existing team familiarity | ✓ Good |
| Mixed autonomy model | Balance speed with control for brand-critical decisions | ✓ Good |
| Skills as Python functions | Separation of concerns, updateable without retraining agents | ✓ Good |
| Internal-only for v1 | Reduce risk, prove value before customer exposure | ✓ Good |
| Mock data for v1 | Ship faster, add real APIs later | ✓ Good |
| LLM-as-Judge pattern | Quality control without hardcoded rules | ✓ Good |
| Gemini 2.0 Flash for visuals | Cost-effective, good quality labels | ✓ Good |
| Sequential crew process | Predictable task execution order | ✓ Good |

---
*Last updated: 2026-01-30 after v1.0 milestone*
