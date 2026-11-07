# Typography Evidence Base — Creative Direction Typography Skill

**Propósito**: Separar criterio de decisión (teoría) de evidencia de conversión/lectura (estudios de campo). El skill usa teoría para estructura de type scale, selección de fonts, jerarquía. Evidencia empírica solo donde existe y es verificable.

**Regla**: No citar papers sin DOI/URL verificable y hallazgo exacto. Si no se verifica → THEORY. En el skill NO citar bibliografía — solo usar para argumentos de desarrollo.

---

## 1. TEORÍA DISCIPLINAR — Criterio de Decisión (No Evidencia de Conversión)

| Referencia | Concepto Clave | Aplicación en Skill | Tipo |
|------------|----------------|---------------------|------|
| **Bringhurst, R. (2004). *The Elements of Typographic Style* (v3.2).** | Escalas modulares: ratios armónicos (1.25, 1.333, 1.414, 1.5, 1.618). Tipo como sistema, no decisiones aisladas. | Definición de type scale ratio (Paso 3). Base 16px + ratio 1.25 (Major Third) o 1.333 (Perfect Fourth). | THEORY |
| **Tschichold, J. (1928/1991). *The New Typography*.** | Jerarquía por peso/tamaño/espacio. Asimetría controlada. Grid tipográfico. | Roles semánticos (Paso 5): heading > body > label > caption por peso visual, no solo tamaño. | THEORY |
| **Müller-Brockmann, J. (1981). *Grid Systems in Graphic Design*.** | Baseline grid, modular scale, leading (line-height) como unidad rítmica. | Line-height por paso de escala (Paso 3). Baseline grid para alineación vertical. | THEORY |
| **Google Material Design (2014-2024). *Type System*.** | Type scale 13 pasos, font families (Roboto, Google Sans), token naming. | Estructura de tokens `typography.semantic.*` y naming convention. | THEORY |
| **Apple Human Interface Guidelines (2024). *Typography*.** | Dynamic Type, scaling, accessibility sizes, SF Pro variable font. | Responsive type scale, accessibility considerations, system font stack fallbacks. | THEORY |
| **W3C CSS Fonts Module Level 4 (2023). *font-variation-settings, font-optical-sizing*.** | Variable fonts axes: wght, wdth, opsz, slnt, GRAD, etc. `font-optical-sizing: auto`. | Variable font support detection, single-axis vs multi-axis feasibility. | THEORY |
| **WCAG 2.2 / APCA (2023). *Contrast & Text Spacing*.** | Text spacing (letter-spacing, word-spacing, line-height, paragraph spacing) para accesibilidad. | **Solo referencia metodológica** — validación real en FASE 5 con contrast_analyzer.py + text spacing checks. | THEORY |

> **Nota**: Estas referencias informan **cómo estructurar** el sistema tipográfico (escalas, jerarquía, variable fonts, tokens). **No** prueban que "Inter aumenta legibilidad 15% vs Roboto". Eso requiere evidencia empírica.

---

## 2. EVIDENCIA EMPÍRICA 2020+ — Estudios de Campo (Legibilidad, Rendimiento, Conversión)

> **NO HAY ESTUDIOS VERIFICABLES CON HALLÁZGO EXACTO COINCIDENTE**. Los papers citados anteriormente (Sheedy 2021, Beymer 2020, Rello 2022, Wallace 2023, Chen 2024, Google 2025) no tienen DOI/URL verificable que confirme el hallazgo exacto atribuido. Eliminados.

---

## 3. EVIDENCIA FALTANTE / DÉBIL — Declaración Explícita

| Tema | Estado | Acción en Skill |
|------|--------|-----------------|
| **Font serif vs sans-serif → conversión en landing pages** | Sin estudios controlados 2020+ que aíslen font family | Teoría (Bringhurst: serif para lectura prolongada, sans para UI). Skill decide por brand guidelines + feasibility. |
| **Font de marca específica → brand recall / trust** | Solo estudios de preferencia declarada, no comportamiento | Teoría (Tschichold: consistencia). No afirmar "nuestra font aumenta trust". |
| **Line-height óptimo → conversión** | Estudios de legibilidad (velocidad/comprensión), no conversión | Teoría (Müller-Brockmann: 1.4-1.6 para body). FASE 5 valida legibilidad. |
| **Letter-spacing en caps/buttons → conversión** | Solo guías de estilo (Material, Apple), no field studies | Teoría (tracking positivo en caps). Skill aplica convención; no citar como evidencia. |
| **Variable font optical sizing (opsz) → legibilidad en móvil** | Google 2025 reporta "mejora legibilidad", no estudio controlado | Teoría (CSS Fonts 4: opsz automático). Skill habilita si font lo soporta + feasibility green/yellow. |
| **Font loading strategy → SEO ranking** | Correlación (Core Web Vitals), no causalidad aislada | Skill implementa best practice por performance, no por SEO directo. |
| **Variable font wght axis → legibilidad vs static fonts** | Beymer 2020 citado pero hallazgo no verificado | **Sin evidencia empírica verificada**. Marcar `dec-typography-005` como THEORY. |
| **Font-display: swap + subsetting → CLS/LCP** | Wallace 2023 citado pero hallazgo no verificado | **Sin evidencia empírica verificada**. Marcar `dec-typography-006` como THEORY. |
| **Base size 18px mobile → conversión** | Chen 2024 citado pero hallazgo no verificado | **Sin evidencia empírica verificada**. Marcar `dec-typography-003` como THEORY. |
| **VF adoption rate / savings** | HTTP Archive 2025: ~40% adoption (no 12%), Inter VF #1 | Dato observacional, no study. Usar como contexto, no como evidencia de decisión. |

---

## 4. MAPA DE DECISIONES TIPOGRÁFICAS TÍPICAS → EVIDENCIA REAL

| Decisión Típica (output del skill) | Feasibility Ref | Evidencia Usada | Tipo |
|------------------------------------|-----------------|-----------------|------|
| `dec-typography-001`: Font UI principal (Inter Variable / Roboto Flex / System UI) | `dec-typography-001` (yellow Elementor / green Figma) | **THEORY**: Sin evidencia empírica verificada. Decidir por licencia, VF support, performance. | THEORY |
| `dec-typography-002`: Font Display/Brand (marca o Google Font similar) | `dec-typography-002` (green si licencia web; yellow si self-hosted) | Teoría: Bringhurst (personalidad), Tschichold (consistencia). **Sin evidencia empírica para brand font vs genérica**. | THEORY |
| `dec-typography-003`: Type scale ratio 1.25 (Major Third), base 16px desktop / 18px mobile | `dec-typography-003` (green: CSS rem/em nativo) | Teoría: Bringhurst (ratios armónicos). **NO hay evidencia empírica verificada para base 18px mobile**. | THEORY |
| `dec-typography-004`: Line-height por paso (body 1.5, heading 1.2, caption 1.4) | `dec-typography-004` (green) | Teoría: Müller-Brockmann (baseline grid), WCAG 2.2 (text spacing). **Sin evidencia empírica 2020+ para line-height específico**. | THEORY |
| `dec-typography-005`: Font weights 400/500/600/700 (variable font wght axis) | `dec-typography-005` (yellow Elementor / green Figma) | **THEORY**: Sin evidencia empírica verificada. Feasibility: Elementor single-axis via Custom CSS. | THEORY |
| `dec-typography-006`: Font loading: `font-display: swap`, preload, subsetting latin | `dec-typography-006` (green: CSS nativo) | **THEORY**: Sin evidencia empírica verificada. Best practice CSS. | THEORY |
| `dec-typography-007`: Text spacing tokens (letter/word/line/paragraph) para WCAG 2.2 | `dec-typography-007` (green) | Teoría: WCAG 2.2 Success Criterion 1.4.12. **Validación en FASE 5**. | THEORY |
| `dec-typography-008`: Fallback font stack (system-ui, -apple-system, BlinkMacSystemFont, ...) | `dec-typography-008` (green) | Teoría: CSS Fonts 4, Material/Apple HIG. Performance: zero flash. | THEORY |

> **Todas las decisiones tipográficas base son THEORY**. No hay evidencia empírica 2020+ verificable para ninguna decisión de conversión/legibilidad.

---

## 5. FORMATO DE REFERENCIA EN DECISIONES

En `evidence_refs` del `design-decision-schema.json`:

```json
"evidence_refs": [
  "skills/creative-direction/typography/references/typography-evidence.md#bringhurst-scale",
  "skills/creative-direction/typography/references/typography-evidence.md#wcag-text-spacing"
]
```

Cada ancla en `typography-evidence.md` tiene formato:
```markdown
### bringhurst-scale
**Referencia**: Bringhurst 2004 — The Elements of Typographic Style...
**Concepto**: Escalas modulares: ratios armónicos (1.25, 1.333, 1.414, 1.5, 1.618)...
**Aplicación**: Type scale ratio...
**Tipo**: THEORY
```

---

## 6. REGLAS DE USO EN SKILL

1. **Citar siempre** la ancla exacta en `evidence_refs` (solo las verificadas arriba — solo THEORY)
2. **Etiquetar** implícitamente: si la ancla existe en sección 1 → THEORY; sección 2 → EMPIRICAL (vacía)
3. **No mezclar**: una decisión puede tener ambas, pero el rationale debe distinguir "Estructura basada en Bringhurst; sin evidencia de campo 2020+"
4. **Si no hay ancla empírica** → no inventar. Decir "Basado en teoría X (Bringhurst/Tschichold/Müller-Brockmann); sin evidencia de campo 2020+"
5. **Feasibility primero**: Paso 0 carga feasibility. Variable font multi-axis en Elementor = red/yellow según workaround.
6. **En el skill NO citar bibliografía** — solo usar para argumentos de desarrollo. El skill referencia `typography-evidence.md` como fuente.
7. **Licencia web verificada**: Paso 2 es obligatorio. Sin licencia → human_review_required + alternativa Google Font.
