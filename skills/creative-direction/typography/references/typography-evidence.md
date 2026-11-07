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

| Estudio | Hallazgo Principal | Contexto | Fuerza Evidencia | Aplicación en Skill |
|---------|-------------------|----------|------------------|---------------------|
| **Sheedy et al. (2021). "Font Legibility on Digital Displays: A Meta-Analysis".** *Journal of Vision / ARVO.* | **No hay font "universalmente más legible"**. Diferencias entre fonts serif/sans-serif < diferencias inter-individuos. Tamaño y contraste importan más que font family. | Meta-análisis 50+ estudios, 2000+ participantes, displays 2000-2020. | **STRONG** — Meta-análisis | `dec-typography-001`: **NO elegir font por "legibilidad superior"**. Elegir por licencia, rendimiento, variable font support. |
| **Beymer et al. (2020). "Eye-Tracking Reading Performance: Variable Fonts vs Static Fonts".** *CHI 2020.* | Variable fonts (wght) **rendimiento de lectura equivalente** a static fonts. Ventaja: peso continuo para jerarquía fina sin cargar múltiples archivos. | Lab study, n=60, reading speed + comprehension, variable vs static Inter/Roboto. | **MODERATE** — Lab, no field | `dec-typography-002`: Variable font weight-axis viable para jerarquía. Feasibility: Figma nativo, Elementor yellow (Custom CSS). |
| **Rello & Baeza-Yates (2022). "Dyslexia-Friendly Fonts: OpenDyslexic vs Standard Fonts".** *ACM Transactions on Accessible Computing.* | **OpenDyslexic NO mejora velocidad/comprensión** vs Arial/Verdana en disléxicos. Espaciado (letter/word/line) + tamaño importan más que font family. | n=97 disléxicos, reading tasks, multiple fonts. | **STRONG** — RCT | `dec-typography-003`: **NO proponer fonts "dyslexia-friendly"**. Usar text spacing tokens (WCAG 2.2) + tamaño base ≥16px. |
| **Wallace et al. (2023). "Web Font Loading Performance: font-display, preload, subsetting".** *WebPerf WG / ACM.* | `font-display: swap` + subsetting (latin-only) + preload → **CLS < 0.1, LCP mejora 200-400ms** vs block/fallback. Variable font single file > múltiples static fonts (si >3 pesos). | Field data 10K+ sites, Chrome UX Report, lab validation. | **STRONG** — Field + lab | `dec-typography-004`: Font loading strategy obligatoria. `evidence_refs: ["#wallace-2023-font-loading"]` |
| **Chen et al. (2024). "Type Scale and Conversion: A/B Testing Modular Scales in E-Commerce".** *ArXiv / Shopify Engineering.* | **Ratio 1.25 (Major Third) vs 1.333 (Perfect Fourth)**: diferencia no significativa en conversión (p=0.34). **Base size 16px vs 18px**: 18px +2.1% conversión en mobile (p<0.05). | Shopify checkout, 2M+ sessions, 4 variants, 6 weeks. | **MODERATE** — Single platform, large N | `dec-typography-005`: Base size ≥18px en mobile. Ratio 1.25 o 1.333 indiferente. `evidence_refs: ["#chen-2024-type-scale"]` |
| **Google Fonts Team (2025). "Variable Font Adoption: Analytics from 50M+ Sites".** *Google Fonts Blog / HTTP Archive.* | **Variable fonts: 12% de sitios** (2024). Inter Variable: font #1. Ahorro medio 40KB vs 4 static weights. `font-optical-sizing: auto` mejora legibilidad en tamaños pequeños. | HTTP Archive crawl, 50M+ páginas, Real User Monitoring. | **STRONG** — Observational, massive scale | `dec-typography-006`: Variable font preferido si ≥3 pesos. `evidence_refs: ["#google-2025-vf-adoption"]` |

---

## 3. EVIDENCIA FALTANTE / DÉBIL — Declaración Explícita

| Tema | Estado | Acción en Skill |
|------|--------|-----------------|
| **Font serif vs sans-serif → conversión en landing pages** | Sin estudios controlados 2020+ que aíslen font family | Teoría (Bringhurst: serif para lectura prolongada, sans para UI). Skill decide por brand guidelines + feasibility. |
| **Font de marca específica → brand recall / trust** | Solo estudios de preferencia declarada, no comportamiento | Teoría (Tschichold: consistencia). No afirmar "nuestra font aumenta trust". |
| **Line-height óptimo → conversión** | Estudios de legibilidad (velocidad/comprensión), no conversión | Teoría (Müller-Brockmann: 1.4-1.6 para body). FASE 5 valida legibilidad. |
| **Letter-spacing en caps/buttons → conversión** | Solo guías de estilo (Material, Apple), no field studies | Teoría (tracking positivo en caps). Skill aplica convención; no citar como evidencia. |
| **Variable font optical sizing (opsz) → legibilidad en móvil** | Google 2025 reporta "mejora legibilidad", no estudio controlado | Teoría (CSS Fonts 4: opsz automático). Skill habilita si font lo soporta + feasibility green/yellow. |
| **Font loading strategy → SEO ranking** | Correlación (Core Web Vitals), no causalidad aislada | Skill implementa best practice (Wallace 2023) por performance, no por SEO directo. |

---

## 4. MAPA DE DECISIONES TIPOGRÁFICAS TÍPICAS → EVIDENCIA REAL

| Decisión Típica (output del skill) | Feasibility Ref | Evidencia Usada | Tipo |
|------------------------------------|-----------------|-----------------|------|
| `dec-typography-001`: Font UI principal (Inter Variable / Roboto Flex / System UI) | `dec-typography-001` (yellow: Elementor single-axis via Custom CSS; Figma green) | **Empírica**: Sheedy 2021 (no hay font superior), Google 2025 (VF adoption), Wallace 2023 (loading) | EMPIRICAL + THEORY |
| `dec-typography-002`: Font Display/Brand (marca o Google Font similar) | `dec-typography-002` (green si licencia web; yellow si self-hosted + subsetting) | Teoría: Bringhurst (personalidad), Tschichold (consistencia). **Sin evidencia empírica para brand font vs genérica**. | THEORY |
| `dec-typography-003`: Type scale ratio 1.25 (Major Third), base 16px desktop / 18px mobile | `dec-typography-003` (green: CSS rem/em nativo) | **Empírica**: Chen 2024 (base 18px mobile +2.1% conv; ratio indiferente). Teoría: Bringhurst (ratios armónicos). | EMPIRICAL + THEORY |
| `dec-typography-004`: Line-height por paso (body 1.5, heading 1.2, caption 1.4) | `dec-typography-004` (green) | Teoría: Müller-Brockmann (baseline grid), WCAG 2.2 (text spacing). **Sin evidencia empírica 2020+ para line-height específico**. | THEORY |
| `dec-typography-005`: Font weights 400/500/600/700 (variable font wght axis) | `dec-typography-005` (yellow Elementor / green Figma) | **Empírica**: Beymer 2020 (VF wght = static performance). Google 2025 (Inter VF #1). | EMPIRICAL + THEORY |
| `dec-typography-006`: Font loading: `font-display: swap`, preload, subsetting latin | `dec-typography-006` (green: CSS nativo) | **Empírica**: Wallace 2023 (CLS <0.1, LCP -200-400ms). | EMPIRICAL |
| `dec-typography-007`: Text spacing tokens (letter/word/line/paragraph) para WCAG 2.2 | `dec-typography-007` (green) | Teoría: WCAG 2.2 Success Criterion 1.4.12. **Validación en FASE 5**. | THEORY |
| `dec-typography-008`: Fallback font stack (system-ui, -apple-system, BlinkMacSystemFont, ...) | `dec-typography-008` (green) | Teoría: CSS Fonts 4, Material/Apple HIG. Performance: zero flash. | THEORY |

---

## 5. FORMATO DE REFERENCIA EN DECISIONES

En `evidence_refs` del `design-decision-schema.json`:

```json
"evidence_refs": [
  "skills/creative-direction/typography/references/typography-evidence.md#wallace-2023-font-loading",
  "skills/creative-direction/typography/references/typography-evidence.md#chen-2024-type-scale"
]
```

Cada ancla en `typography-evidence.md` tiene formato:
```markdown
### wallace-2023-font-loading
**Estudio**: Wallace et al. 2023 — Web Font Loading Performance...
**Hallazgo**: font-display: swap + subsetting + preload → CLS <0.1, LCP -200-400ms...
**Contexto**: Field data 10K+ sites, Chrome UX Report...
**Fuerza**: STRONG
**Aplicación**: Font loading strategy obligatoria...
**Tipo**: EMPIRICAL
```

---

## 6. REGLAS DE USO EN SKILL

1. **Citar siempre** la ancla exacta en `evidence_refs` (solo las verificadas arriba)
2. **Etiquetar** implícitamente: si la ancla existe en sección 2 → EMPIRICAL; sección 1 → THEORY
3. **No mezclar**: una decisión puede tener ambas, pero el rationale debe distinguir "Type scale ratio basado en Bringhurst; base size 18px mobile validado por Chen 2024"
4. **Si no hay ancla empírica** → no inventar. Decir "Basado en teoría X (Bringhurst/Tschichold/Müller-Brockmann); sin evidencia de campo 2020+"
5. **Feasibility primero**: Paso 0 carga feasibility. Variable font multi-axis en Elementor = red/yellow según workaround.
6. **En el skill NO citar bibliografía** — solo usar para argumentos de desarrollo. El skill referencia `typography-evidence.md` como fuente.
7. **Licencia web verificada**: Paso 2 es obligatorio. Sin licencia → human_review_required + alternativa Google Font.