---
name: conversion-strategy
description: Use when defining conversion goals, user journeys, and commercial structure for design projects
---

# Conversion Strategy Skill

## Purpose
Translate business goals into design requirements: user journey, conversion funnel, value proposition architecture.

## When to Use
- Project kickoff (commercial specs)
- Landing page optimization
- Funnel redesign
- CRO hypothesis formation

## Core Procedures

### 1. Goal → Journey Mapping
```
Input: Business goal (leads, sales, signups, downloads)
Output: User journey map with conversion points

Steps:
  1. Define primary conversion action (macro)
  2. Define micro-conversions (steps toward macro)
  3. Map user states: Unaware → Aware → Interested → Convinced → Acting
  4. Identify friction points per state
  5. Define success metrics per step
```

### 2. Value Proposition Architecture
First screen must answer in < 3 seconds:
- **What** — Product/service name + category
- **For whom** — Target audience identifier
- **Problem** — Pain point addressed
- **Why this** — Differentiator (not features — outcome)
- **Next step** — Single clear CTA

Structure options:
- Problem → Consequence → Solution
- Benefit → Evidence → Action
- Before → Intervention → Result
- Feature → Advantage → Impact
- Objection → Response → Proof

### 3. CTA Hierarchy
| Level | Purpose | Visual Weight | Placement |
|-------|---------|---------------|-----------|
| Primary | Macro conversion | Maximum (filled, brand color) | Hero, sticky, end of sections |
| Secondary | Micro conversion / info | Medium (outline, secondary) | Nav, section ends, cards |
| Contextual | In-context action | Minimum (text link, icon) | Inline, tooltips, tables |

Rules:
- One primary CTA per viewport
- Primary ≠ Secondary in visual weight
- Fitts's Law: size ≥ 44×44px, predictable positions
- Label = action verb + outcome ("Get Diagnosis", not "Submit")

### 4. Social Proof Strategy
Types (prioritized):
1. **Verifiable testimonials** — Name, role, company, photo, outcome
2. **Case studies** — Challenge, approach, result, metrics
3. **Client logos** — Recognizable, relevant, permissioned
4. **Certifications/badges** — Issuer, date, verification link
5. **Data/results** — Specific numbers, timeframe, source
6. **Experience signals** — Years, projects, publications

**Never invent** — mark missing as `PENDING_VERIFICATION`

### 5. Friction Audit
| Friction Type | Detection | Remediation |
|---------------|-----------|-------------|
| Form fields | Count > 5, sensitive fields early | Progressive disclosure, smart defaults |
| Cognitive load | Jargon, choices, unclear next step | Simplify copy, reduce options, guide |
| Trust gaps | No proof, no security signals, vague | Add proof, trust badges, transparency |
| Technical | Slow load, broken flow, mobile bugs | Performance fix, QA, responsive fix |

### 6. Offer Design
- Package: What's included, what's not
- Pricing: Anchor, tiers, annual discount
- Guarantee: Risk reversal (trial, refund, pilot)
- Urgency: Real (limited capacity) not fake (countdown)

## Decision Criteria
- Conversion ≠ manipulation (SYSTEM.md Rule 4)
- Every element serves journey progression
- Evidence verifiable or marked PENDING
- Mobile-first CTA placement

## References
- `references/conversion-frameworks.md`
- `references/cta-patterns.md`
- `references/social-proof-types.md`
- `references/friction-patterns.md`

## Workflows
- `workflows/conversion-optimization.md`

## Templates
- `templates/conversion-brief.md`
- `templates/journey-map-template.json`
- `templates/cta-spec-template.json`

## Evaluations
- `evaluations/conversion-heuristic.md`
- `evaluations/cro-hypothesis-template.md`