#!/usr/bin/env python3
"""
Audit brand-guidelines.md for completeness against Kapferer Brand Identity Prism
+ operational components.

Usage: python audit-brand-guidelines.py <brand-guidelines.md> [--output audit.json]

Returns exit code 0, writes JSON to stdout and optionally to file.
"""

import sys, json, re
from pathlib import Path
from typing import Dict, List, Any


REQUIRED_SECTIONS = {
    # Kapferer Prism facets
    "physique": {
        "required": True,
        "keywords": ["paleta", "tipografia", "logo", "imagery", "estilo visual", "color", "fuente"],
        "section_name": "Physique (Identidad Física)"
    },
    "personality": {
        "required": True,
        "keywords": ["personalidad", "tono", "voz", "aaker", "dimensiones", "caracter"],
        "section_name": "Personality (Personalidad)"
    },
    "culture": {
        "required": True,
        "keywords": ["valores", "mision", "vision", "arquetipo", "cultura", "proposito"],
        "section_name": "Culture (Cultura)"
    },
    "relationship": {
        "required": True,
        "keywords": ["relacion", "servicio", "promesa", "cliente", "experiencia"],
        "section_name": "Relationship (Relación)"
    },
    "reflection": {
        "required": True,
        "keywords": ["reflejo", "audiencia", "usuario", "persona", "target", "publico"],
        "section_name": "Reflection (Reflejo)"
    },
    "self_image": {
        "required": True,
        "keywords": ["esencia", "tagline", "posicionamiento", "autoimagen", "identidad nucleo"],
        "section_name": "Self-Image (Autoimagen)"
    },
    # Operational
    "governance": {
        "required": True,
        "keywords": ["gobernanza", "aprobacion", "excepciones", "evolucion", "council", "comite"],
        "section_name": "Governance (Gobernanza)"
    },
}


def load_markdown(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return ""


def find_section(content: str, keywords: List[str]) -> Dict[str, Any]:
    """Busca sección que contenga keywords. Retorna {found, line_start, line_end, excerpt}."""
    lines = content.split("\n")
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(kw.lower() in line_lower for kw in keywords):
            # Encontrar extensión de la sección (hasta siguiente heading o 20 líneas)
            start = i
            end = min(i + 30, len(lines))
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("#") and j > i:
                    end = j
                    break
            excerpt = "\n".join(lines[start:end])[:500]
            return {"found": True, "line_start": start + 1, "line_end": end, "excerpt": excerpt}
    return {"found": False, "line_start": None, "line_end": None, "excerpt": ""}


def detect_contradictions(content: str) -> List[str]:
    """Detecta contradicciones simples (formal vs casual, etc.). Heurístico."""
    contradictions = []
    content_lower = content.lower()

    # Formal vs casual en tono
    if "formal" in content_lower and "casual" in content_lower:
        # Verificar si están en contexto de tono de voz
        formal_idx = content_lower.find("formal")
        casual_idx = content_lower.find("casual")
        if abs(formal_idx - casual_idx) < 500:  # cerca en el texto
            contradictions.append("Tono de voz: menciona 'formal' y 'casual' en contexto cercano")

    # Paleta: colores contradictorios (ej. "solo azul" y "rojo principal")
    # Muy heurístico, solo bandera
    if "solo azul" in content_lower and "rojo" in content_lower:
        contradictions.append("Paleta: 'solo azul' y mención de rojo")

    # Arquetipo múltiple sin claridad primaria/secundaria
    archetype_keywords = ["hero", "explorer", "sage", "innocent", "creator", "ruler",
                          "magician", "lover", "caregiver", "jester", "everyman", "outlaw"]
    found_archetypes = [a for a in archetype_keywords if a in content_lower]
    if len(found_archetypes) > 2:
        contradictions.append(f"Múltiples arquetipos mencionados sin jerarquía clara: {', '.join(found_archetypes)}")

    return contradictions


def audit_brand_guidelines(md_path: Path) -> Dict[str, Any]:
    content = load_markdown(md_path)
    if not content:
        return {
            "manual_exists": False,
            "completeness_score": 0.0,
            "missing_sections": [s["section_name"] for s in REQUIRED_SECTIONS.values()],
            "contradictions": [],
            "decisions_requiring_human_review": [
                "dec-brand-001", "dec-brand-002", "dec-brand-003", "dec-brand-004",
                "dec-brand-005", "dec-brand-006", "dec-brand-007", "dec-brand-008"
            ],
            "section_details": {}
        }

    results = {}
    found_count = 0
    missing = []
    decisions_requiring_review = []

    # Map section to decision IDs
    section_to_decisions = {
        "physique": ["dec-brand-007"],
        "personality": ["dec-brand-003", "dec-brand-004"],
        "culture": ["dec-brand-001", "dec-brand-002"],
        "relationship": ["dec-brand-005"],
        "reflection": ["dec-brand-005"],
        "self_image": ["dec-brand-005", "dec-brand-006"],
        "governance": ["dec-brand-008"],
    }

    for key, spec in REQUIRED_SECTIONS.items():
        section_result = find_section(content, spec["keywords"])
        results[key] = {
            "section_name": spec["section_name"],
            "found": section_result["found"],
            "location": {"start": section_result["line_start"], "end": section_result["line_end"]} if section_result["found"] else None,
            "excerpt": section_result["excerpt"] if section_result["found"] else ""
        }
        if section_result["found"]:
            found_count += 1
        else:
            missing.append(spec["section_name"])
            decisions_requiring_review.extend(section_to_decisions.get(key, []))

    contradictions = detect_contradictions(content)
    if contradictions:
        # Todas las decisiones afectadas por contradicciones
        decisions_requiring_review = list(set(decisions_requiring_review + [
            "dec-brand-001", "dec-brand-002", "dec-brand-003", "dec-brand-004",
            "dec-brand-005", "dec-brand-006", "dec-brand-007", "dec-brand-008"
        ]))

    completeness_score = found_count / len(REQUIRED_SECTIONS)

    return {
        "manual_exists": True,
        "completeness_score": round(completeness_score, 2),
        "missing_sections": missing,
        "contradictions": contradictions,
        "decisions_requiring_human_review": sorted(list(set(decisions_requiring_review))),
        "section_details": results
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python audit-brand-guidelines.py <brand-guidelines.md> [--output audit.json]", file=sys.stderr)
        sys.exit(1)

    md_path = Path(sys.argv[1])
    output_path = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = Path(sys.argv[idx + 1])

    result = audit_brand_guidelines(md_path)

    # Output to stdout (JSON)
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    print()

    # Optional file output
    if output_path:
        output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    sys.exit(0)


if __name__ == "__main__":
    main()