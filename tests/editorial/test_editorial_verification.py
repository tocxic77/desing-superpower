"""
Tests de verificación del skill editorial (schema v0.2 canónico).

Cubre:
  - validación del schema v0.2 sobre decisions y outputs editoriales
  - coherencia cross-layer en los tres estados de branding
  - fallos esperados: ancla rota, specialist=art-director, dominio cruzado, feasibility red,
    branding no aprobado con output no provisional
  - forma v0.2 en el verificador de feasibility

Ejecutar: pytest tests/editorial -q
"""


import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "templates" / "design-decision-schema.json"
VERIFY_CROSS = ROOT / "skills" / "creative-direction" / "editorial" / "scripts" / "verify-editorial-coherence.py"
VERIFY_FEAS = ROOT / "skills" / "production" / "feasibility" / "scripts" / "verify-feasibility-refs.py"
FIXTURES = Path(__file__).parent / "fixtures"

sys.path.insert(0, str(Path(__file__).parent))
import build_fixtures  # noqa: E402

BRAND = {k: FIXTURES / f"brand-identity-{k}.json" for k in ("complete", "incomplete", "missing")}


def run(script: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True)


@pytest.fixture(scope="module")
def paths(tmp_path_factory) -> dict:
    out = tmp_path_factory.mktemp("editorial-fixtures")
    built = {k: v for k, v in build_fixtures.build(out).items()}
    return built


def decisions_of(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data["decisions"]


def test_schema_v02_accepts_all_outputs(paths):
    import jsonschema

    validator = jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    for key in ("decisions", "complete", "draft"):
        for dec in decisions_of(paths[key]):
            errors = list(validator.iter_errors(dec))
            assert not errors, f"{key}/{dec['decision_id']}: {[e.message for e in errors]}"


@pytest.mark.parametrize("editorial_key,brand_key", [("complete", "complete"), ("draft", "incomplete"), ("draft", "missing")])
def test_cross_layer_passes(paths, editorial_key, brand_key):
    r = run(VERIFY_CROSS, paths[editorial_key], paths["decisions"], BRAND[brand_key], paths["feasibility"])
    assert r.returncode == 0, r.stderr
    assert "VERIFICATION PASSED" in r.stdout


def test_fails_when_brand_complete_but_draft(paths):
    r = run(VERIFY_CROSS, paths["draft"], paths["decisions"], BRAND["complete"], paths["feasibility"])
    assert r.returncode == 1
    assert "brand complete but provisional=true" in r.stderr


def test_fails_when_brand_incomplete_but_not_provisional(paths):
    r = run(VERIFY_CROSS, paths["complete"], paths["decisions"], BRAND["incomplete"], paths["feasibility"])
    assert r.returncode == 1
    assert "human_review_required=false" in r.stderr


def test_fails_on_broken_evidence_anchor(paths, tmp_path):
    data = json.loads(paths["complete"].read_text(encoding="utf-8"))
    data["decisions"][0]["evidence_refs"] = [
        "skills/creative-direction/editorial/references/editorial-evidence.md#spool-patterns"
    ]
    broken = tmp_path / "broken-anchor.json"
    broken.write_text(json.dumps(data), encoding="utf-8")
    r = run(VERIFY_CROSS, broken, paths["decisions"], BRAND["complete"], paths["feasibility"])
    assert r.returncode == 1
    assert "ancla inexistente" in r.stderr


def test_fails_when_specialist_is_art_director(paths, tmp_path):
    data = json.loads(paths["complete"].read_text(encoding="utf-8"))
    data["decisions"][1]["specialist"] = "art-director"
    bad = tmp_path / "specialist.json"
    bad.write_text(json.dumps(data), encoding="utf-8")
    r = run(VERIFY_CROSS, bad, paths["decisions"], BRAND["complete"], paths["feasibility"])
    assert r.returncode == 1
    assert "art-director" in r.stderr


def test_fails_when_prior_decision_domain_mismatches(paths, tmp_path):
    decisions = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    for dec in decisions:
        if dec["decision_id"] == "dec-typography-003":
            dec["specialist"] = "color"
    bad = tmp_path / "decisions-crossdomain.json"
    bad.write_text(json.dumps(decisions), encoding="utf-8")
    r = run(VERIFY_CROSS, paths["complete"], bad, BRAND["complete"], paths["feasibility"])
    assert r.returncode == 1
    assert "dominio esperado 'typography'" in r.stderr


def test_fails_when_feasibility_is_red(paths, tmp_path):
    feas = json.loads(paths["feasibility"].read_text(encoding="utf-8"))
    for entry in feas["decisions_evaluated"]:
        if entry["decision_id"] == "dec-editorial-005":
            entry["classification"] = "red"
    bad = tmp_path / "feasibility-red.json"
    bad.write_text(json.dumps(feas), encoding="utf-8")
    r = run(VERIFY_CROSS, paths["complete"], paths["decisions"], BRAND["complete"], bad)
    assert r.returncode == 1
    assert "no existe o es 'red'" in r.stderr


def test_feasibility_verifier_accepts_v02(paths):
    r = run(VERIFY_FEAS, paths["feasibility"], paths["decisions"], "--schema", SCHEMA)
    assert r.returncode == 0, r.stderr
    assert "22 decisiones" in r.stdout


def test_feasibility_verifier_accepts_document_form(paths):
    r = run(VERIFY_FEAS, paths["feasibility"], paths["complete"])
    assert r.returncode == 0, r.stderr


def test_feasibility_verifier_rejects_art_director_specialist(paths, tmp_path):
    decisions = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    decisions[0]["specialist"] = "art-director"
    bad = tmp_path / "decisions-ad.json"
    bad.write_text(json.dumps(decisions), encoding="utf-8")
    r = run(VERIFY_FEAS, paths["feasibility"], bad, "--schema", SCHEMA)
    assert r.returncode == 1
    assert "art-director" in r.stderr
