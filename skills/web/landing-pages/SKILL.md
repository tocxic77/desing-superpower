---
name: landing-pages
description: Use when designing high-conversion landing pages — structure, patterns, and platform-specific implementation
---

# Landing Pages Skill

## Purpose
Design and specify landing pages that convert: structure, components, platform adaptation.

## When to Use
- New landing page project
- Landing page audit/optimization
- Template creation
- A/B test variant design

## Core Procedures

### 1. Landing Page Anatomy (Standard Sections)
| Section | Purpose | Required | Conversion Role |
|---------|---------|----------|-----------------|
| Hero | Value prop + primary CTA | Yes | Hook + macro conversion |
| Problem/Empathy | Validate pain point | Yes | Build trust, qualify |
| Solution | Present offering | Yes | Communicate value |
| Benefits/Features | Detail value | Yes | Support decision |
| Social Proof | Evidence | Yes | Reduce risk |
| Objection Handling | Address barriers | Contextual | Remove friction |
| Secondary CTA | Micro-conversion | Yes | Capture interested |
| Footer | Trust signals, nav | Yes | Credibility |

### 2. Hero Patterns
**Pattern A: Direct Response**
- Headline: Outcome + timeframe
- Subhead: How it works (1 line)
- Primary CTA: Action + outcome
- Visual: Product in use / result demo

**Pattern B: Consultative**
- Headline: Problem question
- Subhead: Empathy + authority
- Primary CTA: "Get Assessment" / "Book Call"
- Visual: Expert imagery / trust signal

**Pattern C: Product-Led**
- Headline: Category + differentiator
- Subhead: Key benefit
- Primary CTA: "Start Free" / "See Demo"
- Visual: Interactive demo / screenshot

### 3. Responsive Specifications
| Breakpoint | Hero | Content | CTA | Nav |
|------------|------|---------|-----|-----|
| Mobile (375px) | Stacked, CTA sticky | Single column, full width | Sticky bottom bar | Hamburger |
| Tablet (768px) | Side-by-side | 2-col grid | Inline + sticky | Expanded |
| Desktop (1440px) | Full layout | Multi-col | Inline | Full |

### 4. Elementor Implementation Notes
- Use **Flexbox containers** (not sections/columns)
- Global styles → Theme Style → tokens
- Custom CSS for token overrides only
- Dynamic tags for content (not hardcoded)
- Responsive modes: edit per breakpoint
- Avoid: absolute positioning, fixed heights, !important

### 5. Conversion Checklist (Pre-Launch)
- [ ] Hero answers 5 questions in 3 seconds
- [ ] Single primary CTA per viewport
- [ ] CTA labels = action + outcome
- [ ] Social proof: verifiable, specific, relevant
- [ ] Form: ≤ 5 fields, progressive, inline validation
- [ ] No horizontal overflow at 375px
- [ ] LCP < 2.5s (hero image optimized)
- [ ] Contrast AA all text
- [ ] Keyboard navigable
- [ ] Thank you page / success state defined

## Decision Criteria
- Structure serves conversion journey (not aesthetics)
- Platform constraints respected (Elementor patterns)
- Mobile-first — desktop enhances, doesn't define
- Every section has conversion rationale

## References
- `references/landing-page-patterns.md`
- `references/elementor-best-practices.md`
- `references/mobile-first-specs.md`

## Workflows
- `workflows/landing-page-production.md`

## Templates
- `templates/landing-page-brief.md`
- `templates/landing-page-spec.json`
- `templates/elementor-template-kit.json`

## Evaluations
- `evaluations/landing-page-heuristic.md`
- `evaluations/conversion-benchmark.md`