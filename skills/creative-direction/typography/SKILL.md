---
name: creative-direction-typography
version: 1.0.0
description: Use when defining type scale, font families, hierarchy, and text roles for a project. Produces typography decisions valid against design-decision-schema.json with feasibility_ref traceability.
---

# Creative Direction — Typography Skill

## When to Use
- FASE 3 del workflow `design-production.md`: después de `feasibility-report.json`
- Definir type scale (tamaños, pesos, line-height) para nuevo proyecto
- Seleccionar font families (brand + UI) y definir fallbacks
- Definir roles semánticos de texto (heading, body, caption, label, code)
- Auditar tipografía existente contra accesibilidad y viabilidad de plataforma
- Resolver conflictos entre font de marca y platform constraints

## Procedure

### Paso 0 — Cargar Feasibility (OBLIGATORIO)
```python
# Antes de cualquier propuesta tipográfica:
feasibility = read_json("feasibility-report.json")
platform = feasibility["platform"]

# Extraer restricciones tipográficas relevantes:
typo_constraints = [
    d for d in feasibility["decisions_evaluated"]
    if d["decision_id"].startswith("dec-typography-")
]
# Cada entrada tiene: classification (green/yellow/red), constraints[], workaround, blocking_reason
```
**Regla**: Si `typo_constraints` está vacío → **DETENER**, solicitar FASE 2 completa. No proponer type scale sin saber qué soporta la plataforma (variable fonts, font loading, text styles).

### Paso 1 — Análisis de Contexto
Inputs requeridos (desde `brief-normalizado.json`):
- `brand_guidelines`: font families de marca existentes (nombre, pesos disponibles, licencia web)
- `business_goal`: lectura prolongada, conversión, impacto visual, datos densos
- `target_audience`: demografía, accesibilidad (low vision, dislexia), idiomas/scripts
- `platform`: Elementor, Figma, o ambos
- `existing_tokens`: `design-system/tokens/typography.json` (primitives + semantic)

### Paso 2 — Verificar Licencias y Disponibilidad Web
Para cada font de marca:
1. Verificar licencia web (Google Fonts, Adobe Fonts, self-hosted con licencia)
2. Verificar pesos disponibles vs necesarios (regular, medium, semibold, bold)
3. Verificar soporte de variable font (si aplica)
4. Si no hay licencia web → **no proponer**, marcar `human_review_required=true` con alternativa (Google Font similar)

### Paso 3 — Definir Type Scale (Escalas de Tamaño)
Basado en teoría disciplinar (Bringhurst, Tschichold, Material Design, iOS HIG):
1. Base size: 16px (1rem) para body
2. Scale ratio: 1.25 (Major Third) o 1.333 (Perfect Fourth) o 1.618 (Golden Ratio)
3. Generar pasos: xs, sm, base, lg, xl, 2xl, 3xl, 4xl, 5xl
4. Cada paso: `font-size`, `line-height`, `letter-spacing` (si aplica)
5. **No decidir contraste aquí** — solo escala. Contraste = FASE 5 (contrast_analyzer.py)

### Paso 4 — Definir Font Families y Pesos
- **Display/Brand**: Font de marca (headlines, hero, branding)
- **UI/Body**: Font optimizada para lectura (Inter, Roboto, System UI, etc.)
- **Mono**: Font para código/datos (JetBrains Mono, Fira Code, etc.)
- Para cada una: pesos necesarios (400, 500, 600, 700) + variable font si disponible
- Fallbacks: system-ui stack como último recurso

### Paso 5 — Definir Roles Semánticos de Texto
Mapear a `colors.semantic.*` y `typography.semantic.*`:
- `heading.xl` → `heading.xxl` → display
- `heading.lg` → `heading.md` → `heading.sm` → section headers
- `body.lg` → `body.md` → `body.sm` → párrafos
- `label.lg` → `label.md` → `label.sm` → UI labels, forms
- `caption` → metadata, timestamps
- `code` → inline code, data

### Paso 6 — Generar Decisiones (Output)
Para cada decisión tipográfica, emitir objeto válido contra `design-decision-schema.json` (v0.2):

```json
{
  "specialist": "typography",
  "category": "typography",
  "decision_id": "dec-typography-001",
  "decision": "Establecer Inter Variable (opsz, wght) como font UI principal; 400-700 weights",
  "rationale": "Inter optimizada para UI, variable font soporta opsz + wght, licencia SIL Open Font. Feasibility: Figma Variable font + Elementor single-axis weight via Custom CSS = yellow. Sin evidencia empírica verificada de font específica → legibilidad.",
  "owner": "art-director",
  "constraints": ["Licencia SIL OFL verificada", "Elementor: single-axis weight via Custom CSS scoped", "Figma: Variable font nativo (wght + opsz)"],
  "feasibility_ref": "dec-typography-001",
  "validation_required": ["a11y", "performance"],
  "human_review_required": false,
  "tokens_affected": ["{typography.families.ui}", "{typography.weights.regular}", "{typography.weights.medium}", "{typography.weights.semibold}", "{typography.weights.bold}"],
  "platform_specific": {
    "elementor": {"widget": "Heading/Text Editor", "custom_css_needed": true, "theme_style_mapping": "Global Typography UI Font (weight solo via Custom CSS)"},
    "figma": {"component_name": "Text Styles/UI", "variable_collection": "Typography", "variant_props": ["size", "weight", "lineHeight"]}
  },
  "evidence_refs": ["skills/creative-direction/typography/references/typography-evidence.md#bringhurst-scale", "skills/creative-direction/typography/references/typography-evidence.md#variable-font-support"],
  "alternatives_considered": [],
  "references": {},
  "provisional": false,
  "depends_on": []
}
```

**Propiedad de la decisión**: `specialist` = quien produce (este skill: `typography`), `category` = dominio de la decisión, `owner` = rol accountable que aprueba (`art-director`). No colapsar los tres — ver `templates/DECISION-FIELDS.md`.

**Regla de viabilidad**: Si una decisión propuesta no tiene `feasibility_ref` válido (green/yellow) → **no emitirla**. En su lugar:
- Marcar `human_review_required: true` en decisión alternativa
- O proponer workaround documentado (ej. Custom CSS para variable font weight) con `feasibility_ref` yellow

### Paso 7 — Validación Pre-Entrega
Ejecutar checklist de `skills/production/feasibility/SKILL.md#verification` contra `design-decisions.json` generado antes de pasar a FASE 4.

---

## Pitfalls

| Pitfall | Síntoma | Prevención |
|---------|---------|------------|
| **Proponer sin leer feasibility** | Decisiones `red` en FASE 3, re-work total | Paso 0 obligatorio: cargar feasibility primero |
| **Ignorar licencia web** | Font de marca no deployable; legal risk | Paso 2: verificar licencia ANTES de proponer |
| **Variable font multi-axis en Elementor** | Theme Style no soporta `font-variation-settings` dinámico | Clasificar como yellow (Custom CSS scoped single-axis) o red (multi-axis) |
| **Type scale sin line-height** | Legibilidad rota en responsive | Cada paso de escala DEBE incluir line-height |
| **Contraste decidido en este skill** | Paleta pasa skill pero falla FASE 5 | Contraste = FASE 5 únicamente. Skill solo propone size/weight |
| **Sin fallback stack** | Fuente no carga → layout roto | Siempre definir fallback system-ui en `platform_specific` |

---

## Verification

**Checklist de salida del skill (ejecutable antes de pasar a FASE 4):**

1. **Feasibility cargada**: `feasibility-report.json` leído y `typo_constraints` extraídos
2. **Licencias verificadas**: Cada font propuesta tiene licencia web confirmada
3. **Decisiones válidas**: Cada decisión pasa `jsonschema.validate()` contra `design-decision-schema.json`
4. **Feasibility_ref presente**: 100% decisiones tienen `feasibility_ref` que matchea `decision_id` en feasibility con classification `green` o `yellow`
5. **Sin decisiones red**: Ninguna decisión apunta a feasibility classification `red`
6. **Tokens referenciados**: Cada `tokens_affected` existe en `design-system/tokens/typography.json`
7. **Evidencia categorizada**: Cada `evidence_refs` apunta a entrada en `typography-evidence.md` con etiqueta `THEORY` o `EMPIRICAL`
8. **Contraste NO decidido**: Ninguna decisión incluye ratio de contraste o afirmación "pasa AA" — eso es FASE 5
9. **Cobertura completa**: Type scale, font families, roles semánticos cubiertos según `brief-normalizado.json`

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
    if d['specialist'] != 'typography': continue
    if d['feasibility_ref'] not in valid_refs:
        errors.append(f\"{d['decision_id']}: feasibility_ref inválido\")
    if 'contrast' in d.get('rationale','').lower():
        errors.append(f\"{d['decision_id']}: decide contraste en rationale\")
    for tok in d.get('tokens_affected', []):
        pass
if errors:
    print('❌ ERRORES:', errors); exit(1)
print('✅ Typography decisions PASAN verificación')
"
```

---

## Referencias Requeridas

- `references/typography-evidence.md` — Teoría disciplinar + Evidencia empírica 2020+
- `skills/production/feasibility/references/platform-constraints.md` — Constraints Elementor/Figma
- `design-system/tokens/typography.schema.json` — Schema de tokens tipográficos
- `templates/design-decision-schema.json` — Contrato de decisión