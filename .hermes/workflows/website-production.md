# Workflow: Website Production (Elementor / HTML / Figma)

## Trigger
`new-project` workflow completes with approved `design-plan.json`

## Input
- `design-plan.json` (consolidated specs)
- `direction.json` (visual direction + tokens)
- `ux-specs.json` (IA, components, responsive, a11y)
- `commercial-specs.json` (conversion strategy, copy, CTAs, proof)
- `brand-audit.json` (if applicable)

## Process

### 1. Build Phase (Web Builder)
- Select target platform adapter (Elementor, HTML, Figma)
- Create staging environment
- Implement pages/components per specs:
  - Apply design tokens exactly
  - Implement component specs exactly
  - Insert copy blocks from commercial specs
  - Place CTAs per CTA architecture
  - Integrate social proof placeholders (mark PENDING if missing)
- Optimize assets (images, fonts, critical CSS)
- Capture screenshots: desktop, tablet, mobile
- Output: `build-log.json`, `staging-url`, `screenshots/`, `diffs/`

### 2. Validate Phase (Design Critic) — PARALLEL VALIDATORS
Run all validators against staging URL:

| Validator | Tool | Threshold Config |
|-----------|------|------------------|
| Contrast | `contrast_analyzer` | WCAG AA (4.5:1 / 3:1) |
| Accessibility | `accessibility_audit` (axe-core) | 0 violations |
| Performance | `performance_audit` (Lighthouse) | LCP/INP/CLS targets |
| Visual Regression | `visual_regression` (Playwright) | Baseline comparison |
| Responsive | `responsive_analyzer` | 0 overflow @ 375/768/1440 |
| Visual Hierarchy | `visual_hierarchy` | H1 > CTA > Body clarity |
| Typography | `typography_audit` | Scale, line-height, measure |
| Conversion | `conversion_audit` | 100-pt heuristic score |

- Each validator outputs structured diagnostics
- Design Critic consolidates into `audit-before.json`
- Assign severity: Critical / High / Medium / Low

### 3. Correct Phase (Design Loop)
For each issue (priority: Critical → High → Medium):

```
IF severity == Critical:
  ESCALATE to human — BLOCK delivery
  DO NOT auto-fix

IF severity == High AND auto_fix_allowed:
  TRY correction (max 3 retries)
  Web Builder applies minimal fix
  Re-run affected validators
  IF fixed: CONTINUE
  IF not fixed after 3 retries: ESCALATE

IF severity == Medium AND auto_fix_allowed AND no_design_impact:
  TRY correction (max 2 retries)
  Re-run validators
  IF fixed: CONTINUE
  IF not fixed: LOG advisory

IF severity == Low:
  LOG advisory — no auto-correction
```

- Track all corrections in `corrections.json`
- Each correction: `issue_id`, `action_taken`, `validator_re_run`, `result`
- Regression check: re-run ALL validators after each correction batch

### 4. Verify Phase (Design Critic)
- Full validator suite re-run → `audit-after.json`
- Compare `audit-before` vs `audit-after`
- Confirm all Critical/High resolved
- Confirm no new regressions introduced
- Quality gate decision: PASS / FAIL / ESCALATE

### 5. Delivery Preparation
If PASS:
- Generate `final-report.md` with:
  - Executive summary
  - Validator scorecards
  - Correction log
  - Screenshots (before/after)
  - Deployment checklist
- Package for handoff
- Request production deployment approval

If FAIL/ESCALATE:
- Document blocking issues
- Provide alternatives
- Request human intervention

## Output
- `runs/<project>/build-log.json`
- `runs/<project>/audit-before.json`
- `runs/<project>/audit-after.json`
- `runs/<project>/corrections.json`
- `runs/<project>/screenshots/`
- `runs/<project>/diff/`
- `runs/<project>/final-report.md`

## Quality Gates
| Gate | Criteria | Blocking |
|------|----------|----------|
| Build Complete | All pages implemented, screenshots captured | Yes |
| Critical Issues | 0 Critical issues remaining | Yes |
| High Issues | 0 High issues remaining | Yes |
| Performance | LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1 | Yes |
| Accessibility | 0 axe-core violations (WCAG 2.2 AA) | Yes |
| Visual Regression | No unintended changes vs baseline | Yes |
| Conversion Score | ≥ 70/100 heuristic | Advisory |

## Iteration Limits
- Max 5 full design loop cycles per project
- Max 3 correction retries per High issue
- Max 2 correction retries per Medium issue
- Exceeding limits → ESCALATE

## Escalation Triggers
- Critical issue cannot be resolved
- High issue fails 3 correction attempts
- Design Critic and Web Builder disagree on fix approach
- Brand integrity violation detected
- Platform limitation prevents spec compliance