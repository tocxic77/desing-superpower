"""
Tests de contrast_analyzer: issue_id determinista y contrato con diagnostic-schema.json.

El bug original usaba hash(), que está salteado por PYTHONHASHSEED: dos corridas
idénticas del mismo run_id+element producían issue_id distinto.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "templates" / "diagnostic-schema.json"
MODULE = "tools.validators.contrast_analyzer"

TOKENS = {
    "semantic": {
        "text": {"primary": "#6B7280"},
        "background": {"primary": "#FFFFFF"},
        "cta": {"primary_bg": "#2563EB"},
    }
}


def _diag(run_id="2026-11-07_acme-landing_01", element=".hero__subtitle"):
    sys.path.insert(0, str(ROOT))
    from tools.validators.contrast_analyzer import make_diagnostic

    return make_diagnostic(
        run_id=run_id,
        element=element,
        fg_hex="#6B7280",
        bg_hex="#FFFFFF",
        ratio=3.0,
        required_ratio=4.5,
        tokens=TOKENS,
        scope="hero-section",
    )


def test_issue_id_matches_schema_pattern():
    diag = _diag()
    assert diag.issue_id.startswith("A11Y-")
    assert len(diag.issue_id) == 8 and diag.issue_id[5:].isdigit()


def test_issue_id_stable_within_process():
    assert _diag().issue_id == _diag().issue_id


@pytest.mark.parametrize("seed_a,seed_b", [("0", "1"), ("12345", "99999")])
def test_issue_id_stable_across_processes(seed_a, seed_b):
    """Dos procesos con PYTHONHASHSEED distinto deben coincidir."""
    code = (
        "import json,sys;"
        f"sys.path.insert(0, {str(ROOT)!r});"
        "from tools.validators.contrast_analyzer import make_diagnostic;"
        "d=make_diagnostic(run_id='2026-11-07_acme-landing_01',element='.hero__subtitle',"
        "fg_hex='#6B7280',bg_hex='#FFFFFF',ratio=3.0,required_ratio=4.5,"
        "tokens={'semantic':{}},scope='hero-section');"
        "print(d.issue_id)"
    )
    out = []
    for seed in (seed_a, seed_b):
        env = {**os.environ, "PYTHONHASHSEED": seed}
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, cwd=ROOT)
        assert r.returncode == 0, r.stderr
        out.append(r.stdout.strip())
    assert out[0] == out[1], f"issue_id no determinista entre procesos: {out}"


def test_issue_id_differs_per_element():
    assert _diag(element=".hero__subtitle").issue_id != _diag(element=".cta__label").issue_id


def test_diagnostic_validates_against_schema():
    import jsonschema

    diag = _diag().to_dict() if hasattr(_diag(), "to_dict") else json.loads(json.dumps(_diag(), default=lambda o: o.__dict__))
    validator = jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    errors = [f"{'/'.join(map(str, e.path))}: {e.message}" for e in validator.iter_errors(diag)]
    assert not errors, errors
