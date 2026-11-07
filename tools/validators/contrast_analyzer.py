#!/usr/bin/env python3
"""
Contrast Analyzer — Pure WCAG 2.2 Contrast Calculation

This module provides the core contrast calculation logic WITHOUT any browser dependency.
It can be tested in isolation, then wrapped by a Playwright-based extractor.

WCAG 2.2 AA thresholds:
- Normal text (≤18pt or ≤14pt bold): 4.5:1
- Large text (>18pt or >14pt bold): 3:1
- UI components / graphical objects: 3:1
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal


# ──────────────────────────────────────────────────────────────────────
# Core color math (pure functions, no I/O)
# ──────────────────────────────────────────────────────────────────────

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert #RRGGBB or #RRGGBBAA to (r, g, b) 0-255."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) == 8:
        hex_color = hex_color[:6]  # ignore alpha for contrast
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_linear(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    """Convert sRGB 0-255 to linear RGB 0-1."""
    def channel(c: int) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(channel(c) for c in rgb)


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    """WCAG 2.2 relative luminance (Y component)."""
    r, g, b = rgb_to_linear(rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """
    Calculate WCAG 2.2 contrast ratio between foreground and background.
    Returns ratio as float (e.g., 4.52 for 4.52:1).
    """
    fg_lum = relative_luminance(hex_to_rgb(fg_hex))
    bg_lum = relative_luminance(hex_to_rgb(bg_hex))
    lighter = max(fg_lum, bg_lum)
    darker = min(fg_lum, bg_lum)
    return (lighter + 0.05) / (darker + 0.05)


@dataclass(frozen=True)
class ContrastResult:
    """Result of a single contrast check."""
    fg_hex: str
    bg_hex: str
    ratio: float
    passes_aa_normal: bool   # ≥ 4.5:1
    passes_aa_large: bool    # ≥ 3:1
    passes_aaa_normal: bool  # ≥ 7:1
    passes_aaa_large: bool   # ≥ 4.5:1

    def to_dict(self) -> dict:
        return asdict(self)


def analyze_contrast(fg_hex: str, bg_hex: str) -> ContrastResult:
    """
    Pure contrast analysis — no browser, no I/O.
    """
    ratio = contrast_ratio(fg_hex, bg_hex)
    return ContrastResult(
        fg_hex=fg_hex,
        bg_hex=bg_hex,
        ratio=round(ratio, 2),
        passes_aa_normal=ratio >= 4.5,
        passes_aa_large=ratio >= 3.0,
        passes_aaa_normal=ratio >= 7.0,
        passes_aaa_large=ratio >= 4.5,
    )


# ──────────────────────────────────────────────────────────────────────
# Palette-aware suggestions (uses design-system tokens)
# ──────────────────────────────────────────────────────────────────────

def load_tokens(tokens_dir: Path) -> dict:
    """Load design-system color tokens."""
    colors_file = tokens_dir / "colors.json"
    if not colors_file.exists():
        return {}
    with open(colors_file, encoding="utf-8") as f:
        return json.load(f)


def resolve_token(token_ref: str, tokens: dict) -> str | None:
    """Resolve a semantic token reference like '{colors.semantic.cta.primary_bg}'."""
    # Handle {colors.semantic.cta.primary_bg} format
    match = re.match(r"\{colors\.semantic\.([^}]+)\}", token_ref)
    if match:
        path = match.group(1).split(".")
        current = tokens.get("semantic", {})
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        if isinstance(current, str) and current.startswith("#"):
            return current
    # Handle direct hex
    if token_ref.startswith("#"):
        return token_ref
    return None


def suggest_fixes(
    fg_hex: str,
    bg_hex: str,
    tokens: dict,
    target_ratio: float = 4.5,
    max_suggestions: int = 5
) -> list[dict]:
    """
    Given a failing pair, suggest token-compliant fixes.
    Returns list of {action, new_fg, new_bg, new_ratio, token_ref}.
    """
    suggestions = []
    semantic = tokens.get("semantic", {})
    primitives = tokens.get("primitives", {})

    def resolve_value(val: str) -> str | None:
        """Resolve a token reference to hex."""
        if val.startswith("#"):
            return val
        # Handle {colors.semantic.xxx} or {neutral-50} format
        match = re.match(r"\{([^}]+)\}", val)
        if match:
            path = match.group(1).split(".")
            # Try primitives first
            if path[0] in primitives:
                current = primitives
                for key in path:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        return None
                if isinstance(current, dict) and "value" in current:
                    return current["value"]
                elif isinstance(current, str):
                    return current
            # Try semantic
            current = tokens
            for key in path:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            if isinstance(current, str) and current.startswith("#"):
                return current
            elif isinstance(current, dict) and "value" in current:
                return current["value"]
        return None

    # Collect all semantic color values (resolved)
    def collect_colors(obj: dict, prefix: str = ""):
        for k, v in obj.items():
            if isinstance(v, str):
                resolved = resolve_value(v)
                if resolved:
                    yield f"{prefix}.{k}" if prefix else k, resolved
            elif isinstance(v, dict):
                yield from collect_colors(v, f"{prefix}.{k}" if prefix else k)

    token_colors = list(collect_colors(semantic))

    # Strategy 1: Keep FG, find compliant BG from tokens
    for token_ref, token_bg in token_colors:
        result = analyze_contrast(fg_hex, token_bg)
        if result.ratio >= target_ratio:
            suggestions.append({
                "action": "change_background",
                "description": f"Change background to {token_ref}",
                "new_fg": fg_hex,
                "new_bg": token_bg,
                "new_ratio": result.ratio,
                "token_ref": token_ref,
            })

    # Strategy 2: Keep BG, find compliant FG from tokens
    for token_ref, token_fg in token_colors:
        result = analyze_contrast(token_fg, bg_hex)
        if result.ratio >= target_ratio:
            suggestions.append({
                "action": "change_foreground",
                "description": f"Change foreground to {token_ref}",
                "new_fg": token_fg,
                "new_bg": bg_hex,
                "new_ratio": result.ratio,
                "token_ref": token_ref,
            })

    # Strategy 3: Both from tokens (semantic pairs)
    cta_pairs = [
        ("cta.primary_text", "cta.primary_bg"),
        ("cta.secondary_text", "cta.secondary_bg"),
        ("text.primary", "background.primary"),
        ("text.secondary", "background.secondary"),
        ("text.inverse", "background.inverse"),
    ]
    for fg_ref, bg_ref in cta_pairs:
        fg_val = resolve_value(f"{{colors.semantic.{fg_ref}}}")
        bg_val = resolve_value(f"{{colors.semantic.{bg_ref}}}")
        if fg_val and bg_val:
            result = analyze_contrast(fg_val, bg_val)
            if result.ratio >= target_ratio:
                suggestions.append({
                    "action": "use_semantic_pair",
                    "description": f"Use {fg_ref} on {bg_ref}",
                    "new_fg": fg_val,
                    "new_bg": bg_val,
                    "new_ratio": result.ratio,
                    "token_ref": f"{fg_ref} / {bg_ref}",
                })

    # Deduplicate and sort by ratio (best first)
    seen = set()
    unique = []
    for s in suggestions:
        key = (s["new_fg"], s["new_bg"])
        if key not in seen:
            seen.add(key)
            unique.append(s)

    unique.sort(key=lambda x: -x["new_ratio"])
    return unique[:max_suggestions]


# ──────────────────────────────────────────────────────────────────────
# Diagnostic output (conforms to diagnostic-schema.json)
# ──────────────────────────────────────────────────────────────────────

@dataclass
class ContrastDiagnostic:
    """Diagnostic conforming to DesignDiagnostic schema."""
    run_id: str
    issue_id: str
    category: Literal["accessibility"]
    severity: Literal["critical", "high", "medium", "low"]
    element: str
    problem: str
    measured_value: float
    required_value: float
    suggested_action: str
    scope: str
    auto_fix_allowed: bool
    verification_required: bool
    brand_constraint: str
    regression_check: list[str]
    evidence: dict
    validator: Literal["contrast_analyzer"]
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "issue_id": self.issue_id,
            "category": self.category,
            "severity": self.severity,
            "element": self.element,
            "problem": self.problem,
            "measured_value": self.measured_value,
            "required_value": self.required_value,
            "suggested_action": self.suggested_action,
            "scope": self.scope,
            "auto_fix_allowed": self.auto_fix_allowed,
            "verification_required": self.verification_required,
            "brand_constraint": self.brand_constraint,
            "regression_check": self.regression_check,
            "evidence": self.evidence,
            "validator": self.validator,
            "timestamp": self.timestamp,
        }


def make_diagnostic(
    run_id: str,
    element: str,
    fg_hex: str,
    bg_hex: str,
    ratio: float,
    required_ratio: float,
    tokens: dict,
    scope: str = "unknown",
    is_large_text: bool = False,
) -> ContrastDiagnostic:
    """Create a diagnostic from a contrast failure."""
    from datetime import datetime, timezone

    passes = ratio >= required_ratio
    severity = "critical" if not passes and required_ratio >= 4.5 else "high"
    # SHA-256 (no hash()): hash() está salteado por PYTHONHASHSEED y cambia entre
    # procesos, así que el mismo run_id+element producía distinto issue_id en cada corrida.
    digest = hashlib.sha256(f"{run_id}:{element}".encode("utf-8")).digest()
    issue_num = int.from_bytes(digest[:4], "big") % 1000
    issue_id = f"A11Y-{issue_num:03d}"

    # Build suggested action from token suggestions
    suggestions = suggest_fixes(fg_hex, bg_hex, tokens, target_ratio=required_ratio)
    suggested_action = suggestions[0]["description"] if suggestions else "Adjust colors to meet contrast ratio"

    # Brand constraint: which token is involved
    brand_constraint = ""
    for token_ref, token_val in [
        ("colors.semantic.text.primary", tokens.get("semantic", {}).get("text", {}).get("primary")),
        ("colors.semantic.background.primary", tokens.get("semantic", {}).get("background", {}).get("primary")),
        ("colors.semantic.cta.primary_bg", tokens.get("semantic", {}).get("cta", {}).get("primary_bg")),
    ]:
        if token_val in (fg_hex, bg_hex):
            brand_constraint = token_ref
            break

    return ContrastDiagnostic(
        run_id=run_id,
        issue_id=issue_id,
        category="accessibility",
        severity=severity,
        element=element,
        problem=f"Contrast ratio {ratio:.2f}:1 fails WCAG AA {'large' if is_large_text else 'normal'} text threshold ({required_ratio}:1)",
        measured_value=ratio,
        required_value=required_ratio,
        suggested_action=suggested_action,
        scope=scope,
        auto_fix_allowed=True,
        verification_required=True,
        brand_constraint=brand_constraint,
        regression_check=[element],
        evidence={},
        validator="contrast_analyzer",
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    )


# ──────────────────────────────────────────────────────────────────────
# CLI for testing
# ──────────────────────────────────────────────────────────────────────

def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: contrast_analyzer.py <fg_hex> <bg_hex> [--tokens <dir>] [--large-text]")
        sys.exit(1)

    fg = sys.argv[1]
    bg = sys.argv[2]
    tokens_dir = Path(sys.argv[sys.argv.index("--tokens") + 1]) if "--tokens" in sys.argv else Path("design-system/tokens")
    is_large = "--large-text" in sys.argv

    tokens = load_tokens(tokens_dir)
    result = analyze_contrast(fg, bg)

    print(json.dumps({
        "fg": fg,
        "bg": bg,
        "ratio": result.ratio,
        "passes_aa_normal": result.passes_aa_normal,
        "passes_aa_large": result.passes_aa_large,
        "passes_aaa_normal": result.passes_aaa_normal,
        "passes_aaa_large": result.passes_aaa_large,
        "suggestions": suggest_fixes(fg, bg, tokens, target_ratio=4.5 if not is_large else 3.0)
    }, indent=2))


if __name__ == "__main__":
    main()