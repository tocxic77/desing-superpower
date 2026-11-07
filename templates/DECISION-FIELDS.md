# Campos de una decisión de diseño — semántica normativa

Contrato: `templates/design-decision-schema.json` (v0.2, **canónico**). v0.1 archivado en `templates/design-decision-schema.v0.1.json`.

## Los tres campos que se confunden

| Campo | Pregunta que responde | Valores | Ejemplo |
|-------|------------------------|---------|---------|
| `specialist` | ¿Quién **produce** la decisión? | Especialista de dominio (`color`, `typography`, `branding`, `editorial`, `layout`, `interaction`, `conversion`) o agente de fase (`feasibility`, `ux-designer`, `web-builder`, `design-critic`, `sales-specialist`, `orchestrator`) | `"editorial"` |
| `category` | ¿A qué **dominio** pertenece? | Mismo vocabulario de dominio | `"editorial"` |
| `owner` | ¿Quién la **aprueba**? (accountable) | Rol o persona | `"art-director"` |

**Regla**: no se colapsan. Si los tres dicen lo mismo se perdió la trazabilidad de propiedad:

- `specialist` = `color` → la decisión de color la produce el skill color. **`art-director` NO es un valor válido de `specialist`** (v0.1 lo permitía por ambigüedad; v0.2 lo rechaza).
- `category` = `color` → pertenece al dominio color. Difiere de `specialist` cuando un especialista emite fuera de su dominio (p.ej. `specialist: editorial` + `category: layout` para reglas de reflow).
- `owner` = `art-director` → el Art Director firma. Con `human_review_required: true`, `owner` nombra al humano o su rol responsable de aprobar, nunca al agente que produjo.

## Resto de campos

| Campo | Obligatorio | Nota |
|-------|-------------|------|
| `decision_id` | sí | `dec-<dominio>-<NNN>`; el prefijo sigue el **dominio**, no el productor |
| `decision` | sí | ≥10 caracteres, accionable |
| `rationale` | sí | teoría / evidencia empírica verificada / declaración explícita de ausencia |
| `constraints` | sí | ≥1 elemento; si no hay, `["ninguna conocida"]` |
| `feasibility_ref` | sí | `decision_id` del `feasibility-report.json`, clasificación green o yellow |
| `validation_required` | sí | `true` (validación por defecto) o lista de validadores de FASE 5 |
| `human_review_required` | sí | obliga a `true` si `provisional: true` |
| `provisional` | no | si `true` → exige `depends_on` no vacío y `human_review_required: true` |
| `depends_on` | no | `decision_id`s bloqueantes |
| `references` | no | cross-layer: ids de decisiones previas que consume |
| `evidence_refs` | no | `ruta#ancla` a un archivo de referencias del skill; el ancla debe existir |
| `alternatives_considered` | no | obligatorio en decisiones estratégicas de branding |
| `tokens_affected` | no | tokens de `design-system/tokens/` |
| `platform_specific` | no | specs para el Builder (string u objeto por plataforma) |

## Formato del archivo de decisiones

`design-decisions.json` es un **array** de objetos decisión (FASE 3, condición de salida). No envolver en `{"decisions": [...]}`: `skills/production/feasibility/SKILL.md#verification` itera con `jq '.[]'`. Si un proyecto ya usa el envoltorio, `verify-editorial-coherence.py` acepta ambos, pero el formato canónico es el array.
