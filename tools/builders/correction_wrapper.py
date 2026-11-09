#!/usr/bin/env python3
"""
correction_wrapper.py — FASE 6 Correction Wrapper

Wrapper que invoca design_loop.py sobre el HTML del builder cuando el Critic detecta issues.
- Input: index.html + diagnostic.json
- Si hay issues con auto_fix_allowed=true: aplica fix mínimo (vía design_loop.py), 
  re-valida con contrast_analyzer.py, verifica que no hay regresiones
- Output: index.html corregido + corrections.json
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

ROOT = Path(__file__).resolve().parents[2]
DESIGN_LOOP = ROOT / "tools" / "orchestrator" / "design_loop.py"
CONTRAST_ANALYZER = ROOT / "tools" / "validators" / "contrast_analyzer.py"
SCHEMA_PATH = ROOT / "templates" / "diagnostic-schema.json"


def load_diagnostic(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def has_auto_fix_issues(diagnostic: dict[str, Any]) -> bool:
    """Check if any issues have auto_fix_allowed=true."""
    for diag in diagnostic.get("diagnostics", []):
        if diag.get("auto_fix_allowed", False):
            return True
    return False


def run_design_loop(html_path: Path, run_id: str, tokens_dir: Path, schema_path: Path) -> Path:
    """Run design_loop.py and return the final corrected HTML path."""
    result = subprocess.run([
        sys.executable, str(DESIGN_LOOP),
        str(html_path),
        "--run-id", run_id,
        "--tokens", str(tokens_dir),
        "--schema", str(schema_path)
    ], capture_output=True, text=True, cwd=ROOT)

    if result.returncode != 0:
        print(f"❌ design_loop.py failed: {result.stderr}", file=sys.stderr)
        return html_path

    # design_loop.py saves artifacts to runs/{run_id}/
    run_dir = ROOT / "runs" / run_id
    final_html = run_dir / "final.html"
    if final_html.exists():
        return final_html

    # Fallback: look for _fixed.html
    fixed_html = html_path.with_stem(html_path.stem + "_fixed")
    if fixed_html.exists():
        return fixed_html

    return html_path


def verify_no_regressions(html_path: Path, tokens_dir: Path, run_id: str) -> bool:
    """Run contrast check on corrected HTML to verify no regressions."""
    from tools.validators.contrast_analyzer import (
        analyze_contrast, load_tokens
    )
    from playwright.sync_api import sync_playwright
    from tools.orchestrator.design_loop import (
        SELECTORS_TO_CHECK, THRESHOLDS, get_computed_colors
    )

    tokens = load_tokens(tokens_dir)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(html_path.as_uri())
        page.wait_for_load_state("networkidle")

        for selector, is_large in SELECTORS_TO_CHECK:
            colors = get_computed_colors(page, selector)
            if not colors:
                continue

            fg, bg = colors
            required = THRESHOLDS["contrast_aa_large" if is_large else "contrast_aa_normal"]
            result = analyze_contrast(fg, bg)

            if (is_large and not result.passes_aa_large) or (not is_large and not result.passes_aa_normal):
                print(f"❌ REGRESIÓN: {selector} ratio={result.ratio:.2f}:1 required={required}:1", file=sys.stderr)
                browser.close()
                return False

        browser.close()

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="FASE 6 Correction Wrapper")
    parser.add_argument("html", help="Path to HTML file")
    parser.add_argument("diagnostic", help="Path to diagnostic.json from Critic")
    parser.add_argument("--tokens", default="design-system/tokens", help="Tokens directory")
    parser.add_argument("--schema", default=str(SCHEMA_PATH), help="Diagnostic schema path")
    parser.add_argument("--run-id", required=True, help="Unique run identifier")
    parser.add_argument("--output", default="index_corrected.html", help="Output corrected HTML")
    parser.add_argument("--corrections-output", default="corrections.json", help="Corrections log")
    args = parser.parse_args()

    html_path = Path(args.html).resolve()
    diagnostic_path = Path(args.diagnostic)
    tokens_dir = Path(args.tokens)
    schema_path = Path(args.schema)

    if not html_path.exists():
        print(f"❌ HTML not found: {html_path}", file=sys.stderr)
        return 1
    if not diagnostic_path.exists():
        print(f"❌ Diagnostic not found: {diagnostic_path}", file=sys.stderr)
        return 1

    diagnostic = load_diagnostic(diagnostic_path)

    print(f"🔧 Correction Wrapper: {args.run_id}")
    print(f"   HTML: {html_path}")
    print(f"   Diagnostic: {diagnostic_path}")

    # Check if there are auto-fixable issues
    if not has_auto_fix_issues(diagnostic):
        print("✅ No hay issues auto-fixable. HTML no requiere corrección.")
        # Copy HTML to output
        output_path = Path(args.output).resolve()
        output_path.write_text(html_path.read_text(encoding="utf-8"), encoding="utf-8")

        corrections = {
            "run_id": args.run_id,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "input_html": str(html_path),
            "output_html": str(output_path),
            "corrections_applied": [],
            "regressions_found": False,
        }
        Path(args.corrections_output).write_text(json.dumps(corrections, indent=2), encoding="utf-8")
        print(f"   Output: {output_path}")
        return 0

    print("🔄 Issues auto-fixables detectados. Ejecutando design_loop.py...")

    # Run design_loop.py
    corrected_html = run_design_loop(html_path, args.run_id, tokens_dir, schema_path)

    if corrected_html == html_path:
        print("❌ design_loop no produjo HTML corregido", file=sys.stderr)
        return 1

    # Verify no regressions
    print("🔍 Verificando regresiones...")
    if not verify_no_regressions(corrected_html, tokens_dir, args.run_id):
        print("❌ Regresiones detectadas en HTML corregido", file=sys.stderr)
        return 1

    # Copy corrected HTML to output
    output_path = Path(args.output).resolve()
    output_path.write_text(corrected_html.read_text(encoding="utf-8"), encoding="utf-8")

    # Build corrections log
    corrections = {
        "run_id": args.run_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "input_html": str(html_path),
        "diagnostic": str(diagnostic_path),
        "output_html": str(output_path),
        "corrected_by": "design_loop.py",
        "corrections_applied": [
            {
                "selector": d.get("element"),
                "issue_id": d.get("issue_id"),
                "old_fg": d.get("measured_value"),
                "action": d.get("suggested_action"),
                "auto_fix_allowed": d.get("auto_fix_allowed"),
            }
            for d in diagnostic.get("diagnostics", [])
            if d.get("auto_fix_allowed", False)
        ],
        "regressions_found": False,
    }
    Path(args.corrections_output).write_text(json.dumps(corrections, indent=2), encoding="utf-8")

    print(f"✅ Corrección completada: {len(corrections['corrections_applied'])} fixes aplicados")
    print(f"   HTML corregido: {output_path}")
    print(f"   Log: {args.corrections_output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())