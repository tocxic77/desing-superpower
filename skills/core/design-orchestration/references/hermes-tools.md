# Design Superpowers — Hermes Tools Reference

This document maps Design Superpowers concepts to Hermes Agent tooling.

## Core Tools

| Superpowers Action | Hermes Tool |
|---|---|
| Read a file | `read_file` |
| Create a new file | `write_file` |
| Edit a file (targeted patch) | `patch` |
| Run a shell command | `terminal` |
| Search file contents | `search_files` |
| Find files by name | `search_files` with `target: "files"` |
| Fetch a URL / read a webpage | `web_extract(urls=[...])` |
| Search the web | `web_search(query=...)` |
| Dispatch a subagent | `delegate_task(goal=..., context=..., toolsets=[...], role="leaf")` |
| Task tracking | `todo` tool |
| Invoke a skill | `skill_view("design-superpowers:category/skill-name")` |

## Skill Invocation

Design Superpowers skills are registered with Hermes' native skill loader under the `design-superpowers:` namespace:

```python
# Load a skill
skill_view("design-superpowers:core/design-orchestration")
skill_view("design-superpowers:sales/conversion-strategy")
skill_view("design-superpowers:web/landing-pages")

# Load a skill's reference file
skill_view("design-superpowers:core/design-orchestration", file_path="references/design-principles.md")
```

## Subagent Dispatch

Use `delegate_task` to spawn isolated subagents for parallel or sequential workstreams:

```python
delegate_task(
    goal="Design a landing page hero section with conversion optimization",
    context="Project: acme-corp-landing. Brief: B2B SaaS, target: CTOs, primary CTA: 'Book Demo'. Brand tokens in design-system/tokens/. Platform: wordpress_elementor.",
    toolsets=["design-superpowers"],
    role="leaf"
)
```

## Task Tracking

Use the `todo` tool for task tracking within a session:

```python
todo(action="add", tasks=[
    {"content": "Validate brief against schema", "status": "in_progress"},
    {"content": "Generate design plan", "status": "pending"},
    {"content": "Build in Elementor staging", "status": "pending"},
    {"content": "Run validator suite", "status": "pending"},
])
```

## Design System Tokens

Tokens are the single source of truth. All agents consume from `design-system/tokens/`:

- `colors.json` + `colors.schema.json` — Semantic color roles with contrast verification
- `typography.json` + `typography.schema.json` — Type scale, font families, responsive overrides
- `spacing.json` + `spacing.schema.json` — 4px base unit scale, semantic aliases
- `shadows.json` — Elevation scale, semantic mappings
- `breakpoints.json` — Breakpoint definitions, container widths, grid columns
- `border-radius.json` — Radius scale, semantic mappings
- `z-index.json` — Layer scale, semantic mappings

## Project Workspace Pattern

Each project run creates a workspace under `runs/`:

```
runs/
└── 2026-11-07_acme-landing/
    ├── brief.json              # Validated brief
    ├── design-plan.json        # Consolidated plan from all agents
    ├── build-log.json          # Web Builder execution log
    ├── audit-before.json       # Design Critic initial audit
    ├── audit-after.json        # Final audit after corrections
    ├── corrections.json        # Design Loop correction log
    ├── screenshots/            # Playwright captures (desktop/tablet/mobile)
    ├── diff/                   # Visual regression diffs
    └── final-report.md         # Delivery report
```

## Agent Configurations

7 core agents defined in `.hermes/agents/`:

| Agent | Config File | Temperature | Key Tools |
|---|---|---|---|
| Orchestrator | `orchestrator.yaml` | 0.2 | task_router, dependency_manager, design_loop, quality_gate |
| Art Director | `art-director.yaml` | 0.4 | token_manager, component_style_guide, visual_hierarchy_guard |
| UX Designer | `ux-designer.yaml` | 0.3 | ia_mapper, component_specifier, responsive_specifier, a11y_designer |
| Web Builder | `web-builder.yaml` | 0.1 | elementor_builder, html_builder, figma_exporter, asset_optimizer |
| Brand Designer | `brand-designer.yaml` | 0.3 | identity_system_designer, token_generator, guideline_compiler |
| Sales Specialist | `sales-specialist.yaml` | 0.3 | conversion_strategist, visual_copywriter, cta_architect, offer_designer |
| Design Critic | `design-critic.yaml` | 0.1 | contrast_analyzer, accessibility_audit, performance_audit, visual_regression |

**Critical**: Design Critic is independent — it receives only staging URL + specs, not builder context.

## Workflows

Defined in `.hermes/workflows/`:

- `new-project.md` — Brief validation, project setup, agent assignment
- `website-production.md` — Build → Validate (parallel) → Correct loop
- `branding-production.md` — Strategy → Visual system → Tokens → Guidelines → Assets
- `presentation-production.md` — Narrative → Slides → Build → Export validation
- `design-loop.md` — Core auto-correction engine (max 5 cycles, 3 retries/issue)

## Quality Gates

10 gates in `.hermes/policies/quality-gates.md`:

| Gate | Blocking | Threshold |
|---|---|---|
| Brief Validation | Yes | Schema valid |
| Spec Consistency | Yes | All agents aligned |
| Build Complete | Yes | All pages/components built |
| Critical Issues | Yes | 0 critical |
| High Issues | Yes | 0 high |
| Performance | Yes | LCP≤2.5s, INP≤200ms, CLS≤0.1 |
| Accessibility | Yes | WCAG 2.2 AA |
| Visual Regression | Yes | ≤5% pixel diff |
| Conversion | Advisory | Score ≥70/100 |
| Brand Compliance | Yes | 100% token compliance |

## Validation Thresholds (from `.hermes/config.yaml`)

```yaml
validation_thresholds:
  contrast_aa_normal: 4.5
  contrast_aa_large: 3.0
  lcp_ms: 2500
  inp_ms: 200
  cls: 0.10
  conversion_min_score: 70
```

## Staging-Only Rule (Enforced)

- **All agent operations target staging environments only.**
- Production deployment requires explicit human approval.
- No agent holds production credentials.
- See `.hermes/policies/security.md` and `approval-rules.md`.

## MCP Servers

Defined in `.hermes/config.yaml`:

| Server | Type | Capabilities |
|---|---|---|
| design_orchestrator | Python | task_router, dependency_manager, design_loop, correction_engine |
| wordpress_elementor | Node | inspect, create, update, capture, validate Elementor pages |
| figma | Node | read files, extract tokens, export, compare components |
| browser | Python | Playwright automation, screenshots, DOM inspection |
| analytics | Node | GA4, Search Console, Clarity data |
| asset_manager | Node | upload, optimize, transform, CDN |

## Environment Variables

See `.env.example` for all required variables:

- `HERMES_MODEL`, `HERMES_PROVIDER` — LLM config
- `WORDPRESS_STAGING_URL`, `WORDPRESS_STAGING_USER`, `WORDPRESS_STAGING_APP_PASSWORD` — Elementor staging
- `FIGMA_ACCESS_TOKEN`, `FIGMA_FILE_KEY` — Figma integration
- `GA4_MEASUREMENT_ID`, `GSC_SITE_URL`, `CLARITY_PROJECT_ID` — Analytics