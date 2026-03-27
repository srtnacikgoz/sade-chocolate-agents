---
phase: 06-the-curator
plan: 02
subsystem: creative-tools
status: complete
completed: 2026-01-30
duration: 3 min

tags:
  - curator
  - skills
  - gemini-api
  - image-generation
  - style-guide

dependency-graph:
  requires:
    - 01-temel-altyapi (skills module structure)
    - 05-the-alchemist (skill pattern reference)
  provides:
    - gorsel_tasarla skill function
    - Style guide integration
    - Gemini prompt generation
  affects:
    - 06-03 (CuratorAgent will use gorsel_tasarla)
    - Future visual design workflows

tech-stack:
  added:
    - "curator_skills.py module"
  patterns:
    - "@tool decorator for CrewAI skills"
    - "Dynamic file loading with defaults"
    - "Narrative prompt engineering"

key-files:
  created:
    - src/sade_agents/skills/curator_skills.py (248 lines)
  modified:
    - src/sade_agents/skills/__init__.py

decisions:
  - id: curator-001
    what: "Narrative prompt format for Gemini"
    why: "Gemini performs better with story-like prompts vs keyword lists"
    impact: "Prompts are descriptive paragraphs, not bullet points"

  - id: curator-002
    what: "Max 25 character text limit for labels"
    why: "Gemini text rendering constraint for quality output"
    impact: "Product name + gramaj must fit in 25 chars"

  - id: curator-003
    what: "Default style config when files don't exist"
    why: "Skill should work even if style_guide/ is empty"
    impact: "Provides sensible defaults for quiet luxury aesthetic"

  - id: curator-004
    what: "3 variation modes: prompt, varyasyon_prompt, bilgi"
    why: "Different use cases in Curator workflow"
    impact: "Single tool handles multiple design phases"
---

# Phase 6 Plan 02: Curator Visual Design Skills Summary

**One-liner:** Gemini prompt generation skill with style guide integration and 3-mode operation (single/variation/info) for label design.

## What Was Built

### Core Implementation

**gorsel_tasarla skill function:**
- Decorated with @tool for CrewAI integration
- 3 operational modes:
  - `prompt`: Single design prompt with style guide integration
  - `varyasyon_prompt`: 3 variations (Minimalist, Organic, Geometric)
  - `bilgi`: Style guide specs and color palette info
- Max 25 character text rendering limit enforced
- Turkish docstrings and comments throughout

**Helper Functions:**
- `_load_style_config()`: Loads style_config.json or provides defaults
- `_load_brand_colors()`: Loads brand_colors.json or provides defaults
- `_build_label_prompt()`: Constructs narrative Gemini prompts

**Style Guide Integration:**
- Dynamic loading from `style_guide/*.json`
- Graceful fallback to quiet luxury defaults
- Color palette: Sade Brown (#3D2314), Cream (#F5F0E8)
- Aesthetic keywords: elegant, minimalist, sophisticated, timeless
- Avoidance: flashy, loud, busy, cluttered

### Technical Details

**Prompt Structure:**
```
Create a premium product label for a quiet luxury chocolate brand named Sade.

Product: {name} - {description}
Label Text: "{text}" (render this text clearly)

Design Aesthetic:
elegant, minimalist, sophisticated, timeless, refined

Color Palette:
- Primary (chocolate): #3D2314
- Secondary (cream): #F5F0E8
- Use neutral, muted tones throughout

Composition:
- minimalist, centered
- ample white space
- Typography: elegant serif or clean sans-serif

AVOID: flashy, loud, busy, cluttered, cheap

The design should feel timeless, sophisticated, and whisper luxury rather than shout it.
Render the text clearly with proper spacing for print-ready output at 300 DPI.
```

**Variation Workflow:**
1. Agent calls gorsel_tasarla(urun_adi, mod="varyasyon_prompt")
2. Gets 3 prompt variations with different focuses
3. Sends each to Gemini sequentially
4. Saves to outputs/labels/{urun_adi}/v1/
5. Presents to user for selection

### Skills Module Update

Updated `skills/__init__.py`:
- Added gorsel_tasarla import from curator_skills
- Updated __all__ list (alphabetical order)
- All skills now exportable from sade_agents.skills

## Commits

| Task | Commit | Message |
|------|--------|---------|
| 1 | 4a893bc | feat(06-02): implement gorsel_tasarla skill for Curator |
| 2 | f2586a6 | feat(06-02): export gorsel_tasarla from skills module |

## Verification Results

All success criteria met:

- ✅ curator_skills.py created (248 lines, exceeds min_lines: 80)
- ✅ @tool decorator used (line 123)
- ✅ 3 modes implemented (prompt, varyasyon_prompt, bilgi)
- ✅ Style guide loading functions exist (_load_style_config, _load_brand_colors)
- ✅ Max 25 character limit enforced and documented
- ✅ Turkish docstrings throughout
- ✅ gorsel_tasarla exported from sade_agents.skills
- ✅ Python syntax validation passed
- ✅ Pattern matches alchemist_skills.py reference

**Must-Have Truths Verified:**
- ✅ gorsel_tasarla accepts product info and creates prompt
- ✅ Reads style_guide files and integrates into prompt
- ✅ Gemini API call mocked (skill generates prompt, API call in next plan)
- ✅ Importable from sade_agents.skills

**Key Links Verified:**
- ✅ curator_skills.py → style_guide/*.json (Path loading at line 16)
- ✅ __init__.py → curator_skills.py (import at line 16)

## Deviations from Plan

None - plan executed exactly as written.

## Key Insights

### What Worked Well

1. **Default fallback pattern**: Skill works even with empty style_guide directory
2. **Narrative prompt structure**: Clear, descriptive prompts for Gemini
3. **Multi-mode design**: Single tool handles different workflow phases
4. **Text length constraint**: 25 char limit prevents rendering issues
5. **Turkish documentation**: Maintains codebase consistency

### Technical Patterns Established

1. **Style guide loading pattern:**
   ```python
   config_path = STYLE_GUIDE_DIR / "style_config.json"
   if config_path.exists():
       with open(config_path, "r", encoding="utf-8") as f:
           return json.load(f)
   return {default_values}
   ```

2. **Variation prompt structure:**
   - Base prompt with common elements
   - Variation focus added to each (1-2 sentences)
   - Agent instructions included for workflow guidance

3. **Agent-facing output:**
   - Prompts in code blocks for copy-paste
   - Technical specs section
   - Agent instruction section (what to do next)

## Next Phase Readiness

### Ready for 06-03 (CuratorAgent)

**Available now:**
- ✅ gorsel_tasarla skill function
- ✅ Style guide integration
- ✅ Prompt generation for single/variations

**Agent can:**
1. Query style guide info: `gorsel_tasarla(mod="bilgi")`
2. Generate single prompt: `gorsel_tasarla(urun_adi, gramaj, aciklama)`
3. Generate variations: `gorsel_tasarla(urun_adi, mod="varyasyon_prompt")`

**Still needed (06-03 or later):**
- Actual Gemini API integration (currently mock)
- Image saving and file management
- Refinement/editing workflow
- Version tracking for iterations

### Blockers/Concerns

None. Style guide files are optional - defaults provided.

### Future Enhancements

1. **Style guide expansion:**
   - typography.json for font specifications
   - templates.json for layout presets
   - reference_images/ for visual inspiration

2. **Prompt optimization:**
   - A/B testing different prompt structures
   - Gemini-specific tips (aspect ratio, composition keywords)
   - Negative prompting for undesired elements

3. **Multi-product batch:**
   - Generate prompts for product catalog
   - Maintain consistency across product line
   - Seasonal/campaign-specific variations

4. **Quality scoring:**
   - Evaluate generated images against style guide
   - Automated composition analysis
   - Brand consistency metrics

## Usage Example

```python
from sade_agents.skills import gorsel_tasarla

# Get style guide info
info = gorsel_tasarla(mod="bilgi")
print(info)
# Output: Style keywords, color palette, specs

# Generate single prompt
prompt = gorsel_tasarla(
    urun_adi="Antep Fistikli",
    urun_gramaj="50g",
    urun_aciklama="Antep fistigi parcali sütlü çikolata"
)
# Output: Ready-to-use Gemini prompt

# Generate 3 variations
variations = gorsel_tasarla(
    urun_adi="Ruby Tablet",
    urun_gramaj="85g",
    mod="varyasyon_prompt"
)
# Output: 3 prompts (Minimalist, Organic, Geometric)
```

## Performance Metrics

**Execution time:** 3 minutes
**Lines of code:** 248 (curator_skills.py)
**Commits:** 2 (atomic per task)
**Files modified:** 2

**Velocity:**
- Task 1: ~2 min (implementation)
- Task 2: ~1 min (export update)

## Lessons Learned

1. **Defaults are essential**: Skills shouldn't fail when data files missing
2. **Narrative > Keywords**: Gemini responds better to story-like prompts
3. **Multi-mode tools**: Single skill can serve multiple workflow phases
4. **Agent instructions**: Output should guide what to do next
5. **Text constraints**: Know API limits upfront (25 char for text rendering)

---

**Status:** Complete ✅
**Duration:** 3 minutes
**Quality:** All verification checks passed
**Ready for:** 06-03 CuratorAgent implementation
