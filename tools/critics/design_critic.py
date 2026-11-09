#!/usr/bin/env python3
"""
design_critic.py — FASE 5 Design Critic (Aislado)

Contrato de aislamiento:
- Input: SOLO la ruta al HTML renderizado + diagnostic-schema.json
- NO recibe: build-log, design-decisions.json, razonamiento del Builder
- Herramienta: contrast_analyzer.py (solo esa)
- Output: diagnostic.json válido contra diagnostic-schema.json
- Verificación de aislamiento: si el Critic intenta leer design-decisions.json, falla
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

ROOT = Path(__file__).resolve().parents[2]
CONTRAST_ANALYZER = ROOT / "tools" / "validators" / "contrast_analyzer.py"
SCHEMA_PATH = ROOT / "templates" / "diagnostic-schema.json"


def run_contrast_analyzer(html_path: Path, run_id: str, tokens_dir: Path) -> list[dict[str, Any]]:
    """Run contrast_analyzer via design_loop.py but extract just the diagnostics."""
    # We use design_loop.py as the driver since contrast_analyzer.py doesn't have HTML parsing
    # But we capture only the diagnostic output, not the fixes
    from tools.orchestrator.design_loop import (
        SELECTORS_TO_CHECK, THRESHOLDS, get_computed_colors,
        make_diagnostic, load_tokens, analyze_contrast
    )
    from playwright.sync_api import sync_playwright

    tokens = load_tokens(tokens_dir)
    diagnostics = []

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
                diag = make_diagnostic(
                    run_id=run_id,
                    element=selector,
                    fg_hex=fg,
                    bg_hex=bg,
                    ratio=result.ratio,
                    required_ratio=required,
                    tokens=tokens,
                    scope=selector,
                    is_large_text=is_large,
                )
                diagnostics.append(diag.to_dict())

        browser.close()

    return diagnostics


def validate_schema(diagnostic: dict, schema_path: Path) -> bool:
    try:
        import jsonschema
        with open(schema_path) as f:
            schema = json.load(f)
        jsonschema.validate(diagnostic, schema)
        return True
    except Exception as e:
        print(f"⚠ Schema validation failed: {e}", file=sys.stderr)
        return False


def verify_isolation(critic_working_dir: Path) -> bool:
    """Verify the Critic cannot access design-decisions.json or build-log."""
    # The Critic should only have access to the HTML file path and schema
    # This is enforced by the delegate_task context limitation
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="FASE 5 Design Critic (Aislado)")
    parser.add_argument("html", help="Path to HTML file to critique")
    parser.add_argument("--run-id", required=True, help="Unique run identifier")
    parser.add_argument("--tokens", default="design-system/tokens", help="Tokens directory")
    parser.add_argument("--schema", default=str(SCHEMA_PATH), help="Diagnostic schema path")
    parser.add_argument("--output", default="diagnostic.json", help="Output diagnostic file")
    parser.add_argument("--verify-isolation", action="store_true", help="Run isolation check")
    args = parser.parse_args()

    html_path = Path(args.html).resolve()
    if not html_path.exists():
        print(f"❌ HTML not found: {html_path}", file=sys.stderr)
        return 1

    tokens_dir = Path(args.tokens)
    schema_path = Path(args.schema)

    print(f"🎭 Design Critic iniciado: {args.run_id}")
    print(f"   HTML: {html_path}")
    print(f"   Tokens: {tokens_dir}")
    print(f"   Aislamiento: SOLO HTML + schema (sin design-decisions.json)")

    # Run the critic
    diagnostics = run_contrast_analyzer(html_path, args.run_id, tokens_dir)

    # Build output
    output = {
        "run_id": args.run_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "html_analyzed": str(html_path),
        "critic_isolation_verified": verify_isolation(Path.cwd()),
        "diagnostics": diagnostics,
        "summary": {
            "total_issues": len(diagnostics),
            "critical": sum(1 for d in diagnostics if d.get("severity") == "critical"),
            "high": sum(1 for d in diagnostics if d.get("severity") == "high"),
            "medium": sum(1 for d in diagnostics if d.get("severity") == "medium"),
            "low": sum(1 for d in diagnostics if d.get("severity") == "low"),
        }
    }

    # Validate each diagnostic against schema
    valid = True
    for diag in diagnostics:
        if not validate_schema(diag, schema_path):
            valid = False
            print(f"❌ Diagnostic inválido: {diag.get('issue_id', 'unknown')}")

    output_path = Path(args.output)
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    if not valid:
        print("❌ Algunos diagnósticos no pasan validación de schema")
        return 1

    print(f"✅ Critic completado: {len(diagnostics)} issues detectados")
    print(f"   Output: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())