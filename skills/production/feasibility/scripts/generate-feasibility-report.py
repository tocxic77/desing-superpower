#!/usr/bin/env python3
"""
generate-feasibility-report.py — Productor de FASE 2

Fuente de verdad: skills/production/feasibility/references/platform-constraints.md
Las tablas §1.x (Elementor) y §2.x (Figma) se parsean en runtime; este script NO
mantiene su propia tabla de clasificación. Ver
tests/feasibility/test_generate_report.py::test_matchers_cover_every_md_row.

Uso:
    python generate-feasibility-report.py <brief-normalizado.json> [--platform elementor|figma|both] [-o out.json]

Exit codes:
    0 = todas green/yellow (FASE 2 pasa)
    2 = hay decisiones red (el workflow bloquea en FASE 3)
    1 = error de entrada
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
CONSTRAINTS_MD = ROOT / "skills" / "production" / "feasibility" / "references" / "platform-constraints.md"

PLATFORM_HEADING = re.compile(r"^##\s+(\d)\.\s+(.+)$")
CLASS_HEADING = re.compile(r"^###\s+[\d.]+\s+(Green|Yellow|Red)\b", re.I)

STOPWORDS = {
    "con", "para", "the", "and", "del", "los", "las", "una", "uno", "por", "que",
    "sobre", "desde", "sus", "sin", "via", "mas", "como", "solo", "es", "en",
    "de", "la", "el", "y", "o", "a", "e", "por", "pro",
}

# Patrón regex explícito por fila del markdown (clave = normalize(nombre de la fila)).
# No se auto-derivan tokens del nombre: los nombres del markdown son demasiado
# genéricos ("Widgets nativos (...)", "Theme Style ...") y el auto-matching producía
# falsos positivos. El test exige cobertura total y ausencia de patrones huérfanos.
PATTERNS: dict[str, str] = {
    "flexbox containers": r"\bflexbox\b|\bflex(?:box)? container\b|contenedor(?:es)? flex",
    "theme style → global colors/typography": r"theme style|site settings|global colou?rs?|global typograph",
    "widgets nativos (heading, text editor, button, icon, image, spacer, divider)": r"heading widget|text editor|button widget|icon widget|image widget|\bspacer\b|\bdivider\b|widgets? nativos?",
    "loop grid / loop carousel": r"loop grid|loop carousel",
    "form widget (nativo)": r"form widget|formulario nativo",
    "motion effects (entrada, scroll, mouse)": r"motion effects?|fade-up|entrance animation",
    "custom css por widget/container": r"custom css|css custom|css por widget|linear-gradient|var\(--",
    "breakpoints: mobile (≤767px), tablet (768-1024px), desktop (≥1025px)": r"breakpoints?|\bresponsive\b|(?:\bdesktop\b.*\btablet\b)|(?:\btablet\b.*\bmobile\b)",
    "grid asimetrico / masonry": r"masonry|grid asimetric|asymmetric grid|grid asym",
    "variables css fluidas (clamp)": r"\bclamp\b|\bfluida?s?\b|\bfluid\b",
    "componentes anidados complejos (card con sub-componentes)": r"\bnested\b|anidad[oa]s?",
    "animaciones lottie": r"lottie",
    "custom post type fields en loop": r"custom post type|\bacf\b|dynamic tags?",
    "sticky header transparente → solido en scroll": r"sticky",
    "fuentes variables (variable fonts) — single-axis (weight) via @font-face + custom css": r"single[-\s]?axis|weight[-\s]?only|@font-face",
    "css subgrid": r"subgrid",
    "container queries": r"container quer",
    "view transitions api": r"view transitions?",
    "web components / shadow dom": r"web components?|shadow dom",
    "fuentes variables (variable fonts) — multi-axis / font-variation-settings dinamico": r"multi[-\s]?axis|font-variation-settings|\bwdth\b|\bopsz\b|\bslnt\b",
    "aspect-ratio en image widget": r"aspect[-\s]?ratio",
    "scroll-driven animations (css animation-timeline: scroll())": r"scroll[-\s]driven|animation-timeline",
    "form multi-step nativo": r"multi[-\s]?step",
    "variables (color, number, string, boolean)": r"\bvariables?\b|global colou?rs?",  # equivalencia: Global Colors (WP) = Variables (Figma)
    "component properties (variant, text, boolean, instance swap)": r"component propert|\binstance swap\b|\bvariant\s*=",
    "auto layout (stack, grid, wrap)": r"auto[-\s]?layout|\bflexbox\b|\bflex container\b",  # equivalencia: Flexbox (WP) = Auto Layout
    "text styles + variable fonts": r"text styles?",
    "color styles (legacy) → migrados a variables": r"colou?r styles?",
    "export: svg, png, webp, pdf": r"\bexport\b|\bsvg\b|\bwebp\b",
    "design tokens json (plugin: figma tokens / tokens studio)": r"design tokens?|tokens studio|figma tokens",
    "component playground / interactive components": r"component playground|interactive components?|\binteraction\b",
    "widgets basicos (heading, button, image, icon)": r"text style|heading component|button component|image component|icon component|\bwidgets? basicos?|\bbutton widget\b|\bimage widget\b|\bheading widget\b|widget nativo",
    "variables semanticas (global colors/typography)": r"variable.*color|semantic.*color|global colou?rs?|global typograph|color variable|typography variable|global typography|typography global",
    "css custom properties export directo": r"css custom propert|css variables? export",
    "responsive breakpoints en auto layout": r"breakpoints?",
    "motion / prototype animations → css": r"smart animate|prototyp",
    "content reel / data-driven components": r"content reel|data-driven",
    "variable fonts con axes no estandar (opsz, grad, etc.)": r"\bgrad\b|axes? no estandar|non[-\s]standard axes?",
    "blend modes avanzados (difference, exclusion, hue, etc.)": r"blend modes?|\bdifference\b|\bexclusion\b|hue blend",
    "filters no estandar (blur() en background, backdrop-filter)": r"backdrop|filters? no estandar|\bblur\(",
    "text on path / curved text": r"text on path|curved text",
    "component properties anidadas > 2 niveles": r"nested component|component properties anidadas",
    "scroll-based animations en prototipo": r"scroll[-\s]based|scroll animation",
    "grid no uniforme (tracks con minmax, auto-fit, named lines)": r"minmax|auto-fit|named lines|grid no uniforme",
    "fuentes no web-safe sin licencia web": r"licencia web|non[-\s]?web[-\s]?safe|no web[-\s]?safe",
    "efectos de capa (inner shadow, outer glow, drop shadow con spread)": r"inner shadow|outer glow|drop shadow",
}


def row_pattern(row: dict[str, Any]) -> re.Pattern[str] | None:
    pat = PATTERNS.get(row["capability_norm"])
    return re.compile(pat, re.I) if pat else None

def normalize(text: str) -> str:
    text = text.replace("*", "").replace("`", "").strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).lower().strip()


def parse_constraints(md_path: Path = CONSTRAINTS_MD) -> list[dict[str, Any]]:
    """Una fila por capacidad de las tablas §1.x (Elementor) y §2.x (Figma)."""
    rows: list[dict[str, Any]] = []
    platform = None
    klass = None
    in_fence = False

    for raw in md_path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        pm = PLATFORM_HEADING.match(line)
        if pm:
            title = pm.group(2).upper()
            if "ELEMENTOR" in title:
                platform, klass = "elementor", None
            elif "FIGMA" in title:
                platform, klass = "figma", None
            else:
                platform, klass = None, None
            continue

        cm = CLASS_HEADING.match(line)
        if cm:
            klass = cm.group(1).lower()
            continue

        if not (platform and klass) or not line.startswith("|"):
            continue

        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        capability = cells[0].replace("**", "").strip()
        if not capability or capability.lower().startswith("capacidad") or set(capability) <= set("-: "):
            continue

        rows.append({
            "platform": platform,
            "classification": klass,
            "capability": capability,
            "capability_norm": normalize(capability),
            "workaround": cells[1] if len(cells) > 1 else "",
            "detail": " | ".join(cells[1:]),
            "example": next((c for c in cells if "dec-" in c), ""),
        })
    return rows


def match_rows(rows: list[dict[str, Any]], text: str) -> list[dict[str, Any]]:
    """Filas del markdown cuyo patrón explícito aparece en el texto de la decisión."""
    return [r for r in rows if (pat := row_pattern(r)) and pat.search(text)]


RANK = {"green": 0, "yellow": 1, "red": 2}


def classify(rows: list[dict[str, Any]], text: str, platform: str, css_prohibited: bool) -> dict[str, Any]:
    platform_rows = [r for r in rows if r["platform"] == platform]
    matched = match_rows(platform_rows, text)

    if not matched:
        return {
            "platform": platform,
            "classification": "yellow",
            "capability": "no mapeada en platform-constraints.md",
            "constraints": [f"{platform}: capacidad no documentada"],
            "workaround": "Revisión manual: la capacidad no aparece en §1/§2 del markdown",
            "blocking_reason": None,
        }

    worst = max(matched, key=lambda r: RANK[r["classification"]])
    klass = worst["classification"]
    workaround = worst["workaround"] if klass in ("yellow", "red") else None
    blocking = None

    if klass == "yellow" and css_prohibited and "custom css" in normalize(worst["detail"]):
        klass = "red"
        blocking = (f"yellow escalado a red: el workaround de «{worst['capability']}» "
                    f"depende de Custom CSS y el brief lo prohíbe")
        workaround = None

    if klass == "red" and not blocking:
        blocking = f"Bloqueado en {platform}: «{worst['capability']}»"

    return {
        "platform": platform,
        "classification": klass,
        "capability": worst["capability"],
        "constraints": [f"{platform}: {worst['capability']} ({klass})"],
        "workaround": workaround,
        "blocking_reason": blocking,
    }


def detect_custom_css_prohibited(text: str) -> bool:
    """¿El brief prohíbe CSS custom? Convierte yellow -> red cuando el workaround lo exige."""
    t = normalize(text)
    return any(re.search(p, t) for p in [
        r"sin\s+css", r"no\s+css", r"sin\s+custom\s+css", r"no\s+custom\s+css",
        r"sin\s+codigo", r"prohibido\s+css", r"sin\s+html\s+personalizado",
        r"only\s+native", r"solo\s+nativo", r"no\s+css\s+custom",
    ])


def decision_text(dec: dict[str, Any]) -> str:
    parts = [dec.get("decision", ""), dec.get("rationale", ""), dec.get("category", "")]
    parts += [str(c) for c in (dec.get("constraints") or [])]
    return " ".join(p for p in parts if p)


def _decompose_mandatory(mand: str, idx: int) -> list[dict[str, Any]]:
    """Descompone un mandatorio abstracto en decisiones de capacidad concretas."""
    m = mand.lower()
    out = []
    base = f'mand-{idx:03d}'
    
    if 'hero' in m:
        out.extend([
            {'decision_id': f'{base}-a', 'decision': 'Hero: layout con Flexbox Containers',
             'rationale': 'Hero section requiere layout responsive de 2 columnas', 'category': 'layout'},
            {'decision_id': f'{base}-b', 'decision': 'Hero: imagen principal con Image widget',
             'rationale': 'Imagen hero nativa accesible', 'category': 'layout'},
            {'decision_id': f'{base}-c', 'decision': 'Hero: tipografía display via Global Typography',
             'rationale': 'H1 hero usa scale Display XL', 'category': 'typography'},
            {'decision_id': f'{base}-d', 'decision': 'Hero: color de fondo/overlay via Global Colors',
             'rationale': 'Background hero mapeado a token semántico', 'category': 'color'},
        ])
        if 'video' in m or 'background' in m:
            out.append({'decision_id': f'{base}-bg', 'decision': 'Hero: video background / parallax',
                        'rationale': 'Video background requiere Custom CSS + performance budget',
                        'category': 'layout'})
    elif 'cta' in m or 'call to action' in m or 'botón principal' in m:
        out.extend([
            {'decision_id': f'{base}-a', 'decision': 'CTA: Button widget nativo',
             'rationale': 'Botón principal usa widget Button de Elementor', 'category': 'layout'},
            {'decision_id': f'{base}-b', 'decision': 'CTA: color semántico via Global Colors',
             'rationale': 'cta.primary_bg mapeado a Global Color', 'category': 'color'},
            {'decision_id': f'{base}-c', 'decision': 'CTA: tipografía button via Global Typography',
             'rationale': 'Label del botón usa scale Button', 'category': 'typography'},
            {'decision_id': f'{base}-d', 'decision': 'CTA: placement en Flexbox Container',
             'rationale': 'Posicionamiento responsive del CTA', 'category': 'layout'},
        ])
    elif 'contraste' in m or 'contrast' in m or 'aa' in m:
        # No es capacidad de plataforma -> validation_only
        out.append({'decision_id': f'{base}-val', 'decision': mand,
                    'rationale': 'Validación AA en FASE 5 con contrast_analyzer.py',
                    'category': 'validation_only'})
    elif 'social proof' in m or 'testimon' in m or 'reseña' in m:
        out.extend([
            {'decision_id': f'{base}-a', 'decision': 'Social proof: grid de cards con Flexbox Containers',
             'rationale': 'Sección testimonials usa layout grid responsive', 'category': 'layout'},
            {'decision_id': f'{base}-b', 'decision': 'Social proof: imágenes de avatar con Image widget',
             'rationale': 'Avatares de clientes', 'category': 'layout'},
            {'decision_id': f'{base}-c', 'decision': 'Social proof: tipografía body via Global Typography',
             'rationale': 'Texto de testimonios en scale Body', 'category': 'typography'},
        ])
    elif 'formul' in m or 'form ' in m or 'contact' in m:
        out.extend([
            {'decision_id': f'{base}-a', 'decision': 'Formulario: Form widget nativo',
             'rationale': 'Formulario de contacto usa widget Form nativo', 'category': 'interaction'},
            {'decision_id': f'{base}-b', 'decision': 'Formulario: validación HTML5 + honeypot',
             'rationale': 'Validación nativa sin dependencias', 'category': 'interaction'},
        ])
    else:
        # Fallback: decisión genérica
        out.append({'decision_id': f'{base}', 'decision': mand,
                    'rationale': 'Mandatorio sin descomposición conocida', 'category': 'layout'})
    return out


def infer_decisions(brief: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Deriva decisiones del brief, aceptando dos formas:
      - brief.mandatories: ["Hero section", "CTA principal"] (canónico)
      - requirements: [{id, description}, ...] (fixtures)
    Descompone mandatorios abstractos en capacidades concretas.
    """
    inner = brief.get('brief') if isinstance(brief.get('brief'), dict) else {}
    mandatories = inner.get('mandatories') or brief.get('mandatories') or []
    requirements = brief.get('requirements') or inner.get('requirements') or []

    out: list[dict[str, Any]] = []
    for i, item in enumerate(mandatories, start=1):
        desc = item if isinstance(item, str) else str(item.get('description', item))
        out.extend(_decompose_mandatory(desc, i))
    
    for req in requirements:
        if isinstance(req, dict):
            rid = req.get('id') or f'req-{len(out) + 1:03d}'
            desc = req.get('description') or req.get('requirement') or ''
        else:
            rid, desc = f'req-{len(out) + 1:03d}', str(req)
        out.append({'decision_id': rid, 'decision': desc,
                    'rationale': 'Requerimiento del brief', 'category': 'layout'})
    return out


def generate(brief_path: Path, platform: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    proposed = brief.get("decisions_proposed") or infer_decisions(brief)
    if not proposed:
        raise ValueError(
            "el brief no contiene decisiones evaluables: se esperaba 'decisions_proposed', "
            "'brief.mandatories' o 'requirements'. Un report vacío NO es un pass.")

    if platform == "auto":
        inner = brief.get("brief") if isinstance(brief.get("brief"), dict) else {}
        declared = (inner.get("constraints") or {}).get("platforms") or []
        platform = "both" if len(declared) != 1 else declared[0]

    # Separar validation_only (no son capacidades de plataforma)
    validation_only = [d for d in proposed if d.get("category") == "validation_only"]
    proposed = [d for d in proposed if d.get("category") != "validation_only"]

    platforms = ["elementor", "figma"] if platform == "both" else [platform]
    css_prohibited = detect_custom_css_prohibited(json.dumps(brief, ensure_ascii=False))

    evaluated = []
    for dec in proposed:
        text = decision_text(dec)
        per = [classify(rows, text, p, css_prohibited) for p in platforms]
        final = max(per, key=lambda r: RANK[r["classification"]])
        evaluated.append({
            "decision_id": dec.get("decision_id", "dec-unknown"),
            "requirement": dec.get("decision", "")[:160],
            "platform_capability": "; ".join(f"{r['platform']}: {r['capability']}" for r in per),
            "classification": final["classification"],
            "constraints": [c for r in per for c in r["constraints"]],
            "workaround": (next((r["workaround"] for r in per if r["workaround"]), None)
                           if final["classification"] == "yellow" else None),
            "blocking_reason": next((r["blocking_reason"] for r in per if r["blocking_reason"]), None),
            "per_platform": {r["platform"]: r["classification"] for r in per},
        })

    # Añadir validation_only como green (no bloquean, no son capacidades)
    for val in validation_only:
        evaluated.append({
            "decision_id": val.get("decision_id", "val-unknown"),
            "requirement": val.get("decision", "")[:160],
            "platform_capability": "validation_only (no platform capacity)",
            "classification": "green",
            "constraints": ["Validación en FASE 5: contrast_analyzer.py"],
            "workaround": None,
            "blocking_reason": None,
            "per_platform": {"elementor": "green", "figma": "green"},
        })

    counts = {k: sum(1 for d in evaluated if d["classification"] == k) for k in RANK}
    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "generator": "generate-feasibility-report.py",
            "source_of_truth": str(CONSTRAINTS_MD.relative_to(ROOT)).replace("\\", "/"),
            "platform": platform,
            "brief_id": brief.get("project", brief.get("project_id", "unknown")),
            "css_custom_prohibited": css_prohibited,
        },
        "platform": platform,
        "overall_feasibility": "blocked" if counts["red"] else ("conditional" if counts["yellow"] else "pass"),
        "summary": counts,
        "requirements": brief.get("requirements", []),
        "decisions_evaluated": evaluated,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera feasibility-report.json (FASE 2)")
    ap.add_argument("brief", help="brief-normalizado.json")
    ap.add_argument("--platform", choices=["elementor", "figma", "both", "auto"], default="auto",
                    help="auto = lee brief.constraints.platforms")
    ap.add_argument("-o", "--output", default="feasibility-report.json")
    ap.add_argument("--md", default=str(CONSTRAINTS_MD))
    args = ap.parse_args()

    brief = Path(args.brief)
    if not brief.exists():
        print(f"❌ No existe {brief}", file=sys.stderr)
        return 1

    rows = parse_constraints(Path(args.md))
    if not rows:
        print(f"❌ No se pudo parsear ninguna capacidad de {args.md}", file=sys.stderr)
        return 1

    report = generate(brief, args.platform, rows)
    Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    s = report["summary"]
    print(f"✅ {args.output}: {s['green']} green, {s['yellow']} yellow, {s['red']} red "
          f"(overall: {report['overall_feasibility']})")
    for d in report["decisions_evaluated"]:
        if d["classification"] != "green":
            print(f"   {d['classification'].upper():6} {d['decision_id']}: {d['platform_capability']}")
    if s["red"]:
        print("⛔ Hay decisiones RED: FASE 3 debe bloquear estas decisiones.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
