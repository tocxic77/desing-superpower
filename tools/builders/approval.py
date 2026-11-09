#!/usr/bin/env python3
"""
approval.py — FASE 7 Approval Script Mínimo

Script que lee diagnostic.json (post-corrección) y decide:
- risk=low + 0 issues → approve
- risk=medium → human_review
- risk=high O issues críticos sin resolver → block
- Persiste approval-record.json con timestamp, decisión, razón
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_diagnostic(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def assess_risk(diagnostic: dict[str, Any]) -> tuple[str, str]:
    """
    Assess overall risk based on diagnostic summary.
    Returns (risk_level, reason)
    """
    summary = diagnostic.get("summary", {})
    total = summary.get("total_issues", 0)
    critical = summary.get("critical", 0)
    high = summary.get("high", 0)
    medium = summary.get("medium", 0)
    low = summary.get("low", 0)

    # Critical issues = always high risk
    if critical > 0:
        return "high", f"{critical} issue(s) crítico(s) sin resolver"

    # High issues = medium risk if no critical
    if high > 0:
        return "medium", f"{high} issue(s) de severidad alta"

    # Medium issues = low risk if no high/critical
    if medium > 0:
        return "low", f"{medium} issue(s) de severidad media (aceptables)"

    # Low issues only = low risk
    if low > 0:
        return "low", f"{low} issue(s) de severidad baja (informativos)"

    # Zero issues = low risk
    return "low", "0 issues detectados — HTML pasa validación"


def decide_approval(risk: str) -> tuple[str, str]:
    """
    Decide approval action based on risk.
    Returns (decision, reason)
    """
    if risk == "low":
        return "approve", "Riesgo bajo: HTML aprobado para producción"
    elif risk == "medium":
        return "human_review", "Riesgo medio: requiere revisión humana antes de producción"
    else:  # high
        return "block", "Riesgo alto: bloqueado para producción, requiere corrección obligatoria"


def main():
    import argparse

    parser = argparse.ArgumentParser(description="FASE 7 Approval Script")
    parser.add_argument("diagnostic", help="Path to diagnostic.json (post-corrección)")
    parser.add_argument("--html", help="Path to HTML file (for record)")
    parser.add_argument("--run-id", required=True, help="Unique run identifier")
    parser.add_argument("--output", default="approval-record.json", help="Output approval record")
    args = parser.parse_args()

    diagnostic_path = Path(args.diagnostic)
    if not diagnostic_path.exists():
        print(f"❌ Diagnostic not found: {diagnostic_path}", file=sys.stderr)
        return 1

    diagnostic = load_diagnostic(diagnostic_path)

    print(f"✅ Approval Script: {args.run_id}")
    print(f"   Diagnostic: {diagnostic_path}")
    if args.html:
        print(f"   HTML: {args.html}")

    # Assess risk
    risk, risk_reason = assess_risk(diagnostic)
    decision, decision_reason = decide_approval(risk)

    print(f"   Risk: {risk.upper()} — {risk_reason}")
    print(f"   Decision: {decision.upper()} — {decision_reason}")

    # Build approval record
    record = {
        "run_id": args.run_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "diagnostic_analyzed": str(diagnostic_path),
        "html_analyzed": args.html,
        "risk_assessment": {
            "level": risk,
            "reason": risk_reason,
            "summary": diagnostic.get("summary", {}),
        },
        "decision": decision,
        "decision_reason": decision_reason,
        "critic_isolation_verified": diagnostic.get("critic_isolation_verified", False),
    }

    # Write approval record
    output_path = Path(args.output).resolve()
    output_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"✅ Registro de aprobación: {output_path}")
    print(f"   Decision: {decision.upper()}")

    # Exit codes for CI/CD integration
    if decision == "approve":
        return 0
    elif decision == "human_review":
        return 2  # Warning but not failure
    else:  # block
        return 1


if __name__ == "__main__":
    sys.exit(main())