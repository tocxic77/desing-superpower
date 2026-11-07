# Quality Gates Policy

## Gate Definitions
Each gate is a mandatory checkpoint. Failure = block progression.

### Gate 1: Brief Validation (Pre-Build)
- Brief schema valid
- Required fields present
- Brand assets available or placeholder created
- Platform supported
- **Blocking**: Yes

### Gate 2: Spec Consistency (Pre-Build)
- Art Director tokens ≠ Brand Designer tokens (conflict check)
- UX specs reference valid tokens
- Commercial specs align with UX flows
- No circular dependencies in component specs
- **Blocking**: Yes

### Gate 3: Build Complete (Post-Build)
- All pages/components implemented per specs
- Screenshots captured (desktop, tablet, mobile)
- Build log complete with diffs
- Staging URL accessible
- **Blocking**: Yes

### Gate 4: Critical Issues (Post-Validate)
- 0 Critical severity issues
- **Blocking**: Yes

### Gate 5: High Issues (Post-Correct)
- 0 High severity issues remaining after max retries
- **Blocking**: Yes

### Gate 6: Performance (Post-Validate)
- LCP ≤ 2500ms (or project override)
- INP ≤ 200ms (or project override)
- CLS ≤ 0.10 (or project override)
- Measured on staging, mobile simulation
- **Blocking**: Yes

### Gate 7: Accessibility (Post-Validate)
- 0 axe-core violations (WCAG 2.2 AA)
- Contrast ratios all pass
- Keyboard navigation functional
- Semantic HTML/structure valid
- **Blocking**: Yes

### Gate 8: Visual Regression (Post-Correct)
- No unintended visual changes vs baseline
- Baseline = previous approved version or design spec render
- Threshold: ≤ 5% pixel difference (configurable)
- **Blocking**: Yes

### Gate 9: Conversion Heuristic (Post-Validate)
- Score ≥ 70/100 (or project override)
- Evaluated by Conversion Audit validator
- **Blocking**: Advisory (does not block, but flags)

### Gate 10: Brand Compliance (Post-Validate)
- 100% token compliance
- No unauthorized brand asset usage
- No unapproved token overrides
- **Blocking**: Yes

## Gate Evaluation Order
1. Brief Validation → 2. Spec Consistency → 3. Build Complete → 4. Critical Issues → 5. High Issues → 6. Performance → 7. Accessibility → 8. Visual Regression → 9. Conversion → 10. Brand Compliance

## Override Process
- Only human can override a blocking gate
- Override recorded in `runs/<project>/gate-overrides.json`
- Requires: gate name, reason, risk assessment, mitigation, approver
- Override expires at project end

## Continuous Validation
- Gates 4-10 re-evaluated after every correction batch
- Regression detection: any previously-passed gate that fails
- Regression → immediate block + root cause analysis