# Workflow: Branding Production

## Trigger
New brand project or rebrand approved via `new-project` workflow.

## Input
- Brand strategy brief (positioning, audience, personality, differentiation)
- Competitive landscape analysis
- Existing assets (if rebrand)
- Application requirements (digital, print, environmental, motion)

## Process

### 1. Strategy → Visual System (Brand Designer + Art Director)
- Brand Designer: Translate strategy into identity system concepts (3 directions)
- Art Director: Develop design tokens for each direction
- Present directions with rationale mapped to strategy
- Human selects direction (or hybrid)

### 2. Identity System Development (Brand Designer)
- Logo system: primary, secondary, monochrome, responsive variants
- Color palette: primary, secondary, semantic, accessibility-compliant
- Typography: headline, body, UI fonts with scales
- Iconography: style, grid, weight rules
- Graphic elements: patterns, illustrations, photography style
- Motion principles (if applicable)

### 3. Token Generation (Brand Designer → Art Director)
- Export all decisions to `design-system/tokens/`:
  - `colors.json` — with contrast ratios pre-verified
  - `typography.json` — with scale, line-height, measure
  - `spacing.json` — base unit, scale, component spacing
  - `shadows.json` — elevation system
  - `breakpoints.json` — responsive tokens
  - `border-radius.json` — component radius scale
  - `z-index.json` — layering system

### 4. Guidelines Compilation (Brand Designer)
- Machine-readable guidelines (JSON schema for validators)
- Human-readable guidelines (Markdown + Figma/PDF)
- Application examples per channel
- Do's/Don'ts with visual evidence
- Asset usage rules

### 5. Asset Production (Brand Designer)
- Logo files (SVG, PNG, WebP — all variants)
- Icon set (SVG, optimized)
- Pattern/library files
- Template files (Elementor, Figma, PPTX, InDesign)
- Social media kit

### 6. Validation (Design Critic)
- Contrast verification across all color combinations
- Token consistency (no duplicate/conflicting values)
- Accessibility compliance (WCAG 2.2 AA)
- Scalability test (logo at 16px → 2000px)
- Cross-platform render test

### 7. Delivery
- `brand-guidelines.json` (machine-readable)
- `brand-guidelines.md` (human-readable)
- `design-system/tokens/` (complete)
- `assets/` (production-ready)
- `templates/` (starter templates)
- `brand-audit-report.md`

## Output
- `runs/<project>/brand-guidelines.json`
- `runs/<project>/brand-guidelines.md`
- `design-system/tokens/*.json` (updated)
- `assets/brand/<project>/`
- `templates/branding/`
- `runs/<project>/brand-audit-report.md`

## Quality Gates
- All color combos pass WCAG AA contrast
- Tokens validated against schema
- Logo renders correctly at all scales
- Guidelines pass machine-validation
- Human sign-off on creative direction