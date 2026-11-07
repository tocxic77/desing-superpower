# Approval Rules Policy

## Approval Matrix

| Action | Required Approver | Evidence Required | Auto-Approved If |
|--------|-------------------|-------------------|------------------|
| Project kickoff | Project Lead | Validated brief | — |
| Creative direction | Art Director + Client | Direction mockups + rationale | — |
| Brand token changes | Brand Designer + Art Director | Impact analysis + regression | — |
| Staging deployment | Web Builder | Build log + screenshots | All quality gates PASS |
| **Production deployment** | **Client + Project Lead** | **Final report + all gates PASS** | **NEVER** |
| Budget/timeline change | Project Lead | Updated plan + impact | — |
| Scope change | Project Lead + Client | Revised brief + specs | — |
| Brand exception | Brand Designer + Art Director | Mockup + justification | — |
| Critical issue waiver | Client + Project Lead | Risk assessment + mitigation | — |
| Tool/dependency upgrade | Tech Lead | Security audit + compat test | Patch version only |

## Approval Workflow

```
Request → Evidence Package → Reviewer(s) → Decision → Record
              │                   │
              ▼                   ▼
        Auto-check:          Human decision:
        - Gates PASS?        - Approve
        - No conflicts?      - Reject (with reason)
        - Schema valid?      - Request changes
```

## Evidence Package Standards
Every approval request includes:
- **What**: Clear description of change/action
- **Why**: Business/design rationale
- **Impact**: Affected components, pages, systems
- **Risk**: What could go wrong (honest assessment)
- **Mitigation**: How risk is reduced
- **Rollback**: How to undo if needed
- **Gates**: Current gate status (for deployments)

## Auto-Approval Conditions
- Staging deploy: All quality gates PASS + no Critical/High issues
- Dependency patch updates: Automated security scan PASS
- Token reads: Always allowed (read-only)
- Validator runs: Always allowed

## Never Auto-Approve
- Production deployment
- Brand token modifications
- Budget increases
- Scope expansions
- Critical issue waivers
- Credential changes
- New tool integrations

## Record Keeping
- All approvals in `runs/<project>/approvals.json`
- Format: `id`, `timestamp`, `action`, `requester`, `approver`, `decision`, `evidence_ref`
- Append-only — never modify historical records
- Quarterly audit: approval velocity, rejection reasons, override frequency

## Escalation
- Reviewer unavailable > 24h → escalate to next level
- Disagreement between reviewers → Project Lead decides
- Client disagrees with technical assessment → documented, technical team provides alternatives