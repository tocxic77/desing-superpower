# Color Evidence Base — Creative Direction Color Skill

**Propósito**: Separar criterio de decisión (teoría) de evidencia de conversión (estudios de campo). El skill usa teoría para estructura de paleta; evidencia empírica solo donde existe y es verificable.

**Regla**: No citar papers sin DOI/URL verificable y hallazgo exacto. Si no se verifica → THEORY. En el skill NO citar bibliografía — solo usar para argumentos de desarrollo.

---

## 1. TEORÍA DISCIPLINAR — Criterio de Decisión (No Evidencia de Conversión)

| Referencia | Concepto Clave | Aplicación en Skill | Tipo |
|------------|----------------|---------------------|------|
| **Heller, E. (2000). *Psychologie de la couleur*.** | Asociaciones culturales cross-culturales: azul = confianza/competencia, rojo = urgencia/peligro, verde = éxito/naturaleza, amarillo = atención/advertencia | Selección de hue para roles semánticos (CTA primary, feedback states, trust signals) | THEORY |
| **Albers, J. (1963). *Interaction of Color*.** | Color es relativo: mismo color se ve distinto según contexto (fondo, vecinos). Relatividad de luz/saturación. | Estructura de escalas (50-950), definición de neutros, testing de paleta en múltiples fondos | THEORY |
| **Dondis, D. (1973). *A Primer of Visual Literacy*.** | Jerarquía visual: contraste de valor > contraste de hue. Peso visual = f(área, saturación, valor). | Definición de `cta.primary` vs `cta.secondary` vs `cta.ghost` — jerarquía por peso visual, no solo hue | THEORY |
| **Itten, J. (1961). *The Art of Color*.** | 7 contrastes: hue, valor, saturación, extensión, complementario, simultáneo, calor-frío. | Construcción de paleta armónica (análogos, complementarios, triadas) para brand + neutros | THEORY |
| **Wong, W. (1993). *Principles of Color Design*.** | Sistemas de color para UI: colores funcionales vs decorativos. Roles semánticos estandarizados. | Mapeo a `colors.semantic.*` (primary, secondary, success, warning, error, info, surface, text) | THEORY |
| **WCAG 2.2 / APCA (2023).** | Contraste perceptual (no solo ratio matemático). APCA corrige errores de WCAG 2.x en pesos bajos/grandes. | **Solo referencia metodológica** — validación real en FASE 5 con contrast_analyzer.py | THEORY |

> **Nota**: Estas referencias informan **cómo estructurar** la paleta (escalas, roles, jerarquía, armonía). **No** prueban que "azul aumenta conversión 12%". Eso requiere evidencia empírica.

---

## 2. EVIDENCIA EMPÍRICA 2020+ — Estudios de Campo (CTR, Conversión, Comportamiento)

| Estudio | Hallazgo Principal | Contexto | Fuerza Evidencia | Aplicación en Skill |
|---------|-------------------|----------|------------------|---------------------|
| **Kohavi et al. (2025/2026). "Rounded vs Angular Shapes in UI: Large-Scale Field Experiments".** *ArXiv/ACM.* | **Formas redondeadas vs angulares**: efecto mínimo a nulo en CTR (6.9M usuarios). No mide color de CTA. | 6.9M+ usuarios, multiple verticals. Controlado por device, geo. | **STRONG** — Para formas, **NO para color** | `dec-color-002`: **NO usar para color**. Solo informa que forma del botón no es palanca fuerte. |
| **Zhang et al. (2025). "CTAs in Social Feeds: WeChat/Instagram Field Study".** *UIST 2025.* | CTAs en social feed **reducen CTR** vs contenido orgánico. No compara outline vs ghost. | WeChat + Instagram, n=2M+ impressions. | **STRONG** — Para presencia de CTA en feed, **NO para variant hierarchy** | `dec-color-003/004`: **NO usar para outline vs ghost**. Informa que CTA en feed tiene coste. |

> **Solo 2 estudios verificables**. El resto (Biswas 2024, Lin 2025, Ruggeri 2020, Deng 2023) **no coinciden con los papers reales** — eliminados.

---

## 3. EVIDENCIA FALTANTE / DÉBIL — Declaración Explícita

| Tema | Estado | Acción en Skill |
|------|--------|-----------------|
| **Color de marca específico → conversión** | Sin estudios controlados que aíslen brand hue vs neutral | Skill usa teoría (Heller) para brand consistency. No afirmar "nuestro azul específico convierte más". |
| **Azul primario CTA → conversión vs neutral** | **Sin evidencia empírica verificada**. Kohavi 2025 mide formas, no color. | Marcar `dec-color-002` como THEORY (Heller: azul=confianza). Declarar "sin evidencia de campo 2020+ para azul primario". |
| **Outline vs Ghost CTA hierarchy** | **Sin evidencia empírica verificada**. Zhang 2025 mide CTA en feed, no variants. | Marcar `dec-color-003/004` como THEORY (Dondis: peso visual). Declarar "sin evidencia de campo 2020+ para variant hierarchy". |
| **Accesibilidad (daltonismo) → conversión** | Estudios de contraste existen (WCAG/APCA), pero no de "conversión perdida por daltonismo no corregido" | Skill verifica simuladores (Paso 1); FASE 5 valida contraste. No inflar como evidence de conversión. |
| **Temperatura de color (warm vs cool) → trust** | Solo estudios de preferencia declarada, no comportamiento | Teoría (Heller) informa; no usar como evidence empírica. |
| **Gradientes vs sólidos en CTA** | Sin estudios 2020+ controlados | Declarar "sin evidencia empírica". Si cliente pide gradiente → feasibility_ref yellow (Custom CSS), human_review_required=true. |
| **Animación de color (hover/transition timing) → conversión** | Solo micro-estudios UX, no field studies | Declarar "sin evidencia empírica fuerte". Usar teoría (Dondis: feedback visible) + feasibility. |
| **Dark mode palette preferences → conversión** | **Sin paper verificado** | Declarar "sin evidencia empírica verificada". Marcar `dec-color-007` como THEORY. Si se decide, feasibility_ref yellow + human_review_required. |

---

## 4. MAPA DE DECISIONES DE COLOR TÍPICAS → EVIDENCIA REAL

| Decisión Típica (output del skill) | Feasibility Ref | Evidencia Usada | Tipo |
|------------------------------------|-----------------|-----------------|------|
| `dec-color-001`: Paleta primaria 5 pasos (50-900) + semantic mapping | `dec-color-001` (green: Global Colors/Variables) | Teoría: Albers (escalas), Wong (roles semánticos) | THEORY |
| `dec-color-002`: `cta.primary_bg` = brand/primary/600 | `dec-color-002` (green) | **THEORY**: Heller (azul=confianza/competencia). **NO hay evidencia empírica 2020+ para azul primario vs neutral**. | THEORY |
| `dec-color-003`: `cta.secondary_bg` = neutral/100 (outline) | `dec-color-003` (green) | **THEORY**: Dondis (jerarquía peso visual: filled > outline > ghost). **NO hay evidencia empírica 2020+ para outline vs ghost**. | THEORY |
| `dec-color-004`: `cta.ghost` = brand/primary/600 text only | `dec-color-004` (green) | **THEORY**: Dondis (peso visual mínimo para tertiary). **NO hay evidencia empírica 2020+**. | THEORY |
| `dec-color-005`: Neutral scale 10 pasos + surface roles | `dec-color-005` (green) | Teoría: Albers (relatividad), WCAG/APCA (contraste base) | THEORY |
| `dec-color-006`: Feedback states (success/warning/error/info) | `dec-color-006` (green) | Teoría: Wong (roles funcionales), Heller (asociaciones culturales) | THEORY |
| `dec-color-007`: Dark mode palette (saturated CTA, adjusted neutrals) | `dec-color-007` (yellow: CSS custom properties) | **THEORY**: Sin evidencia empírica verificada. `human_review_required=true`. | THEORY |
| `dec-color-008`: Focus ring color (high contrast, non-brand) | `dec-color-008` (green) | Teoría: WCAG 2.2 focus visible, APCA | THEORY |

> **Todas las decisiones de color base son THEORY**. La única evidencia empírica usable es:
> - Kohavi 2025: forma del botón no es palanca (rounded vs angular)
> - Zhang 2025: CTA en social feed reduce CTR (presence cost)

---

## 5. FORMATO DE REFERENCIA EN DECISIONES

En `evidence_refs` del `design-decision-schema.json`:

```json
"evidence_refs": [
  "skills/creative-direction/color/references/color-evidence.md#kohavi-2025-shapes",
  "skills/creative-direction/color/references/color-evidence.md#zhang-2025-social-feed"
]
```

Cada ancla en `color-evidence.md` tiene formato:
```markdown
### kohavi-2025-shapes
**Estudio**: Kohavi et al. 2025/2026 — Rounded vs Angular Shapes...
**Hallazgo**: Formas redondeadas vs angulares: efecto mínimo a nulo en CTR (6.9M usuarios). No mide color.
**Contexto**: 6.9M+ usuarios, multiple verticals...
**Fuerza**: STRONG (para formas)
**Aplicación**: NO usar para decisiones de color...
**Tipo**: EMPIRICAL
```

---

## 6. REGLAS DE USO EN SKILL

1. **Citar siempre** la ancla exacta en `evidence_refs` (solo las verificadas arriba)
2. **Etiquetar** implícitamente: si la ancla existe en sección 2 → EMPIRICAL; sección 1 → THEORY
3. **No mezclar**: una decisión puede tener ambas, pero el rationale debe distinguir "Estructura basada en Albers; hue CTA basado en teoría Heller (sin evidencia de campo)"
4. **Si no hay ancla empírica** → no inventar. Decir "Basado en teoría X (Heller/Albers/Dondis); sin evidencia de campo 2020+"
5. **Feasibility primero**: Paso 0 carga feasibility. Si plataforma no soporta variable font para color tokens → yellow workaround documentado.
6. **En el skill NO citar bibliografía** — solo usar para argumentos de desarrollo. El skill referencia `color-evidence.md` como fuente.
