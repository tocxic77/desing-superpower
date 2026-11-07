# Design Superpowers

**Autonomous agent architecture for design, execution, and commercial optimization.**

A system of engineering for design — not a collection of prompts. The same architecture that powers [Superpowers](https://github.com/nous-research/hermes-agent/tree/main/plugins/superpowers) for code, adapted for visual design, UX, branding, editorial, and conversion-focused deliverables.

## Core Philosophy

> **No design is done because the agent says it's done. It's done when it has been built, inspected, validated, and approved against defined criteria.**

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      DESIGN ORCHESTRATOR                         │
│              Interprets brief · Plans · Distributes · Controls  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌─────────────────┐ ┌───────────────┐ ┌─────────────────┐
│ CREATIVE        │ │ BUILD ENGINE  │ │ VALIDATION      │
│ INTELLIGENCE    │ │               │ │ ENGINE          │
│                 │ │ • WordPress   │ │                 │
│ • Art Direction │ │   / Elementor │ │ • Visual QA     │
│ • UX Strategy   │ │ • Figma       │ │ • Accessibility │
│ • Branding      │ │ • HTML/CSS    │ │ • Performance   │
│ • Copywriting   │ │ • PDF / PPT   │ │ • Conversion    │
└─────────────────┘ └───────────────┘ └─────────────────┘
         ▲                 ▲                 ▲
         └─────────────────┼─────────────────┘
                           ▼
              ┌─────────────────────────────┐
              │      DESIGN LOOP            │
              │  Build → Validate → Correct │
              │      (auto-correction)      │
              └─────────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────────┐
              │    SALES INTELLIGENCE       │
              │  Conversion · Persuasion ·  │
              │  Experimentation · Evidence │
              └─────────────────────────────┘
```

## Key Components

| Layer | Purpose | Tools |
|-------|---------|-------|
| **Orchestrator** | Coordinates agents, workflows, quality gates | Hermes + MCP |
| **Creative Intelligence** | Art direction, UX, branding, copy | Skills + LLMs |
| **Build Engine** | Implements in target platform | Elementor, Figma, HTML, PDF, PPT |
| **Validation Engine** | Objective quality checks | Playwright, axe-core, Lighthouse |
| **Sales Intelligence** | Conversion optimization, CRO | Analytics, experimentation |
| **Design Loop** | Auto-correction with evidence | Correction engine + regression tests |

## Repository Structure

```
design-superpowers/
├── README.md
├── SYSTEM.md              # Five golden rules (manifesto)
├── AGENTS.md              # Agent definitions & responsibilities
├── pyproject.toml         # Python tooling config
├── package.json           # Node tooling config
├── .env.example
│
├── .hermes/               # Hermes integration
│   ├── config.yaml
│   ├── agents/            # 7 core agent definitions
│   ├── workflows/         # Project workflows
│   └── policies/          # Security, brand, quality gates
│
├── skills/                # Design skills (knowledge layer)
│   ├── core/              # Orchestration, direction, systems, critique
│   ├── visual-design/     # Typography, color, composition, branding
│   ├── ux-ui/             # Research, interaction, a11y, IA
│   ├── web/               # Conversion, landing, Elementor, performance
│   ├── sales/             # Strategy, copy, CTA, social proof, CRO
│   ├── editorial/         # PPT, PDF, reports, infographics
│   ├── digital-content/   # Social, email, campaigns, ads
│   ├── tools/             # Figma, image gen, assets, export
│   └── quality/           # Visual QA, a11y, responsive, performance, conversion
│
├── tools/                 # Executable tools (capability layer)
│   ├── mcp/               # MCP servers (WordPress, Figma, browser, analytics)
│   ├── validators/        # Contrast, visual regression, a11y, performance
│   ├── builders/          # Elementor, HTML, Figma, PPTX, PDF builders
│   └── orchestrator/      # Task router, design loop, correction engine
│
├── templates/             # Reusable starting points
├── design-system/         # Tokens, components, guidelines
├── projects/              # Project workspaces (gitignored)
├── evaluations/           # Benchmarks, regression, scoring
└── reports/               # Output reports (gitignored)
```

## The 7 Core Agents

| Agent | Function | Modifies |
|-------|----------|----------|
| **Orchestrator** | Coordinates project, workflows, assignments | Workflows, task distribution |
| **Art Director** | Defines visual direction, concepts, design system | Visual concepts, tokens |
| **UX Designer** | Architects experience, components, flows | IA, wireframes, UX specs |
| **Web Builder** | Implements in staging (Elementor, HTML, Figma) | Code, pages, components |
| **Brand Designer** | Develops identity systems, applications | Brand guidelines, assets |
| **Sales Specialist** | Optimizes conversion, copy, CTAs, offers | Commercial structure, messaging |
| **Design Critic** | **Independent** auditor — finds defects, authorizes fixes | Audit reports, corrections |

> **Critical:** The Design Critic is independent from the Builder. It does not confirm the Builder's work — it challenges it.

## Design Loop (Auto-Correction)

```
BRIEF → PLAN → BUILD → VALIDATE → [PASS] → DELIVER
                    ↓
              [FAIL] → DIAGNOSE → CORRECT → RE-VALIDATE
                    ↓
              (max 3 iterations/issue, 5 cycles/project)
```

Each validation produces structured diagnostics:

```json
{
  "issue_id": "A11Y-004",
  "category": "accessibility",
  "severity": "high",
  "element": ".hero__subtitle",
  "problem": "Insufficient contrast",
  "measured_value": 3.0,
  "required_value": 4.5,
  "suggested_action": "Darken background overlay",
  "scope": "hero-section",
  "auto_fix_allowed": true,
  "verification_required": true
}
```

## Quantitative Standards (Initial)

| Metric | Threshold | Reference |
|--------|-----------|-----------|
| Contrast (normal text) | ≥ 4.5:1 | WCAG 2.2 AA |
| Contrast (large text) | ≥ 3:1 | WCAG 2.2 AA |
| CLS | ≤ 0.10 | Core Web Vitals |
| LCP | ≤ 2.5s | Core Web Vitals |
| INP | ≤ 200ms | Core Web Vitals |
| Touch targets | ≥ 44×44px | Design preference |
| Horizontal overflow | 0 unjustified | Visual QA |

## Commercial Evaluation Model (100 pts)

| Dimension | Weight |
|-----------|--------|
| Value proposition clarity | 20 |
| Visual hierarchy & CTA | 20 |
| Credibility & social proof | 15 |
| Friction reduction | 15 |
| Copywriting quality | 10 |
| Offer-design coherence | 10 |
| Mobile adaptation | 10 |

## Implementation Phases

| Phase | Goal | Deliverable |
|-------|------|-------------|
| **1. Operational Core** | Build & validate a landing page | Orchestrator, Art Director, Web Builder, Design Critic + Playwright, axe-core, Lighthouse |
| **2. Pro Production** | Multi-format production tool | WP/Elementor MCP, Figma MCP, design tokens, PDF/PPT, branding |
| **3. Commercial Intelligence** | Designs connected to results | Sales Intelligence, CRO, analytics, CRM, A/B testing |
| **4. Learning & Autonomy** | Fewer errors, better quality | Decision library, correction history, visual benchmarks |

## Quick Start (Local)

```bash
# Clone
git clone https://github.com/your-org/design-superpowers
cd design-superpowers

# Install Python tools
pip install -e .

# Install Node tools
npm install

# Configure Hermes
cp .env.example .env
# Edit .env with your keys

# Register with Hermes (when ready)
# hermess skill install ./skills
```

## Evidence & Traceability

Every run produces an auditable trail:

```
runs/
└── 2026-11-07_landing-client/
    ├── brief.json
    ├── design-plan.json
    ├── build-log.json
    ├── audit-before.json
    ├── audit-after.json
    ├── screenshots/
    ├── corrections.json
    ├── diff/
    └── final-report.md
```

## Golden Rules (from SYSTEM.md)

1. **Design with intent, never decoration** — Every visual decision serves a goal
2. **Differentiation is mandatory** — No generic templates or Dribbble clones
3. **Evidence over opinion** — Contrast, responsive, performance validated by tools
4. **Conversion doesn't justify manipulation** — No fake testimonials, dark patterns
5. **No delivery without QC** — Build → Validate → Correct → Verify, all traced

## Tech Stack

| Component | Technology |
|-----------|------------|
| Orchestration | Hermes Agent |
| Tool Protocol | MCP (Model Context Protocol) |
| Browser Automation | Playwright |
| Accessibility | axe-core (Node) |
| Performance | Lighthouse (Node) |
| Backend Tools | Python 3.11+ |
| Visual Processing | Python + OpenCV |
| Web Processing | TypeScript |
| WordPress | REST API + custom plugin |
| Figma | Figma API + plugin |
| PDF | HTML/CSS → PDF or ReportLab |
| Presentations | PptxGenJS / python-pptx |
| Version Control | Git |
| Reporting | JSON + Markdown |

> **Runtime split**: Python = pure validators (`contrast_analyzer.py`, `design_loop.py`) + Python MCP servers (`design_orchestrator`, `browser`, `asset_manager`). Node = browser-based validators (axe-core, Lighthouse, visual regression, responsive, conversion, typography, hierarchy) + Node MCP servers (`wordpress_elementor`, `figma`, `analytics`). `playwright` Python solo lanza Chromium para `design_loop.py`; validaciones de a11y/performance corren en Node via scripts `validate:*` en package.json.

## Contributing

This is a design engineering system. Contributions should:
- Add verifiable tools, not prompts
- Include validation criteria with thresholds
- Maintain agent independence (Critic ≠ Builder)
- Follow the skill structure: `SKILL.md` + `references/` + `workflows/` + `templates/` + `evaluations/`

## License

MIT — Build better design systems.