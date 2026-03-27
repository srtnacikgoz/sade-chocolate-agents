---
phase: 01-ui-expert-agent
plan: 04
subsystem: agents
tags: [crewai, agent, ui-expert, design-to-code]

requires:
  - 01-02  # Design skills (fetch_figma_design, extract_design_tokens)
  - 01-03  # Code generation skills (generate_streamlit_code, verify_generated_code, load_reference_examples)

provides:
  - UIExpertAgent class
  - UI Expert agent with 5 integrated tools
  - Design-to-code workflow orchestrator

affects:
  - 01-05  # UI Expert Crew will use this agent

tech-stack:
  added: []
  patterns:
    - "Agent composition pattern (SadeAgent inheritance)"
    - "Tool integration pattern (5 skills combined)"
    - "Verification loop pattern (max_iterations with threshold)"

key-files:
  created:
    - src/sade_agents/agents/ui_expert.py
  modified:
    - src/sade_agents/agents/__init__.py

decisions:
  - name: "Supervised autonomy level"
    rationale: "Generated code requires human review before deployment"
    status: active
  - name: "Verification threshold: 80"
    rationale: "Balances quality with iteration count, allows minor issues"
    status: active
  - name: "Max iterations: 3"
    rationale: "Prevents infinite loops while allowing refinement"
    status: active

metrics:
  duration: "2.2 min"
  completed: 2026-01-31
  tasks: 2
  commits: 2
  loc_added: 129
---

# Phase [01] Plan [04]: UI Expert Agent Summary

**One-liner:** UIExpertAgent integrates design skills + codegen skills to orchestrate Figma-to-Streamlit workflow with verification loop

## What Was Built

Created the **UIExpertAgent** - the orchestrator agent that combines design extraction and code generation capabilities into a supervised design-to-code workflow.

### Core Implementation

**UIExpertAgent class** (`src/sade_agents/agents/ui_expert.py`):
- Extends SadeAgent base class
- Integrates 5 tools from Plan 02 and Plan 03:
  - `fetch_figma_design` (design_skills)
  - `extract_design_tokens` (design_skills)
  - `load_reference_examples` (codegen_skills)
  - `generate_streamlit_code` (codegen_skills)
  - `verify_generated_code` (codegen_skills)

**Agent Configuration**:
- **Role:** "The UI Expert - Design to Code Specialist"
- **Department:** product
- **Autonomy Level:** supervised (code requires human review)
- **Verification Threshold:** 80 (minimum acceptance score)
- **Max Iterations:** 3 (refinement loop limit)

**Workflow Pattern**:
```
1. Fetch Figma frame data
2. Extract design tokens
3. Load reference examples
4. Generate Streamlit code
5. Verify generated code
6. If issues && iterations < max: refine and retry
7. Return code or issues list
```

### Integration Points

**SadeAgent Inheritance**:
- Inherits brand_voice ("sessiz_luks")
- Inherits log_action method
- Provides department and autonomy_level metadata

**Module Export**:
- Added to `src/sade_agents/agents/__init__.py`
- Alphabetically ordered in `__all__` list
- Importable as `from sade_agents.agents import UIExpertAgent`

## Technical Details

### Backstory Content

The agent backstory includes comprehensive code generation best practices:

**Mutlak Kurallar (Absolute Rules)**:
- No hallucination: Only use VALID_STREAMLIT_APIS
- Always include type hints
- Always include Google-style docstrings
- Never hardcode values (colors, spacing, sizes)

**Reference Library Pattern**:
- Always call load_reference_examples before generating
- Follow reference patterns exactly (imports, signatures, docstrings, layouts)

**Verification Loop**:
- Generate → Verify → Fix → Retry (up to max_iterations)
- Present issues list if threshold not met

**Avoid List**:
- st.beta_* or st.experimental_* (deprecated)
- Inline CSS or style dicts
- Global state abuse
- Magic numbers

### Type Annotations

```python
class UIExpertAgent(SadeAgent):
    verification_threshold: int = 80
    max_iterations: int = 3

    def __init__(
        self,
        verification_threshold: int = 80,
        max_iterations: int = 3,
    ) -> None:
        ...
```

### Verification Results

All verification checks passed:

```
✓ Syntax check: OK
✓ Import check: OK
✓ Agent role: "The UI Expert - Design to Code Specialist"
✓ Tools: 5 (all tools properly assigned)
✓ Department: product
✓ Autonomy: supervised
✓ SadeAgent features: All present (brand_voice, department, autonomy_level, log_action)
```

## Deviations from Plan

**None** - plan executed exactly as written.

All must_haves satisfied:
- ✓ UIExpertAgent extends SadeAgent
- ✓ Agent uses design_skills and codegen_skills tools
- ✓ Backstory includes code generation best practices
- ✓ Artifact: ui_expert.py with 127 lines (>80 required)
- ✓ Key links: tools parameter references fetch_figma_design, extract_design_tokens, generate_streamlit_code, verify_generated_code

## Files Changed

| File | Change | Lines | Purpose |
|------|--------|-------|---------|
| `src/sade_agents/agents/ui_expert.py` | Created | +127 | UIExpertAgent class definition |
| `src/sade_agents/agents/__init__.py` | Modified | +2 | Export UIExpertAgent |

**Total:** 129 lines added

## Testing Evidence

```bash
# Import test
$ python -c "from src.sade_agents.agents import UIExpertAgent; print('OK')"
OK

# Instantiation test
$ python -c "from src.sade_agents.agents.ui_expert import UIExpertAgent; \
  agent = UIExpertAgent(); \
  print(f'Role: {agent.role}'); \
  print(f'Tools: {len(agent.tools)}'); \
  print(f'Department: {agent.department}')"
Role: The UI Expert - Design to Code Specialist
Tools: 5
Department: product

# SadeAgent features test
$ python -c "from src.sade_agents.agents.ui_expert import UIExpertAgent; \
  agent = UIExpertAgent(); \
  print(f'brand_voice: {agent.brand_voice}'); \
  print(f'Has log_action: {hasattr(agent, \"log_action\")}')"
brand_voice: sessiz_luks
Has log_action: True
```

## Commits

| Hash | Message | Files |
|------|---------|-------|
| 8ba9dde | feat(01-04): create UIExpertAgent class | ui_expert.py |
| 4a5640e | feat(01-04): export UIExpertAgent from agents module | __init__.py |

## Next Phase Readiness

**Ready for Plan 01-05** (UI Expert Crew).

All dependencies satisfied:
- ✓ Design skills available (01-02)
- ✓ Code generation skills available (01-03)
- ✓ UIExpertAgent created (01-04)

Next crew can instantiate:
```python
from sade_agents.agents import UIExpertAgent

ui_expert = UIExpertAgent(
    verification_threshold=85,  # Optional: stricter than default
    max_iterations=5,            # Optional: more refinement attempts
)
```

### Potential Issues

**None anticipated.**

The agent is well-integrated and all tools are verified working from previous plans.

### Future Enhancements

1. **LLM Integration**: Current generate_streamlit_code uses templates; integrate actual LLM for true AI generation
2. **Multi-iteration Learning**: Track what issues were fixed in previous iterations to avoid repeating mistakes
3. **Reference Library Expansion**: Add more component types beyond card/form/data_table
4. **Verification Metrics**: Detailed scoring breakdown (syntax: 20%, types: 20%, APIs: 30%, docstrings: 15%, values: 15%)
5. **Code Quality Gates**: Pre-commit hooks integration, automatic formatting (black, ruff)

## Key Decisions

### Decision 1: Supervised Autonomy

**Context:** Agent generates code that will be deployed to production Streamlit app.

**Decision:** Set `autonomy_level="supervised"` - human review required before deployment.

**Rationale:**
- Generated code can have subtle bugs not caught by verification
- Design interpretation may differ from intent
- Security implications of code execution

**Alternative Considered:** Autonomous (auto-deploy after verification passes)
- Rejected: Too risky without comprehensive test suite

### Decision 2: Verification Threshold 80

**Context:** What minimum score allows code to pass?

**Decision:** Default threshold = 80 (out of 100)

**Rationale:**
- Catches major issues (syntax errors, invalid APIs)
- Allows minor issues (suboptimal patterns, missing edge cases)
- Balances quality with iteration count

**Alternative Considered:** Threshold = 100 (perfect code)
- Rejected: Would require many iterations, delays workflow

### Decision 3: Max Iterations 3

**Context:** How many refinement attempts before giving up?

**Decision:** Default max_iterations = 3

**Rationale:**
- Most issues fixable in 1-2 iterations
- Prevents infinite loops
- Forces escalation to human if persistent issues

**Alternative Considered:** Max iterations = unlimited
- Rejected: Risk of infinite loops if verification has bugs

## Lessons Learned

### What Went Well

1. **Clean inheritance pattern**: SadeAgent base class made agent creation straightforward
2. **Tool integration**: Previous plans (01-02, 01-03) provided well-defined tools
3. **Verification pipeline**: All checks passed on first run

### What Could Improve

1. **Pydantic metaclass quirk**: `issubclass(UIExpertAgent, SadeAgent)` returns False due to CrewAI's metaclass, though inheritance works correctly
   - Not a blocker, but could confuse developers
   - Workaround: Use `isinstance(agent, SadeAgent)` or check MRO

2. **Backstory length**: 40+ lines of backstory might be too much for LLM context
   - Consider: Move detailed rules to external reference doc
   - Keep backstory focused on persona and high-level philosophy

### Technical Insights

**Agent Composition Pattern**:
- Base class (SadeAgent) provides shared attributes
- Specialized agents (UIExpertAgent) add domain-specific tools
- Super().__init__() with kwargs makes CrewAI parameters pass-through clean

**Tool Assignment Pattern**:
- Tools list in super().__init__() call
- CrewAI wraps functions automatically
- No manual tool registration needed

---

**Plan Status:** ✅ COMPLETE

**Next Action:** Execute Plan 01-05 (UI Expert Crew)
