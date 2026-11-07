---
name: creative-direction
description: Use when defining visual direction, design tokens, and brand application — the Art Director's skill
---

# Creative Direction Skill

## Purpose
Translate brief + brand into coherent visual language: tokens, hierarchy, component style, art direction.

## When to Use
- New project visual direction
- Design system creation/extension
- Brand application to new format
- Visual hierarchy decisions

## Core Procedures

### 1. Direction Synthesis
```
Input: Brief, brand assets, competitive refs, business goals
Output: direction.json + token updates
Process:
  1. Analyze brief for emotional/functional attributes
  2. Map attributes to visual properties (color temp, type personality, space, imagery)
  3. Generate 2-3 direction concepts with rationale
  4. Select/merge based on brief priorities
  5. Extract tokens
```

### 2. Token Management
Tokens are **immutable during build** — only Art Director modifies.

| Token File | Contents | Validation |
|------------|----------|------------|
| colors.json | Palette, semantic roles, contrast ratios | WCAG AA pre-verified |
| typography.json | Font stacks, scale, line-height, measure | Readability + hierarchy |
| spacing.json | Base unit, scale, component spacing | 4px/8px grid |
| shadows.json | Elevation levels (0-5) | Consistent depth |
| breakpoints.json | Mobile, tablet, desktop, wide | Content-driven |
| border-radius.json | Radius scale (none → full) | Component consistency |
| z-index.json | Layer names → values | No conflicts |

### 3. Component Style Guide
Define per-component:
- Variants (primary, secondary, ghost, etc.)
- States (default, hover, focus, active, disabled)
- Responsive adaptations
- Token mappings (which tokens each property uses)

### 4. Visual Hierarchy Rules
- H1: Max 1 per view, token: `typography.display-xl`
- H2: Section headers, token: `typography.display-lg`
- H3: Subsection, token: `typography.heading-md`
- Body: `typography.body-lg` / `typography.body-md`
- CTA Primary: `typography.button`, `colors.cta-primary`, 44×44 min
- CTA Secondary: `typography.button`, `colors.cta-secondary`, 44×44 min

### 5. Image Art Direction
- Hero: aspect ratio, focal point, overlay specs
- Content images: aspect ratios, cropping rules
- Icons: style, weight, sizing tokens
- Illustrations: style guide, color mapping

### 6. Brand Integrity Checks
- Before any token change: run `brand-audit` validator
- Deviation threshold: ΔE > 2 for colors, > 10% for spacing
- Exception process: brand-integrity.md

## Decision Criteria
- Every token traces to brief objective
- Differentiation > convention (SYSTEM.md Rule 2)
- Accessibility baked in (contrast pre-verified)
- Scalability: tokens work at 320px and 1920px

## References
- `references/color-theory.md`
- `references/typography-scale.md`
- `references/visual-hierarchy-principles.md`
- `references/brand-application-rules.md`

## Workflows
- `workflows/visual-direction.md`

## Templates
- `templates/direction-brief.md`
- `templates/token-extraction-checklist.md`

## Evaluations
- `evaluations/direction-consistency.md`