---
name: creative-direction-editorial
description: Define editorial composition: grid, hierarchy, rhythm, density, section library. Validates cross-layer coherence with color, typography, branding. Handles provisional branding states.
category: creative-direction
tags: [editorial, grid, hierarchy, composition, rhythm, density, layout, responsive]
version: "0.1.0"
author: design-superpowers
requires_feasibility: true
feasibility_category: "editorial"
platforms: ["elementor", "figma", "html", "pdf", "pptx"]
---

# Creative Direction — Editorial Skill

**When to use**: Page/screen composition, layout system, section library, responsive reflow rules. Input: `brief-normalizado.json` + `feasibility-report.json` + `design-decisions.json` (color, typography, branding) + `brand-identity.json` o `draft-brand-identity.json`. Output: `editorial-composition.json` (branding completo) o `draft-editorial-composition.json` (branding incomplete/missing).

**Golden rule**: Editorial **valida coherencia cross-layer**, no decide autónomamente arquetipo ni densidad semántica. Si branding provisional → decisiones dependientes marcan `human_review_required=true` + `provisional: true`.

---

## Inputs Requeridos

| Input | Descripción | Obligatorio |
|-------|-------------|-------------|
| `brief-normalizado.json` | Brief validado con business_goal, audience, content_structure | SÍ |
| `feasibility-report.json` | Output del skill feasibility (Paso 0) | SÍ |
| `design-decisions.json` | Decisiones de color, typography, branding (ya validadas) | SÍ |
| `brand-identity.json` \| `draft-brand-identity.json` | Identidad de marca (estado complete/incomplete/missing) | SÍ |
| `design-system/tokens/` | Tokens actuales para auditoría | SÍ |

---

## Procedure

### Paso 0: Cargar Feasibility y Decisiones Previas (Obligatorio)
```bash
# Validar feasibility
./skills/production/feasibility/verify.sh feasibility-report.json design-decisions.json
# Validar schema de decisiones previas
jsonschema -i design-decisions.json templates/design-decision-schema.json
```
- Si falla → **DETENER**, devolver a fase anterior.
- Extraer `brand_status` de `brand-identity.json`/`draft-brand-identity.json` → `meta.manual_status` ∈ `{"complete", "incomplete", "missing"}`.
- Indexar decisiones previas por `decision_id` para cross-reference.

### Paso 1: Sistema Unificado — Consumir Tokens (Vignelli Canon)
**Decisión**: `dec-editorial-001`
- Verificar que `design-decisions.json` contiene decisiones de:
  - Color: `dec-color-001` a `dec-color-006` (paleta, CTA hierarchy, semantic roles)
  - Typography: `dec-typography-001` a `dec-typography-008` (font, scale, line-height, weights, spacing)
  - Branding (si complete): `dec-brand-001` a `dec-brand-008` (arquetipo, personality, positioning, visual system)
- **Output**: Confirmación de tokens consumidos + mapping a retícula.
- `feasibility_ref`: `dec-editorial-001` (green: decisión técnica, no plataforma)
- `human_review_required`: `false`
- `evidence_refs`: `editorial-evidence.md#vignelli-canon`

### Paso 2: Jerarquía Compositiva — Coherencia con Typography + Color
**Decisión**: `dec-editorial-002`

**Validación cross-layer obligatoria**:
1. **Typography hierarchy** (de `dec-typography-003` scale + `dec-typography-004` line-height):
   - Extraer: base size, ratio, steps (-2 to +4), line-height per role
   - Calcular: tamaño visual hero title, section headings, body, caption
2. **Color CTA hierarchy** (de `dec-color-002` primary, `dec-color-003` outline, `dec-color-004` ghost):
   - Extraer: background, border, text colors per variant
   - Calcular: peso visual relativo (filled > outline > ghost)
3. **Coherencia**: Verificar que el paso tipográfico del hero title (ej. step +3/+4) tiene peso visual coherente con CTA primary (filled). Si hero title es step +2 pero CTA primary es filled → **warning**: posible desbalance jerárquico.
4. **Sección mapping** (Müller-Brockmann page structure / Samara layout patterns):
   - Hero: title (max step), subtitle (step 0/+1), CTA primary
   - Features: heading (step +1/+2), body (step 0), icon/illustration
   - Proof: heading (step +1), testimonial/metric (step 0)
   - CTA Section: heading (step +1), CTA primary + secondary
   - Footer: caption (step -1/-2), legal links

**Output**: Jerarquía documentada con mapping tipografía-color por sección.
- `feasibility_ref`: `dec-editorial-002` (green)
- `human_review_required`: `false` (validación técnica)
- `evidence_refs`: `editorial-evidence.md#lupton-hierarchy`, `editorial-evidence.md#tschichold-whitespace`
- `references`: `{ "typography_scale": "dec-typography-003", "cta_hierarchy": "dec-color-002" }`

### Paso 3: Retícula — Columnas, Gutters, Baseline, Breakpoints
**Decisión**: `dec-editorial-003`

**Input**: `feasibility-report.json` (platform breakpoints), `design-system/tokens/breakpoints.json`, `dec-typography-004` line-height.

**Proceso**:
1. **Baseline grid**: `base_line_height = dec-typography-004.body` (1.5) × `base_font_size` (16px) = 24px baseline unit.
2. **Columnas**: 12 columnas desktop (≥1024px), 8 tablet (768-1023px), 4 mobile (<768px). Basado en Müller-Brockmann + Samara.
3. **Gutters**: Múltiplo de baseline unit. Desktop: 24px (1 baseline), Tablet: 16px, Mobile: 12px.
4. **Márgenes**: Múltiplo de gutter. Desktop: 48px (2 gutters), Tablet: 32px, Mobile: 24px.
5. **Módulos**: Columnas × filas baseline. Altura de fila = baseline unit.
6. **Validación feasibility**: Verificar que Elementor/Figma soportan esta retícula (Theme Style > Container > Grid, Figma auto-layout).
   - Elementor: Container flexbox + grid experimental → **yellow** (workaround: Custom CSS grid)
   - Figma: Auto-layout + grid → **green**

**Output**: Retícula completa con especificaciones por breakpoint.
- `feasibility_ref`: `dec-editorial-003` (yellow para Elementor, green para Figma)
- `human_review_required`: `false`
- `evidence_refs`: `editorial-evidence.md#muller-brockmann-grids`, `editorial-evidence.md#samara-grid-anatomy`
- `platform_specific`: `{ "elementor": "Custom CSS grid workaround", "figma": "Auto-layout + grid native" }`

### Paso 4: Espacio para Branding — Logo, Tagline, Arquetipo
**Decisión**: `dec-editorial-004`

**Input**: `brand-identity.json`/`draft-brand-identity.json` → `meta.manual_status`, `brand_identity.visual_system.logo_usage`, `brand_identity.archetype`, `brand_identity.positioning.tagline_candidates`.

**Proceso**:
1. **Si `manual_status == "complete"`**:
   - Leer `logo_usage`: clear space, minimum size, placement zones
   - Leer `archetype.primary` + `positioning.tagline_candidates`
   - Definir: zona hero para logo (top-left/center), clear space = 2× baseline unit
   - Definir: zona para tagline (hero subtitle area o dedicated band)
   - Validar: retícula (Paso 3) tiene columnas/módulos para acomodar sin reflow
2. **Si `manual_status == "incomplete"`**:
   - Espacio reservado genérico: logo zone = 4 columnas × 3 baseline rows, tagline zone = 8 columnas × 2 baseline rows
   - `human_review_required: true`, `provisional: true`, `depends_on: ["dec-brand-007"]`
   - `rationale`: "brand-guidelines.md incompleto en logo-usage; espacio reservado genérico"
3. **Si `manual_status == "missing"`**:
   - Espacio reservado genérico (mismo que incomplete)
   - `human_review_required: true`, `provisional: true`, `depends_on: ["dec-brand-001", "dec-brand-007"]`
   - `rationale`: "Sin brand-guidelines.md; arquetipo y logo pendientes. Espacio reservado genérico."

**Output**: Especificación de zonas de branding en retícula.
- `feasibility_ref`: `dec-editorial-004` (green)
- `human_review_required`: `false` si complete, `true` si incomplete/missing
- `provisional`: `true` si incomplete/missing
- `depends_on`: decisions de branding afectadas
- `evidence_refs`: `editorial-evidence.md#vignelli-canon`, `editorial-evidence.md#kapferer-physique`

### Paso 5: Ritmo Vertical / Baseline Grid Alignment
**Decisión**: `dec-editorial-005`

**Input**: `dec-typography-004` line-height tokens, `dec-editorial-003` baseline unit.

**Proceso**:
1. Baseline unit = `base_font_size` × `line-height_body` = 16px × 1.5 = 24px.
2. Validar que todos los `line-height` tokens son múltiplos o fracciones simples del baseline unit:
   - body 1.5 = 1 baseline ✅
   - heading 1.2 = 0.8 baseline → **ajustar a 1.25 (1 baseline) o 1.5 (1 baseline)** para alineación
   - caption 1.4 → ajustar a 1.5 o 1.0
   - button 1.0 = 0.67 baseline → ajustar a 1.0 (no baseline-aligned, acceptable para inline)
3. Definir `vertical_rhythm_scale`: múltiplos de baseline para spacing entre secciones (1, 2, 3, 4 baselines).
4. Section padding: desktop 4 baselines (96px), tablet 3 (72px), mobile 2 (48px).

**Output**: Vertical rhythm system alineado a baseline grid.
- `feasibility_ref`: `dec-editorial-005` (green)
- `human_review_required`: `false`
- `evidence_refs`: `editorial-evidence.md#bringhurst-rhythm`, `editorial-evidence.md#muller-brockmann-grids`

### Paso 6: Densidad Compositiva — Coherencia con Arquetipo
**Decisión**: `dec-editorial-006`

**Input**: `brand_identity.archetype` (si complete), `brief-normalizado.json` (content_structure), retícula (Paso 3).

**Proceso**:
1. **Calcular densidad objetivo**: elementos por módulo de retícula (contenido + UI + whitespace).
   - Métrica: `density_index = (elementos_visuales) / (área_cm²)` o `whitespace_ratio = área_whitespace / área_total`.
2. **Mapping teórico arquetipo → densidad** (Hofmann + Tschichold + Vignelli):
   | Arquetipo | Densidad | Whitespace Ratio | Rationale |
   |-----------|----------|------------------|-----------|
   | Hero | Alta (denso, activo) | 0.35-0.45 | Acción, movimiento, energía |
   | Explorer | Media-Alta | 0.40-0.50 | Descubrimiento, amplitud |
   | Sage | Baja (espaciado, calmo) | 0.55-0.65 | Claridad, contemplación |
   | Innocent | Media | 0.45-0.55 | Simplicidad, honestidad |
   | Creator | Media-Alta | 0.40-0.50 | Expresión, detalle |
   | Ruler | Media | 0.45-0.55 | Orden, autoridad |
   | Magician | Media-Alta | 0.40-0.50 | Transformación, misterio |
   | Lover | Media | 0.45-0.55 | Intimidad, belleza |
   | Caregiver | Baja-Media | 0.50-0.60 | Cuidado, calidez |
   | Jester | Alta | 0.35-0.45 | Diversión, dinamismo |
   | Everyman | Media | 0.45-0.55 | Accesibilidad, familiaridad |
   | Outlaw | Alta | 0.35-0.45 | Ruptura, intensidad |
3. **Si `manual_status == "complete"`**: Usar arquetipo aprobado → densidad objetivo.
4. **Si `manual_status ∈ {"incomplete", "missing"}"`**:
   - Calcular densidad basada en `brief-normalizado.json` (content_structure density hint)
   - `human_review_required: true`, `provisional: true`, `depends_on: ["dec-brand-001"]`
   - `rationale`: "Arquetipo provisional/pendiente; densidad calculada por contenido. Revisar al aprobar branding."

**Output**: Densidad objetivo + whitespace ratio + mapping a retícula (módulos ocupados vs libres).
- `feasibility_ref`: `dec-editorial-006` (green)
- `human_review_required`: `false` si complete, `true` si incomplete/missing
- `provisional`: `true` si incomplete/missing
- `evidence_refs`: `editorial-evidence.md#hofmann-density`, `editorial-evidence.md#tschichold-whitespace`

### Paso 7: Library de Secciones — Patrones Compuestos
**Decisión**: `dec-editorial-007`

**Input**: Jerarquía (Paso 2), Retícula (Paso 3), Branding zones (Paso 4), Ritmo (Paso 5), Densidad (Paso 6).

**Proceso**: Definir 8-12 patrones de sección reutilizables (convención de industria: estructura de página Müller-Brockmann + agrupación de módulos Samara), cada uno con:
- Nombre + propósito
- Estructura de retícula (columnas, filas baseline)
- Elementos: heading level, body, media, CTA variant, branding elements
- Responsive behavior (reflow rules per breakpoint)
- Densidad (whitespace ratio dentro de la sección)
- Coherencia validada: CTA variant coincide con jerarquía de sección, tipografía escala coincide con heading level

**Patrones mínimos**:
1. `hero-primary`: Logo + headline (max step) + subtitle + CTA primary + secondary
2. `hero-branded`: Logo prominent + tagline + brand imagery + CTA ghost
3. `feature-grid`: Heading + 3-4 cards (icon + title + body + link)
4. `proof-testimonial`: Heading + carousel/grid de testimonials/metrics
5. `cta-section`: Heading + CTA primary + secondary + trust signals
6. `content-band`: Heading + rich text + media (alternating)
7. `footer-comprehensive`: Brand mark + nav columns + legal + social
8. `section-divider`: Whitespace band + optional decorative element

**Output**: Library completa con especificaciones por patrón.
- `feasibility_ref`: `dec-editorial-007` (green)
- `human_review_required`: `false`
- `evidence_refs`: `editorial-evidence.md#samara-layout-patterns`, `editorial-evidence.md#muller-brockmann-page-structure`
- **Nota**: library de secciones = convención de industria derivada de la anatomía de retícula; no hay estudio empírico que la respalde

### Paso 8: Reglas Responsive — Reflow sin Ruptura
**Decisión**: `dec-editorial-008`

**Input**: Retícula breakpoints (Paso 3), Section library (Paso 7), Feasibility platform constraints.

**Proceso**:
1. Definir **reflow rules** por patrón:
   - Columnas: 12→8→4 (desktop→tablet→mobile)
   - Gutters: 24→16→12px
   - Márgenes: 48→32→24px
   - Baseline unit: 24px (constante) o 20px mobile
2. **Stacking order**: Content first, media second, CTA last (mobile-first).
3. **Branding zones**: Logo/tagline zones se adaptan (no desaparecen). Mobile: logo 4col, tagline 8col stacked.
4. **Validación feasibility**: Elementor responsive editing + Figma auto-layout constraints.
   - Elementor: Responsive controls nativos → **green**
   - Figma: Auto-layout + constraints → **green**

**Output**: Reflow rules por patrón + breakpoint.
- `feasibility_ref`: `dec-editorial-008` (green)
- `human_review_required`: `false`
- `evidence_refs`: `editorial-evidence.md#samara-responsive`, `editorial-evidence.md#samara-layout-patterns`

**Propiedad de la decisión**: `specialist` = quien produce (este skill: `editorial`), `category` = dominio de la decisión, `owner` = rol accountable que aprueba (`art-director`). No colapsar los tres — ver `templates/DECISION-FIELDS.md`.

### Paso 9: Generar Output Final
**Archivo**: `editorial-composition.json` (branding complete) o `draft-editorial-composition.json` (branding incomplete/missing)

**Estructura**:
```json
{
  "meta": {
    "generated_at": "2026-11-07T...",
    "skill_version": "0.1.0",
    "brand_status": "complete|incomplete|missing",
    "provisional_decisions": ["dec-editorial-004", "dec-editorial-006"],
    "human_review_required_count": 2
  },
  "decisions": [
    {
      "decision_id": "dec-editorial-001",
      "specialist": "editorial",
      "category": "editorial",
      "decision": "Sistema unificado: tokens color/typography/branding consumidos como single source of truth",
      "rationale": "Vignelli canon — coherencia sistema. Tokens válidos cross-referenciados. Sin evidencia empírica verificada de retícula → conversión.",
      "evidence_refs": ["skills/creative-direction/editorial/references/editorial-evidence.md#vignelli-canon"],
      "feasibility_ref": "dec-editorial-001",
      "human_review_required": false,
      "alternatives_considered": [],
      "validation_required": false,
      "platform_specific": {},
      "references": {
        "color_decisions": ["dec-color-001", ..., "dec-color-006"],
        "typography_decisions": ["dec-typography-001", ..., "dec-typography-008"],
        "branding_decisions": ["dec-brand-001", ..., "dec-brand-008"]
      }
    },
    ...
  ],
  "editorial_composition": {
    "grid": { "columns": {"desktop": 12, "tablet": 8, "mobile": 4}, "gutters": {...}, "baseline": 24 },
    "hierarchy": { "sections": [...], "typography_color_mapping": {...} },
    "branding_zones": { "logo": {...}, "tagline": {...}, "provisional": true },
    "vertical_rhythm": { "baseline_unit": 24, "section_padding": {...} },
    "density": { "target_whitespace_ratio": 0.45, "archetype_mapping": "Hero", "provisional": true },
    "section_library": { "hero-primary": {...}, "feature-grid": {...}, ... },
    "responsive_rules": { "reflow": {...}, "breakpoints": {...} }
  }
}
```

---

## Pitfalls

1. **No validar cross-layer** → Decisiones editoriales incoherentes con color/typography/branding. Paso 2 y 4 obligatorios.
2. **Asumir arquetipo aprobado** → Si branding `incomplete/missing`, decisiones de espacio branding y densidad **deben** ser `provisional: true` + `human_review_required: true`.
3. **Retícula infeasible** → Paso 3 debe validar contra feasibility-report.json. Elementor grid = yellow (Custom CSS workaround).
4. **Baseline grid roto** → Paso 5 debe alinear line-height tokens a baseline unit. Heading 1.2 → ajustar a 1.25 o 1.5.
5. **Densidad sin arquetipo** → Si branding provisional, densidad basada en contenido + flag provisional.
6. **Output naming incorrecto** → `draft-editorial-composition.json` si branding no complete.
7. **Referencias faltantes** → Cada decisión debe referenciar decisions IDs que consume (`references` field).

---

## Verification

### Checks de Coherencia Cross-Layer (Ejecutables)

```bash
# 1. Feasibility válida + forma v0.2 (script canónico, sin jq)
python skills/production/feasibility/scripts/verify-feasibility-refs.py \
  feasibility-report.json design-decisions.json \
  --schema templates/design-decision-schema.json

# 2. Schema validation (v0.2 canónico)
jsonschema -i editorial-composition.json templates/design-decision-schema.json

# 3. Cross-layer coherence verification (13 reglas + semántica specialist/category/owner)
python skills/creative-direction/editorial/scripts/verify-editorial-coherence.py \
  editorial-composition.json \
  design-decisions.json \
  brand-identity.json \
  feasibility-report.json
```

### Script `verify-editorial-coherence.py` — Reglas de Validación

La implementación vive en `scripts/verify-editorial-coherence.py` (fuente única). No se duplica el código aquí: una copia embebida se desincroniza del verificador real.

| # | Regla | Severidad |
|---|-------|-----------|
| 0 | `specialist` es un productor de dominio válido y ≠ `art-director`; `category` presente; `owner` (aprobador) presente | ERROR |
| 1 | `feasibility_ref` presente y, si se pasa el feasibility-report, green/yellow | ERROR |
| 2 | `dec-editorial-002` referencia `typography_scale` y `cta_hierarchy` existentes | ERROR |
| 3 | branding `complete` → 004/006 sin `human_review_required` ni `provisional` | ERROR |
| 4 | branding `incomplete`/`missing` → 004/006 con `human_review_required: true` y `provisional: true` (`depends_on`: WARNING) | ERROR |
| 5 | `dec-editorial-001` referencia decisiones de color/typography/branding existentes | ERROR |
| 6/9 | `dec-editorial-003` y `-008` con `feasibility_ref` | ERROR |
| 7 | `dec-editorial-005` referencia `typography_line_height` | WARNING |
| 8 | `dec-editorial-007` referencia `cta_hierarchy` y `typography_scale` | WARNING |
| 10 | `meta.output_file` con prefijo `draft-` si branding no está completo | WARNING |
| 11 | `meta.provisional_decisions` = decisiones con `provisional: true` | WARNING |
| 12 | `meta.human_review_required_count` = conteo real | WARNING |
| 13 | `evidence_refs` → archivo y ancla existentes en el archivo de evidencia | ERROR |
| 14 | decisiones previas referenciadas: dominio del `decision_id` = `specialist`, `owner` presente, `feasibility_ref` green/yellow | ERROR |

Exit 0 = PASS; exit 1 = FAIL. Acepta `design-decisions.json` como array canónico o `{"decisions": [...]}`.

### Verification Gates (Deben PASSAR)

| Gate | Comando | Exit Code Esperado |
|------|---------|-------------------|
| Feasibility válida + forma v0.2 | `python skills/production/feasibility/scripts/verify-feasibility-refs.py feasibility-report.json design-decisions.json --schema templates/design-decision-schema.json` | 0 |
| Schema validation (v0.2) | `jsonschema -i editorial.json templates/design-decision-schema.json` | 0 |
| Cross-layer coherence | `python skills/creative-direction/editorial/scripts/verify-editorial-coherence.py editorial.json design-decisions.json brand.json feasibility-report.json` | 0 |

---

## Outputs

| Archivo | Cuándo | Contenido |
|---------|--------|-----------|
| `editorial-composition.json` | Branding complete | Composición aprobada, decisiones con cross-refs válidos |
| `draft-editorial-composition.json` | Branding incomplete/missing | Composición con decisiones provisionales marcadas |

---

## Referencias

- `skills/creative-direction/editorial/references/editorial-evidence.md` — Teoría compositiva (Müller-Brockmann, Samara, Lupton, Bringhurst, Tschichold, Vignelli, Hofmann) + Kapferer solo para el espacio de marca. NO evidencia empírica.
- `templates/design-decision-schema.json` — Contrato de decisión **v0.2 (canónico)**; `feasibility_ref` obligatorio.
- `templates/DECISION-FIELDS.md` — Semántica de `specialist` / `category` / `owner`.
- `templates/design-decision-schema.v0.1.json` — ARCHIVADO, no usar.
- `skills/creative-direction/editorial/scripts/verify-editorial-coherence.py` — Verificador cross-layer (14 reglas).
- `skills/production/feasibility/scripts/verify-feasibility-refs.py` — Verificación de FASE 3 sin jq.
- `skills/production/feasibility/SKILL.md` — Paso 0 feasibility.
- `skills/creative-direction/color/SKILL.md` — Decisiones de color consumidas.
- `skills/creative-direction/typography/SKILL.md` — Decisiones de tipografía consumidas.
- `skills/creative-direction/branding/SKILL.md` — Decisiones de branding consumidas.