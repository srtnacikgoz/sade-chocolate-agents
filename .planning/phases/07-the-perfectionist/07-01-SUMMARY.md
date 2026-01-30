---
phase: 07-the-perfectionist
plan: 01
subsystem: quality
tags: [pydantic, audit, quality-control, brand-voice, llm-as-judge]

# Dependency graph
requires:
  - phase: 01-temel-altyapi
    provides: Project structure, base configuration
  - phase: 06-the-curator
    provides: Style guide JSON files (brand_colors, typography, style_config)
provides:
  - AuditResult Pydantic model for structured audit output
  - Audit criteria dictionary for 5 agent output types
  - denetle() skill with LLM-as-Judge pattern for brand voice verification
  - stil_kilavuzu_yukle() skill for loading style guide files
  - onaylanmis_ornekler_yukle() skill with benchmark examples
affects: [07-the-perfectionist, orchestration, all-agents]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "LLM-as-Judge pattern for quality control"
    - "Structured audit results with Pydantic models"
    - "Content-type specific audit criteria"

key-files:
  created:
    - src/sade_agents/models/__init__.py
    - src/sade_agents/models/audit_result.py
    - src/sade_agents/skills/perfectionist_skills.py
  modified:
    - src/sade_agents/skills/__init__.py

key-decisions:
  - "AuditResult model includes 4 separate scores (overall, tone, vocabulary, structure) for granular feedback"
  - "Verdict thresholds: onay (80+), revizyon_gerekli (50-79), red (<50)"
  - "denetle() returns prompt for LLM instead of doing evaluation itself (LLM-as-Judge pattern)"
  - "Benchmark examples stored in code, will accumulate as approved content grows"

patterns-established:
  - "LLM-as-Judge: Tools return evaluation prompts, not evaluations - agent's LLM does the judging"
  - "Audit criteria vary by content type with different thresholds (metin: 75, gorsel_prompt: 80, trend_raporu: 65)"

# Metrics
duration: 4min
completed: 2026-01-30
---

# Phase 07 Plan 01: Perfectionist Core Summary

**AuditResult Pydantic model with scoring fields and 3 skills implementing LLM-as-Judge pattern for brand voice verification**

## Performance

- **Duration:** 4 min
- **Started:** 2026-01-30T12:39:32Z
- **Completed:** 2026-01-30T12:43:11Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Created AuditResult model with 4-dimensional scoring (overall, tone, vocabulary, structure)
- Implemented AUDIT_CRITERIA_BY_TYPE for 5 agent output types with content-specific thresholds
- Built denetle() skill that generates comprehensive audit prompts with forbidden/preferred phrases
- Added stil_kilavuzu_yukle() to read existing style guide JSON files
- Implemented onaylanmis_ornekler_yukle() with 9 benchmark examples across 4 content types

## Task Commits

Each task was committed atomically:

1. **Task 1: AuditResult Pydantic Modeli ve Denetim Kriterleri** - `21cef5c` (feat)
2. **Task 2: Perfectionist Skills Implementasyonu** - `b4d6a9d` (feat)

## Files Created/Modified
- `src/sade_agents/models/__init__.py` - Exports AuditResult and AUDIT_CRITERIA_BY_TYPE
- `src/sade_agents/models/audit_result.py` - AuditResult Pydantic model with scoring fields and verdict logic
- `src/sade_agents/skills/perfectionist_skills.py` - Three audit skills (denetle, stil_kilavuzu_yukle, onaylanmis_ornekler_yukle)
- `src/sade_agents/skills/__init__.py` - Added exports for perfectionist skills

## Decisions Made

**1. LLM-as-Judge pattern instead of rule-based evaluation**
- Rationale: denetle() returns a prompt for the agent's LLM to evaluate, not a hardcoded score. This leverages LLM's nuanced understanding of "Sessiz Luks" tone rather than rigid keyword matching.

**2. Content-type specific thresholds**
- Rationale: Different outputs have different quality bars. Gorsel prompts need 80+ (visual brand identity critical), trend reports only need 65+ (informational, less brand-facing).

**3. Benchmark examples embedded in code**
- Rationale: Start with 9 hand-picked approved examples. As Perfectionist approves more content, these will grow organically. Better than empty database initially.

**4. Four separate scoring dimensions**
- Rationale: Granular feedback (tone_score, vocabulary_score, structure_score) helps agents understand specific weaknesses rather than just one number.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

**Python version compatibility during verification**
- Issue: System Python 3.14 incompatible with crewai dependencies
- Resolution: Used existing .venv with Python 3.13 for all verification commands
- Impact: None on deliverables, verification successful

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for next plan:**
- AuditResult model validated (JSON serialization works)
- All 3 skills importable and functional
- Style guide integration verified (3 JSON files loaded successfully)
- Benchmark examples tested (3 metin examples, 1 gorsel_prompt, 1 fiyat_analizi, 1 recete)

**Blockers:** None

**Notes:**
- PerfectionistAgent implementation (07-02) can now use these skills
- denetle() prompt includes all brand voice rules from "Sessiz Luks" philosophy
- Style guide path resolution works correctly (uses Path relative to skills file)

---
*Phase: 07-the-perfectionist*
*Completed: 2026-01-30*
