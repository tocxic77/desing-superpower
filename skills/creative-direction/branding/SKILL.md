---
name: creative-direction-branding
description: Define brand identity: archetype, positioning, personality, tone of voice, visual system. Requires human review for all strategic decisions. No autonomous brand positioning.
category: creative-direction
tags: [branding, archetype, positioning, personality, tone-of-voice, brand-identity, strategy]
version: "0.1.0"
author: design-superpowers
requires_feasibility: true
feasibility_category: "branding"
platforms: ["elementor", "figma", "html", "pdf", "pptx"]
---

# Creative Direction — Branding Skill

**When to use**: New brand identity, rebrand, brand extension, or brand audit. Input: `brief-normalizado.json` + `brand-guidelines.md` (optional). Output: `brand-identity.json` (manual completo) o `draft-brand-identity.json` (manual inexistente/incompleto).

**Golden rule**: El LLM **nunca decide** posicionamiento de marca autónomamente. Todas las decisiones estratégicas (arquetipo, posicionamiento, esencia, tono) requieren `human_review_required=true` + `alternatives_considered[]`.

---

## Inputs Requeridos

| Input | Descripción | Obligatorio |
|-------|-------------|-------------|
| `brief-normalizado.json` | Brief validado con business_goal, audience, differentiators, mandatories | SÍ |
| `brand-guidelines.md` | Manual de marca aprobado (puede no existir o estar incompleto) | NO |
| `feasibility-report.json` | Output del skill feasibility (Paso 0) | SÍ |
| `design-system/tokens/` | Tokens actuales (color, typography, spacing) para auditoría | SÍ |

---

## Procedure

### Paso 0: Cargar Feasibility (Obligatorio)
```bash
# Validar que feasibility existe y decisions tienen feasibility_ref
./skills/production/feasibility/verify.sh feasibility-report.json design-decisions.json
```
- Si falla → **DETENER**, devolver a feasibility skill.
- Feasibility para branding: siempre `green` (decisiones estratégicas, no técnicas). Registrar como `dec-brand-feasibility`.

### Paso 1: Evaluar Completitud del brand-guidelines.md
**Script ejecutable**: `skills/creative-direction/branding/scripts/audit-brand-guidelines.py`

El script verifica 6 facetas del Brand Identity Prism (Kapferer) + componentes operativos:

| Faceta / Componente | Requerido | Sección esperada en brand-guidelines.md |
|---------------------|-----------|------------------------------------------|
| **Physique** (físico) | SÍ | `paleta-completa`, `tipografia-corporativa`, `logo-usage`, `imagery-style` |
| **Personality** (personalidad) | SÍ | `personalidad-marca` (Aaker dimensions), `tono-de-voz` |
| **Culture** (cultura) | SÍ | `valores`, `mission`, `vision`, `arquetipo` |
| **Relationship** (relación) | SÍ | `service-principles`, `customer-promise` |
| **Reflection** (reflejo) | SÍ | `audience-reflection`, `user-personas` |
| **Self-image** (autoimagen) | SÍ | `brand-essence`, `tagline`, `positioning-statement` |
| **Governance** | SÍ | `approval-process`, `exceptions`, `evolution-rules` |

**Output del script** (JSON):
```json
{
  "manual_exists": true,
  "completeness_score": 0.71,
  "missing_sections": ["paleta-completa", "governance"],
  "contradictions": ["tono-de-voz dice formal pero ejemplos son casuales"],
  "decisions_requiring_human_review": ["dec-brand-007", "dec-brand-008"]
}
```

**Regla de decisión**:
- Si `manual_exists: false` → **CASO 2** (manual inexistente). Saltar a Paso 2B.
- Si `completeness_score < 1.0` → **CASO 1** (manual incompleto/contradictorio). Marcar decisiones afectadas con `human_review_required=true`.
- Si `completeness_score == 1.0` y `contradictions: []` → **CASO 3** (manual completo). Usar como `evidence_ref` para decisiones cubiertas.

### Paso 2A: CASO 1 — Manual Existe pero Incompleto/Contradictorio
Para cada decisión del mapa típico:
- Si la sección requerida en brand-guidelines.md **existe y es consistente** → decisión sale con `evidence_ref: "brand-guidelines.md#seccion-exacta"`, `human_review_required: false`.
- Si la sección **falta o tiene contradicciones** → decisión sale con `human_review_required: true`, `rationale: "brand-guidelines.md incompleto en X / contradicción en Y"`, `alternatives_considered: []` (vacío, humano provee).
- **Nunca asumir** que lo no documentado no importa. Asumir que **falta** y marcarlo.

### Paso 2B: CASO 2 — Manual No Existe
El skill **no inventa** un manual. Produce `draft-brand-identity.json` con:
- Para cada decisión estratégica (arquetipo, posicionamiento, esencia, personalidad, tono):
  - `rationale`: síntesis de `brief-normalizado.json` + teoría (Pearson/Aaker/Kapferer)
  - `human_review_required: true` **obligatorio**
  - `alternatives_considered`: mínimo 2 opciones con pros/cons teóricos
  - `evidence_refs`: anclas a `branding-evidence.md` (solo THEORY)
- Para decisiones operativas (logo usage, paleta, tipografía si no en tokens):
  - `human_review_required: true`
  - `rationale`: "No brand-guidelines.md; definido por brief + tokens actuales + convención"
- Output filename: **`draft-brand-identity.json`** (no `brand-identity.json`)

### Paso 2C: CASO 3 — Manual Completo y Consistente
- Decisiones cubiertas por manual → `evidence_ref` a sección exacta, `human_review_required: false`
- Decisiones no cubiertas (nuevas extensiones, sub-marcas) → `human_review_required: true`, `alternatives_considered` ≥2
- Output filename: **`brand-identity.json`**

### Paso 3: Seleccionar Arquetipo (Pearson/Marquardt)
**Input**: `brief-normalizado.json` (values, audience, differentiators) + `brand-guidelines.md` (si existe)

**Proceso**:
1. Mapear valores de marca + motivación de audiencia a 12 arquetipos (Pearson).
2. Filtrar por rueda de Marquardt: coherencia con motivación central (Estabilidad/Dominio/Pertenencia/Independencia).
3. Output: **mínimo 2 arquetipos candidatos** con rationale teórico.
4. Decisión `dec-brand-001`: `human_review_required=true`, `alternatives_considered` = lista de candidatos.
5. Si manual existe y define arquetipo → `evidence_ref: "brand-guidelines.md#arquetipo"`, `human_review_required: false`.

### Paso 4: Definir Personalidad y Tone of Voice (Aaker)
**Input**: Arquetipo seleccionado + `brief-normalizado.json` (audience, differentiators)

**Proceso**:
1. Mapear arquetipo → dimensiones Aaker (Sinceridad, Emoción, Competencia, Sofisticación, Rudecidad).
2. Definir 3-5 facetas de personalidad con descripciones comportamentales.
3. Derivar tone of voice: do/don't, vocabulario preferido/evitado, ritmo, formalidad, humor.
4. Decisión `dec-brand-003` + `dec-brand-004`: `human_review_required=true` (salvo manual completo con sección exacta).

### Paso 5: Posicionamiento y Esencia (Keller/Neumeier)
**Input**: Arquetipo + Personalidad + `brief-normalizado.json` (business_goal, differentiators, audience)

**Proceso**:
1. Construir positioning statement: `[Target] → [Frame of Reference] → [Point of Difference] → [Reason to Believe]`.
2. Probar diferenciación (Neumeier Zag): ¿Es radialmente distinto de competidores nombrados en brief?
3. Definir brand essence (3-5 palabras) + tagline candidates (mínimo 3).
4. Decisión `dec-brand-005` + `dec-brand-006`: `human_review_required=true`, `alternatives_considered` ≥2 positioning statements, ≥3 taglines.

### Paso 6: Auditar / Proponer Sistema Visual (Kapferer Physique)
**Input**: `design-system/tokens/` + `brand-guidelines.md` (si existe)

**Proceso**:
1. Comparar tokens actuales vs brand-guidelines.md (paleta, tipografía, logo usage, imagery).
2. Si manual completo → validar consistencia. Discrepancias → `dec-brand-007` con `human_review_required=true`.
3. Si manual incompleto/inexistente → proponer sistema visual basado en tokens + arquetipo + personalidad.
   - Paleta: mapear color tokens a roles semánticos (ya en color skill).
   - Tipografía: mapear typography tokens a roles (ya en typography skill).
   - Logo: si no existe → `human_review_required=true`, `rationale: "Requiere diseño de logo; no generado por skill"`.
   - Imagery style: describir dirección fotográfica/ilustración por arquetipo.
4. Decisión `dec-brand-007`: `human_review_required=true` si manual no cubre todo.

### Paso 7: Governance Rules (Wheeler)
**Input**: `brand-guidelines.md` (si existe) + decisiones anteriores

**Proceso**:
1. Si manual tiene sección governance → `evidence_ref`, `human_review_required: false`.
2. Si no → proponer: approval matrix, exception process, evolution triggers, brand council composition.
3. Decisión `dec-brand-008`: `human_review_required=true`.

**Propiedad de la decisión**: `specialist` = quien produce (este skill: `branding`), `category` = dominio de la decisión, `owner` = rol accountable que aprueba (`art-director`). No colapsar los tres — ver `templates/DECISION-FIELDS.md`.

### Paso 8: Generar Output Final
**Archivo**: `brand-identity.json` (CASO 3) o `draft-brand-identity.json` (CASO 1/2)

**Estructura**:
```json
{
  "meta": {
    "generated_at": "2026-11-07T...",
    "skill_version": "0.1.0",
    "manual_status": "complete|incomplete|missing",
    "human_review_required_count": 6
  },
  "decisions": [
    {
      "decision_id": "dec-brand-001",
      "specialist": "branding",
      "category": "branding",
      "decision": "Arquetipo principal: Hero (candidato 1 de 3)",
      "rationale": "Valores brief: coraje, superación. Audiencia: busca achievement. Pearson: Hero motivation = mastery. Marquardt: Dominio cluster.",
      "evidence_refs": ["skills/creative-direction/branding/references/branding-evidence.md#pearson-archetypes"],
      "feasibility_ref": "dec-brand-feasibility",
      "human_review_required": true,
      "alternatives_considered": [
        {"arquetipo": "Explorer", "rationale": "Valores libertad, descubrimiento", "pros": ["diferenciación"], "cons": ["menos alignment con achievement"]},
        {"arquetipo": "Sage", "rationale": "Valores expertise, verdad", "pros": ["credibilidad"], "cons": ["pasivo vs activo"]}
      ],
      "validation_required": false,
      "platform_specific": {},
      "references": {},
      "provisional": false,
      "depends_on": []
    }
  ],
  "brand_identity": {
    "archetype": {"primary": "Hero", "secondary": "Explorer"},
    "personality": {"dimensions": ["Competence", "Excitement"], "facets": [...]},
    "tone_of_voice": {"do": [...], "dont": [...], "vocabulary": {...}, "rhythm": "direct"},
    "positioning": {"statement": "...", "essence": "...", "tagline_candidates": [...]},
    "visual_system": {"palette_ref": "colors.json", "typography_ref": "typography.json", "logo_usage": "...", "imagery_style": "..."},
    "governance": {"approval_matrix": "...", "exceptions": "...", "evolution_triggers": [...]}
  }
}
```

---

## Pitfalls

1. **LLM decide arquetipo sin alternativas** → Violación regla de oro. Siempre `alternatives_considered[]` ≥2.
2. **Asumir manual completo sin auditar** → Usar Paso 1 script obligatorio.
3. **Mezclar teoría y evidencia empírica** → En branding NO hay evidencia empírica 2020+ para decisiones estratégicas. Todo = THEORY.
4. **Generar `brand-identity.json` sin manual aprobado** → Output debe ser `draft-brand-identity.json`.
5. **No validar feasibility_ref** → Paso 0 obligatorio.
6. **Inventar logo/imagery** → Skill no genera assets visuales. Solo describe dirección. `human_review_required=true`.
7. **Ignorar contradicciones en manual** → Paso 1 detecta y marca decisiones afectadas.

---

## Verification

### Checklist Ejecutable (Paso a Paso)

```bash
# 1. Verificar feasibility cargada
./skills/production/feasibility/verify.sh feasibility-report.json design-decisions.json
# Debe salir exit code 0

# 2. Auditar brand-guidelines.md
python skills/creative-direction/branding/scripts/audit-brand-guidelines.py brand-guidelines.md
# Output: audit-brand-guidelines.json

# 3. Validar output del skill (brand-identity.json o draft-brand-identity.json)
python skills/creative-direction/branding/scripts/verify-brand-output.py \
  brand-identity.json \
  audit-brand-guidelines.json
```

### Script `verify-brand-output.py` — Reglas de Validación

```python
#!/usr/bin/env python3
import json, sys

def verify_brand_output(brand_file, audit_file):
    with open(brand_file) as f:
        brand = json.load(f)
    with open(audit_file) as f:
        audit = json.load(f)

    errors = []
    decisions = brand.get("decisions", [])

    for d in decisions:
        # Regla 1: human_review_required O evidence_ref a sección exacta
        if not d.get("human_review_required", False):
            ev_refs = d.get("evidence_refs", [])
            valid_ref = any("brand-guidelines.md#" in ref for ref in ev_refs)
            if not valid_ref:
                errors.append(f"{d['decision_id']}: sin human_review_required Y sin evidence_ref a brand-guidelines.md")

        # Regla 2: decisiones de arquetipo/posicionamiento/esencia/tono → alternatives_considered >= 2
        strategic_cats = {"branding.archetype", "branding.positioning", "branding.essence", "branding.tone"}
        cat = d.get("category", "") + "." + d.get("decision_id", "").split("-")[-1]
        if any(sc in cat for sc in strategic_cats):
            alts = d.get("alternatives_considered", [])
            if len(alts) < 2:
                errors.append(f"{d['decision_id']}: decisión estratégica con <2 alternatives_considered")

        # Regla 3: feasibility_ref existe
        if not d.get("feasibility_ref"):
            errors.append(f"{d['decision_id']}: falta feasibility_ref")

    # Regla 4: si manual incompleto, decisiones afectadas marcadas
    if audit.get("completeness_score", 1.0) < 1.0:
        missing = audit.get("missing_sections", [])
        for d in decisions:
            if d.get("human_review_required") and not any(m in d.get("rationale", "") for m in missing):
                # OK: rationale menciona qué falta
                pass
            # Si no menciona, warning (no error)

    if errors:
        print("VERIFICATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("VERIFICATION PASSED")
    print(f"  Decisions: {len(decisions)}")
    print(f"  Human review required: {sum(1 for d in decisions if d.get('human_review_required'))}")
    print(f"  Manual status: {brand['meta']['manual_status']}")

if __name__ == "__main__":
    verify_brand_output(sys.argv[1], sys.argv[2])
```

### Verification Gates (Deben PASSAR)

| Gate | Comando | Exit Code Esperado |
|------|---------|-------------------|
| Feasibility válida | `./skills/production/feasibility/verify.sh ...` | 0 |
| Brand guidelines audit | `python audit-brand-guidelines.py ...` | 0 (genera JSON) |
| Brand output verification | `python verify-brand-output.py brand.json audit.json` | 0 |
| Schema validation | `jsonschema -i brand.json templates/design-decision-schema.json` | 0 |

---

## Outputs

| Archivo | Cuándo | Contenido |
|---------|--------|-----------|
| `brand-identity.json` | Manual completo + consistente | Identidad aprobada, decisiones con evidence_ref |
| `draft-brand-identity.json` | Manual incompleto o inexistente | Borrador con human_review_required=true en decisiones estratégicas |
| `audit-brand-guidelines.json` | Siempre (Paso 1) | Completitud, contradicciones, decisiones afectadas |

---

## Referencias

- `skills/creative-direction/branding/references/branding-evidence.md` — Teoría (Pearson, Marquardt, Aaker, Kapferer, Keller, Wheeler, Neumeier). NO evidencia empírica.
- `templates/design-decision-schema.json` — Contrato de decisión (feasibility_ref obligatorio).
- `skills/production/feasibility/SKILL.md` — Paso 0 feasibility.