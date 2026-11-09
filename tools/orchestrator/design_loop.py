#!/usr/bin/env python3
"""
Design Loop Micro-Cycle — Phase 1

Runs the complete detect → diagnose → correct → re-validate cycle
on a static HTML file using the pure contrast_analyzer.

This is the HEART of Design Superpowers. No Elementor, no Figma, no LLM.
Just: HTML + CSS + Playwright (for DOM) + pure contrast math.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.validators.contrast_analyzer import (
    analyze_contrast,
    load_tokens,
    make_diagnostic,
    suggest_fixes,
    resolve_token,
)


# ──────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────

THRESHOLDS = {
    "contrast_aa_normal": 4.5,
    "contrast_aa_large": 3.0,
}

SELECTORS_TO_CHECK = [
    (".hero__subtitle", False),   # normal text
    (".hero__title", True),       # large text
    (".cta-primary", True),       # large text (button)
    (".body-text", False),        # normal text
]


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

def get_computed_colors(page, selector: str) -> tuple[str, str] | None:
    """Extract computed foreground and background colors for an element."""
    result = page.evaluate(f"""
        (() => {{
            const el = document.querySelector('{selector}');
            if (!el) return null;
            const style = window.getComputedStyle(el);
            let fg = style.color;
            let bg = style.backgroundColor;

            // Walk up for background if transparent
            let current = el;
            while (bg === 'rgba(0, 0, 0, 0)' || bg === 'transparent') {{
                current = current.parentElement;
                if (!current) break;
                bg = window.getComputedStyle(current).backgroundColor;
            }}

            // Convert rgb(r, g, b) to hex
            function toHex(cssColor) {{
                const m = cssColor.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
                if (!m) return cssColor; // already hex or named
                return '#' + [m[1], m[2], m[3]].map(x => parseInt(x).toString(16).padStart(2, '0')).join('');
            }}

            return {{ fg: toHex(fg), bg: toHex(bg) }};
        }})()
    """)
    if result:
        return result["fg"], result["bg"]
    return None


def apply_css_fix(html_path: Path, selector: str, new_fg: str | None, new_bg: str | None) -> Path:
    """Apply a minimal CSS fix to the HTML, return new file path."""
    content = html_path.read_text(encoding="utf-8")

    # Build the fix CSS
    rules = []
    if new_fg:
        rules.append(f"color: {new_fg} !important;")
    if new_bg:
        rules.append(f"background-color: {new_bg} !important;")

    fix_css = f"\n    {selector} {{\n        " + "\n        ".join(rules) + "\n    }}\n"

    # Insert before </style>
    if "</style>" in content:
        new_content = content.replace("</style>", fix_css + "</style>")
    else:
        # Fallback: inject style block
        new_content = content.replace("</head>", f"<style>{fix_css}</style></head>")

    # Write to new file
    new_path = html_path.with_stem(html_path.stem + "_fixed")
    new_path.write_text(new_content, encoding="utf-8")
    return new_path


def validate_schema(diagnostic: dict, schema_path: Path) -> bool:
    """Validate diagnostic against JSON schema."""
    try:
        import jsonschema
        with open(schema_path) as f:
            schema = json.load(f)
        jsonschema.validate(diagnostic, schema)
        return True
    except Exception as e:
        print(f"  ⚠ Schema validation failed: {e}")
        return False


# ──────────────────────────────────────────────────────────────────────
# Main micro-loop
# ──────────────────────────────────────────────────────────────────────

def run_micro_loop(html_path: Path, run_id: str, tokens_dir: Path, schema_path: Path, max_iterations: int = 3) -> dict:
    """
    Execute the micro-loop:
    1. Launch Playwright, load HTML
    2. For each selector, extract colors → analyze contrast
    3. If failure: create diagnostic, apply fix, re-validate
    4. Track corrections, ensure no regressions
    """
    from playwright.sync_api import sync_playwright

    tokens = load_tokens(tokens_dir)
    all_diagnostics = []
    all_corrections = []
    iteration = 0
    current_html = html_path

    print(f"🔄 Starting micro-loop for {run_id}")
    print(f"   HTML: {html_path}")
    print(f"   Tokens: {tokens_dir}")
    print(f"   Schema: {schema_path}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            while iteration < max_iterations:
                iteration += 1
                print(f"\n  ── Iteration {iteration}/{max_iterations} ──")

                # Load current HTML
                page.goto(current_html.as_uri())
                page.wait_for_load_state("networkidle")

                iteration_diagnostics = []
                iteration_fixes = []

                for selector, is_large in SELECTORS_TO_CHECK:
                    colors = get_computed_colors(page, selector)
                    if not colors:
                        print(f"  ⚠ {selector}: not found")
                        continue

                    fg, bg = colors
                    required = THRESHOLDS["contrast_aa_large" if is_large else "contrast_aa_normal"]
                    result = analyze_contrast(fg, bg)

                    print(f"  🔍 {selector}: fg={fg} bg={bg} ratio={result.ratio:.2f}:1 required={required}:1 {'✅' if (result.passes_aa_large if is_large else result.passes_aa_normal) else '❌'}")

                    if (is_large and not result.passes_aa_large) or (not is_large and not result.passes_aa_normal):
                        # Create diagnostic
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
                        diag_dict = diag.to_dict()
                        iteration_diagnostics.append(diag_dict)
                        all_diagnostics.append(diag_dict)

                        # Get suggested fix
                        suggestions = suggest_fixes(fg, bg, tokens, target_ratio=required)
                        if suggestions:
                            fix = suggestions[0]
                            print(f"     → Fix: {fix['description']} (new ratio: {fix['new_ratio']:.2f}:1)")
                            iteration_fixes.append({
                                "selector": selector,
                                "old_fg": fg,
                                "old_bg": bg,
                                "new_fg": fix["new_fg"],
                                "new_bg": fix["new_bg"],
                                "action": fix["action"],
                                "description": fix["description"],
                            })

                if not iteration_fixes:
                    print("  ✅ All checks passed!")
                    break

                # Apply fixes to create new HTML
                new_html = current_html
                for fix in iteration_fixes:
                    new_html = apply_css_fix(
                        new_html,
                        fix["selector"],
                        fix["new_fg"] if fix["new_fg"] != fix["old_fg"] else None,
                        fix["new_bg"] if fix["new_bg"] != fix["old_bg"] else None,
                    )

                # Record correction
                correction = {
                    "iteration": iteration,
                    "html_before": str(current_html),
                    "html_after": str(new_html),
                    "fixes_applied": iteration_fixes,
                    "diagnostics_before": iteration_diagnostics,
                }
                all_corrections.append(correction)

                # Re-validate with new HTML (regression check)
                current_html = new_html
                print(f"  📝 Applied {len(iteration_fixes)} fix(es), re-validating...")

                # Quick regression check: re-run all selectors on new HTML
                page.goto(current_html.as_uri())
                page.wait_for_load_state("networkidle")

                regression_issues = []
                for selector, is_large in SELECTORS_TO_CHECK:
                    colors = get_computed_colors(page, selector)
                    if not colors:
                        continue
                    fg, bg = colors
                    required = THRESHOLDS["contrast_aa_large" if is_large else "contrast_aa_normal"]
                    result = analyze_contrast(fg, bg)
                    passes = result.passes_aa_large if is_large else result.passes_aa_normal
                    if not passes:
                        regression_issues.append({
                            "selector": selector,
                            "ratio": result.ratio,
                            "required": required,
                        })

                if regression_issues:
                    print(f"  ⚠ REGRESSION DETECTED: {len(regression_issues)} element(s) still failing")
                    for r in regression_issues:
                        print(f"     {r['selector']}: {r['ratio']:.2f}:1 (need {r['required']}:1)")
                else:
                    print("  ✅ No regressions — all elements pass")

            # Final validation
            final_diagnostics = []
            page.goto(current_html.as_uri())
            page.wait_for_load_state("networkidle")
            for selector, is_large in SELECTORS_TO_CHECK:
                colors = get_computed_colors(page, selector)
                if not colors:
                    continue
                fg, bg = colors
                required = THRESHOLDS["contrast_aa_large" if is_large else "contrast_aa_normal"]
                result = analyze_contrast(fg, bg)
                passes = result.passes_aa_large if is_large else result.passes_aa_normal
                if not passes:
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
                    final_diagnostics.append(diag.to_dict())

        finally:
            browser.close()

    # Build run artifacts
    run_dir = PROJECT_ROOT / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    artifacts = {
        "run_id": run_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "iterations": iteration,
        "html_initial": str(html_path),
        "html_final": str(current_html),
        "audit_before": all_diagnostics[:len(SELECTORS_TO_CHECK)],  # first iteration only
        "audit_after": final_diagnostics,
        "corrections": all_corrections,
        "success": len(final_diagnostics) == 0,
    }

    # Save artifacts
    (run_dir / "audit-before.json").write_text(json.dumps(artifacts["audit_before"], indent=2))
    (run_dir / "audit-after.json").write_text(json.dumps(artifacts["audit_after"], indent=2))
    (run_dir / "corrections.json").write_text(json.dumps(artifacts["corrections"], indent=2))
    (run_dir / "run-summary.json").write_text(json.dumps(artifacts, indent=2))

    # Copy final HTML to run dir
    shutil.copy2(current_html, run_dir / "final.html")

    print(f"\n📁 Artifacts saved to: {run_dir}")
    print(f"   Success: {artifacts['success']}")
    print(f"   Iterations: {iteration}")
    print(f"   Final diagnostics: {len(final_diagnostics)}")

    return artifacts


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Design Loop Micro-Cycle")
    parser.add_argument("html", nargs="?", default="tests/fixtures/hero.html", help="HTML file to validate")
    parser.add_argument("--run-id", default=None, help="Run ID (default: timestamp)")
    parser.add_argument("--tokens", default="design-system/tokens", help="Tokens directory")
    parser.add_argument("--schema", default="templates/diagnostic-schema.json", help="Diagnostic schema")
    parser.add_argument("--max-iterations", type=int, default=3, help="Max correction iterations")
    args = parser.parse_args()

    html_path = PROJECT_ROOT / args.html
    if not html_path.exists():
        print(f"❌ HTML not found: {html_path}")
        sys.exit(1)

    run_id = args.run_id or f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_microloop"
    tokens_dir = PROJECT_ROOT / args.tokens
    schema_path = PROJECT_ROOT / args.schema

    if not schema_path.exists():
        print(f"❌ Schema not found: {schema_path}")
        sys.exit(1)

    result = run_micro_loop(html_path, run_id, tokens_dir, schema_path, args.max_iterations)
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()