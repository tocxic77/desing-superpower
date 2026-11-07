---
name: design-orchestration
description: Use when coordinating multi-agent design projects — establishes workflow, quality gates, and delivery standards
---

# Design Orchestration Skill

## Purpose
Coordinate the full design production pipeline: brief → plan → build → validate → correct → deliver. Ensures all agents follow SYSTEM.md rules and quality gates.

## When to Use
- Starting any new design project
- Managing project through design loop
- Enforcing quality standards
- Escalation handling

## Core Procedures

### 1. Brief Interpretation
```
Input: Raw brief (client doc, meeting notes, email)
Output: Normalized brief JSON (schemas/brief-schema.json)
Steps:
  1. Extract: project type, business goal, audience, actions, platform, constraints
  2. Validate against schema
  3. Flag missing critical fields → request clarification
  4. Create project workspace
  5. Emit brief-validated.json
```

### 2. Workflow Selection
| Project Type | Workflow |
|--------------|----------|
| Landing page / website | website-production |
| Brand identity | branding-production |
| Presentation | presentation-production |
| Social campaign | digital-content-production |
| Multi-format | website-production + relevant sub-workflows |

### 3. Agent Task Distribution
```
Task → Agent → Output Artifact
Visual direction → Art Director → direction.json + tokens/
UX specs → UX Designer → ux-specs.json
Commercial specs → Sales Specialist → commercial-specs.json
Brand audit → Brand Designer → brand-audit.json (if existing brand)
Build → Web Builder → build-log.json + staging
Audit → Design Critic → audit-<n>.json
Corrections → Web Builder → corrections.json
```

### 4. Design Loop Control
- Max 5 cycles per project
- Max 3 retries per High issue
- Max 2 retries per Medium issue
- Track in design-loop-log.json
- Termination conditions: PASS, MAX_CYCLES, STALLED, REGRESSION_SPIKE, TOKEN_CONFLICT

### 5. Quality Gate Enforcement
Evaluate gates in order (quality-gates.md). Block on failure. Record all gate results.

### 6. Escalation Handling
| Trigger | Action |
|---------|--------|
| Critical issue | Immediate human notification, block delivery |
| High issue ×3 failed | Escalate with diagnosis + alternatives |
| Max cycles reached | Escalate with full loop log + recommendations |
| Token conflict | Escalate to Art Director + Brand Designer |
| Brand integrity violation | Immediate block + Brand Designer review |

### 7. Delivery Report Generation
Final report includes:
- Executive summary (1 paragraph)
- Validator scorecards (table)
- Correction log (table)
- Before/after screenshots
- Deployment checklist
- Known limitations / PENDING items
- Handoff instructions

## Decision Criteria
- **Always** follow SYSTEM.md golden rules
- **Never** skip quality gates
- **Never** auto-approve production deployment
- **Prefer** minimal corrections over redesign
- **Escalate** when uncertainty > threshold

## References
- `references/workflow-patterns.md`
- `references/escalation-guide.md`
- `references/report-template.md`

## Workflows
- `workflows/new-project.md`
- `workflows/website-production.md`
- `workflows/branding-production.md`
- `workflows/presentation-production.md`
- `workflows/design-loop.md`

## Templates
- `templates/brief-schema.json`
- `templates/design-plan-template.json`
- `templates/final-report-template.md`

## Evaluations
- `evaluations/orchestration-benchmark.md`