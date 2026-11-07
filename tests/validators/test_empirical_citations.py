"""
Test: Evidencia empírica debe tener identificador verificable (DOI/URL).

Motivo: en color y typography se citaban papers EMPIRICAL sin DOI/URL real
(Kohavi/Zhang en color; Sheedy/Beymer/Rello/Wallace/Chen/Google en typography).
Este test falla si existe cualquier entrada marcada EMPIRICAL sin DOI o URL
verificable en los archivos *-evidence.md.
"""

import re
import sys
from pathlib import Path

import pytest

EVIDENCE_FILES = [
    "skills/creative-direction/color/references/color-evidence.md",
    "skills/creative-direction/typography/references/typography-evidence.md",
    "skills/creative-direction/branding/references/branding-evidence.md",
    "skills/creative-direction/editorial/references/editorial-evidence.md",
]

DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)
URL_PATTERN = re.compile(r"https?://[^\s)]+", re.I)


def extract_empirical_entries(filepath: Path) -> list[dict]:
    """Extrae entradas marcadas como EMPIRICAL de un archivo de evidencia."""
    text = filepath.read_text(encoding="utf-8")
    entries = []

    # Buscar en formato de tabla (sección 2) y formato de ancla (sección 0)
    # Patrón: **Tipo**: EMPIRICAL
    lines = text.splitlines()
    in_code_block = False
    current_entry = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # Detectar encabezados de ancla (### slug)
        if re.match(r"^#{3,4}\s+\w+", stripped):
            if current_entry:
                entries.append(current_entry)
            current_entry = {"anchor": stripped[3:].strip(), "line": i + 1, "tipo": None, "refs": []}

        # Detectar campo **Tipo**: EMPIRICAL/THEORY/DECLARACIÓN
        if current_entry and "**Tipo**" in stripped:
            match = re.search(r"\*\*Tipo\*\*\s*:\s*(\w+)", stripped, re.I)
            if match:
                current_entry["tipo"] = match.group(1).upper()

        # Capturar DOI/URL en la entrada
        if current_entry:
            current_entry["refs"].extend(DOI_PATTERN.findall(line))
            current_entry["refs"].extend(URL_PATTERN.findall(line))

        # Detectar en tabla: fila con EMPIRICAL
        if "|" in stripped and "EMPIRICAL" in stripped.upper():
            # Extraer referencias de la fila
            doi_in_row = DOI_PATTERN.findall(stripped)
            url_in_row = URL_PATTERN.findall(stripped)
            entries.append({
                "anchor": "table-row",
                "line": i + 1,
                "tipo": "EMPIRICAL",
                "refs": doi_in_row + url_in_row,
                "raw": stripped
            })

    if current_entry:
        entries.append(current_entry)

    return [e for e in entries if e.get("tipo") == "EMPIRICAL"]


def has_verifiable_identifier(refs: list[str]) -> bool:
    """Verifica si hay al menos un DOI o URL que parezca real."""
    if not refs:
        return False
    # Filtrar placeholders comunes
    real_refs = [r for r in refs if not any(p in r.lower() for p in ["example.com", "placeholder", "todo", "xxx"])]
    return len(real_refs) > 0


@pytest.mark.parametrize("evidence_file", EVIDENCE_FILES)
def test_empirical_citations_have_verifiable_identifiers(evidence_file):
    """Cada entrada EMPIRICAL debe tener DOI o URL verificable."""
    path = Path(evidence_file)
    assert path.exists(), f"No existe {evidence_file}"

    empirical_entries = extract_empirical_entries(path)

    for entry in empirical_entries:
        assert has_verifiable_identifier(entry["refs"]), (
            f"{path}:{entry.get('line', '?')} - Entrada EMPIRICAL sin DOI/URL verificable. "
            f"Ancla: {entry['anchor']}. Referencias encontradas: {entry['refs'] or 'NINGUNA'}. "
            f"Regla: eliminar o marcar como THEORY (como se hizo con Kohavi/Zhang en color)."
        )


def test_typography_has_zero_empirical_citations():
    """Typography debe tener 0 citas EMPIRICAL - todas deben ser THEORY."""
    path = Path("skills/creative-direction/typography/references/typography-evidence.md")
    empirical_entries = extract_empirical_entries(path)
    assert len(empirical_entries) == 0, (
        f"Typography tiene {len(empirical_entries)} entrada(s) EMPIRICAL residual(es). "
        f"El archivo declara en Sección 2: 'NO HAY ESTUDIOS VERIFICABLES'. "
        f"Todas las decisiones tipográficas deben ser THEORY."
    )


def test_color_has_zero_empirical_citations():
    """Color debe tener 0 citas EMPIRICAL - Kohavi y Zhang eliminados."""
    path = Path("skills/creative-direction/color/references/color-evidence.md")
    empirical_entries = extract_empirical_entries(path)
    assert len(empirical_entries) == 0, (
        f"Color tiene {len(empirical_entries)} entrada(s) EMPIRICAL residual(es). "
        f"Kohavi y Zhang fueron eliminados; el archivo declara vacío empírico."
    )


def test_no_empirical_without_doi_or_url_across_all_evidence():
    """Test global: ningún archivo de evidencia tiene EMPIRICAL sin identificador."""
    all_empirical = []
    for ef in EVIDENCE_FILES:
        path = Path(ef)
        for entry in extract_empirical_entries(path):
            if not has_verifiable_identifier(entry["refs"]):
                all_empirical.append(f"{ef}:{entry.get('line','?')} #{entry['anchor']}")
    assert not all_empirical, (
        "Encontradas citas EMPIRICAL sin identificador verificable:\n" + "\n".join(all_empirical) +
        "\n\nAcción requerida: eliminar o reclasificar como THEORY."
    )