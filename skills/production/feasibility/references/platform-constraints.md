# Platform Constraints — Verified Reference

**Versión verificada**: Elementor 3.24.x (V4 Atomic) / Figma Desktop 118.x (Variables + Component Properties GA)
**Fecha de verificación**: 2026-11-07
**Nota**: Las restricciones DEBEN re-verificarse en cada release mayor de plataforma (Elementor 4.x, Figma 119+). No asumir compatibilidad hacia adelante.

---

## 1. WORDPRESS / ELEMENTOR (V4 Atomic)

### 1.1 Green — Nativo, editable, performante

| Capacidad | Detalle | Ejemplo de decisión viable |
|-----------|---------|---------------------------|
| **Flexbox Containers** | Layout nativo, responsive por breakpoint | `dec-layout-001: "Usar Flexbox Container para hero 2-col, reverse en móvil"` |
| **Theme Style → Global Colors/Typography** | Tokens mapeados 1:1 a CSS custom properties | `dec-color-001: "Mapear colors.semantic.cta.primary_bg a Global Color 'Primary'"` |
| **Widgets nativos (Heading, Text Editor, Button, Icon, Image, Spacer, Divider)** | Output limpio, accesible, editable en editor visual | `dec-typography-001: "H1 usa Heading widget con Global Typography 'Display XL'"` |
| **Loop Grid / Loop Carousel** | Queries dinámicas, paginación, plantilla de item | `dec-editorial-001: "Blog archive usa Loop Grid con template de card"` |
| **Form widget (nativo)** | Validación HTML5, honeypot, reCAPTCHA v3, webhooks | `dec-interaction-001: "Contact form usa Form widget nativo, 4 campos"` |
| **Motion Effects (Entrada, Scroll, Mouse)** | CSS/JS nativo, sin librerías externas | `dec-branding-001: "Fade-up en scroll para section testimonials"` |
| **Custom CSS por widget/container** | Scoped al elemento, no rompe Theme Style | `dec-color-002: "Overlay hero: background: linear-gradient(var(--color-bg), transparent)"` |
| **Breakpoints: Mobile (≤767px), Tablet (768-1024px), Desktop (≥1025px)** | 3 breakpoints fijos, editable por widget | `dec-layout-002: "Padding section: Desktop 80px, Tablet 60px, Mobile 40px"` |

### 1.2 Yellow — Posible con workaround documentado

| Capacidad | Workaround | Coste/Riesgo | Ejemplo de decisión condicional |
|-----------|------------|--------------|--------------------------------|
| **Grid asimétrico / Masonry** | CSS Grid custom en `Custom CSS` del container + `@supports` fallback | Mantenibilidad media; rompe editor visual en esa zona | `dec-layout-003: "Masonry gallery → CSS Grid custom, documentar en build-log"` |
| **Variables CSS fluidas (clamp)** | Definir en Theme Style → Custom CSS global `html { --space-fluid: clamp(1rem, 3vw, 2rem); }` | No editable en UI; solo vía código | `dec-typography-002: "Fluid type scale → Custom CSS global, no Theme Style"` |
| **Componentes anidados complejos (card con sub-componentes)** | Container dentro de Container + `display: contents` hack | Accesibilidad risk; testing requerido | `dec-editorial-002: "Card anidada → containers anidados, auditar a11y"` |
| **Animaciones Lottie** | Widget Lottie nativo (desde 3.18) — peso archivo + JS runtime | Performance: +50-100KB JS; validar LCP | `dec-branding-002: "Lottie en hero solo si LCP < 2.5s en staging"` |
| **Custom Post Type fields en Loop** | ACF Pro + Dynamic Tags (Elementor Pro) | Dependencia ACF; lock-in | `dec-editorial-003: "Team grid usa ACF fields via Dynamic Tags"` |
| **Sticky header transparente → sólido en scroll** | Motion Effects + Custom CSS `transition: background 0.3s` | Requiere JS para detectar scroll; no nativo puro | `dec-layout-004: "Sticky header con transición → Motion Effects + CSS custom"` |

### 1.3 Red — Bloqueado, requiere rediseño o excepción humana

| Capacidad | Por qué bloquea | Alternativa viable |
|-----------|-----------------|-------------------|
| **CSS Subgrid** | No soportado en output de Elementor (Chrome sí, pero wrapper impide) | Usar Flexbox anidado o Grid en container padre |
| **Container Queries** | No expuesto en UI; CSS custom no aplica a shadow DOM interno | Breakpoints fijos + media queries en Custom CSS global |
| **View Transitions API** | Requiere control total del DOM de navegación; Elementor no expone | Fade simple con Motion Effects |
| **Web Components / Shadow DOM** | Widgets renderizan en Light DOM; no hay slot/projection nativo | Patrones de container + CSS custom |
|| **Fuentes variables (Variable Fonts) — Multi-axis / `font-variation-settings` dinámico** | Theme Style solo soporta weight fijos; control dinámico de múltiples ejes no editable en UI | Cargar weights estáticos como fuentes separadas; usar variable font solo si single-axis (weight) |
|| **Fuentes variables (Variable Fonts) — Single-axis (weight) vía `@font-face` + Custom CSS** | Custom CSS scoped en widget/container: `@font-face { font-family: 'InterVar'; src: url(...); } .selector { font-family: 'InterVar'; font-variation-settings: 'wght' 400; }` | Mantenibilidad media; no editable en Theme Style; requiere test cross-browser | `dec-typography-003: "Inter Variable font weight-only via Custom CSS scoped, no Theme Style"` |
| **Aspect-ratio en Image widget** | No expuesto; `object-fit` limitado | Container con `aspect-ratio` en Custom CSS + Image como background |
| **Scroll-driven animations (CSS `animation-timeline: scroll()`)** | No soportado en output; requeriría JS polyfill pesado | Motion Effects nativos (scroll-based) |
| **Form multi-step nativo** | Widget Form es single-step | Multi-step = múltiples páginas + query params (workaround frágil) |

---

## 2. FIGMA (Desktop 118.x, Variables + Component Properties GA)

### 2.1 Green — Nativo, exportable a tokens/CSS, sincronizable

| Capacidad | Detalle | Ejemplo de decisión viable |
|-----------|---------|---------------------------|
| **Variables (Color, Number, String, Boolean)** | Scoped a collections/modes; exportable via Figma REST API | `dec-color-003: "Definir brand/primary/500-900 como Color variables en collection 'Brand'"` |
| **Component Properties (Variant, Text, Boolean, Instance Swap)** | Single source of truth; docs generables; dev handoff nativo | `dec-branding-003: "Button component: variant=primary/secondary/ghost, size=sm/md/lg, state=default/hover/disabled"` |
| **Auto Layout (Stack, Grid, Wrap)** | Maps 1:1 a Flexbox/CSS Grid; responsive real | `dec-layout-005: "Card usa Auto Layout vertical, gap=16, padding=24"` |
| **Text Styles + Variable Fonts** | Weight/axis expuestos; exportable a CSS `@font-face` | `dec-typography-003: "Inter Variable font: weight 400-700 via Text Style + Variable axes"` |
| **Color Styles (legacy) → migrados a Variables** | Compatibilidad hacia atrás; migración asistida | `dec-color-004: "Migrar Color Styles a Variables collection 'Semantic'"` |
| **Export: SVG, PNG, WebP, PDF** | Assets listos para web; SVG optimizable | `dec-branding-004: "Logo export SVG + PNG 2x/3x para fallback"` |
| **Design Tokens JSON (plugin: Figma Tokens / Tokens Studio)** | Sync bidireccional con repo; CI/CD integrable | `dec-color-005: "Sync tokens a design-system/tokens/colors.json via Tokens Studio"` |
| **Component Playground / Interactive Components** | Prototipo funcional; validación UX pre-build | `dec-interaction-002: "Validar dropdown interaction en Figma antes de build"` |

### 2.2 Yellow — Posible con plugin/workaround documentado

| Capacidad | Workaround | Coste/Riesgo | Ejemplo de decisión condicional |
|-----------|------------|--------------|--------------------------------|
| **CSS Custom Properties export directo** | Plugin "Figma to CSS Variables" o Tokens Studio → JSON → transform script | Requiere pipeline de build; versión de tokens puede desincronizarse | `dec-color-006: "Export variables a CSS custom properties via script post-export"` |
| **Responsive breakpoints en Auto Layout** | Modes (Mobile/Tablet/Desktop) en Variables + Auto Layout wrap | No es CSS real; solo preview. Handoff manual a dev | `dec-layout-006: "Definir breakpoints como Number variables + modes, documentar en handoff"` |
| **Motion / Prototype animations → CSS** | Plugin "Figmotion" + export Lottie/JSON → implementar en Elementor Motion Effects | Pérdida de fidelidad; solo reference | `dec-branding-005: "Micro-interactions en Figma → reference para Elementor Motion Effects"` |
| **Content Reel / Data-driven components** | Plugin "Content Reel" o "Google Sheets Sync" para poblar | Solo design-time; no runtime | `dec-editorial-004: "Usar Content Reel para real data en reviews, no en build"` |
| **Variable fonts con axes no estándar (opsz, GRAD, etc.)** | Definir como Number variables + documentar axes soportados | Export a CSS requiere `@font-face` manual con `font-variation-settings` | `dec-typography-004: "Usar opsz para optical size → documentar, no exportar automático"` |

### 2.3 Red — No exportable a CSS / No implementable en Elementor sin pérdida

| Capacidad | Por qué bloquea | Alternativa viable |
|-----------|-----------------|-------------------|
| **Blend modes avanzados (difference, exclusion, hue, etc.)** | CSS `mix-blend-mode` soporte limitado en navegadores + Elementor no expone | Usar opacity + overlay colors simulados |
| **Filters no estándar (blur() en background, backdrop-filter)** | `backdrop-filter` requiere contexto de stacking; Elementor containers no garantizan | Usar overlay semi-transparente + blur en imagen de fondo pre-renderizada |
| **Text on path / curved text** | No hay equivalente CSS nativo; requiere SVG path + JS | Evitar; usar layout rectilíneo |
| **Component properties anidadas > 2 niveles** | Figma permite, pero handoff a CSS/Elementor explota combinatoriamente | Aplanar a variants planas (max 3 props: variant, size, state) |
| **Scroll-based animations en prototipo** | No exportable; solo preview en Figma | Documentar como reference para Motion Effects |
| **Grid no uniforme (tracks con minmax, auto-fit, named lines)** | Auto Layout Grid es uniforme; CSS Grid custom no representable | Usar Auto Layout wrap + gap, o documentar como yellow para dev |
| **Fuentes no web-safe sin licencia web** | Figma usa fuentes locales; deploy requiere licencia web separada | Verificar licencia web ANTES de decidir; si no → fuente alternativa |
| **Efectos de capa (inner shadow, outer glow, drop shadow con spread)** | `box-shadow` soporta spread, pero `filter: drop-shadow()` no; inner shadow = `box-shadow: inset` | Usar solo `box-shadow` estándar; evitar inner glow complejo |

---

## 3. MATRIZ RÁPIDA DE DECISIÓN (para Feasibility Skill)

| Decisión creativa | Elementor | Figma | Acción Feasibility |
|-------------------|-----------|-------|-------------------|
| Nueva paleta de colores | Green (Global Colors) | Green (Variables) | ✅ Pass |
| Tipografía variable fluida | Yellow (Custom CSS global) | Green (Variable font + Text Style) | ⚠️ Conditional — documentar pipeline |
| Variable font single-axis (weight) | Yellow (Custom CSS scoped + @font-face) | Green (Variable font + Text Style) | ⚠️ Conditional — test cross-browser |
| Grid asimétrico hero | Yellow (CSS Grid custom) | Red (no exportable) | ⚠️ Conditional — solo si Elementor yellow aceptado |
| Animación Lottie compleja | Yellow (widget nativo, peso) | Yellow (plugin Figmotion → Lottie) | ⚠️ Conditional — validar LCP |
| Blend mode difference | Red | Red | ❌ Blocked — rediseñar |
| Breakpoints custom (más de 3) | Red (solo 3 fijos) | Yellow (modes en variables) | ❌ Blocked en Elementor — usar 3 breakpoints |
| Componente card anidado 3 niveles | Yellow (containers anidados) | Red (props anidadas >2) | ⚠️ Conditional — aplanar en Figma |

> **Regla de oro**: Si Figma = Red y Elementor = Yellow → **Red** (no se puede diseñar lo que no se puede construir). Si Figma = Green y Elementor = Yellow → **Yellow** (diseñable, build con workaround documentado).