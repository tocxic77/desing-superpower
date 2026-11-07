#!/usr/bin/env python3
"""
Verify brand-identity.json or draft-brand-identity.json output against:
1. Each decision has human_review_required=true OR evidence_ref to brand-guidelines.md#section
2. Strategic decisions (archetype, positioning, essence, tone) have >=2 alternatives_considered
3. All decisions have feasibility_ref
4. If manual incomplete, affected decisions marked with rationale mentioning missing sections

Usage: python verify-brand-output.py <brand-file.json> <audit-file.json>

Exit code 0 = PASS, 1 = FAIL
"""

import sys, json
from pathlib import Path
from typing import Dict, List, Any


STRATEGIC_DECISION_IDS = {
    "dec-brand-001",  # archetype primary
    "dec-brand-002",  # archetype secondary
    "dec-brand-003",  # personality
    "dec-brand-004",  # tone of voice
    "dec-brand-005",  # positioning statement
    "dec-brand-006",  # brand essence / tagline
}


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR loading {path}: {e}", file=sys.stderr)
        sys.exit(1)


def verify_brand_output(brand_file: Path, audit_file: Path) -> List[str]:
    brand = load_json(brand_file)
    audit = load_json(audit_file)

    errors = []
    warnings = []

    decisions = brand.get("decisions", [])
    manual_status = brand.get("meta", {}).get("manual_status", "unknown")
    audit_missing = audit.get("missing_sections", [])
    audit_contradictions = audit.get("contradictions", [])

    for d in decisions:
        decision_id = d.get("decision_id", "unknown")

        # Regla 1: human_review_required O evidence_ref a brand-guidelines.md#seccion
        human_review = d.get("human_review_required", False)
        evidence_refs = d.get("evidence_refs", [])
        has_brand_guideline_ref = any(
            "brand-guidelines.md#" in ref for ref in evidence_refs
        )

        if not human_review and not has_brand_guideline_ref:
            errors.append(
                f"{decision_id}: NO tiene human_review_required=true NI evidence_ref a brand-guidelines.md#seccion"
            )

        # Regla 2: decisiones estratégicas → alternatives_considered >= 2
        if decision_id in STRATEGIC_DECISION_IDS:
            alternatives = d.get("alternatives_considered", [])
            if len(alternatives) < 2:
                errors.append(
                    f"{decision_id}: decisión estratégica (arquetipo/posicionamiento/esencia/tono) "
                    f"con solo {len(alternatives)} alternatives_considered (mínimo 2)"
                )

        # Regla 3: feasibility_ref obligatorio
        if not d.get("feasibility_ref"):
            errors.append(f"{decision_id}: falta feasibility_ref")

        # Regla 4: si manual incompleto, decisiones afectadas deben mencionar qué falta en rationale
        if audit_missing and human_review:
            rationale = d.get("rationale", "").lower()
            mentioned = any(missing.lower() in rationale for missing in audit_missing)
            if not mentioned and audit_missing:
                warnings.append(
                    f"{decision_id}: human_review_required=true pero rationale no menciona "
                    f"secciones faltantes del manual: {audit_missing}"
                )

        # Validar estructura de alternatives_considered
        alternatives = d.get("alternatives_considered", [])
        for i, alt in enumerate(alternatives):
            if not isinstance(alt, dict):
                warnings.append(f"{decision_id}: alternative[{i}] no es objeto")
            elif "rationale" not in alt:
                warnings.append(f"{decision_id}: alternative[{i}] sin rationale")

    # Validaciones de meta
    meta = brand.get("meta", {})
    if "manual_status" not in meta:
        warnings.append("meta.manual_status faltante (debe ser: complete|incomplete|missing)")

    if meta.get("manual_status") == "complete" and audit_missing:
        errors.append(f"meta.manual_status='complete' pero audit muestra secciones faltantes: {audit_missing}")

    if meta.get("manual_status") == "missing" and audit.get("manual_exists"):
        errors.append("meta.manual_status='missing' pero audit.manual_exists=true")

    # Output
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  - {w}")

    return errors


def main():
    if len(sys.argv) < 3:
        print("Usage: python verify-brand-output.py <brand-identity.json> <audit-brand-guidelines.json>", file=sys.stderr)
        sys.exit(1)

    brand_file = Path(sys.argv[1])
    audit_file = Path(sys.argv[2])

    if not brand_file.exists():
        print(f"ERROR: {brand_file} no existe", file=sys.stderr)
        sys.exit(1)
    if not audit_file.exists():
        print(f"ERROR: {audit_file} no existe", file=sys.stderr)
        sys.exit(1)

    errors = verify_brand_output(brand_file, audit_file)

    if errors:
        print("VERIFICATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # Success summary
    brand = load_json(brand_file)
    decisions = brand.get("decisions", [])
    human_review_count = sum(1 for d in decisions if d.get("human_review_required"))

    print("VERIFICATION PASSED")
    print(f"  Decisions: {len(decisions)}")
    print(f"  Human review required: {human_review_count}")
    print(f"  Manual status: {brand.get('meta', {}).get('manual_status', 'unknown')}")
    sys.exit(0)


if __name__ == "__main__":
    main()