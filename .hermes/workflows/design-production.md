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
- `overall_feasibility == "pass"` o `"conditional"` → **CONTINUAR a FASE 3.1**
- `overall_feasibility == "blocked"` → **DETENER workflow, escalar a humano con `blocking_reason`**
- Si `feasibility-report.json` no existe o no tiene `decisions_evaluated` → **FALLAR FASE 2, DETENER**

---

## FASE 3.1 — BRANDING GATE (NUEVO)

**Propósito**: Validar output del branding skill (`brand-identity.json` o `draft-brand-identity.json`) antes de permitir que Color/Typography/Builder usen decisiones de marca.

| | |
|---|---|
| **Input** | `brand-identity.json` o `draft-brand-identity.json` (output del branding skill) |
| **Herramientas** | `read_file`, `skill_view("creative-direction-branding")` |
| **Output** | `brand-approval.json` (si aprobado) / bloqueo con lista de decisiones pendientes |

### Procedimiento:

1. **Leer archivo de identidad de marca**:
   - Si existe `brand-identity.json` → `manual_status` esperado: `"complete"`
   - Si existe `draft-brand-identity.json` → `manual_status` en `["incomplete", "missing"]`
   - Si no existe ninguno → **FALLAR FASE 3.1, DETENER** (branding skill no ejecutado)

2. **Evaluar `meta.manual_status`**:

   #### CASO A: `manual_status == "complete"` (brand-guidelines.md completo y consistente)
   - Validar que decisiones estratégicas (`dec-brand-001` a `dec-brand-006`) tienen `evidence_ref` a `brand-guidelines.md#seccion-exacta`
   - Validar que `human_review_required == false` en decisiones estratégicas
   - **Generar `brand-approval.json` automáticamente** (ver formato abajo)
   - **CONTINUAR a FASE 3.2 (Color/Typography)**

   #### CASO B: `manual_status == "incomplete"` (manual existe pero incompleto/contradictorio)
   - **NO bloquear FASE 3 entera**. Separar decisiones:
     - **Estratégicas pendientes**: `dec-brand-001` a `dec-brand-006` con `human_review_required == true`
     - **Operativas listas**: `dec-brand-007`, `dec-brand-008` si tienen `evidence_ref` a manual
   - **Color y Typography PUEDEN AVANZAR** usando decisiones operativas con `evidence_ref` (paleta, tipografía, logo usage documentados)
   - **Builder NO PUEDE** construir sistema de marca completo (falta arquetipo, posicionamiento, esencia, tono aprobados)
   - **Builder PUEDE** construir componentes que NO dependan de decisiones estratégicas pendientes:
     - Tokens de color (si `dec-brand-007` tiene `evidence_ref`)
     - Tokens de tipografía (si `dec-brand-007` tiene `evidence_ref`)
     - Layouts, componentes UI, páginas sin copy de posicionamiento/tono
   - **Bloquear solo**: decisiones de copy/voz/posición de marca, hero messaging, tagline, brand manifesto
   - Requerir `brand-approval.json` firmado por humano para decisiones estratégicas pendientes antes de pasar a FASE 4 (Build) con sistema de marca completo
   - **Continuar a FASE 3.2 (Color/Typography) con flag `brand_partial: true`**

   #### CASO C: `manual_status == "missing"` (sin brand-guidelines.md)
   - **BLOQUEO COMPLETO**. Sin manual no hay nada que aprobar.
   - `draft-brand-identity.json` requiere revisión humana completa + creación de `brand-guidelines.md` aprobado
   - **NO CONTINUAR** a FASE 3.2 ni FASE 4
   - Escalar a humano: "Brand guidelines requerido. Revisar draft-brand-identity.json, crear brand-guidelines.md, re-ejecutar branding skill."

3. **Generación de `brand-approval.json`**:

   **Formato esperado** (archivo manual creado por humano, NO generado por skill):
   ```json
   {
     "approved_at": "2026-11-07T14:30:00Z",
     "approved_by": "nombre.apellido@dominio.com",
     "manual_status_at_approval": "complete|incomplete",
     "decisions_approved": [
       "dec-brand-001",
       "dec-brand-002",
       "dec-brand-003",
       "dec-brand-004",
       "dec-brand-005",
       "dec-brand-006"
     ],
     "brand_guidelines_updated": true,
     "brand_guidelines_version": "v1.0",
     "output_file": "brand-identity.json",
     "notes": "Aprobado arquetipo Hero/Explorer, positioning statement v3, tagline 'Build boldly'"
   }
   ```

   **Cómo se crea** (comando del Orchestrator / humano):
   - **Opción 1 (CLI)**: `hermes approve-brand --decisions dec-brand-001,dec-brand-002,... --notes "..."`
   - **Opción 2 (Manual)**: Humano crea archivo `brand-approval.json` en raíz del proyecto y hace commit
   - **Opción 3 (UI)**: Hermes desktop → botón "Approve Brand" en panel del proyecto → genera JSON

   **Validación automática** (FASE 3.1 verifica):
   - `decisions_approved` cubre todas las decisiones estratégicas pendientes (`human_review_required == true` en `dec-brand-001` a `006`)
   - `brand_guidelines_updated == true` (confirmación de que manual refleja decisiones)
   - `output_file` existe y es `brand-identity.json` (no draft)

4. **Condición de salida FASE 3.1**:
   - **CASO A**: `brand-approval.json` existe y válido → **CONTINUAR a FASE 3.2**
   - **CASO B**: `brand-approval.json` existe para decisiones estratégicas pendientes → **CONTINUAR a FASE 3.2 con `brand_partial: true`**
   - **CASO B sin approval**: **BLOQUEAR FASE 4 (Build) para sistema de marca**, permitir FASE 3.2
   - **CASO C**: **DETENER workflow completo**, escalar a humano

---

## FASE 3.2 — CREATIVE DECISIONS (Color, Typography, Editorial, Layout, Interaction)

| | |
|---|---|
| **Skills** | `creative-direction/{color,typography,editorial,layout,interaction}` (según `specialist-list.json`) |
| **Input** | `brief-normalizado.json` + `feasibility-report.json` + `brand-identity.json` (o `draft-brand-identity.json` con `brand_partial: true`) |
| **Herramientas** | `skill_view("creative-direction/<specialist>")`, `read_file("templates/design-decision-schema.json")` |
| **Output** | `design-decisions.json` (array de objetos válidos contra `design-decision-schema.json`) |

**Procedimiento**:
1. Para cada especialista en `specialist-list.json` (excluyendo `branding`, ya ejecutado en FASE 3.1):
   - Cargar skill correspondiente
   - **Si `brand_partial: true`**: skills de color/typography leen `brand-identity.json`/`draft-brand-identity.json` para tokens operativos (`dec-brand-007`, `dec-brand-008` con `evidence_ref`). No usan decisiones estratégicas pendientes.
   - Ejecutar procedimiento del skill
   - Producir decisión con **todos los campos requeridos** del schema
2. Agregar todas las decisiones en `design-decisions.json` (incluyendo decisiones de branding ya validadas)
3. **VALIDACIÓN CRÍTICA** (punto de fallo explícito):
   - Validar `design-decisions.json` contra `templates/design-decision-schema.json` — **v0.2 es la versión canónica**; v0.1 está archivado (`design-decision-schema.v0.1.json`) y no debe usarse
   - **VERIFICAR**: `specialist` identifica al productor de la decisión (especialista de dominio), `category` el dominio, `owner` el rol accountable — ver `templates/DECISION-FIELDS.md`
   - **VERIFICAR**: cada decisión tiene `feasibility_ref` que matchea una entrada en `feasibility-report.json.decisions_evaluated`
   - **VERIFICAR**: cada `feasibility_ref` apunta a clasificación `green` o `yellow` (no `red`)
   - **VERIFICAR**: `design-decisions.json` es un array (no `{"decisions": [...]}`); `verify-feasibility-refs.sh` itera con `jq '.[]'`

**Condición de salida**:
- `design-decisions.json` existe, pasa schema, **y** todas las decisiones tienen `feasibility_ref` válido → **CONTINUAR a FASE 4**
- **SI ALGUNA DECISIÓN FALTA `feasibility_ref` O APUNTA A `red`** → **DETENER, DEVOLVER A FASE 2** (no continuar a FASE 4)
- Si validación de schema falla → **DETENER, DEVOLVER A FASE 3.2** (re-ejecutar skill con corrección)

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
- `templates/design-decision-schema.json` — FASE 3 (v0.2, **canónico**)
- `templates/design-decision-schema.v0.1.json` — ARCHIVADO, no usar
- `templates/DECISION-FIELDS.md` — semántica de specialist/category/owner
- `templates/diagnostic-schema.json` — FASE 5
- `templates/final-report-template.md` — FASE 7
- `skills/production/feasibility/references/platform-constraints.md` — FASE 2
- `.hermes/workflows/design-loop.md` — Lógica de corrección (FASE 6)
- `.hermes/workflows/website-production.md` — Sub-workflow landing page
- `.hermes/workflows/branding-production.md` — Sub-workflow brand
- `.hermes/workflows/presentation-production.md` — Sub-workflow presentation