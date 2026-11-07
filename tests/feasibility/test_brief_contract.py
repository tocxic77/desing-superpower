"""
Contrato de entrada del productor de FASE 2.

Dos defectos que estos tests impiden que vuelvan:
  1. Un brief vacío o con forma desconocida producía `overall: pass` con 0 decisiones
     (un report vacío no es un pass).
  2. El productor sólo entendía `requirements`; el brief canónico del repo usa
     `brief.mandatories` y `brief.constraints.platforms`.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "skills" / "production" / "feasibility" / "scripts" / "generate-feasibility-report.py"


def _run(tmp: Path, brief: dict, extra: list[str] | None = None) -> tuple[int, str, dict | None]:
    bp = tmp / "brief.json"
    bp.write_text(json.dumps(brief), encoding="utf-8")
    out = tmp / "r.json"
    cmd = [sys.executable, str(GENERATOR), str(bp), "-o", str(out)] + (extra or [])
    res = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
    return res.returncode, res.stdout + res.stderr, data


def test_canonical_brief_shape_is_understood(tmp_path):
    """brief.mandatories + brief.constraints.platforms (templates/brief-schema.json)."""
    brief = {
        "project_id": "canon-001",
        "brief": {
            "business_goal": "x",
            "mandatories": ["Hero section", "CTA principal"],
            "constraints": {"platforms": ["elementor", "figma"]},
        },
    }
    code, out, report = _run(tmp_path, brief)
    assert code in (0, 2), out
    ids = [d["decision_id"] for d in report["decisions_evaluated"]]
    assert ids == ["mand-001", "mand-002"], ids
    assert report["platform"] == "both"


def test_single_declared_platform_is_respected(tmp_path):
    brief = {"project_id": "canon-002",
             "brief": {"mandatories": ["Flexbox Containers"],
                       "constraints": {"platforms": ["elementor"]}}}
    code, out, report = _run(tmp_path, brief)
    assert code == 0, out
    assert report["platform"] == "elementor"
    assert report["decisions_evaluated"][0]["per_platform"] == {"elementor": "green"}


def test_empty_brief_fails_instead_of_passing(tmp_path):
    """0 decisiones evaluadas no puede ser 'pass'."""
    code, out, report = _run(tmp_path, {"project_id": "empty"})
    assert code == 1, out
    assert report is None
    assert "decisiones evaluables" in out


def test_red_decisions_have_no_workaround(tmp_path):
    """Un red está bloqueado: publicar un workaround al lado es contradictorio."""
    brief = {"project_id": "red-wa",
             "brief": {"mandatories": ["Hero con grid asimétrico masonry"],
                       "constraints": {"platforms": ["elementor", "figma"]},
                       "constraints_extra": ["sin CSS custom"]}}
    brief["constraints"] = ["sin CSS custom"]
    code, out, report = _run(tmp_path, brief)
    assert code == 2, out
    for d in report["decisions_evaluated"]:
        if d["classification"] == "red":
            assert d["workaround"] is None, d
            assert d["blocking_reason"]
