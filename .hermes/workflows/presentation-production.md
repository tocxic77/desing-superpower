# Workflow: Presentation Production (PPTX / PDF)

## Trigger
Presentation brief approved via `new-project` workflow.

## Input
- Presentation brief: audience, goal, narrative, slide count, format (PPTX/PDF/both)
- Content: raw text, data, images, brand assets
- Template selection: executive / commercial / technical

## Process

### 1. Narrative Architecture (Art Director + Sales Specialist)
- Define slide flow: hook → problem → solution → evidence → ask
- Map each slide to narrative beat
- Define visual hierarchy per slide type
- Sales Specialist: optimize for persuasion (not decoration)

### 2. Slide Specs (UX Designer)
- Component specs for each slide type:
  - Title slide
  - Section divider
  - Content slide (text + visual)
  - Data visualization slide
  - Quote/testimonial slide
  - CTA/closing slide
- Responsive specs (if PDF → mobile view)
- Accessibility specs (reading order, alt text, contrast)

### 3. Build (Web Builder — PPTX/PDF Builder)
- Apply design tokens
- Implement slide specs exactly
- Insert content with copy optimization
- Data viz: charts generated from data (not images)
- Image placement per art direction
- Export: PPTX (editable) + PDF (print/lock)

### 4. Validate (Design Critic)
- Visual consistency across slides
- Typography scale adherence
- Contrast compliance
- Reading order (accessibility)
- File size optimization
- PPTX editability check

### 5. Correct → Verify (Design Loop)
- Same loop as website-production

## Output
- `runs/<project>/presentation.pptx`
- `runs/<project>/presentation.pdf`
- `runs/<project>/slide-specs.json`
- `runs/<project>/final-report.md`

## Quality Gates
- All slides pass contrast check
- Typography scale consistent
- Reading order logical (a11y)
- PPTX fully editable (no flattened elements)
- File size < 50MB (PPTX), < 20MB (PDF)
- Brand token compliance 100%