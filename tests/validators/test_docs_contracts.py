"""
Contratos de documentación: el ejemplo de diagnóstico debe validar contra el schema
y las anclas citadas deben existir de verdad.

Motivo histórico: `design-loop.md` mostraba un diagnóstico con campos que el schema
rechaza (`additionalProperties: false`) y las `evidence_refs` apuntaban a encabezados
que no existían (o que sólo aparecían dentro de un bloque de código de ejemplo).
"""

# anchor-check: ignore — las refs rotas de este archivo son fixtures del propio test

import json
import re
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".hermes" / "workflows" / "design-loop.md"
SCHEMA = ROOT / "templates" / "diagnostic-schema.json"
ANCHORS_TOOL = ROOT / "tools" / "validators" / "verify_evidence_anchors.py"


def _example_diagnostic() -> dict:
    text = WORKFLOW.read_text(encoding="utf-8")
    idx = text.index("## Diagnostic Schema")
    block = re.search(r"```json\n(.*?)```", text[idx:], re.S)
    assert block, "el workflow no tiene bloque json de diagnóstico"
    return json.loads(block.group(1))


def test_design_loop_example_validates_against_schema():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = [f"{'/'.join(map(str, e.path))}: {e.message}" for e in validator.iter_errors(_example_diagnostic())]
    assert not errors, errors


def test_design_loop_example_has_no_rejected_fields():
    rejected = {"cycle", "selector", "unit", "affects_tokens", "token_references"}
    assert not rejected & set(_example_diagnostic()), "el ejemplo sigue mostrando campos rechazados"


def test_repo_has_no_broken_evidence_anchors():
    result = subprocess.run([sys.executable, str(ANCHORS_TOOL), "--root", str(ROOT)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_anchor_tool_detects_fenced_pseudo_heading(tmp_path):
    (tmp_path / "ev").mkdir()
    (tmp_path / "ev" / "proof-evidence.md").write_text(
        "# Evidencia\n\n### real-anchor\n**Tipo**: THEORY\n\n"
        "```markdown\n### fake-anchor\n```\n",
        encoding="utf-8",
    )
    (tmp_path / "doc.md").write_text(
        "ver ev/proof-evidence.md#real-anchor\n", encoding="utf-8")
    ok = subprocess.run([sys.executable, str(ANCHORS_TOOL), "--root", str(tmp_path)],
                        capture_output=True, text=True)
    assert ok.returncode == 0, ok.stdout + ok.stderr

    # Un encabezado dentro de un bloque de código no es ancla
    (tmp_path / "doc.md").write_text(
        "ver ev/proof-evidence.md#fake-anchor\n", encoding="utf-8")
    bad = subprocess.run([sys.executable, str(ANCHORS_TOOL), "--root", str(tmp_path)],
                         capture_output=True, text=True)
    assert bad.returncode == 1
    assert "fake-anchor" in bad.stderr
