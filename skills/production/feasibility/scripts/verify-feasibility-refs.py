#!/usr/bin/env python3
"""
verify-feasibility-refs.py

Implementación canónica (sin dependencia de jq) de la verificación de FASE 3:
cada decisión de `design-decisions.json` debe tener `feasibility_ref` válido
(green/yellow) y cumplir la forma del schema v0.2.

Uso:
    python verify-feasibility-refs.py <feasibility-report.json> <design-decisions.json> [--schema PATH]

Acepta `design-decisions.json` como array (canónico) o como {"decisions": [...]}.

Exit codes:
    0 = PASS
    1 = FAIL (devolver a FASE 2 si es por feasibility; a FASE 3.2 si es por forma)
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REQUIRED_V2 = ("specialist", "category", "owner", "constraints", "feasibility_ref",
               "decision", "rationale", "validation_required", "human_review_required")


def load(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def as_decisions(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("decisions"), list):
        return data["decisions"]
    return []


def main() -> int:
    if len(sys.argv) < 3:
        print("Uso: python verify-feasibility-refs.py <feasibility-report.json> <design-decisions.json> [--schema PATH]",
              file=sys.stderr)
        return 1

    feas_path, decisions_path = sys.argv[1], sys.argv[2]
    schema_path = None
    if "--schema" in sys.argv:
        schema_path = sys.argv[sys.argv.index("--schema") + 1]

    feas = load(feas_path)
    decisions = as_decisions(load(decisions_path))

    if not decisions:
        print("❌ design-decisions.json no contiene decisiones (¿envoltorio inesperado?)", file=sys.stderr)
        return 1

    valid_refs = {
        d.get("decision_id"): d.get("classification")
        for d in feas.get("decisions_evaluated", [])
        if d.get("classification") in ("green", "yellow")
    }

    errors: List[str] = []

    for dec in decisions:
        dec_id = dec.get("decision_id", "<sin id>")

        for field in REQUIRED_V2:
            if field not in dec or dec[field] in (None, "", []):
                errors.append(f"{dec_id}: falta campo requerido v0.2 '{field}'")

        if dec.get("specialist") == "art-director":
            errors.append(f"{dec_id}: specialist='art-director' (productor en specialist, aprobador en owner)")

        feas_ref = dec.get("feasibility_ref")
        if not feas_ref:
            errors.append(f"{dec_id}: missing feasibility_ref")
        elif feas_ref not in valid_refs:
            errors.append(f"{dec_id}: feasibility_ref '{feas_ref}' no existe o es 'red' en feasibility-report")

    if schema_path:
        try:
            import jsonschema
        except ImportError:
            print("⚠️ jsonschema no instalado: se omite validación de schema", file=sys.stderr)
        else:
            schema = load(schema_path)
            validator = jsonschema.Draft202012Validator(schema)
            for dec in decisions:
                for err in validator.iter_errors(dec):
                    path = ".".join(str(p) for p in err.path) or "<root>"
                    errors.append(f"{dec.get('decision_id')}: schema {path}: {err.message}")

    req_count = len(feas.get("requirements", []) or [])
    eval_count = len(feas.get("decisions_evaluated", []) or [])
    if eval_count < req_count:
        print(f"⚠️ ADVERTENCIA: feasibility-report evalúa {eval_count} decisiones pero el brief tiene {req_count} requisitos",
              file=sys.stderr)

    if errors:
        print("❌ VERIFICACIÓN FALLÓ:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"✅ VERIFICACIÓN PASÓ: {len(decisions)} decisiones con feasibility_ref válido (green/yellow) y forma v0.2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
