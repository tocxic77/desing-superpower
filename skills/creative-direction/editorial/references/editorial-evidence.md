# Editorial Evidence Base — Creative Direction Editorial Skill

**Propósito**: Separar teoría compositiva (retícula, jerarquía, ritmo, densidad) de evidencia empírica de conversión. El skill usa teoría para estructura; evidencia empírica solo donde existe y es verificable.

**Regla**: No citar papers sin DOI/URL verificable y hallazgo exacto. Si no se verifica → THEORY. En el skill NO citar bibliografía — solo usar para argumentos de desarrollo.

---

## 0. ALCANCE DE AUTORES — quién entra y quién no

Esta base cubre **composición editorial** (retícula, jerarquía, ritmo, densidad, patrones de página). Por eso:

- **Entran**: Müller-Brockmann, Samara, Lupton, Bringhurst, Tschichold, Hofmann, Vignelli (composición/tipografía), Kapferer (solo para la expresión de marca dentro de la composición).
- **NO entran**: investigación de UX/comportamiento (p.ej. Spool), eye-tracking, marketing/conversión. Spool estudia comportamiento de usuarios y patrones de interacción web — no composición editorial. Citarlo aquí inflaba la base con un autor de otra área. Su lugar, si se necesitara, sería un skill de UX/conversión, no este.
- **Consecuencia**: la library de secciones (`dec-editorial-007`) se declara **convención de industria**, no teoría canónica. Se deriva de la anatomía de retícula y de la jerarquía funcional, no de un estudio.

---

## 1. TEORÍA DISCIPLINAR — Criterio de Decisión (No Evidencia de Conversión)

### muller-brockmann-grids
**Referencia**: Müller-Brockmann, J. (1981/1996). *Grid Systems in Graphic Design*.
**Concepto**: Sistemas de retícula modular, columnar y baseline grid; coherencia visual mediante estructura matemática.
**Aplicación**: Definición de retícula (`dec-editorial-003`): columnas, gutters, baseline, módulos.
**Tipo**: THEORY

### samara-grid-anatomy
**Referencia**: Samara, T. (2003/2017). *Making and Breaking the Grid: A Graphic Design Layout Workshop*.
**Concepto**: Anatomía de retícula — columnas, filas, módulos, márgenes, gutters, flowlines; cuándo romperla intencionalmente.
**Aplicación**: Validación de retícula y detección de quiebres intencionales vs accidentales (`dec-editorial-003`).
**Tipo**: THEORY

### lupton-hierarchy
**Referencia**: Lupton, E. (2014/2020). *Thinking with Type: A Critical Guide for Designers*.
**Concepto**: Jerarquía tipográfica — escala, peso, espacio, color, posición; tipografía como sistema, no decoración.
**Aplicación**: Jerarquía compositiva (`dec-editorial-002`); mapeo de decisiones de tipografía → peso visual.
**Tipo**: THEORY

### bringhurst-rhythm
**Referencia**: Bringhurst, R. (1992/2004). *The Elements of Typographic Style*.
**Concepto**: Escala modular, proporción, ritmo vertical, leading, medida.
**Aplicación**: Ritmo vertical y alineación a baseline (`dec-editorial-005`).
**Tipo**: THEORY

### tschichold-whitespace
**Referencia**: Tschichold, J. (1928/2006). *The New Typography*.
**Concepto**: Asimetría constructiva, jerarquía por peso/tamaño, espacio en blanco activo; función sobre forma.
**Aplicación**: Espacio en blanco como elemento estructural (`dec-editorial-006`); jerarquía funcional por sección (`dec-editorial-002`, `dec-editorial-007`).
**Tipo**: THEORY

### hofmann-density
**Referencia**: Hofmann, A. (1965/2001). *Graphic Design Manual: Principles and Practice*.
**Concepto**: Punto, línea, plano; contraste, ritmo, equilibrio, proporción; elementos formales básicos.
**Aplicación**: Densidad compositiva y peso visual vs densidad informativa (`dec-editorial-006`).
**Tipo**: THEORY

### vignelli-canon
**Referencia**: Vignelli, M. (2010). *The Vignelli Canon*.
**Concepto**: Retícula unificadora, tipografía restringida, coherencia de sistema.
**Aplicación**: Sistema unificado de tokens (`dec-editorial-001`) y validación cross-layer.
**Tipo**: THEORY

### muller-brockmann-page-structure
**Referencia**: Müller-Brockmann, J. (1981/1996). *Grid Systems in Graphic Design*, capítulo de sistemas de página.
**Concepto**: Organización de la página en zonas y módulos; relación entre estructura de página y jerarquía de contenido.
**Aplicación**: Estructura de secciones (`dec-editorial-007`): qué zonas existen y cómo se relacionan, no qué patrón web "convierte más".
**Tipo**: THEORY

### samara-layout-patterns
**Referencia**: Samara, T. (2003/2017). *Making and Breaking the Grid*, secciones de layout workshop.
**Concepto**: Tipos de página y agrupación de módulos; reutilización de estructuras compositivas.
**Aplicación**: Library de secciones (`dec-editorial-007`) como repertorio compositivo de módulos, y reglas de reflow (`dec-editorial-008`).
**Tipo**: THEORY — **convención de industria**, no hallazgo empírico

### samara-responsive
**Referencia**: Samara, T. (2003/2017). *Making and Breaking the Grid*, capítulo de retículas para medios cambiantes.
**Concepto**: Adaptación de retícula a anchos distintos; reflow por número de columnas y stacking.
**Aplicación**: Reglas responsive / reflow (`dec-editorial-008`).
**Tipo**: THEORY

### kapferer-physique
**Referencia**: Kapferer, J.-N. (2012). *The New Strategic Brand Management* — prisma de identidad, dimensión "physique".
**Concepto**: La marca tiene una dimensión física (soportes, símbolos, territorios visuales) que debe tener lugar en el soporte.
**Aplicación**: Zonas reservadas para branding dentro de la retícula (`dec-editorial-004`). Es teoría **de marca**, no de composición: se cita solo para justificar que el espacio de marca es un requisito, no un adorno.
**Tipo**: THEORY

> **Nota**: Estas referencias informan **cómo estructurar** la composición (retícula, jerarquía, ritmo, densidad). **No** prueban que "retícula de 12 columnas aumenta conversión 12%". Eso requiere evidencia empírica que no existe.

---

## 2. EVIDENCIA EMPÍRICA 2020+ — Estudios de Campo (Layout, Conversión, Comportamiento)

> **NO HAY ESTUDIOS VERIFICABLES CON HALLAZGO EXACTO COINCIDENTE**. No existe literatura 2020+ controlada que demuestre causalidad entre decisiones de retícula/composición específica y métricas de conversión aisladas de contenido, marca, canal y audiencia.

| Tema | Estado | Nota |
|------|--------|------|
| Retícula 12 vs 8 vs 4 columnas → conversión | Sin estudios | Teoría informa; no usar como evidencia empírica |
| Baseline grid estricto vs suelto → legibilidad/engagement | Solo preferencia de diseñadores, no comportamiento de usuarios | No aislable de tipografía/contenido |
| Densidad compositiva (white space ratio) → trust/conversión | Estudios correlacionales antiguos (ej. Lindgaard 2006), no 2020+ controlados | Teoría (Hofmann); no evidencia causal |
| Jerarquía visual (F-pattern, Z-pattern) → task completion | Eye-tracking descriptivo, no experimental causal | Teoría (Lupton/Samara) |
| Espacio en blanco activo vs pasivo → brand perception | Solo estudios de preferencia declarada | Teoría (Tschichold/Vignelli) |

---

## 3. EVIDENCIA FALTANTE / DÉBIL — Declaración Explícita

| Tema | Estado | Acción en Skill |
|------|--------|-----------------|
| **Retícula X columnas → mayor conversión que Y** | **Sin evidencia empírica verificada** | Skill propone retícula basada en contenido + breakpoints. `human_review_required=false` (decisión técnica), pero alternativa documentada. |
| **Densidad compositiva específica → trust/conversión** | Depende de categoría, marca, audiencia. No generalizable. | Skill calcula densidad (elementos/cm²) y mapea a arquetipo. Si arquetipo provisional → `human_review_required=true`. |
| **Jerarquía tipográfica exacta → task completion** | Solo correlacional, no causal. Lupton/Samara descriptivo. | Skill valida coherencia con decisiones typography skill. No decide jerarquía autónomamente. |
| **Grid breaking intencional → engagement** | Sin estudios 2020+ controlados | Teoría (Samara). Skill detecta quiebres; humano decide si intencional. |
| **Arquetipo → densidad compositiva preferida** | Sin estudios. Teoría: Hero=denso/activo, Sage=espaciado/calmo | Skill propone mapping teórico. `human_review_required=true` si arquetipo provisional. |
| **Library de secciones (hero/features/proof) → rendimiento** | Convención de industria, sin validación empírica | Se declara como convención; no se presenta como evidencia. |

---

## 4. MAPA DE DECISIONES DE EDITORIAL TÍPICAS → EVIDENCIA REAL

| Decisión Típica (output del skill) | Feasibility Ref | Evidencia Usada | Tipo | Revisión Humana |
|------------------------------------|-----------------|-----------------|------|-----------------|
| `dec-editorial-001`: Sistema unificado (tokens consumidos) | `dec-editorial-001` (green) | **THEORY**: Vignelli canon — tokens como single source of truth | THEORY | `false` (técnica) |
| `dec-editorial-002`: Jerarquía compositiva (hero → features → proof → CTA) | `dec-editorial-002` (green) | **THEORY**: Lupton hierarchy + Tschichold functional hierarchy. **Valida coherencia** con typography skill decisions. | THEORY | `false` si typography decisions válidas |
| `dec-editorial-003`: Retícula (columnas, gutters, baseline, breakpoints) | `dec-editorial-003` (green/yellow) | **THEORY**: Müller-Brockmann + Samara grid anatomy. **Valida** con feasibility (Elementor/Figma constraints). | THEORY | `false` (técnica, feasibility-driven) |
| `dec-editorial-004`: Espacio para branding (logo, tagline, archetype expression) | `dec-editorial-004` (green) | **THEORY**: Kapferer Physique + Vignelli system. **Depende** de branding decisions. | THEORY | `true` si branding `incomplete/missing` |
| `dec-editorial-005`: Ritmo vertical / baseline grid alignment | `dec-editorial-005` (green/yellow) | **THEORY**: Bringhurst + Müller-Brockmann. **Valida** con typography line-height tokens. | THEORY | `false` (técnica) |
| `dec-editorial-006`: Densidad compositiva (elementos/cm², white space ratio) | `dec-editorial-006` (green) | **THEORY**: Hofmann + Tschichold. **Mapea a arquetipo** (si disponible). | THEORY | `true` si arquetipo provisional |
| `dec-editorial-007`: Library de secciones (hero, features, proof, CTA, footer) | `dec-editorial-007` (green) | **THEORY/convención**: Samara layout patterns + Müller-Brockmann page structure. **Valida** color CTA hierarchy + typography scale. No hay estudio que respalde la library. | THEORY | `false` (técnica) |
| `dec-editorial-008`: Responsive composition (reflow rules, breakpoint behavior) | `dec-editorial-008` (green/yellow) | **THEORY**: Samara responsive grids. **Valida** con feasibility breakpoints. | THEORY | `false` (técnica) |

> **Todas las decisiones de editorial son THEORY**. El skill **valida coherencia cross-layer**; no decide autónomamente arquetipo ni densidad semántica. Si branding provisional → decisiones dependientes marcan `human_review_required=true`.

---

## 5. FORMATO DE REFERENCIA EN DECISIONES

En `evidence_refs` del `design-decision-schema.json` (v0.2, canónico):

```json
"evidence_refs": [
  "skills/creative-direction/editorial/references/editorial-evidence.md#muller-brockmann-grids",
  "skills/creative-direction/editorial/references/editorial-evidence.md#lupton-hierarchy",
  "skills/creative-direction/editorial/references/editorial-evidence.md#bringhurst-rhythm"
]
```

Cada ancla de este archivo es un encabezado `### <ancla>` (sección 1). `verify-editorial-coherence.py` comprueba que el ancla exista: una referencia a un ancla inexistente es error, no warning.

---

## 6. REGLAS DE USO EN SKILL

1. **Citar siempre** la ancla exacta en `evidence_refs` (solo las de la sección 1 — solo THEORY)
2. **Etiquetar** implícitamente: si el ancla está en sección 1 → THEORY; sección 2 → EMPIRICAL (vacía)
3. **No mezclar**: rationale debe decir "Basado en teoría Müller-Brockmann/Lupton/Bringhurst; sin evidencia de campo 2020+ para retícula → conversión"
4. **Si no hay ancla empírica** → no inventar. Decir "Basado en teoría X (Müller-Brockmann/Lupton/Vignelli); sin evidencia empírica 2020+"
5. **Feasibility primero**: Paso 0 carga feasibility. Decisiones de retícula/responsive validan contra platform constraints.
6. **Cross-layer validation**: Cada decisión editorial **debe** referenciar decisions de color, typography, branding que consume.
7. **En el skill NO citar bibliografía** — solo usar para argumentos de desarrollo. El skill referencia `editorial-evidence.md` como fuente.
8. **Output naming**: Si branding `missing/incomplete` → `draft-editorial-composition.json`. Si branding `complete` → `editorial-composition.json`.
9. **Provisional flag**: Decisiones que dependen de arquetipo/branding provisional llevan `provisional: true` + `depends_on: ["dec-brand-001", ...]`.
10. **No importar autores de otras áreas**: si la referencia no es de composición/tipografía (o marca, para el caso de Kapferer), no entra aquí aunque sea prestigiosa.
