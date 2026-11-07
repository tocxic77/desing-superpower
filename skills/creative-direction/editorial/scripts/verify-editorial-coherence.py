#!/usr/bin/env python3
"""
verify-editorial-coherence.py

Validación de coherencia cross-layer para decisiones de editorial.

Verifica:
  0. Semántica de propiedad: specialist (productor de dominio), category, owner (aprobador).
  1. Cada decisión editorial tiene feasibility_ref no vacío.
  2. Jerarquía referencia typography_scale y cta_hierarchy existentes.
  3. Zonas de branding coherentes con brand_status (complete/incomplete/missing).
  4. Densidad coherente con arquetipo (provisional si branding no aprobado).
  5. Sistema unificado referencia las decisiones previas que existen.
  6-9. Retícula, ritmo vertical, section library y responsive referencian decisions válidas.
  10-12. Naming del output, meta.provisional_decisions y conteo de human_review_required.
  13. evidence_refs apuntan a anclas que EXISTEN en el archivo de referencias.
  14. Las decisiones referenciadas (color/typography/branding) son válidas: dominio correcto,
      owner presente y feasibility_ref green/yellow si se entrega el feasibility-report.

Uso:
    python verify-editorial-coherence.py <editorial.json> <design-decisions.json> <brand-identity.json> [feasibility-report.json]

`design-decisions.json` puede ser un array (formato canónico FASE 3) o {"decisions": [...]}.

Exit codes:
    0 = PASS (todas las verificaciones pasan)
    1 = FAIL (errores críticos)

Versión: 0.2.0 (2026-11-07) — schema canónico v0.2
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

DOMAIN_SPECIALISTS = {
    "color", "typography", "branding", "editorial",
    "layout", "interaction", "conversion",
}
PHASE_AGENTS = {
    "feasibility", "ux-designer", "web-builder",
    "design-critic", "sales-specialist", "orchestrator",
}
VALID_SPECIALISTS = DOMAIN_SPECIALISTS | PHASE_AGENTS

# Dominio esperado de las decisiones previas referenciadas
EXPECTED_DOMAIN = {"dec-color-": "color", "dec-typography-": "typography", "dec-brand-": "branding"}


def load_json(path: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def get_decisions_by_id(decisions_data: Any) -> Dict[str, Dict[str, Any]]:
    """Indexar decisiones por decision_id. Acepta array canónico o envoltorio {"decisions": [...]}."""
    if isinstance(decisions_data, list):
        decisions = decisions_data
    elif isinstance(decisions_data, dict):
        decisions = decisions_data.get("decisions", [])
    else:
        decisions = []
    if not isinstance(decisions, list):
        return {}
    return {d.get("decision_id"): d for d in decisions if isinstance(d, dict) and d.get("decision_id")}


def expected_domain(decision_id: str) -> Optional[str]:
    for prefix, domain in EXPECTED_DOMAIN.items():
        if decision_id.startswith(prefix):
            return domain
    return None


def verify_editorial_coherence(
    editorial_path: str,
    decisions_path: str,
    brand_path: str,
    feasibility_path: Optional[str] = None,
) -> List[str]:
    editorial = load_json(editorial_path)
    decisions = load_json(decisions_path)
    brand = load_json(brand_path)
    feasibility = load_json(feasibility_path) if feasibility_path else None

    brand_status = (brand.get("meta") or {}).get("manual_status", "unknown")
    editorial_decisions = get_decisions_by_id(editorial)
    prior_decisions = get_decisions_by_id(decisions)

    errors: List[str] = []
    warnings: List[str] = []

    valid_feas_ids: Set[str] = set()
    if feasibility:
        for entry in feasibility.get("decisions_evaluated", []):
            if entry.get("classification") != "red":
                valid_feas_ids.add(entry.get("decision_id"))

    # Regla 0: semántica de propiedad (specialist / category / owner)
    for dec_id, dec in editorial_decisions.items():
        specialist = dec.get("specialist")
        category = dec.get("category")
        owner = dec.get("owner")

        if not specialist:
            errors.append(f"{dec_id}: missing specialist (productor de la decisión)")
        elif specialist == "art-director":
            errors.append(f"{dec_id}: specialist='art-director' — el aprobador va en owner, no en specialist")
        elif specialist not in VALID_SPECIALISTS:
            errors.append(f"{dec_id}: specialist '{specialist}' no es un productor válido")
        elif specialist not in DOMAIN_SPECIALISTS:
            warnings.append(f"{dec_id}: specialist '{specialist}' es un agente de fase, no un especialista de dominio")

        if not category:
            errors.append(f"{dec_id}: missing category (dominio de la decisión)")
        elif category != "editorial":
            warnings.append(f"{dec_id}: category '{category}' != 'editorial' en un output del skill editorial")

        if not isinstance(owner, str) or not owner.strip():
            errors.append(f"{dec_id}: missing owner (rol accountable que aprueba)")

    # Regla 1: feasibility_ref presente
    for dec_id, dec in editorial_decisions.items():
        feas_ref = dec.get("feasibility_ref")
        if not feas_ref:
            errors.append(f"{dec_id}: missing feasibility_ref")
        elif not isinstance(feas_ref, str) or not feas_ref.strip():
            errors.append(f"{dec_id}: feasibility_ref empty or invalid")
        elif feasibility is not None and feas_ref not in valid_feas_ids:
            errors.append(f"{dec_id}: feasibility_ref '{feas_ref}' no existe o es 'red' en feasibility-report")

    # Regla 2: jerarquía referencia typography_scale + cta_hierarchy
    hier = editorial_decisions.get("dec-editorial-002")
    if hier:
        refs = hier.get("references", {})
        if "typography_scale" not in refs:
            errors.append("dec-editorial-002: missing typography_scale in references")
        elif refs["typography_scale"] not in prior_decisions:
            errors.append(f"dec-editorial-002: typography_scale references unknown decision: {refs['typography_scale']}")

        if "cta_hierarchy" not in refs:
            errors.append("dec-editorial-002: missing cta_hierarchy in references")
        elif refs["cta_hierarchy"] not in prior_decisions:
            errors.append(f"dec-editorial-002: cta_hierarchy references unknown decision: {refs['cta_hierarchy']}")

    # Reglas 3 y 4: branding zones y densidad vs brand_status
    for dec_id, brand_field in (("dec-editorial-004", "dec-brand-007"), ("dec-editorial-006", "dec-brand-001")):
        dec = editorial_decisions.get(dec_id)
        if not dec:
            continue
        hr = dec.get("human_review_required", False)
        provisional = dec.get("provisional", False)

        if brand_status == "complete":
            if hr:
                errors.append(f"{dec_id}: brand complete but human_review_required=true")
            if provisional:
                errors.append(f"{dec_id}: brand complete but provisional=true")
        elif brand_status in ("incomplete", "missing"):
            if not hr:
                errors.append(f"{dec_id}: brand {brand_status} but human_review_required=false")
            if not provisional:
                errors.append(f"{dec_id}: brand {brand_status} but provisional=false")
            if brand_field not in (dec.get("depends_on") or []):
                warnings.append(f"{dec_id}: brand {brand_status} but doesn't depend_on {brand_field}")

    # Regla 5: sistema unificado referencia decisiones previas existentes
    unified = editorial_decisions.get("dec-editorial-001")
    if unified:
        refs = unified.get("references", {})
        expected_color = [f"dec-color-{i:03d}" for i in range(1, 7)]
        expected_typo = [f"dec-typography-{i:03d}" for i in range(1, 9)]
        expected_brand = [f"dec-brand-{i:03d}" for i in range(1, 9)]

        for cat, expected in (
            ("color_decisions", expected_color),
            ("typography_decisions", expected_typo),
            ("branding_decisions", expected_brand),
        ):
            actual = refs.get(cat, [])
            missing = [e for e in expected if e in prior_decisions and e not in actual]
            if missing:
                warnings.append(f"dec-editorial-001: missing references in {cat}: {missing}")
            unknown = [e for e in actual if e not in prior_decisions]
            if unknown:
                errors.append(f"dec-editorial-001: {cat} references decisions inexistentes: {unknown}")

    # Regla 6/9: retícula y responsive con feasibility_ref
    for dec_id in ("dec-editorial-003", "dec-editorial-008"):
        dec = editorial_decisions.get(dec_id)
        if dec and not dec.get("feasibility_ref"):
            errors.append(f"{dec_id}: missing feasibility_ref")

    # Regla 7: ritmo vertical referencia typography line-height
    rhythm = editorial_decisions.get("dec-editorial-005")
    if rhythm:
        refs = rhythm.get("references", {})
        if "typography_line_height" not in refs:
            warnings.append("dec-editorial-005: missing typography_line_height reference (expected for baseline alignment)")
        elif refs["typography_line_height"] not in prior_decisions:
            warnings.append(f"dec-editorial-005: typography_line_height references unknown: {refs['typography_line_height']}")

    # Regla 8: section library valida coherencia con CTA + typography
    sections = editorial_decisions.get("dec-editorial-007")
    if sections:
        refs = sections.get("references", {})
        if "cta_hierarchy" not in refs:
            warnings.append("dec-editorial-007: missing cta_hierarchy reference for CTA variant mapping")
        if "typography_scale" not in refs:
            warnings.append("dec-editorial-007: missing typography_scale reference for heading levels")

    # Regla 10: naming del output coherente con brand_status
    meta = editorial.get("meta", {})
    output_file = meta.get("output_file", "")
    if brand_status == "complete":
        if "draft-" in output_file:
            warnings.append(f"meta.output_file: brand complete but file named draft: {output_file}")
    elif brand_status in ("incomplete", "missing"):
        if "draft-" not in output_file and output_file:
            warnings.append(f"meta.output_file: brand {brand_status} but file not named draft: {output_file}")

    # Regla 11: meta.provisional_decisions coincide con provisional=true
    provisional_in_meta = set(meta.get("provisional_decisions", []))
    provisional_actual = {k for k, v in editorial_decisions.items() if v.get("provisional") is True}
    if provisional_in_meta != provisional_actual:
        missing_in_meta = provisional_actual - provisional_in_meta
        extra_in_meta = provisional_in_meta - provisional_actual
        if missing_in_meta:
            warnings.append(f"meta.provisional_decisions missing: {missing_in_meta}")
        if extra_in_meta:
            warnings.append(f"meta.provisional_decisions extra (not provisional): {extra_in_meta}")

    # Regla 12: meta.human_review_required_count
    hr_count_meta = meta.get("human_review_required_count", 0)
    hr_count_actual = sum(1 for v in editorial_decisions.values() if v.get("human_review_required") is True)
    if hr_count_meta != hr_count_actual:
        warnings.append(f"meta.human_review_required_count: {hr_count_meta} != actual {hr_count_actual}")

    # Regla 13: evidence_refs → ancla existente
    for dec_id, dec in editorial_decisions.items():
        for ref in dec.get("evidence_refs") or []:
            if "#" not in ref:
                warnings.append(f"{dec_id}: evidence_ref sin ancla: {ref}")
                continue
            file_part, anchor = ref.split("#", 1)
            candidates = [Path(file_part)]
            if not Path(file_part).is_absolute():
                candidates.append(Path(editorial_path).parent / file_part)
            evidence_file = next((c for c in candidates if c.exists()), None)
            if evidence_file is None:
                errors.append(f"{dec_id}: evidence_ref apunta a archivo inexistente: {file_part}")
                continue
            headings = set()
            for line in evidence_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("#"):
                    headings.add(line.lstrip("#").strip())
            if anchor not in headings:
                errors.append(f"{dec_id}: evidence_ref ancla inexistente en {file_part}: #{anchor}")

    # Regla 14: decisiones previas referenciadas son válidas (dominio + owner + feasibility)
    referenced: Set[str] = set()
    for dec in editorial_decisions.values():
        for value in (dec.get("references") or {}).values():
            if isinstance(value, str):
                referenced.add(value)
            elif isinstance(value, list):
                referenced.update(v for v in value if isinstance(v, str))
        referenced.update(d for d in (dec.get("depends_on") or []) if isinstance(d, str))

    for ref_id in sorted(referenced):
        target = prior_decisions.get(ref_id) or editorial_decisions.get(ref_id)
        if target is None:
            errors.append(f"reference a decisión inexistente: {ref_id}")
            continue
        if ref_id in editorial_decisions:
            continue  # referencia intra-documento: ya validada en reglas 0-12
        dom = expected_domain(ref_id)
        if dom and target.get("specialist") != dom:
            errors.append(f"{ref_id}: specialist '{target.get('specialist')}' != dominio esperado '{dom}'")
        if not str(target.get("owner") or "").strip():
            errors.append(f"{ref_id}: decisión referenciada sin owner (no accountable)")
        if feasibility is not None:
            feas_ref = target.get("feasibility_ref")
            if not feas_ref or feas_ref not in valid_feas_ids:
                errors.append(f"{ref_id}: feasibility_ref '{feas_ref}' ausente o 'red' en feasibility-report")

    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    return errors


def main():
    if len(sys.argv) < 4:
        print(
            "Usage: python verify-editorial-coherence.py "
            "<editorial.json> <design-decisions.json> <brand-identity.json> [feasibility-report.json]",
            file=sys.stderr,
        )
        sys.exit(1)

    editorial_file, decisions_file, brand_file = sys.argv[1:4]
    feasibility_file = sys.argv[4] if len(sys.argv) > 4 else None

    errors = verify_editorial_coherence(editorial_file, decisions_file, brand_file, feasibility_file)

    if errors:
        print("VERIFICATION FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    brand_status = (load_json(brand_file).get("meta") or {}).get("manual_status", "unknown")
    dec_count = len(get_decisions_by_id(load_json(editorial_file)))

    print("VERIFICATION PASSED")
    print(f"  Brand status: {brand_status}")
    print(f"  Editorial decisions: {dec_count}")
    print("  Schema: design-decision-schema.json (v0.2, canónico)")
    sys.exit(0)


if __name__ == "__main__":
    main()
