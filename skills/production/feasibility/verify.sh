#!/usr/bin/env bash
# verify.sh — wrapper de compatibilidad para los skills que documentan esta ruta.
#
# Implementación real: verify-feasibility-refs.py (sin dependencia de jq).
# Uso: ./verify.sh <feasibility-report.json> <design-decisions.json> [--schema <schema.json>]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${SCRIPT_DIR}/scripts/verify-feasibility-refs.py"

# En Git-Bash/MSYS el python es nativo: no traduce rutas POSIX (/c/... -> C:/...)
if command -v cygpath >/dev/null 2>&1; then
  TARGET="$(cygpath -w "${TARGET}")"
fi

exec python3 "${TARGET}" "$@"
