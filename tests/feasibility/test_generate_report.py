"""
Tests del productor de FASE 2 (`generate-feasibility-report.py`).

El punto crítico: la clasificación no puede derivar del markdown sin que nadie lo note.
`test_every_md_row_classifies_as_documented` toma el ejemplo de decisión que cada fila
de platform-constraints.md declara y exige que el clasificador devuelva la misma clase.
Si alguien añade una capacidad al markdown sin sinónimos, o cambia una clase, esto falla.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "production" / "feasibility" / "scripts" / "generate-feasibility-report.py"
MD = ROOT / "skills" / "production" / "feasibility" / "references" / "platform-constraints.md"
FIXTURES = Path(__file__).parent / "fixtures"

sys.path.insert(0, str(SCRIPT.parent))
import importlib.util

spec = importlib.util.spec_from_file_location("gen_feasibility", SCRIPT)
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

ROWS = gen.parse_constraints(MD)
RANK = {"green": 0, "yellow": 1, "red": 2}


def _classify(decision_text: str, platform: str) -> str:
    return gen.classify(ROWS, decision_text, platform, css_prohibited=False)["classification"]


def test_md_parses_both_platforms():
    platforms = {r["platform"] for r in ROWS}
    assert platforms == {"elementor", "figma"}, platforms
    classes = {r["classification"] for r in ROWS}
    assert classes == {"green", "yellow", "red"}, classes
    assert len(ROWS) >= 30, f"sólo {len(ROWS)} capacidades parseadas: el parser se rompió"


@pytest.mark.parametrize("row", [r for r in ROWS if r["example"]], ids=lambda r: f'{r["platform"]}-{r["capability"][:34]}')
def test_every_md_row_classifies_as_documented(row):
    """El ejemplo de cada fila debe clasificar en la clase de esa fila."""
    text = row["example"].split(":", 1)[-1] if "dec-" in row["example"] else row["example"]
    got = _classify(text, row["platform"])
    assert got == row["classification"], (
        f'La fila «{row["capability"]}» ({row["platform"]}) está documentada como '
        f'{row["classification"]} pero su propio ejemplo clasifica {got}.\n'
        f'Ejemplo: {row["example"]}'
    )


def test_every_row_has_explicit_pattern():
    """Toda fila del markdown debe tener un patrón explícito en el script."""
    missing = [f'{r["platform"]}: {r["capability"]}' for r in ROWS if r["capability_norm"] not in gen.PATTERNS]
    assert not missing, "filas del markdown sin patrón en PATTERNS: " + "; ".join(missing)


def test_no_orphan_patterns():
    """Y ningún patrón debe sobrar respecto al markdown (evita drift al revés)."""
    norms = {r["capability_norm"] for r in ROWS}
    orphans = sorted(set(gen.PATTERNS) - norms)
    assert not orphans, "patrones que ya no existen en el markdown: " + "; ".join(orphans)


def test_asymmetric_masonry_without_custom_css_is_red(tmp_path):
    """Caso pedido: grid asimétrico en Elementor sin CSS custom -> red."""
    brief = {
        "project": "red-case",
        "constraints": ["Sin CSS custom permitido"],
        "requirements": [{"id": "dec-layout-001", "description": "Hero con grid asimétrico masonry"}],
    }
    p = tmp_path / "brief.json"
    p.write_text(json.dumps(brief), encoding="utf-8")

    out = tmp_path / "feasibility-report.json"
    res = subprocess.run([sys.executable, str(SCRIPT), str(p), "--platform", "elementor", "-o", str(out)],
                         capture_output=True, text=True)

    assert res.returncode == 2, res.stdout + res.stderr
    report = json.loads(out.read_text(encoding="utf-8"))
    d = report["decisions_evaluated"][0]
    assert d["classification"] == "red", d
    assert "Custom CSS" in d["blocking_reason"]
    assert report["overall_feasibility"] == "blocked"


def test_asymmetric_masonry_with_custom_css_is_yellow(tmp_path):
    """El mismo grid, con CSS custom permitido, es yellow con workaround."""
    brief = {
        "project": "yellow-case",
        "requirements": [{"id": "dec-layout-001", "description": "Hero con grid asimétrico masonry"}],
    }
    p = tmp_path / "brief.json"
    p.write_text(json.dumps(brief), encoding="utf-8")
    out = tmp_path / "r.json"
    res = subprocess.run([sys.executable, str(SCRIPT), str(p), "--platform", "elementor", "-o", str(out)],
                         capture_output=True, text=True)

    assert res.returncode == 0, res.stdout + res.stderr
    d = json.loads(out.read_text(encoding="utf-8"))["decisions_evaluated"][0]
    assert d["classification"] == "yellow"
    assert d["workaround"], "yellow sin workaround documentado"


def test_subgrid_is_red_on_elementor(tmp_path):
    brief = {"project": "subgrid", "requirements": [
        {"id": "dec-layout-002", "description": "Usar CSS Subgrid en las cards"}]}
    p = tmp_path / "brief.json"
    p.write_text(json.dumps(brief), encoding="utf-8")
    out = tmp_path / "r.json"
    res = subprocess.run([sys.executable, str(SCRIPT), str(p), "--platform", "elementor", "-o", str(out)],
                         capture_output=True, text=True)
    assert res.returncode == 2
    assert json.loads(out.read_text(encoding="utf-8"))["decisions_evaluated"][0]["classification"] == "red"


def test_global_colors_are_green_on_elementor(tmp_path):
    brief = {"project": "colors", "requirements": [
        {"id": "dec-color-001", "description": "Paleta con Global Colors de Elementor"}]}
    p = tmp_path / "brief.json"
    p.write_text(json.dumps(brief), encoding="utf-8")
    out = tmp_path / "r.json"
    res = subprocess.run([sys.executable, str(SCRIPT), str(p), "--platform", "elementor", "-o", str(out)],
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    assert json.loads(out.read_text(encoding="utf-8"))["decisions_evaluated"][0]["classification"] == "green"


def test_both_platforms_takes_worst_case(tmp_path):
    """Peor clasificación entre plataformas gana."""
    brief = {"project": "worst", "requirements": [
        {"id": "dec-brand-001", "description": "Blend mode difference en la imagen hero"}]}
    p = tmp_path / "brief.json"
    p.write_text(json.dumps(brief), encoding="utf-8")
    out = tmp_path / "r.json"
    subprocess.run([sys.executable, str(SCRIPT), str(p), "--platform", "both", "-o", str(out)],
                   capture_output=True, text=True)
    d = json.loads(out.read_text(encoding="utf-8"))["decisions_evaluated"][0]
    assert d["classification"] == "red"
    assert set(d["per_platform"]) == {"elementor", "figma"}


def test_report_shape_is_stable(tmp_path):
    """El report debe traer las claves que consumen FASE 3 y los verificadores."""
    brief = {"project": "shape", "requirements": [{"id": "dec-layout-001", "description": "Flexbox containers"}]}
    p = tmp_path / "brief.json"
    p.write_text(json.dumps(brief), encoding="utf-8")
    out = tmp_path / "r.json"
    subprocess.run([sys.executable, str(SCRIPT), str(p), "-o", str(out)], capture_output=True, text=True)
    report = json.loads(out.read_text(encoding="utf-8"))
    for key in ("meta", "platform", "overall_feasibility", "summary", "decisions_evaluated"):
        assert key in report, f"falta {key}"
    for d in report["decisions_evaluated"]:
        for key in ("decision_id", "classification", "platform_capability", "constraints"):
            assert key in d, f"falta {key} en la decisión"
        assert d["classification"] in ("green", "yellow", "red")


def test_exit_code_2_is_the_fase3_gate(tmp_path):
    """FASE 3 bloquea si el productor devuelve red: el exit code es el contrato."""
    brief = {"project": "gate", "requirements": [
        {"id": "dec-layout-001", "description": "Container Queries para el hero"}]}
    p = tmp_path / "brief.json"
    p.write_text(json.dumps(brief), encoding="utf-8")
    res = subprocess.run([sys.executable, str(SCRIPT), str(p), "--platform", "elementor",
                          "-o", str(tmp_path / "r.json")], capture_output=True, text=True)
    assert res.returncode == 2
    assert "FASE 3" in res.stdout


def test_sample_brief_fixture_reports_one_red():
    """Fixture versionado: 5 requirements, al menos 1 red."""
    out = Path(__file__).parent / "_generated_feasibility.json"
    res = subprocess.run([sys.executable, str(SCRIPT), str(FIXTURES / "brief-red-test.json"),
                          "--platform", "both", "-o", str(out)], capture_output=True, text=True)
    assert res.returncode == 2, res.stdout + res.stderr
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["summary"]["red"] >= 1
    assert report["overall_feasibility"] == "blocked"
    out.unlink()
