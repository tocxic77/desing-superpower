#!/usr/bin/env python3
"""
test_e2e_circuit.py — Test E2E del circuito completo Design Superpowers

Tres ramas:
1. HAPPY PATH — Brief válido → 0 issues → APPROVE
2. UNHAPPY PATH — Colores que fallan contraste → Critic detecta → Fix → Re-valida → APPROVE
3. RED PATH — Brief con decisiones RED → FASE 3 bloquea → FASE 4 no se ejecuta
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def run_cmd(cmd: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


def run_branch(name: str, brief: dict, tmp: Path, run_id: str) -> dict:
    """Ejecuta una rama completa del E2E y retorna resultado."""
    print(f"\n{'='*70}")
    print(f"RAMA: {name}")
    print(f"{'='*70}")

    brief_path = tmp / f"brief-{run_id}.json"
    brief_path.write_text(json.dumps(brief), encoding="utf-8")

    # PASO 1: FASE 2 — Feasibility
    feas_path = tmp / f"feasibility-{run_id}.json"
    res = run_cmd([
        sys.executable,
        "skills/production/feasibility/scripts/generate-feasibility-report.py",
        str(brief_path),
        "-o", str(feas_path)
    ])
    if res.returncode not in (0, 2):
        return {"status": "FASE2_FAILED", "error": res.stderr, "exit_code": res.returncode}
    feas_report = json.loads(feas_path.read_text())

    # PASO 2: FASE 3 — Decisiones (solo si no hay red en feasibility)
    red_decisions = [d for d in feas_report.get("decisions_evaluated", []) if d.get("classification") == "red"]
    if red_decisions:
        return {
            "status": "FASE3_BLOCKED_BY_RED",
            "red_decisions": [d["decision_id"] for d in red_decisions],
            "feasibility_report": feas_report,
        }

    # Si no hay red, continuamos con decisiones de color+typography
    decisions_path = tmp / f"decisions-{run_id}.json"
    decisions = json.loads((ROOT / "tmp" / "design-decisions-typography.json").read_text())
    # Map feasibility_ref to this run's mandatories
    for d in decisions:
        if d["feasibility_ref"] == "mand-001-c":
            d["feasibility_ref"] = "mand-001-c"
        elif d["feasibility_ref"] == "mand-002-c":
            d["feasibility_ref"] = "mand-002-c"
    decisions_path.write_text(json.dumps(decisions), encoding="utf-8")

    # Verify FASE 3 gate
    res = run_cmd([
        sys.executable,
        "skills/production/feasibility/scripts/verify-feasibility-refs.py",
        str(feas_path), str(decisions_path),
        "--schema", "templates/design-decision-schema.json"
    ])
    if res.returncode != 0:
        return {"status": "FASE3_GATE_FAILED", "error": res.stdout + res.stderr}

    # PASO 3: FASE 4 — Builder HTML
    html_path = tmp / f"index-{run_id}.html"
    res = run_cmd([
        sys.executable,
        "tools/builders/html_builder.py",
        "--decisions", str(decisions_path),
        "--output", str(html_path)
    ])
    if res.returncode != 0:
        return {"status": "FASE4_FAILED", "error": res.stderr}

    # FORZAR FALLO DE CONTRASTE en UNHAPPY_PATH y CORRECTION_FAILS_PATH
    if name in ("UNHAPPY_PATH", "CORRECTION_FAILS_PATH"):
        html_content = html_path.read_text(encoding="utf-8")
        # Cambiar el color del subtítulo a gris bajo contraste
        html_content = html_content.replace(
            ".hero__subtitle {",
            ".hero__subtitle { color: #888888 !important; /* FORZADO para test */"
        )
        html_path.write_text(html_content, encoding="utf-8")
        print(f"   ⚠ HTML modificado para forzar fallo de contraste")

    # PARA CORRECTION_FAILS_PATH: añadir estilo inline con !important 
    # que tiene mayor especificidad que las reglas de stylesheet que inyecta design_loop.py
    if name == "CORRECTION_FAILS_PATH":
        html_content = html_path.read_text(encoding="utf-8")
        # Inyectar style inline en el elemento hero__subtitle - esto no se puede 
        # sobrescribir con reglas de stylesheet (mayor especificidad)
        html_content = html_content.replace(
            'class="hero__subtitle"',
            'class="hero__subtitle" style="color: #888888 !important; background-color: #FAFAFA !important;"'
        )
        html_path.write_text(html_content, encoding="utf-8")
        print(f"   ⚠ HTML con style inline !important que impide auto-fix por stylesheet")

    # PASO 4: FASE 5 — Design Critic
    diagnostic_path = tmp / f"diagnostic-{run_id}.json"
    res = run_cmd([
        sys.executable,
        "tools/critics/design_critic.py",
        str(html_path),
        "--run-id", f"{run_id}-critic",
        "--tokens", "design-system/tokens",
        "--output", str(diagnostic_path)
    ])
    if res.returncode != 0:
        return {"status": "FASE5_FAILED", "error": res.stderr}
    diagnostic = json.loads(diagnostic_path.read_text())

    # PASO 5: FASE 6 — Correction Wrapper (si hay issues)
    final_html = html_path
    final_diagnostic = diagnostic_path
    has_regressions = False
    if diagnostic.get("diagnostics"):
        corrected_html = tmp / f"index-{run_id}_corrected.html"
        corrections_path = tmp / f"corrections-{run_id}.json"
        res = run_cmd([
            sys.executable,
            "tools/builders/correction_wrapper.py",
            str(html_path), str(diagnostic_path),
            "--run-id", f"{run_id}-correction",
            "--tokens", "design-system/tokens",
            "--output", str(corrected_html),
            "--corrections-output", str(corrections_path)
        ])
        if res.returncode != 0:
            return {"status": "FASE6_FAILED", "error": res.stderr}

        # Re-validate after correction
        verify_diagnostic = tmp / f"verify-{run_id}.json"
        res = run_cmd([
            sys.executable,
            "tools/critics/design_critic.py",
            str(corrected_html),
            "--run-id", f"{run_id}-verify",
            "--tokens", "design-system/tokens",
            "--output", str(verify_diagnostic)
        ])
        if res.returncode != 0:
            return {"status": "FASE6_REVALIDATE_FAILED", "error": res.stderr}

        verify = json.loads(verify_diagnostic.read_text())
        if verify.get("diagnostics"):
            # Hay regresiones - issues persisten
            has_regressions = True
            final_diagnostic = verify_diagnostic
            final_html = corrected_html
        else:
            final_html = corrected_html
            final_diagnostic = verify_diagnostic

    # PASO 6: FASE 7 — Approval Script
    approval_path = tmp / f"approval-{run_id}.json"
    res = run_cmd([
        sys.executable,
        "tools/builders/approval.py",
        str(final_diagnostic),
        "--run-id", f"{run_id}-approval",
        "--html", str(final_html),
        "--output", str(approval_path)
    ])
    # approval.py returns: 0=approve, 1=block, 2=human_review
    if res.returncode not in (0, 1, 2):
        return {"status": "FASE7_FAILED", "error": f"stdout: {res.stdout}\nstderr: {res.stderr}", "exit_code": res.returncode}

    approval = json.loads(approval_path.read_text())

    return {
        "status": "COMPLETED",
        "approval": approval,
        "feasibility": feas_report,
        "diagnostics_count": len(diagnostic.get("diagnostics", [])),
        "corrections_applied": diagnostic.get("diagnostics") is not None,
        "has_regressions": has_regressions,
    }


def main():
    print("=" * 70)
    print("E2E TEST — Tres ramas del circuito Design Superpowers")
    print("=" * 70)

    # RAMA 1: HAPPY PATH
    happy_brief = {
        "project": "happy-path",
        "brief": {
            "business_goal": "Validar circuito E2E camino feliz",
            "mandatories": ["Hero section", "CTA principal", "Contraste AA"],
            "constraints": {"platforms": ["elementor", "figma"]},
        },
    }

    # ──────────────────────────────────────────────────────────────
    # RAMA 2: UNHAPPY PATH — Contraste falla
    # ──────────────────────────────────────────────────────────────
    # El builder usa tokens semánticos que pasan contraste.
    # Para forzar un fallo real, generamos el HTML normal y luego
    # modificamos el color del subtítulo a un gris bajo contraste
    # antes de pasarlo al Critic.
    unhappy_brief = {
        "project": "unhappy-contrast",
        "brief": {
            "business_goal": "Validar fix de contraste",
            "mandatories": ["Hero section", "CTA principal", "Contraste AA"],
            "constraints": {"platforms": ["elementor", "figma"]},
        },
    }

    # RAMA 3: RED PATH — Decisiones que producen RED en FASE 2
    red_brief = {
        "project": "red-path",
        "brief": {
            "business_goal": "Validar bloqueo por red",
            "mandatories": [
                "Hero con video de fondo",
                "Tipografía variable multi-axis (wght+wdth+opsz)",
            ],
            "constraints": {"platforms": ["elementor", "figma"]},
        },
    }

    # RAMA 4: CORRECTION_FAILS_PATH — Fix no resuelve el problema
    # HTML con color !important que design_loop.py no puede sobrescribir
    correction_fails_brief = {
        "project": "correction-fails",
        "brief": {
            "business_goal": "Validar bloqueo cuando fix falla",
            "mandatories": ["Hero section", "CTA principal", "Contraste AA"],
            "constraints": {"platforms": ["elementor", "figma"]},
        },
    }

    results = {}

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Ejecutar ramas en secuencia
        for name, brief in [
            ("HAPPY_PATH", happy_brief),
            ("UNHAPPY_PATH", unhappy_brief),
            ("RED_PATH", red_brief),
            ("CORRECTION_FAILS_PATH", correction_fails_brief),
        ]:
            results[name] = run_branch(name, brief, tmp, name.lower().replace("_", "-"))

    # REPORTE FINAL
    print("\n" + "=" * 70)
    print("RESULTADO E2E — CUATRO RAMAS")
    print("=" * 70)

    all_passed = True
    for name, result in results.items():
        print(f"\n--- {name} ---")
        if result["status"] == "COMPLETED":
            approval = result["approval"]
            print(f"  Status: {result['status']}")
            print(f"  Decisión: {approval['decision'].upper()}")
            print(f"  Riesgo: {approval['risk_assessment']['level'].upper()}")
            print(f"  Issues detectados: {result['diagnostics_count']}")
            print(f"  Correcciones aplicadas: {'SÍ' if result['corrections_applied'] else 'NO'}")
            
            # Verificaciones específicas por rama
            if name == "CORRECTION_FAILS_PATH":
                # Esta rama DEBE bloquear, no aprobar
                if approval['decision'] != 'block' and approval['decision'] != 'human_review':
                    print(f"  ❌ CORRECTION_FAILS_PATH: esperaba block/human_review, got {approval['decision']}")
                    all_passed = False
                elif not result.get('has_regressions', False):
                    print(f"  ❌ CORRECTION_FAILS_PATH: esperaba has_regressions=True, got False")
                    all_passed = False
                else:
                    print(f"  ✅ CORRECTION_FAILS_PATH bloqueado correctamente: {approval['decision']} (has_regressions=True)")
            elif approval['decision'] != 'approve':
                all_passed = False
                
        elif result["status"] == "FASE3_BLOCKED_BY_RED":
            print(f"  Status: {result['status']} ✅ (esperado)")
            print(f"  Decisiones RED bloqueadas: {result['red_decisions']}")
        else:
            print(f"  Status: {result['status']} ❌")
            print(f"  Error: {result.get('error', 'N/A')}")
            all_passed = False

    print(f"\n{'='*70}")
    if all_passed:
        print("🎉 TODAS LAS RAMAS PASARON")
        return 0
    else:
        print("❌ ALGUNA RAMA FALLÓ")
        return 1


if __name__ == "__main__":
    sys.exit(main())