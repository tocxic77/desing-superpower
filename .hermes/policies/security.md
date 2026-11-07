# Security Policy

## Staging-Only Rule
- **All agent operations target staging environments only**
- Production deployment requires explicit human approval (signed `approval-rules.md`)
- No agent has production write credentials in config

## Credential Management
- All secrets in `.env` (gitignored) — never in code, config, or logs
- `.env.example` documents required variables
- Rotate credentials quarterly
- Use app passwords / PATs with minimal scope

## Data Handling
- Client data (briefs, assets, analytics) stored in `runs/<project>/` — local only
- No external API calls with client data unless explicitly configured
- Analytics/CRM tokens scoped to read-only where possible
- Screenshots may contain client data — treat as confidential

## Network
- Playwright/Lighthouse run headless locally — no external browser cloud
- Figma API: read-only tokens preferred
- WordPress REST API: staging endpoints only
- No telemetry / usage tracking without opt-in

## Supply Chain
- Pin all dependencies in `pyproject.toml` / `package.json`
- Review new dependencies for security advisories
- MCP servers run locally — no remote execution
- Docker not required for Phase 1 (local execution)

## Incident Response
- If credential leak suspected: rotate immediately, audit logs
- If staging compromised: isolate, rebuild, rotate
- Document incidents in `SECURITY_INCIDENTS.md` (append-only)