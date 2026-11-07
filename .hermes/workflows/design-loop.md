# Workflow: Design Loop (Auto-Correction Engine)

> **Estado**: DOCUMENTADO — NO IMPLEMENTADO. El único validador real es el de contraste (`tools/validators/contrast_analyzer.py`); no existe runner del loop, ni contador de ciclos, ni motor de corrección. Ver README § Implementation Status.

## Purpose
The core auto-correction loop that separates building from validating, enabling autonomous quality improvement.

## Principles
- **Builder ≠ Critic** — Different agents, no shared context during audit
- **Evidence-based** — Every correction triggered by measured violation
- **Minimal change** — Fix only the specific issue, no collateral changes
- **Traceable** — Every correction logged with before/after evidence
- **Bounded** — Hard limits on iterations to prevent infinite loops

## Loop Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    DESIGN LOOP (max 5 cycles)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  BUILD (Web Builder)                                         │
│       │                                                      │
│       ▼                                                      │
│  VALIDATE (Design Critic — parallel validators)              │
│       │                                                      │
│       ├─ PASS ──────────────────► DELIVER                    │
│       │                                                      │
│       └─ FAIL ─────────────────► DIAGNOSE                    │
│                                    │                         │
│                                    ▼                         │
│                              CORRECT (Web Builder)           │
│                                    │                         │
│                                    ▼                         │
│                              RE-VALIDATE                     │
│                                    │                         │
│                              (loop back)                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Input
- Staging URL from Web Builder
- Design specs (tokens, components, commercial)
- Validation thresholds (from config + project overrides)

## Validator Suite (Parallel Execution)

```python
validators = [
    ("contrast", ContrastAnalyzer, {"threshold_aa_normal": 4.5, "threshold_aa_large": 3.0}),
    ("accessibility", AccessibilityAudit, {"standard": "WCAG22AA"}),
    ("performance", PerformanceAudit, {"lcp_ms": 2500, "inp_ms": 200, "cls": 0.10}),
    ("visual_regression", VisualRegression, {"threshold": 0.05}),
    ("responsive", ResponsiveAnalyzer, {"breakpoints": [375, 768, 1440]}),
    ("visual_hierarchy", VisualHierarchy, {}),
    ("typography", TypographyAudit, {}),
    ("conversion", ConversionAudit, {"min_score": 70}),
]
```

## Diagnostic Schema (Per Issue)

El contrato es `templates/diagnostic-schema.json` (`additionalProperties: false`). Este ejemplo valida contra él:

```json
{
  "run_id": "2026-11-07_acme-landing_01",
  "issue_id": "A11Y-417",
  "validator": "contrast_analyzer",
  "category": "accessibility",
  "severity": "high",
  "element": ".hero__subtitle",
  "problem": "Contrast ratio 3.00:1 fails WCAG AA normal text threshold (4.5:1)",
  "measured_value": 3.0,
  "required_value": 4.5,
  "suggested_action": "Darken .hero__subtitle from #6B7280 to #4B5563",
  "scope": "hero-section",
  "auto_fix_allowed": true,
  "verification_required": true,
  "brand_constraint": "colors.semantic.text.primary",
  "regression_check": [".hero__subtitle"],
  "timestamp": "2026-11-07T22:41:09.512Z"
}
```

Campos que el schema **rechaza** (estuvieron en una versión anterior de este ejemplo): `cycle`, `selector`, `unit`, `affects_tokens`, `token_references`. El ciclo vive en el log (`design-loop-log.json`), no en el diagnóstico; la unidad va implícita en `measured_value`/`required_value`. `issue_id` se deriva de `run_id` + `element` con SHA-256 truncado, así que es estable entre corridas (`tests/validators/test_contrast_analyzer.py`).

## Correction Engine

### Auto-Fix Rules
| Severity | Auto-Fix | Max Retries | Human Required |
|----------|----------|-------------|----------------|
| Critical | No | 0 | Yes |
| High | Yes | 3 | If all retries fail |
| Medium | Conditional* | 2 | No |
| Low | No | 0 | Advisory only |

*Medium: Only if `no_design_impact` confirmed by Art Director (async check)

### Correction Process
1. Design Critic authorizes correction → `corrections_authorized[]`
2. Web Builder receives authorized corrections
3. For each correction:
   - Identify minimal change (CSS value, Elementor setting, token override)
   - Apply change in staging
   - Capture screenshot of affected area
   - Run affected validator(s) only (targeted re-validation)
4. Log: `issue_id`, `action_taken`, `validator_re_run`, `result`, `screenshot_after`
5. Full regression check after batch (all validators)

### Correction Constraints (Guardrails)
- **No global token changes** for local issues without impact analysis
- **No brand asset replacement** without authorization
- **No content removal** to pass tests
- **No typography reduction** for overflow without alternative review
- **Rollback required** — every correction saves pre-state
- **Max 3 corrections per cycle** per issue category

## Cycle Tracking

```json
{
  "project": "landing-client",
  "cycle": 1,
  "started_at": "2026-11-07T10:00:00Z",
  "build_log": "build-log.json",
  "audit_before": "audit-1.json",
  "diagnostics_count": 12,
  "by_severity": {"critical": 0, "high": 3, "medium": 5, "low": 4},
  "corrections_authorized": 8,
  "corrections_applied": 7,
  "corrections_failed": 1,
  "audit_after": "audit-2.json",
  "regressions_found": 0,
  "quality_gate": "FAIL",
  "next_cycle": 2
}
```

## Termination Conditions
1. **PASS** — All Critical/High resolved, quality gates met
2. **MAX_CYCLES** — 5 cycles reached → ESCALATE
3. **STALLED** — 2 consecutive cycles with same unresolved High issues → ESCALATE
4. **REGRESSION_SPIKE** — New Critical issues introduced → ESCALATE
5. **TOKEN_CONFLICT** — Correction requires global token change → ESCALATE

## Output
- `runs/<project>/design-loop-log.json` (full cycle history)
- `runs/<project>/audit-<n>.json` (per cycle)
- `runs/<project>/corrections.json` (all corrections)
- `runs/<project>/regression-report.json`

## Integration Points
- Called by: `website-production`, `branding-production`, `presentation-production`
- Uses: `tools/orchestrator/design_loop.py`, `tools/orchestrator/correction_engine.py`, `tools/orchestrator/regression_manager.py`
- Feeds: `tools/orchestrator/quality_gate.py`