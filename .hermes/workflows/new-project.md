# Workflow: New Project Initialization

## Trigger
New client brief received or internal project kickoff.

## Input
- Brief (normalized JSON schema — see `templates/brief-schema.json`)
- Brand assets (logos, guidelines, tokens if existing)
- Business goals and success criteria

## Process

### 1. Brief Validation (Orchestrator)
- Validate brief against schema
- Check for required fields: `project`, `business_goal`, `target_audience`, `primary_action`, `platform`, `approval_required`
- Flag missing `brand_assets` — request or create placeholder
- Output: `runs/<project>/brief-validated.json`

### 2. Project Setup (Orchestrator)
- Create project directory: `runs/YYYY-MM-DD_<project-slug>/`
- Initialize git tracking for project artifacts
- Create subdirectories: `screenshots/`, `diff/`, `corrections/`
- Output: Project workspace ready

### 3. Agent Assignment (Orchestrator)
| Agent | Task | Output |
|-------|------|--------|
| Art Director | Visual direction + tokens | `direction.json`, `tokens/*.json` |
| UX Designer | IA + component specs + responsive | `ux-specs.json` |
| Sales Specialist | Conversion strategy + copy + CTAs | `commercial-specs.json` |
| Brand Designer | Brand audit + token alignment | `brand-audit.json` (if existing brand) |

### 4. Design Plan Synthesis (Orchestrator)
- Consolidate agent outputs into unified `design-plan.json`
- Define component inventory, page structure, asset list
- Set validation thresholds per project (can override defaults)
- Define success criteria mapping

### 5. Handoff to Build
- Trigger `website-production` or relevant production workflow
- Pass `design-plan.json` + all specs to Web Builder

## Output
- `runs/<project>/brief-validated.json`
- `runs/<project>/design-plan.json`
- `runs/<project>/direction.json`
- `runs/<project>/ux-specs.json`
- `runs/<project>/commercial-specs.json`
- `runs/<project>/brand-audit.json` (if applicable)

## Quality Gate
- All specs complete and internally consistent
- No conflicting tokens between Art Director and Brand Designer
- Commercial specs align with UX flows
- Brief validation passes

## Escalation
- Missing critical brief fields → Human clarification required
- Brand conflicts → Human decision required
- Platform not supported → Human approval for custom build