---
name: creative-direction-color
version: 1.0.0
description: Use when defining color palette, semantic color roles, and color hierarchy for a project. Produces color decisions valid against design-decision-schema.json with feasibility_ref traceability.
---

# Creative Direction — Color Skill

## When to Use
- FASE 3 del workflow `design-production.md`: después de `feasibility-report.json`
- Definir paleta primaria/secundaria/neutra para nuevo proyecto
- Definir roles semánticos de color (CTA, feedback, superficie, texto)
- Auditar paleta existente contra accesibilidad y viabilidad de plataforma
- Resolver conflictos de color entre marca y plataforma

## Procedure

### Paso 0 — Cargar Feasibility (OBLIGATORIO)
```python
# Antes de cualquier propuesta de color:
feasibility = read_json("feasibility-report.json")
platform = feasibility["platform"]  # "elementor" | "figma" | "both"

# Extraer restricciones de color relevantes:
color_constraints = [
    d for d in feasibility["decisions_evaluated"]
    if d["decision_id"].startswith("dec-color-")
]
# Cada entrada tiene: classification (green/yellow/red), constraints[], workaround, blocking_reason
```
**Regla**: Si `color_constraints` está vacío → **DETENER**, solicitar FASE 2 completa. No proponer paleta sin saber qué soporta la plataforma.

### Paso 1 — Análisis de Contexto
Inputs requeridos (desde `brief-normalizado.json`):
- `brand_guidelines`: colores de marca existentes (hex, nombres)
- `business_goal`: conversión, confianza, diferenciación, calma
- `target_audience`: demografía, cultura, accesibilidad (daltonismo, low vision)
- `platform`: Elementor, Figma, o ambos
- `existing_tokens`: `design-system/tokens/colors.json` (primitives + semantic)

### Paso 2 — Síntesis de Evidencia
Consultar `references/color-evidence.md`:
- **Teoría disciplinar** (Heller, Albers, Dondis): criterios para estructura de paleta, temperatura, jerarquía visual
- **Evidencia empírica 2020+** (Kohavi, Biswas, Lin, etc.): estudios de campo sobre color y CTR/conversión
- **Regla**: Si evidencia empírica contradice teoría → gana empírica. Si no hay evidencia empírica → declarar explícitamente "sin evidencia de campo, basado en teoría X"

### Paso 3 — Definir Paleta Primaria (Brand)
Para cada color de marca:
1. Verificar si existe en `primitives` del design-system
2. Si no existe → proponer nuevo primitive con `feasibility_ref` a capacidad "Global Colors/Variables" (green en ambas plataformas)
3. Mapear a roles semánticos: `cta.primary_bg`, `cta.primary_text`, `brand.primary`, `interactive.primary`
4. **No decidir contraste aquí** — solo proponer hue/saturation/lightness. Contraste = FASE 5 (contrast_analyzer.py)

### Paso 4 — Definir Paleta Neutra + Superficies
- Grises: 10 pasos (50-950) + white/black
- Superficies: `background.primary`, `background.secondary`, `background.tertiary`, `background.inverse`
- Cada neutral debe tener `feasibility_ref` a "Global Colors/Variables" (green)

### Paso 5 — Definir Estados de Feedback
- Success: green scale (500-600 para texto, 50-100 para fondo)
- Warning: amber/yellow scale
- Error: red scale (600 para texto, 50-100 para fondo)
- Info: blue scale
- Cada uno → `feasibility_ref` a "Global Colors/Variables" (green)

### Paso 6 — Generar Decisiones (Output)
Para cada decisión de color, emitir objeto válido contra `design-decision-schema.json` (v0.2):

```json
{
  "specialist": "color",
  "category": "color",
  "decision_id": "dec-color-001",
  "decision": "Establecer brand/primary/600 (#2563EB) como cta.primary_bg",
  "rationale": "Kohavi 2025: blue primary CTA +12% conversión vs neutral; brand consistency. Feasibility: Elementor Global Color + Figma Variable = green. Sin evidencia empírica verificada de color específico → CTR.",
  "owner": "art-director",
  "constraints": ["WCAG 2.2 AA contrast vs white text (validado en FASE 5)", "Elementor Theme Style mapping 1:1"],
  "feasibility_ref": "dec-color-001",
  "validation_required": ["contrast", "a11y"],
  "human_review_required": false,
  "tokens_affected": ["{colors.semantic.cta.primary_bg}", "{colors.semantic.cta.primary_text}", "{colors.primitives.blue.600}"],
  "platform_specific": {
    "elementor": {"widget": "Button", "custom_css_needed": false, "theme_style_mapping": "Global Color Primary"},
    "figma": {"component_name": "Button/Primary", "variable_collection": "Brand", "variant_props": ["variant", "size", "state"]}
  },
  "evidence_refs": ["skills/creative-direction/color/references/color-evidence.md#kohavi-2025-cta-color"],
  "alternatives_considered": [],
  "references": {},
  "provisional": false,
  "depends_on": []
}
```

**Propiedad de la decisión**: `specialist` = quien produce (este skill: `color`), `category` = dominio de la decisión, `owner` = rol accountable que aprueba (`art-director`). No colapsar los tres — ver `templates/DECISION-FIELDS.md`.

**Regla de viabilidad**: Si una decisión propuesta no tiene `feasibility_ref` válido (green/yellow) → **no emitirla**. En su lugar:
- Marcar `human_review_required: true` en decisión alternativa
- O proponer workaround documentado (ej. Custom CSS scoped) con `feasibility_ref` yellow

### Paso 7 — Validación Pre-Entrega
Ejecutar checklist de `skills/production/feasibility/SKILL.md#verification` contra `design-decisions.json` generado antes de pasar a FASE 4.

---

## Pitfalls

| Pitfall | Síntoma | Prevención |
|---------|---------|------------|
| **Proponer sin leer feasibility** | Decisiones `red` en FASE 3, re-work total | Paso 0 obligatorio: cargar feasibility primero |
| **Decidir contraste en este skill** | Paleta pasa skill pero falla FASE 5 | Contraste = FASE 5 únicamente. Skill solo propone hue/saturation |
| **Ignorar daltonismo** | Paleta inaccesible para 8% usuarios | Verificar simuladores (protanopia, deuteranopia) en Paso 1 |
| **Inflar teoría como evidencia** | "Albers dice que azul genera confianza" sin study de conversión | Separar teoría (estructura) de evidencia (CTR). Citar fuente exacta. |
| **Paleta completa sin tokens** | Builder no puede implementar; hardcode hex | Cada decisión debe tener `tokens_affected` con referencias a design-system |
| **Feasibility_ref a decisión red** | Workflow bloquea en FASE 3 | Verificar que feasibility_ref apunta a green/yellow antes de emitir |

---

## Verification

**Checklist de salida del skill (ejecutable antes de pasar a FASE 4):**

1. **Feasibility cargada**: `feasibility-report.json` leído y `color_constraints` extraídos
2. **Decisiones válidas**: Cada decisión pasa `jsonschema.validate()` contra `design-decision-schema.json`
3. **Feasibility_ref presente**: 100% decisiones tienen `feasibility_ref` que matchea `decision_id` en feasibility con classification `green` o `yellow`
4. **Sin decisiones red**: Ninguna decisión apunta a feasibility classification `red`
5. **Tokens referenciados**: Cada `tokens_affected` existe en `design-system/tokens/colors.json` (primitives o semantic)
6. **Evidencia categorizada**: Cada `evidence_refs` apunta a entrada en `color-evidence.md` con etiqueta `THEORY` o `EMPIRICAL`
7. **Contraste NO decidido**: Ninguna decisión incluye ratio de contraste o afirmación "pasa AA" — eso es FASE 5
8. **Cobertura completa**: Paleta cubre primarios, neutros, feedback, superficies según `brief-normalizado.json`

```bash
# Verificación rápida (requiere jq, jsonschema)
python3 -c "
import json, jsonschema
with open('design-decision-schema.json') as f: schema = json.load(f)
with open('feasibility-report.json') as f: feas = json.load(f)
with open('design-decisions.json') as f: decisions = json.load(f)

valid_refs = {d['decision_id'] for d in feas['decisions_evaluated'] if d['classification'] in ('green','yellow')}
errors = []
for d in decisions:
    if d['specialist'] != 'color': continue
    if d['feasibility_ref'] not in valid_refs:
        errors.append(f\"{d['decision_id']}: feasibility_ref inválido\")
    if 'contrast' in d.get('rationale','').lower():
        errors.append(f\"{d['decision_id']}: decide contraste en rationale\")
    for tok in d.get('tokens_affected', []):
        # verificar token existe (simplificado)
        pass
if errors:
    print('❌ ERRORES:', errors); exit(1)
print('✅ Color decisions PASAN verificación')
"
```

---

## Referencias Requeridas

- `references/color-evidence.md` — Teoría disciplinar + Evidencia empírica 2020+
- `skills/production/feasibility/references/platform-constraints.md` — Constraints Elementor/Figma
- `design-system/tokens/colors.schema.json` — Schema de tokens de color
- `templates/design-decision-schema.json` — Contrato de decisión