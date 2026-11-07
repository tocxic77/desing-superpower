#!/usr/bin/env python3
"""
verify_evidence_anchors.py — comprueba que todo `<algo>-evidence.md#ancla` referenciado
exista realmente como encabezado en el archivo de evidencia.

Motivo: las anclas se citaban sin existir (o existían sólo dentro de un bloque de
código de ejemplo), así que `evidence_refs` apuntaba a la nada y ningún verificador
lo detectaba fuera del skill editorial.

Reglas:
- Sólo cuentan como ancla los encabezados reales (`##`..`####`). Se ignoran los que
  están dentro de bloques ``` ... ``` (un ejemplo de formato no es un encabezado).
- Slug estilo GitHub: minúsculas, espacios -> '-', se descartan caracteres no
  alfanuméricos salvo '-' y '_'.
- Referencias detectadas en *.md, *.json, *.py, *.sh.

Uso: python tools/validators/verify_evidence_anchors.py [--root .] [-v]
Exit 0 = todas las anclas existen; 1 = hay referencias rotas.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "test-venv", "venv", ".venv", "__pycache__",
             "dist", "build", ".pytest_cache", "_generated", "site-packages"}
REF_PATTERN = re.compile(r"([A-Za-z0-9_][A-Za-z0-9_./-]*evidence\.md)#([A-Za-z0-9_.-]+)")
IGNORE_MARKER = "anchor-check: ignore"
HEADING_PATTERN = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
SCAN_SUFFIXES = {".md", ".json", ".py", ".sh", ".yaml", ".yml"}


def slugify(text: str) -> str:
    """Slug GitHub para un encabezado."""
    text = text.strip().lower()
    text = re.sub(r"[`*_]{1,3}", "", text)          # énfasis inline
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # links
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"[\s]+", "-", text).strip("-")


def anchors_of(path: Path) -> set[str]:
    """Anclas reales del archivo: encabezados fuera de bloques de código."""
    anchors: set[str] = set()
    in_fence = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_PATTERN.match(line)
        if m:
            anchors.add(slugify(m.group(2)))
    return anchors


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="raíz del repo")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    evidence_files = {p.resolve(): p for p in iter_files(root) if p.name.endswith("-evidence.md")}
    if not evidence_files:
        print("ERROR: no se encontró ningún *-evidence.md", file=sys.stderr)
        return 1

    anchors = {p: anchors_of(p) for p in evidence_files}
    by_name = {p.name: p for p in evidence_files}

    broken: list[tuple[str, str, str]] = []
    checked = 0
    for path in iter_files(root):
        if path.suffix not in SCAN_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "evidence.md#" not in text:
            continue
        if path.name.startswith("neg-") or IGNORE_MARKER in text:
            continue  # fixtures que prueban el fallo a propósito
        for lineno, line in enumerate(text.splitlines(), start=1):
            for ref_file, anchor in REF_PATTERN.findall(line):
                checked += 1
                target = (root / ref_file).resolve() if ref_file else None
                if target not in evidence_files:
                    target = by_name.get(Path(ref_file).name if ref_file else "", None)
                rel = path.relative_to(root).as_posix()
                if target is None:
                    broken.append((rel, f"{ref_file}#{anchor}", "archivo de evidencia inexistente"))
                elif anchor not in anchors[target]:
                    broken.append((rel, f"{target.name}#{anchor}", "ancla inexistente"))
                elif args.verbose:
                    print(f"ok  {rel}:{lineno} -> {target.name}#{anchor}")

    print(f"Archivos de evidencia: {len(evidence_files)}")
    for p, a in sorted(anchors.items()):
        print(f"  {p.name}: {len(a)} anclas")
    print(f"Referencias comprobadas: {checked}")

    if broken:
        print(f"\n❌ {len(broken)} referencia(s) rota(s):", file=sys.stderr)
        for rel, ref, reason in broken:
            print(f"  {rel} -> {ref} ({reason})", file=sys.stderr)
        return 1

    print("\n✅ Todas las anclas referenciadas existen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
