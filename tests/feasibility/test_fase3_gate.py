"""
Integración FASE 2 -> FASE 3: el productor bloquea lo que el verificador rechaza.

Cadena completa:
  brief  --generate-feasibility-report.py-->  feasibility-report.json   (exit 2 si hay red)
  design-decisions.json --verify-feasibility-refs.py-->  exit 1 si alguna
  decisión referencia una decisión red o inexistente.

El test no simula nada: ejecuta los dos scripts reales por subprocess.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "skills" / "production" / "feasibility" / "scripts" / "generate-feasibility-report.py"
VERIFIER = ROOT / "skills" / "production" / "feasibility" / "scripts" / "verify-feasibility-refs.py"
SCHEMA = ROOT / "templates" / "design-decision-schema.json"


def _decision(decision_id: str, feasibility_ref: str) -> dict:
    return {
        "specialist": "layout",
        "category": "layout",
        "owner": "art-director",
        "decision_id": decision_id,
        "decision": f"Decisión {decision_id}: implementar el hero con grid asimétrico",
        "rationale": "El brief pide composición asimétrica en el hero",
        "constraints": ["Elementor 3.24"],
        "feasibility_ref": feasibility_ref,
        "validation_required": ["responsive", "layout"],
        "human_review_required": False,
    }


def _generate(tmp: Path, brief: dict) -> tuple[int, dict]:
    brief_path = tmp / "brief.json"
    brief_path.write_text(json.dumps(brief), encoding="utf-8")
    out = tmp / "feasibility-report.json"
    res = subprocess.run([sys.executable, str(GENERATOR), str(brief_path),
                          "--platform", "elementor", "-o", str(out)],
                         capture_output=True, text=True)
    return res.returncode, json.loads(out.read_text(encoding="utf-8"))


def _verify(tmp: Path, decisions: list[dict], report_path: Path) -> tuple[int, str]:
    dp = tmp / "design-decisions.json"
    dp.write_text(json.dumps(decisions), encoding="utf-8")
    res = subprocess.run([sys.executable, str(VERIFIER), str(report_path), str(dp),
                          "--schema", str(SCHEMA)], capture_output=True, text=True)
    return res.returncode, res.stdout + res.stderr


BRIEF_RED = {
    "project": "gate-e2e",
    "constraints": ["Sin CSS custom permitido", "Sin plugins adicionales"],
    "requirements": [{"id": "req-001", "description": "Hero con grid asimétrico masonry"}],
}


def test_red_decision_is_blocked_by_both_stages(tmp_path):
    code, report = _generate(tmp_path, BRIEF_RED)
    assert code == 2, "el productor debe devolver 2 con una decisión red"
    assert report["overall_feasibility"] == "blocked"
    assert report["decisions_evaluated"][0]["classification"] == "red"

    vcode, out = _verify(tmp_path, [_decision("dec-layout-001", "req-001")],
                         tmp_path / "feasibility-report.json")
    assert vcode == 1, out
    assert "red" in out


def test_green_decision_passes_both_stages(tmp_path):
    brief = {"project": "gate-e2e-ok",
             "requirements": [{"id": "req-001", "description": "Layout con Flexbox Containers"}]}
    code, report = _generate(tmp_path, brief)
    assert code == 0, report
    assert report["overall_feasibility"] == "pass"
    assert report["decisions_evaluated"][0]["classification"] == "green"

    vcode, out = _verify(tmp_path, [_decision("dec-layout-001", "req-001")],
                         tmp_path / "feasibility-report.json")
    assert vcode == 0, out


def test_yellow_decision_passes_but_is_conditional(tmp_path):
    """Yellow con workaround documentado: no bloquea, el report queda conditional."""
    brief = {"project": "gate-e2e-yellow",
             "requirements": [{"id": "req-001", "description": "Masonry en el hero"}]}
    code, report = _generate(tmp_path, brief)
    assert code == 0, report
    assert report["overall_feasibility"] == "conditional"
    d = report["decisions_evaluated"][0]
    assert d["classification"] == "yellow"
    assert d["workaround"], "un yellow sin workaround no es un yellow"

    vcode, out = _verify(tmp_path, [_decision("dec-layout-001", "req-001")],
                         tmp_path / "feasibility-report.json")
    assert vcode == 0, out


def test_unknown_ref_fails(tmp_path):
    """Referenciar una decisión que no está en el report también falla."""
    brief = {"project": "gate-e2e-unknown",
             "requirements": [{"id": "req-001", "description": "Flexbox Containers"}]}
    _generate(tmp_path, brief)
    vcode, out = _verify(tmp_path, [_decision("dec-layout-002", "req-999")],
                         tmp_path / "feasibility-report.json")
    assert vcode == 1, out
    assert "req-999" in out
