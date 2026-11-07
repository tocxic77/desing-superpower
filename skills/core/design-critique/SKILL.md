---
name: design-critique
description: Use when auditing design outputs — independent validation, defect detection, correction authorization
---

# Design Critique Skill

## Purpose
Independent audit of built artifacts. Find defects, authorize corrections, veto delivery. **Never confirms builder's work — challenges it.**

## When to Use
- Post-build validation (every cycle)
- Pre-delivery quality gate
- Regression detection
- Heuristic evaluation

## Independence Rules
- **No shared context with Web Builder** during audit
- Receive ONLY: staging URL, design specs, brand guidelines, thresholds
- Do NOT know builder intent — only observe output
- Findings based on measured evidence, not assumptions

## Core Procedures

### 1. Validator Suite Execution
Run all validators in parallel against staging URL:

```python
validators = [
    ContrastAnalyzer(threshold_aa_normal=4.5, threshold_aa_large=3.0),
    AccessibilityAudit(standard="WCAG22AA"),
    PerformanceAudit(lcp_ms=2500, inp_ms=200, cls=0.10),
    VisualRegression(threshold=0.05),
    ResponsiveAnalyzer(breakpoints=[375, 768, 1440]),
    VisualHierarchyAnalyzer(),
    TypographyAudit(),
    ConversionAudit(min_score=70),
]
```

### 2. Diagnostic Production
Every issue → structured diagnostic:

```json
{
  "issue_id": "PERF-001",
  "cycle": 1,
  "validator": "performance",
  "category": "performance",
  "severity": "high",
  "element": "hero-image",
  "selector": ".hero img",
  "problem": "LCP element is unoptimized image",
  "measured_value": 4200,
  "required_value": 2500,
  "unit": "ms",
  "suggested_action": "Add width/height, preload, convert to WebP",
  "scope": "hero-section",
  "auto_fix_allowed": true,
  "verification_required": true,
  "affects_tokens": false
}
```

### 3. Severity Classification
| Level | Criteria | Auto-Fix | Blocks Delivery |
|-------|----------|----------|-----------------|
| Critical | Page broken, CTA inaccessible, form fails, security issue | No | Yes |
| High | Contrast fail, overflow, content cut, LCP/INP/CLS fail | Yes (3×) | Yes |
| Medium | Misalignment, spacing inconsistency, minor hierarchy | Conditional (2×) | No |
| Low | Micro-aesthetic, preference, non-blocking | Advisory | No |

### 4. Correction Authorization
- Review each diagnostic
- Set `auto_fix_allowed` based on severity + `affects_tokens` + `scope`
- **Never authorize** token changes for local issues
- **Never authorize** brand asset replacement
- **Never authorize** content removal
- Output: `corrections_authorized[]` with issue_ids

### 5. Post-Correction Verification
- Re-run affected validators (targeted)
- Full regression suite after batch
- Compare `audit-before` vs `audit-after`
- Confirm: issue resolved, no new Critical/High introduced

### 6. Quality Gate Decision
| Decision | Conditions |
|----------|------------|
| PASS | 0 Critical, 0 High, all gates PASS |
| FAIL | High/Critical remain, or gate failure |
| ESCALATE | Stalled, token conflict, regression spike, max cycles |

### 7. Heuristic Evaluation (Beyond Validators)
- UX: Task completion, navigation clarity, form friction
- Conversion: Value prop clarity, CTA hierarchy, proof placement
- Brand: Token compliance, visual consistency, voice alignment
- Editorial: Reading order, heading structure, alt text quality

## Decision Criteria
- **Evidence over opinion** (SYSTEM.md Rule 3)
- Measured value vs required value for every finding
- No "looks wrong" — only "measured X, required Y"
- Minimal correction principle
- Veto power on Critical/High

## References
- `references/validator-specifications.md`
- `references/severity-guide.md`
- `references/heuristic-checklists.md`
- `references/regression-detection.md`

## Workflows
- `workflows/design-loop.md` (core loop)
- `workflows/pre-delivery-audit.md`

## Templates
- `templates/diagnostic-template.json`
- `templates/audit-report-template.md`

## Evaluations
- `evaluations/critic-accuracy.md`
- `evaluations/false-positive-rate.md`