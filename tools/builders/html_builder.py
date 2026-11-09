#!/usr/bin/env python3
"""
html_builder.py — FASE 4 Builder HTML Mínimo

Input: design-decisions.json (solo decisiones color + typography)
Lee: design-system/tokens/colors.json y typography.json
Output: index.html con estructura hero + CTA + párrafo y CSS inline
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TOKENS_DIR = ROOT / "design-system" / "tokens"
COLORS_FILE = TOKENS_DIR / "colors.json"
TYPOGRAPHY_FILE = TOKENS_DIR / "typography.json"


def load_json(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def resolve_token(token_ref: str, tokens: dict[str, Any]) -> str | None:
    """Resolve token reference like '{colors.semantic.cta.primary_bg}' to hex value.
    Handles nested references like {colors.semantic.text.primary} -> {neutral-900} -> #171717
    Also handles direct primitive references like {neutral-50}."""
    # Direct hex
    if token_ref.startswith("#"):
        return token_ref

    match = re.match(r"\{([^}]+)\}", token_ref)
    if not match:
        return None

    path = match.group(1).split(".")
    current = tokens

    # Navigate the path
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            # If we're at a primitive-like key and it's not found, try primitives
            if len(path) == 1 and key in tokens.get("primitives", {}):
                prim = tokens["primitives"][key]
                if isinstance(prim, dict) and "value" in prim:
                    return prim["value"]
                if isinstance(prim, str) and prim.startswith("#"):
                    return prim
            return None

    # If we got a string that's another token reference, recurse
    if isinstance(current, str):
        if current.startswith("#"):
            return current
        if current.startswith("{"):
            return resolve_token(current, tokens)
        # Try as primitive key
        if current in tokens.get("primitives", {}):
            prim = tokens["primitives"][current]
            if isinstance(prim, dict) and "value" in prim:
                return prim["value"]
            if isinstance(prim, str) and prim.startswith("#"):
                return prim
        return None

    # If we got a dict with value
    if isinstance(current, dict) and "value" in current:
        return current["value"]

    return None


def resolve_all_semantic(tokens: dict[str, Any]) -> dict[str, str]:
    """Resolve all semantic color tokens to hex values."""
    resolved = {}

    def walk(obj: dict[str, Any], prefix: str = ""):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, str):
                resolved[key] = resolve_token(v, tokens)
            elif isinstance(v, dict):
                walk(v, key)

    walk(tokens.get("semantic", {}))
    return {k: v for k, v in resolved.items() if v is not None}


def get_font_family(tokens: dict[str, Any], role: str) -> str:
    """Get font-family CSS string for a role (heading/body/mono)."""
    fam = tokens.get("font_families", {}).get(role, {})
    name = fam.get("name", "system-ui")
    fallbacks = fam.get("fallbacks", ["system-ui", "sans-serif"])
    all_fonts = [name] + fallbacks
    return ", ".join(f'"{f}"' for f in all_fonts)


def build_css_variables(semantic_colors: dict[str, str], typography: dict[str, Any]) -> str:
    """Generate CSS custom properties from resolved tokens."""
    lines = [":root {"]

    # Colors
    for key, value in semantic_colors.items():
        css_var = "--" + key.replace(".", "-")
        lines.append(f"  {css_var}: {value};")

    # Typography
    scale = typography.get("scale", {}).get("steps", {})
    for step_name, step_data in scale.items():
        css_var = f"--typo-{step_name.replace('_', '-')}"
        size = step_data.get("size", 16)
        line_height = step_data.get("line_height", 1.5)
        weight = step_data.get("weight", 400)
        letter_spacing = step_data.get("letter_spacing", "0")
        font_family = step_data.get("font_family", "body")
        lines.append(f"  {css_var}-size: {size}px;")
        lines.append(f"  {css_var}-line-height: {line_height};")
        lines.append(f"  {css_var}-weight: {weight};")
        lines.append(f"  {css_var}-letter-spacing: {letter_spacing};")
        lines.append(f"  {css_var}-font-family: var(--font-{font_family});")

    # Font families
    for role in ["heading", "body", "mono"]:
        ff = get_font_family(typography, role)
        lines.append(f"  --font-{role}: {ff};")

    lines.append("}")
    return "\n".join(lines)


def build_component_styles() -> str:
    """Component-specific CSS using the variables."""
    return """
/* Hero section */
.hero {
  background-color: var(--background-primary);
  color: var(--text-primary);
  padding: var(--spacing-xl, 4rem) var(--spacing-lg, 2rem);
  text-align: center;
}

.hero__title {
  font-family: var(--font-heading);
  font-size: var(--typo-display-xl-size);
  line-height: var(--typo-display-xl-line-height);
  font-weight: var(--typo-display-xl-weight);
  letter-spacing: var(--typo-display-xl-letter-spacing);
  color: var(--text-primary);
  margin-bottom: var(--spacing-md, 1rem);
}

.hero__subtitle {
  font-family: var(--font-body);
  font-size: var(--typo-body-lg-size);
  line-height: var(--typo-body-lg-line-height);
  font-weight: var(--typo-body-lg-weight);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-xl, 2rem);
  max-width: 60ch;
  margin-left: auto;
  margin-right: auto;
}

/* CTA Button */
.cta-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-body);
  font-size: var(--typo-button-size);
  line-height: var(--typo-button-line-height);
  font-weight: var(--typo-button-weight);
  letter-spacing: var(--typo-button-letter-spacing);
  background-color: var(--cta-primary-bg);
  color: var(--cta-primary-text);
  padding: var(--spacing-sm, 0.75rem) var(--spacing-xl, 2rem);
  border-radius: var(--border-radius-md, 0.5rem);
  border: none;
  cursor: pointer;
  text-decoration: none;
  transition: background-color 0.2s ease;
}

.cta-primary:hover {
  background-color: var(--cta-primary-hover);
}

/* Paragraph / body text */
.body-text {
  font-family: var(--font-body);
  font-size: var(--typo-body-md-size);
  line-height: var(--typo-body-md-line-height);
  font-weight: var(--typo-body-md-weight);
  color: var(--text-primary);
  max-width: 65ch;
  margin: 0 auto var(--spacing-lg, 1.5rem);
}

/* Responsive */
@media (max-width: 767px) {
  .hero__title {
    font-size: var(--typo-display-lg-size, 3rem);
    line-height: var(--typo-display-lg-line-height, 1.2);
  }
  .hero__subtitle {
    font-size: var(--typo-body-md-size, 1rem);
  }
  .cta-primary {
    padding: var(--spacing-sm, 0.75rem) var(--spacing-lg, 1.5rem);
  }
}
""".strip()


def build_html(semantic_colors: dict[str, str], typography: dict[str, Any]) -> str:
    """Generate complete HTML with inline CSS."""
    css_vars = build_css_variables(semantic_colors, typography)
    component_css = build_component_styles()

    # Get some resolved values for inline styles where needed
    title_color = semantic_colors.get("text.primary", "#171717")
    subtitle_color = semantic_colors.get("text.secondary", "#525252")
    cta_bg = semantic_colors.get("cta.primary_bg", "#2563EB")
    cta_text = semantic_colors.get("cta.primary_text", "#FAFAFA")
    bg_color = semantic_colors.get("background.primary", "#FAFAFA")

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Design Superpowers — Output</title>
  <style>
{css_vars}

{component_css}
  </style>
</head>
<body style="margin: 0; font-family: var(--font-body); background-color: {bg_color}; color: {title_color};">
  <section class="hero" aria-labelledby="hero-title">
    <h1 id="hero-title" class="hero__title">Design Superpowers</h1>
    <p class="hero__subtitle">Sistema autónomo de diseño visual, UX, branding y editorial con viabilidad de plataforma integrada.</p>
    <a href="#" class="cta-primary">Solicitar Demo</a>
  </section>
  <main style="padding: 2rem; max-width: 800px; margin: 0 auto;">
    <p class="body-text">
      Este HTML fue generado automáticamente por el Builder HTML de FASE 4,
      consumiendo tokens de color y tipografía del design system.
      Las decisiones de diseño provienen de FASE 3 y su viabilidad fue verificada en FASE 2.
    </p>
  </main>
</body>
</html>"""
    return html


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Builder HTML FASE 4")
    parser.add_argument("--decisions", default="tmp/design-decisions-typography.json",
                        help="design-decisions.json with color + typography decisions")
    parser.add_argument("--output", default="index.html", help="Output HTML file")
    args = parser.parse_args()

    # Load tokens
    colors_tokens = load_json(COLORS_FILE)
    typo_tokens = load_json(TYPOGRAPHY_FILE)

    # Resolve semantic colors
    semantic_colors = resolve_all_semantic(colors_tokens)

    # Build HTML
    html = build_html(semantic_colors, typo_tokens)

    # Write output
    output_path = Path(args.output)
    output_path.write_text(html, encoding="utf-8")

    print(f"✅ HTML generado: {output_path}")
    print(f"   Semantic colors resueltos: {len(semantic_colors)}")
    print(f"   Tipografía pasos: {len(typo_tokens.get('scale', {}).get('steps', {}))}")


if __name__ == "__main__":
    main()