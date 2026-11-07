---
name: production-feasibility
version: 1.0.0
description: Use when evaluating whether a design decision can be implemented faithfully in the target platform (Elementor, Figma) without visual, functional, or editability loss.
---

# Production Feasibility Skill

## When to Use
- **FASE 2** del workflow `design-production.md`: antes de cualquier decisión creativa final
- Cuando el brief define `platform` y se necesitan constraints concretas
- Auditoria de decisiones existentes (`design-decisions.json`) contra plataforma objetivo
- Validación de que `feasibility_ref` en cada decisión apunta a clasificación `green` o `yellow`
- Cambio de plataforma mid-proyecto (re-evaluación completa)

## Procedure

### 1. Cargar Referencias de Plataforma
```python
# Input: brief-normalizado.json.target_platform
platform = brief["platform"]  # "elementor" | "figma" | "both"
constraints = read_file("skills/production/feasibility/references/platform-constraints.md")
# Parsear sección correspondiente a la plataforma
```

### 2. Evaluar Cada Requerimiento del Brief
Para cada `requirement` en `brief-normalizado.json.requirements[]`:
1. Identificar qué decisión creativa implica (color, tipografía, layout, interaction, branding, editorial)
2. Buscar en `platform-constraints.md` la capacidad correspondiente
3. Clasificar: `green` | `yellow` | `red` usando la matriz de la sección 3 del reference
4. Registrar en `decisions_evaluated[]`:
   ```json
   {
     "decision_id": "dec-color-001",
     "requirement": "Primary CTA debe usar brand color con hover state",
     "platform_capability": "Button widget nativo + Global Colors + hover state",
     "classification": "green",
     "constraints": ["Theme Style mapea 1:1 a CSS custom properties", "Hover state editable en widget"],
     "workaround": null,
     "blocking_reason": null
   }
   ```

### 3. Determinar Feasibilidad General
```python
if any(d.classification == "red" for d in decisions_evaluated):
    overall = "blocked"
elif any(d.classification == "yellow" for d in decisions_evaluated):
    overall = "conditional"
else:
    overall = "pass"
```

### 4. Generar `feasibility-report.json`
```json
{
  "platform": "elementor",
  "platform_version": "3.24.x",
  "verified_date": "2026-11-07",
  "overall_feasibility": "conditional",
  "decisions_evaluated": [...],
  "summary": {
    "green": 12,
    "yellow": 3,
    "red": 0,
    "blocking_decisions": []
  },
  "next_steps": [
    "Documentar workaround para dec-layout-003 (masonry)",
    "Validar LCP para dec-branding-002 (Lottie) en staging"
  ]
}
```

### 5. Entregar a FASE 3
El `feasibility-report.json` se pasa a los skills creativos. Cada decisión que generen **debe** incluir `feasibility_ref` que matchee `decision_id` de este reporte.

---

## Pitfalls

| Pitfall | Síntoma | Prevención |
|---------|---------|------------|
| **Asumir que Figma = Elementor** | Decisión `green` en Figma (variables, auto-layout) pero `red` en Elementor (no exportable) | Siempre evaluar **ambas** plataformas; la más restrictiva gana |
| **Ignorar versión de plataforma** | Elementor 3.24 soporta Lottie; 3.20 no. Feasibility report sin versión = inválido | `platform_version` y `verified_date` obligatorios en reporte |
| **Workaround sin documentar** | `yellow` clasificado pero sin `workaround` ni `blocking_reason` | Checklist Verification exige workaround documentado para cada yellow |
| **Feasibility report incompleto** | Faltan decisiones evaluadas para requisitos del brief | Validar que `len(decisions_evaluated) >= len(brief.requirements)` |
| **Decisiones creativas sin feasibility_ref** | FASE 3 produce `design-decisions.json` sin referenciar FASE 2 | Guard-rail en workflow: FASE 3 falla si falta feasibility_ref |

---

## Verification

**Procedimiento ejecutable para validar que cada decisión en `design-decisions.json` tiene `feasibility_ref` válido contra `feasibility-report.json`:**

### Checklist Paso a Paso (ejecutable por humano o Design Critic)

```bash
#!/usr/bin/env bash
# verify-feasibility-refs.sh
# Uso: ./verify-feasibility-refs.sh <feasibility-report.json> <design-decisions.json>
# Exit code: 0 = PASS, 1 = FAIL

set -euo pipefail

FEASIBILITY_PATH="${1:-}"
DECISIONS_PATH="${2:-}"

if [ -z "$FEASIBILITY_PATH" ] || [ -z "$DECISIONS_PATH" ]; then
    echo "Uso: $0 <feasibility-report.json> <design-decisions.json>"
    exit 1
fi

# 1. Verificar que ambos archivos existen
[ -f "$FEASIBILITY_PATH" ] || { echo "❌ FALTA: $FEASIBILITY_PATH"; exit 1; }
[ -f "$DECISIONS_PATH" ] || { echo "❌ FALTA: $DECISIONS_PATH"; exit 1; }

# 2. Validar JSON syntax
jq empty "$FEASIBILITY_PATH" 2>/dev/null || { echo "❌ JSON inválido: $FEASIBILITY_PATH"; exit 1; }
jq empty "$DECISIONS_PATH" 2>/dev/null || { echo "❌ JSON inválido: $DECISIONS_PATH"; exit 1; }

# 3. Extraer decision_ids válidos del feasibility report (solo green/yellow)
VALID_IDS=$(jq -r '.decisions_evaluated[] | select(.classification != "red") | .decision_id' "$FEASIBILITY_PATH")

if [ -z "$VALID_IDS" ]; then
    echo "⚠️ ADVERTENCIA: feasibility-report no tiene decisiones green/yellow"
fi

# 4. Verificar cada decisión en design-decisions.json
ERRORS=0
for decision in $(jq -c '.[]' "$DECISIONS_PATH"); do
    DECISION_ID=$(echo "$decision" | jq -r '.decision_id')
    FEAS_REF=$(echo "$decision" | jq -r '.feasibility_ref')
    
    # 4a. feasibility_ref existe
    if [ "$FEAS_REF" = "null" ] || [ -z "$FEAS_REF" ]; then
        echo "❌ DECISIÓN $DECISION_ID: falta feasibility_ref"
        ERRORS=$((ERRORS + 1))
        continue
    fi
    
    # 4b. feasibility_ref matchea un decision_id válido (green/yellow)
    if ! echo "$VALID_IDS" | grep -q "^$FEAS_REF$"; then
        echo "❌ DECISIÓN $DECISION_ID: feasibility_ref '$FEAS_REF' no existe o es 'red' en feasibility-report"
        ERRORS=$((ERRORS + 1))
        continue
    fi
    
    # 4c. Double-check: classification del feasibility_ref no es red
    CLASS=$(jq -r ".decisions_evaluated[] | select(.decision_id == \"$FEAS_REF\") | .classification" "$FEASIBILITY_PATH")
    if [ "$CLASS" = "red" ]; then
        echo "❌ DECISIÓN $DECISION_ID: feasibility_ref apunta a clasificación 'red'"
        ERRORS=$((ERRORS + 1))
    fi
done

# 5. Cobertura: feasibility-report debe cubrir todos los requisitos del brief
REQ_COUNT=$(jq '.requirements | length' "$FEASIBILITY_PATH" 2>/dev/null || echo 0)
EVAL_COUNT=$(jq '.decisions_evaluated | length' "$FEASIBILITY_PATH" 2>/dev/null || echo 0)
if [ "$EVAL_COUNT" -lt "$REQ_COUNT" ]; then
    echo "⚠️ ADVERTENCIA: feasibility-report evalúa $EVAL_COUNT decisiones pero brief tiene $REQ_COUNT requisitos"
fi

# 6. Resultado
if [ $ERRORS -eq 0 ]; then
    echo "✅ VERIFICACIÓN PASÓ: todas las decisiones tienen feasibility_ref válido (green/yellow)"
    exit 0
else
    echo "❌ VERIFICACIÓN FALLÓ: $ERRORS errores. DEVOLVER A FASE 2."
    exit 1
fi
```

### Versión Python (para integración en Design Critic / Orchestrator)

```python
def verify_feasibility_refs(feasibility_path: str, decisions_path: str) -> tuple[bool, list[str]]:
    """
    Returns (passed, errors_list)
    """
    import json
    
    with open(feasibility_path) as f:
        feas = json.load(f)
    with open(decisions_path) as f:
        decisions = json.load(f)
    
    # Build valid refs map
    valid_refs = {
        d["decision_id"]: d["classification"]
        for d in feas.get("decisions_evaluated", [])
        if d["classification"] in ("green", "yellow")
    }
    
    errors = []
    for dec in decisions:
        dec_id = dec.get("decision_id")
        feas_ref = dec.get("feasibility_ref")
        
        if not feas_ref:
            errors.append(f"{dec_id}: missing feasibility_ref")
            continue
        
        if feas_ref not in valid_refs:
            errors.append(f"{dec_id}: feasibility_ref '{feas_ref}' not found or red")
            continue
        
        # Optional: cross-check specialist matches
        # if dec.get("specialist") not in feas_ref:
        #     errors.append(f"{dec_id}: specialist mismatch with feasibility_ref")
    
    return len(errors) == 0, errors
```

### Criterios de Aprobación (PASS/FAIL)

| Check | PASS si... | FAIL si... |
|-------|------------|------------|
| Archivos existen | Ambos JSONs presentes y válidos | Cualquiera falta o JSON inválido |
| `feasibility_ref` presente | 100% decisiones lo tienen | Alguna decisión lo omite |
| `feasibility_ref` válido | Matchea `decision_id` en feasibility-report con classification `green`/`yellow` | No matchea o apunta a `red` |
| Cobertura | `len(decisions_evaluated) >= len(brief.requirements)` | Faltan evaluaciones |
| Versión plataforma | `platform_version` y `verified_date` presentes | Faltan metadatos de versión |

> **Nota**: Este checklist DEBE ejecutarse en FASE 3 (condición de salida) y opcionalmente en FASE 5 (Design Critic valida que el Builder no recibió decisiones infeasibles). Si no hay entorno `jq`/`python`, el humano ejecuta la versión manual: abrir ambos JSONs y verificar visualmente cada `feasibility_ref`.