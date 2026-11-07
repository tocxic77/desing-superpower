#!/usr/bin/env python3
"""
build_fixtures.py — fixtures canónicos v0.2 para el skill editorial.

Genera en `out`:
  design-decisions.json             array canónico (color + typography + branding)
  feasibility-report.json           report con entradas para cada decisión
  editorial-composition.json        output editorial, branding complete
  draft-editorial-composition.json  output editorial, branding incomplete (004/006 provisionales)

Semántica de campos: specialist = productor (dominio), category = dominio, owner = aprobador.
"""

import copy
import json
from pathlib import Path

EV = "skills/creative-direction/editorial/references/editorial-evidence.md"

COLOR_CONSTRAINTS = ["WCAG 2.2 AA validado en FASE 5", "Elementor Global Color mapping 1:1"]
TYPO_CONSTRAINTS = ["Licencia web verificada", "Figma Variable + Elementor Custom CSS scoped"]
BRAND_CONSTRAINTS = ["Aprobación humana obligatoria (posición de marca)", "Consistente con brand-guidelines.md"]


def decision(dec_id, specialist, category, text, rationale, feas_ref, evidence, refs=None,
             human=False, constraints=None, validation=False, extra=None):
    d = {
        "decision_id": dec_id,
        "specialist": specialist,
        "category": category,
        "decision": text,
        "rationale": rationale,
        "owner": "art-director",
        "constraints": constraints or ["ninguna conocida"],
        "feasibility_ref": feas_ref,
        "validation_required": validation,
        "human_review_required": human,
        "alternatives_considered": [],
        "platform_specific": {},
        "references": refs or {},
    }
    if evidence:
        d["evidence_refs"] = evidence
    if extra:
        d.update(extra)
    return d


COLOR = [
    decision(f"dec-color-{i:03d}", "color", "color", txt,
             "Propuesta de paleta. Contraste no se decide aquí (FASE 5). Sin evidencia empírica 2020+ de color específico → conversión.",
             f"dec-color-{i:03d}", ["skills/creative-direction/color/references/color-evidence.md"],
             constraints=COLOR_CONSTRAINTS)
    for i, txt in enumerate([
        "brand/primary/600 como cta.primary_bg",
        "Jerarquía de CTA: primary filled, secondary outline, ghost",
        "Escala neutra 50-950 y superficies background.*",
        "Estados de feedback success/warning/error/info",
        "Texto on-surface / on-surface-variant sobre superficies",
        "Tokens semánticos de color consumidos por editorial",
    ], start=1)
]

TYPO = [
    decision(f"dec-typography-{i:03d}", "typography", "typography", txt,
             "Escala y familias desde tokens. Sin evidencia empírica 2020+ de font específica → legibilidad.",
             f"dec-typography-{i:03d}", ["skills/creative-direction/typography/references/typography-evidence.md"],
             constraints=TYPO_CONSTRAINTS)
    for i, txt in enumerate([
        "Inter Variable como font UI principal (400-700)",
        "Font display de marca con fallback system-ui",
        "Type scale ratio 1.25 con base 16px (steps -2..+4)",
        "Line-height: body 1.5, heading 1.25",
        "Roles semánticos de texto (heading/body/label/caption)",
        "Pesos 400/500/600/700 disponibles en web",
        "Mono para datos y código",
        "Fallbacks y font loading",
    ], start=1)
]

BRAND = [
    decision(f"dec-brand-{i:03d}", "branding", "branding", txt,
             "Decisión de marca: requiere aprobación humana explícita.",
             f"dec-brand-{i:03d}", ["skills/creative-direction/branding/references/branding-evidence.md"],
             human=True, constraints=BRAND_CONSTRAINTS)
    for i, txt in enumerate([
        "Arquetipo principal Hero",
        "Arquetipo secundario Explorer",
        "Personalidad Aaker (Competence, Excitement)",
        "Tono de voz (do/dont)",
        "Posicionamiento y tagline",
        "Esencia de marca",
        "Sistema visual (logo usage, imagery)",
        "Gobernanza de marca",
    ], start=1)
]

DECISIONS = COLOR + TYPO + BRAND

ED_COMPLETE = [
    {
        "decision_id": "dec-editorial-001", "specialist": "editorial", "category": "editorial",
        "decision": "Tokens de color, typography y branding consumidos como single source of truth",
        "rationale": "Vignelli canon: coherencia de sistema. Sin evidencia empírica de retícula → conversión.",
        "owner": "art-director",
        "constraints": ["No introducir valores fuera de design-system/tokens"],
        "feasibility_ref": "dec-editorial-001",
        "validation_required": False, "human_review_required": False,
        "alternatives_considered": [], "platform_specific": {},
        "evidence_refs": [f"{EV}#vignelli-canon"],
        "references": {
            "color_decisions": [f"dec-color-{i:03d}" for i in range(1, 7)],
            "typography_decisions": [f"dec-typography-{i:03d}" for i in range(1, 9)],
            "branding_decisions": [f"dec-brand-{i:03d}" for i in range(1, 9)],
        },
    },
    {
        "decision_id": "dec-editorial-002", "specialist": "editorial", "category": "editorial",
        "decision": "Jerarquía compositiva: hero(title step+4, subtitle step+1, CTA primary) → features(step+2) → proof(step+1) → CTA(step+1) → footer(step-1)",
        "rationale": "Lupton hierarchy + Tschichold functional hierarchy; coherencia con type scale aprobada.",
        "owner": "art-director",
        "constraints": ["Jerarquía limitada a steps -2..+4", "Un solo CTA primary por sección"],
        "feasibility_ref": "dec-editorial-002",
        "validation_required": True, "human_review_required": False,
        "alternatives_considered": [], "platform_specific": {},
        "evidence_refs": [f"{EV}#lupton-hierarchy", f"{EV}#tschichold-whitespace"],
        "references": {"typography_scale": "dec-typography-003", "cta_hierarchy": "dec-color-002",
                       "typography_line_height": "dec-typography-004"},
    },
    {
        "decision_id": "dec-editorial-003", "specialist": "editorial", "category": "editorial",
        "decision": "Retícula 12col/24px gutter/48px margin desktop; 8/16/32 tablet; 4/12/24 mobile; baseline 24px",
        "rationale": "Müller-Brockmann + Samara grid anatomy. Feasibility: Figma green, Elementor yellow (Custom CSS grid).",
        "owner": "art-director",
        "constraints": ["Baseline = font-size base x line-height body", "Elementor: Custom CSS grid scoped"],
        "feasibility_ref": "dec-editorial-003",
        "validation_required": True, "human_review_required": False,
        "alternatives_considered": [], "platform_specific": {},
        "evidence_refs": [f"{EV}#muller-brockmann-grids", f"{EV}#samara-grid-anatomy"],
        "references": {},
    },
    {
        "decision_id": "dec-editorial-004", "specialist": "editorial", "category": "editorial",
        "decision": "Zonas de branding: logo top-left 4col x 3rows (clear space 2 baselines), tagline hero 8col x 2rows",
        "rationale": "Kapferer physique + Vignelli system: el espacio de marca es requisito estructural.",
        "owner": "art-director",
        "constraints": ["Clear space mínimo 2 baseline units", "Logo sin recolorear ni deformar"],
        "feasibility_ref": "dec-editorial-004",
        "validation_required": True, "human_review_required": False,
        "alternatives_considered": [], "platform_specific": {},
        "evidence_refs": [f"{EV}#kapferer-physique", f"{EV}#vignelli-canon"],
        "references": {"brand_archetype": "dec-brand-001", "brand_visual_system": "dec-brand-007",
                       "grid": "dec-editorial-003"},
    },
    {
        "decision_id": "dec-editorial-005", "specialist": "editorial", "category": "editorial",
        "decision": "Ritmo vertical: baseline 24px; line-height body 1.5, heading 1.25, caption 1.5; section padding 96/72/48",
        "rationale": "Bringhurst rhythm + Müller-Brockmann baseline grid.",
        "owner": "art-director",
        "constraints": ["Section padding múltiplo del baseline"],
        "feasibility_ref": "dec-editorial-005",
        "validation_required": True, "human_review_required": False,
        "alternatives_considered": [], "platform_specific": {},
        "evidence_refs": [f"{EV}#bringhurst-rhythm", f"{EV}#muller-brockmann-grids"],
        "references": {"typography_line_height": "dec-typography-004", "grid_baseline": "dec-editorial-003"},
    },
    {
        "decision_id": "dec-editorial-006", "specialist": "editorial", "category": "editorial",
        "decision": "Densidad: whitespace ratio 0.40 para arquetipo Hero; ocupación hero 0.70, features 0.60, proof 0.55",
        "rationale": "Hofmann density + Tschichold whitespace; mapeado al arquetipo aprobado.",
        "owner": "art-director",
        "constraints": ["Densidad sujeta al arquetipo aprobado"],
        "feasibility_ref": "dec-editorial-006",
        "validation_required": True, "human_review_required": False,
        "alternatives_considered": [], "platform_specific": {},
        "evidence_refs": [f"{EV}#hofmann-density", f"{EV}#tschichold-whitespace"],
        "references": {"brand_archetype": "dec-brand-001", "grid": "dec-editorial-003"},
    },
    {
        "decision_id": "dec-editorial-007", "specialist": "editorial", "category": "editorial",
        "decision": "Library de 8 secciones (hero-primary, hero-branded, feature-grid, proof-testimonial, cta-section, content-band, footer, divider)",
        "rationale": "Estructura de página Müller-Brockmann + agrupación de módulos Samara. Convención de industria: sin estudio empírico que la respalde.",
        "owner": "art-director",
        "constraints": ["Solo variantes CTA existentes", "Solo heading levels de la escala aprobada"],
        "feasibility_ref": "dec-editorial-007",
        "validation_required": True, "human_review_required": False,
        "alternatives_considered": [], "platform_specific": {},
        "evidence_refs": [f"{EV}#samara-layout-patterns", f"{EV}#muller-brockmann-page-structure"],
        "references": {"cta_hierarchy": "dec-color-002", "typography_scale": "dec-typography-003",
                       "vertical_rhythm": "dec-editorial-005", "grid": "dec-editorial-003"},
    },
    {
        "decision_id": "dec-editorial-008", "specialist": "editorial", "category": "editorial",
        "decision": "Reflow 12→8→4 columnas con baseline constante; stacking content→media→CTA; branding zones adaptadas",
        "rationale": "Samara responsive grids. Feasibility: Elementor responsive controls y Figma constraints = green.",
        "owner": "art-director",
        "constraints": ["Stacking mobile-first: content → media → CTA", "Zonas de branding sobreviven el reflow"],
        "feasibility_ref": "dec-editorial-008",
        "validation_required": True, "human_review_required": False,
        "alternatives_considered": [], "platform_specific": {},
        "evidence_refs": [f"{EV}#samara-responsive", f"{EV}#samara-layout-patterns"],
        "references": {"grid": "dec-editorial-003", "branding_zones": "dec-editorial-004",
                       "section_library": "dec-editorial-007"},
    },
]


def editorial_meta(output_file, brand_status, provisional_ids=()):
    return {
        "generated_at": "2026-11-07T22:05:00.000000Z",
        "skill_version": "0.1.0",
        "brand_status": brand_status,
        "output_file": output_file,
        "provisional_decisions": list(provisional_ids),
        "human_review_required_count": len(provisional_ids),
    }


COMPOSITION = {
    "grid": {"columns": {"desktop": 12, "tablet": 8, "mobile": 4},
             "gutters": {"desktop": 24, "tablet": 16, "mobile": 12},
             "margins": {"desktop": 48, "tablet": 32, "mobile": 24},
             "baseline": 24},
    "hierarchy": {
        "sections": [
            {"name": "hero", "heading_level": "step+4", "subtitle_level": "step+1", "cta_variants": ["primary", "secondary"]},
            {"name": "features", "heading_level": "step+2", "body_level": "step0", "cta_variants": []},
            {"name": "proof", "heading_level": "step+1", "cta_variants": []},
            {"name": "cta-section", "heading_level": "step+1", "cta_variants": ["primary", "secondary"]},
            {"name": "footer", "heading_level": "step-1", "cta_variants": []},
        ],
    },
    "branding_zones": {"logo": {"placement": "top-left", "columns": 4, "rows": 3,
                                "clear_space_baselines": 2, "min_height_px": 32},
                       "tagline": {"placement": "hero-subtitle-zone", "columns": 8, "rows": 2},
                       "provisional": False},
    "vertical_rhythm": {"baseline_unit": 24,
                        "section_padding": {"desktop": 96, "tablet": 72, "mobile": 48}},
    "density": {"target_whitespace_ratio": 0.40, "archetype_mapping": "Hero", "provisional": False},
    "section_library": ["hero-primary", "hero-branded", "feature-grid", "proof-testimonial",
                        "cta-section", "content-band", "footer-comprehensive", "section-divider"],
    "responsive_rules": {"reflow": {"columns": {"desktop": 12, "tablet": 8, "mobile": 4},
                                    "baseline": 24},
                         "stacking_order": ["content", "media", "cta"]},
}


def draft_variant(kind="incompleto"):
    """Editorial con 004/006 provisionales porque el branding no está aprobado."""
    decs = copy.deepcopy(ED_COMPLETE)
    for d in decs:
        if d["decision_id"] == "dec-editorial-004":
            d["human_review_required"] = True
            d["provisional"] = True
            d["depends_on"] = ["dec-brand-007"]
            d["rationale"] = (f"Brand guidelines {kind} en logo_usage: espacio reservado genérico "
                              "(logo 4col x 3rows, tagline 8col x 2rows). Revalidar al aprobarse branding.")
        if d["decision_id"] == "dec-editorial-006":
            d["human_review_required"] = True
            d["provisional"] = True
            d["depends_on"] = ["dec-brand-001"]
            d["rationale"] = (f"Arquetipo provisional (branding {kind}): densidad calculada por estructura "
                              "de contenido del brief. Revalidar al aprobarse el arquetipo.")
    comp = copy.deepcopy(COMPOSITION)
    comp["branding_zones"]["provisional"] = True
    comp["density"]["provisional"] = True
    comp["density"]["archetype_mapping"] = "provisional (branding sin aprobar)"
    return decs, comp


FEAS_ENTRIES = []
for i in range(1, 7):
    FEAS_ENTRIES.append({"decision_id": f"dec-color-{i:03d}", "requirement": f"Capacidad de color {i}",
                         "platform_capability": "Global Colors / Figma Variables",
                         "classification": "green", "constraints": [], "workaround": None, "blocking_reason": None})
for i in range(1, 9):
    FEAS_ENTRIES.append({"decision_id": f"dec-typography-{i:03d}", "requirement": f"Capacidad tipográfica {i}",
                         "platform_capability": "Figma text styles / Elementor Global Fonts",
                         "classification": "green", "constraints": [], "workaround": None, "blocking_reason": None})
for i in range(1, 9):
    FEAS_ENTRIES.append({"decision_id": f"dec-brand-{i:03d}", "requirement": f"Decisión de marca {i}",
                         "platform_capability": "Sin dependencia de plataforma",
                         "classification": "green", "constraints": [], "workaround": None, "blocking_reason": None})
for i in range(1, 9):
    yellow = i == 3
    FEAS_ENTRIES.append({
        "decision_id": f"dec-editorial-{i:03d}", "requirement": f"Capacidad editorial {i}",
        "platform_capability": "Figma auto-layout nativo; Elementor grid/CSS",
        "classification": "yellow" if yellow else "green",
        "constraints": ["Elementor: Custom CSS grid scoped"] if yellow else [],
        "workaround": "Custom CSS grid en contenedor" if yellow else None,
        "blocking_reason": None,
    })

FEASIBILITY = {
    "meta": {"platform": "both", "generated_at": "2026-11-07T21:30:00.000000Z"},
    "platform": "both",
    "requirements": [{"id": f"req-{i:03d}", "description": f"Requisito {i}"} for i in range(1, 9)],
    "decisions_evaluated": FEAS_ENTRIES,
}


def dump(out: Path, name: str, payload) -> Path:
    path = out / name
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def build(out: Path, kind: str = "incompleto", brand_status: str = "incomplete") -> dict:
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "decisions": dump(out, "design-decisions.json", DECISIONS),
        "feasibility": dump(out, "feasibility-report.json", FEASIBILITY),
        "complete": dump(out, "editorial-composition.json",
                         {"meta": editorial_meta("editorial-composition.json", "complete"),
                          "decisions": ED_COMPLETE, "editorial_composition": COMPOSITION}),
    }
    decs, comp = draft_variant(kind)
    paths["draft"] = dump(out, "draft-editorial-composition.json",
                          {"meta": editorial_meta("draft-editorial-composition.json", brand_status,
                                                  ["dec-editorial-004", "dec-editorial-006"]),
                           "decisions": decs, "editorial_composition": comp})
    return paths


if __name__ == "__main__":
    written = build(Path(__file__).parent / "_generated")
    for k, v in written.items():
        print("written:", v)
