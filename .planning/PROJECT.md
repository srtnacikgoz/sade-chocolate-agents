# Sade Chocolate Agents

## What This Is

AI-powered business operations agents for Sade Chocolate — a Turkish premium chocolate brand. Multi-agent system covering marketing, finance, operations, and product departments with specialized roles (Pricing Analyst, Growth Hacker, Alchemist, Narrator, Curator, Perfectionist). Agents work with mixed autonomy: some tasks execute independently, others require human approval.

## Core Value

Every output sounds authentically Sade — consistent brand voice across all departments and touchpoints.

## Requirements

### Validated

<!-- Foundation work already completed -->

- ✓ Agent architecture designed — existing (7 specialized agents defined)
- ✓ Skills/Tools model established — existing (Brain & Muscle separation)
- ✓ Department capability manifests — existing (Finance, Marketing, Operations, Product)
- ✓ Brand strategy documentation — existing (voice, positioning, pricing)

### Active

<!-- Current scope. Building toward these. -->

- [ ] Implement core agent framework (Python + CrewAI)
- [ ] Build The Narrator agent (brand voice guardian)
- [ ] Build The Pricing Analyst agent (competitive intelligence)
- [ ] Build The Growth Hacker agent (trends and opportunities)
- [ ] Build The Alchemist agent (flavor trends and recipes)
- [ ] Build The Curator agent (visual/label design)
- [ ] Build The Perfectionist agent (UX and brand auditing)
- [ ] Skills/tools implementation for each department
- [ ] Inter-agent orchestration (Chief Architect role)
- [ ] Agents integrated into daily workflow

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Customer-facing chat — v1 is internal operations only, not customer service
- External API integrations — no social media APIs, payment systems in v1
- Automated financial transactions — human approval required for any money movement
- sadechocolate.com integration — v2+ per roadmap, not v1

## Context

**Brand Identity:**
- "Sessiz Lüks" (Quiet Luxury) philosophy — sophisticated, understated, never shouty
- Premium positioning competing with Vakko, Butterfly in Turkish market
- The Narrator agent must embody Monocle/Kinfolk editorial voice

**Technical Foundation:**
- Existing design documents in `/architecture/agent_system_design.md`
- Skills architecture in `/skills/README.md` with capability manifests per department
- Python + CrewAI identified as implementation stack in existing roadmap

**Agent Philosophy:**
- "Connoisseur Chip" — agents must understand chocolate craft, not just code
- Difference between Callebaut 811 vs 823, tempering chemistry, ganache science
- Domain expertise embedded in agent prompts and decision-making

## Constraints

- **Brand voice**: All agent outputs must pass The Narrator's "Sade voice" filter
- **Autonomy levels**: Mixed — some tasks autonomous, others require human approval

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python + CrewAI stack | Modular agent framework, existing team familiarity | — Pending |
| Mixed autonomy model | Balance speed with control for brand-critical decisions | — Pending |
| Skills as Python functions | Separation of concerns, updateable without retraining agents | — Pending |
| Internal-only for v1 | Reduce risk, prove value before customer exposure | — Pending |

---
*Last updated: 2026-01-30 after initialization*
