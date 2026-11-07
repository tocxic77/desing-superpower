# Brand Integrity Policy

## Single Source of Truth
- **Design tokens** (`design-system/tokens/`) are the authoritative brand representation
- All agents consume tokens — no hardcoded values in implementations
- Token changes require: impact analysis + Art Director approval + regression test

## Token Governance
| Token Type | Change Authority | Process |
|------------|------------------|---------|
| Colors | Art Director + Brand Designer | Contrast re-verification mandatory |
| Typography | Art Director | Scale/line-height impact analysis |
| Spacing | Art Director | Component regression test |
| Shadows | Art Director | Visual regression test |
| Breakpoints | UX Designer + Art Director | Responsive regression test |
| Brand assets | Brand Designer only | Asset audit + guideline update |

## Brand Drift Prevention
- Every project starts with `brand-audit.json` (Brand Designer)
- Design Critic validates token compliance on every build
- Deviation > threshold → block + escalate
- Emergency overrides logged with rationale + rollback plan

## Asset Protection
- Logos: never stretched, recolored, or placed on violating backgrounds
- Photography: only approved assets from brand library
- Icons: only from approved icon system
- Typography: only approved fonts at approved scales

## Co-Branding / Partner Guidelines
- Partner logos: designated zone, minimum clear space, approved lockups
- Never modify partner assets
- Co-branded templates pre-approved by both parties

## Exception Process
1. Request with visual mockup + business justification
2. Art Director + Brand Designer review (async, 24h SLA)
3. If approved: token override documented in `runs/<project>/brand-exceptions.json`
4. Exception expires at project end — not added to global tokens
5. Design Critic validates exception doesn't violate accessibility

## Audit Trail
- All token reads/writes logged
- Brand exceptions tracked per project
- Quarterly brand health report: drift incidents, exceptions, token coverage