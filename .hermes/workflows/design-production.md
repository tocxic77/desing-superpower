# Design Production Workflow

**Workflow maestro** — Orquesta el pipeline completo: Brief → Feasibility → Creative Decisions → Build → Validation → Correction → Human Approval.

Invoca workflows de dominio (website-production, branding-production, presentation-production) como sub-fases según `project_type`.

---

## FASE 1 — BRIEF INTERPRETATION

| | |
|---|---|
| **Skill** | `core/design-orchestration` |
| **Input** | Brief cliente (documento, notas, email) |
| **Herramientas** | `skill_view("core/design-orchestration")`, `read_file("templates/brief-schema.json")` |
| **Output** | `brief-normalizado.json` (válido contra `brief-schema.json`) + `specialist-list.json` |

**Procedimiento**:
1. Extraer: `project_type`, `business_goal`, `target_audience`, `primary_actions`, `platform`, `constraints`, `approval_required`
2. Validar contra `templates/brief-schema.json`
3. Si campos críticos faltan → **FALLAR FASE 1** → solicitar clarificación (no continuar)
4. Mapear `project_type` → workflow de dominio + lista de especialistas creativos requeridos
5. Emitir `brief-normalizado.json` + `specialist-list.json`

**Condición de salida**: `brief-normalizado.json` existe y pasa validación de schema. Si no → **DETENER workflow, escalar a humano**.

---

## FASE 2 — PRODUCTION FEASIBILITY

| | |
|---|---|
| **Skill** | `production/feasibility` |
| **Input** | `brief-normalizado.json` + `target-platform` (desde brief) |
| **Herramientas** | `skill_view("production/feasibility")`, `read_file("skills/production/feasibility/references/platform-constraints.md")` |
| **Output** | `feasibility-report.json` |

**Procedimiento**:
1. Cargar `platform-constraints.md` para la plataforma objetivo
2. Evaluar cada requerimiento del brief contra constraints de plataforma
3. Clasificar cada decisión potencial: `green` (nativo), `yellow` (workaround documentado), `red` (bloqueado)
4. Generar `feasibility-report.json` con:
   - `platform`
   - `decisions_evaluated[]` (cada una con `decision_id`, `classification`, `constraints`, `workaround`, `blocking_reason`)
   - `overall_feasibility`: `pass` | `conditional` | `blocked`

**Condición de salida**:
- `overall_feasibility == "pass"` o `"conditional"` → **CONTINUAR a FASE 3**
- `overall_feasibility == "blocked"` → **DETENER workflow, escalar a humano con `blocking_reason`**
- Si `feasibility-report.json` no existe o no tiene `decisions_evaluated` → **FALLAR FASE 2, DETENER**

---

## FASE 3 — CREATIVE DECISIONS

| | |
|---|---|
| **Skills** | `creative-direction/{color,typography,branding,editorial,layout,interaction}` (según `specialist-list.json`) |
| **Input** | `brief-normalizado.json` + `feasibility-report.json` |
| **Herramientas** | `skill_view("creative-direction/<specialist>")`, `read_file("templates/design-decision-schema.json")` |
| **Output** | `design-decisions.json` (array de objetos válidos contra `design-decision-schema.json`) |

**Procedimiento**:
1. Para cada especialista en `specialist-list.json`:
   - Cargar skill correspondiente
   - Ejecutar procedimiento del skill (evidence synthesis, decision definition, etc.)
   - Producir decisión con **todos los campos requeridos** del schema
2. Agregar todas las decisiones en `design-decisions.json`
3. **VALIDACIÓN CRÍTICA** (punto de fallo explícito):
   - Validar `design-decisions.json` contra `templates/design-decision-schema.json`
   - **VERIFICAR**: cada decisión tiene `feasibility_ref` que matchea una entrada en `feasibility-report.json.decisions_evaluated`
   - **VERIFICAR**: cada `feasibility_ref` apunta a clasificación `green` o `yellow` (no `red`)

**Condición de salida**:
- `design-decisions.json` existe, pasa schema, **y** todas las decisiones tienen `feasibility_ref` válido → **CONTINUAR a FASE 4**
- **SI ALGUNA DECISIÓN FALTA `feasibility_ref` O APUNTA A `red`** → **DETENER, DEVOLVER A FASE 2** (no continuar a FASE 4)
- Si validación de schema falla → **DETENER, DEVOLVER A FASE 3** (re-ejecutar skill con corrección)

> **Este es el guard-rail principal**: el Builder NUNCA recibe decisiones sin viabilidad verificada. Si el workflow intenta continuar sin `feasibility_ref`, es un bug del workflow, no del schema.

---

## FASE 4 — BUILD

| | |
|---|---|
| **Skill** | `core/design-orchestration` (modo build) |
| **Input** | `design-decisions.json` |
| **Herramientas** | `builders/{elementor,html,figma,ppt,pdf,email,social}` (según plataforma) |
| **Output** | Artefacto en **staging** + `build-log.json` |

**Procedimiento**:
1. Cargar `design-decisions.json`
2. Seleccionar builder según `platform` del brief
3. Ejecutar build aplicando tokens, componentes, specs de las decisiones
4. Registrar cada paso en `build-log.json` (decisión aplicada, token usado, componente creado, warnings)
5. Desplegar a **staging environment** (nunca producción)

**Condición de salida**:
- Artefacto accesible en staging URL + `build-log.json` completo → **CONTINUAR a FASE 5**
- Si build falla (error de builder, token missing, component missing) → **DETENER, DEVOLVER A FASE 3** (decisión infeasible no detectada) o **ESCALAR**

---

## FASE 5 — VALIDATION (INDEPENDIENTE)

| | |
|---|---|
| **Skill** | `core/design-critique` |
| **Input** | **Solo** staging URL (NO `build-log.json`, NO `design-decisions.json`, NO `feasibility-report.json`) |
| **Herramientas** | `tools/validators/*` (contrast, a11y, performance, visual_regression, responsive, hierarchy, typography, conversion) |
| **Aislamiento** | `delegate_task(role="critic", context="staging_url + thresholds only")` |
| **Output** | `diagnostic.json` (array válido contra `templates/diagnostic-schema.json`) |

**Procedimiento**:
1. Spawn `delegate_task` con role="critic" — contexto mínimo: staging URL, thresholds de validación, platform
2. Critic ejecuta suite de validadores (secuencial: Playwright session única para a11y+visual+responsive; Lighthouse aparte para performance)
3. Cada hallazgo → `DesignDiagnostic` (schema validado)
4. Agregar en `diagnostic.json`

**Condición de salida**:
- `diagnostic.json` existe, pasa schema → **CONTINUAR a FASE 6**
- Si Critic no puede acceder a staging → **DETENER, ESCALAR** (infra issue)

---

## FASE 6 — CORRECTION LOOP

| | |
|---|---|
| **Skill** | `core/design-critique` (autoriza) + `core/design-orchestration` (aplica) |
| **Input** | `diagnostic.json` + staging URL |
| **Herramientas** | `tools/validators/*` (re-ejecución targeted), builders (para fixes) |
| **Output** | `corrections-log.json` + staging actualizado |

**Procedimiento**:
1. Filtrar `diagnostic.json`: solo issues con `auto_fix_allowed == true` y `severity` en `["high", "medium"]`
2. Para cada issue:
   - Aplicar corrección mínima (CSS, token, copy, asset)
   - Registrar en `corrections-log.json`: `issue_id`, `action`, `before`, `after`
   - Re-ejecutar **solo validadores afectados** (targeted re-validation)
   - Verificar: issue resuelto + **no regresiones** en `regression_check`
3. Contadores:
   - Max 3 reintentos por issue (High)
   - Max 2 reintentos por issue (Medium)
   - Max 5 ciclos totales por proyecto

**Condición de salida**:
- **PASS**: 0 Critical, 0 High, 0 Medium sin resolver → **CONTINUAR a FASE 7**
- **STALLED**: Max ciclos alcanzado o issue no corregible → **DETENER, ESCALAR a FASE 7 con risk=high**
- **REGRESSION_SPIKE**: Nuevos Critical/High introducidos → **DETENER, ESCALAR**

---

## FASE 7 — HUMAN APPROVAL GATE

| | |
|---|---|
| **Input** | `diagnostic.json` (final) + `corrections-log.json` + `feasibility-report.json` + `brief-normalizado.json` |
| **Decisión** | `approve` | `reject` | `request_changes` |

**Clasificación de riesgo** (calculada automáticamente):
- **Low**: `overall_feasibility == "pass"` AND 0 issues en diagnostic final AND 0 corrections
- **Medium**: `overall_feasibility == "conditional"` OR ≤ 2 Medium issues resueltos OR ≤ 1 correction cycle
- **High**: Cualquier Critical/High resuelto en loop OR `overall_feasibility == "blocked"` (ya escalado antes) OR regression spike

**Reglas de aprobación**:
- **Low**: Auto-aprobación → **OUTPUT: artefacto aprobado para producción**
- **Medium**: Notificación humana con resumen ejecutivo (1 párrafo) + scorecard de validadores → espera confirmación (timeout 24h → auto-escalar)
- **High**: Aprobación humana **obligatoria** con revisión completa → **sin respuesta: BLOQUEAR ENTREGA, notificar, mantener artefacto en staging** (no auto-rechazar)

**Output final**:
- `final-report.md` (template: `templates/final-report-template.md`)
- Artefacto en staging listo para deploy (si aprobado)
- `approval-record.json`: `{decision, reviewer, timestamp, reason}`

---

## MAPEO PROJECT_TYPE → WORKFLOWS DE DOMINIO

| project_type | FASE 3 Specialists | FASE 4 Builder | FASE 5 Validators Extra |
|--------------|-------------------|----------------|------------------------|
| `landing_page` | color, typography, branding, editorial, layout | elementor, html | conversion, hierarchy |
| `brand_identity` | color, typography, branding | figma, pdf, ppt | hierarchy, typography |
| `presentation` | typography, editorial, layout, branding | ppt, pdf | hierarchy, typography |
| `email_campaign` | color, typography, editorial | email | hierarchy, responsive |
| `social_campaign` | color, typography, branding, editorial | social | responsive, conversion |
| `multi_format` | Todos según sub-deliverables | Múltiples | Todos según formato |

---

## ARCHIVOS DE REFERENCIA DEL WORKFLOW

- `templates/brief-schema.json` — FASE 1
- `templates/design-decision-schema.json` — FASE 3
- `templates/diagnostic-schema.json` — FASE 5
- `templates/final-report-template.md` — FASE 7
- `skills/production/feasibility/references/platform-constraints.md` — FASE 2
- `.hermes/workflows/design-loop.md` — Lógica de corrección (FASE 6)
- `.hermes/workflows/website-production.md` — Sub-workflow landing page
- `.hermes/workflows/branding-production.md` — Sub-workflow brand
- `.hermes/workflows/presentation-production.md` — Sub-workflow presentation