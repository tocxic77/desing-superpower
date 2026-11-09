#!/usr/bin/env python3
"""
test_e2e_circuit.py — Test E2E del circuito completo Design Superpowers

Recorre: Brief → FASE 2 → FASE 3 → FASE 4 → FASE 5 → FASE 6 → FASE 7
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


def main():
    print("=" * 70)
    print("E2E TEST — Circuito completo Design Superpowers")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        run_id = "e2e-test-001"

        # ──────────────────────────────────────────────────────────────
        # PASO 1: Brief mínimo
        # ──────────────────────────────────────────────────────────────
        print(f"\n{'='*70}")
        print("PASO 1: Brief mínimo")
        print(f"{'='*70}")

        brief = {
            "project": run_id,
            "brief": {
                "business_goal": "Validar circuito E2E",
                "mandatories": ["Hero section", "CTA principal", "Contraste AA"],
                "constraints": {"platforms": ["elementor", "figma"]},
            },
        }
        brief_path = tmp / "brief.json"
        brief_path.write_text(json.dumps(brief), encoding="utf-8")
        print(f"✅ Brief creado: {brief_path}")

        # ──────────────────────────────────────────────────────────────
        # PASO 2: FASE 2 — Feasibility
        # ──────────────────────────────────────────────────────────────
        print(f"\n{'='*70}")
        print("PASO 2: FASE 2 — Productor Feasibility")
        print(f"{'='*70}")

        feas_path = tmp / "feasibility-report.json"
        res = run_cmd([
            sys.executable,
            "skills/production/feasibility/scripts/generate-feasibility-report.py",
            str(brief_path),
            "-o", str(feas_path)
        ])
        if res.returncode not in (0, 2):
            print(f"❌ FASE 2 falló: {res.stderr}")
            return 1
        print(f"✅ FASE 2 completada (exit={res.returncode}): {feas_path}")

        # ──────────────────────────────────────────────────────────────
        # PASO 3: FASE 3 — Creative Decisions (color + typography)
        # ──────────────────────────────────────────────────────────────
        print(f"\n{'='*70}")
        print("PASO 3: FASE 3 — Decisiones de color + tipografía")
        print(f"{'='*70}")

        # Use the existing typography decisions that reference the feasibility report
        decisions_path = tmp / "design-decisions.json"
        decisions = json.loads((ROOT / "tmp" / "design-decisions-typography.json").read_text())
        # Update feasibility_ref to point to decisions from this run's feasibility report
        for d in decisions:
            # Map to the generated feasibility decisions (mand-001-c, mand-002-c)
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
            print(f"❌ FASE 3 gate falló: {res.stdout}\n{res.stderr}")
            return 1
        print(f"✅ FASE 3 gate pasó: {res.stdout.strip()}")

        # ──────────────────────────────────────────────────────────────
        # PASO 4: FASE 4 — Builder HTML
        # ──────────────────────────────────────────────────────────────
        print(f"\n{'='*70}")
        print("PASO 4: FASE 4 — Builder HTML")
        print(f"{'='*70}")

        html_path = tmp / "index.html"
        res = run_cmd([
            sys.executable,
            "tools/builders/html_builder.py",
            "--decisions", str(decisions_path),
            "--output", str(html_path)
        ])
        if res.returncode != 0:
            print(f"❌ FASE 4 falló: {res.stderr}")
            return 1
        print(f"✅ FASE 4 completada: {html_path}")
        print(f"   {res.stdout.strip()}")

        # ──────────────────────────────────────────────────────────────
        # PASO 5: FASE 5 — Design Critic
        # ──────────────────────────────────────────────────────────────
        print(f"\n{'='*70}")
        print("PASO 5: FASE 5 — Design Critic (Aislado)")
        print(f"{'='*70}")

        diagnostic_path = tmp / "diagnostic.json"
        res = run_cmd([
            sys.executable,
            "tools/critics/design_critic.py",
            str(html_path),
            "--run-id", f"{run_id}-critic",
            "--tokens", "design-system/tokens",
            "--output", str(diagnostic_path)
        ])
        if res.returncode != 0:
            print(f"❌ FASE 5 falló: {res.stderr}")
            return 1
        print(f"✅ FASE 5 completada: {diagnostic_path}")
        print(f"   {res.stdout.strip()}")

        # ──────────────────────────────────────────────────────────────
        # PASO 6: FASE 6 — Correction Wrapper (si hay issues)
        # ──────────────────────────────────────────────────────────────
        diagnostic = json.loads(diagnostic_path.read_text())
        if diagnostic.get("diagnostics"):
            print(f"\n{'='*70}")
            print("PASO 6: FASE 6 — Correction Wrapper")
            print(f"{'='*70}")

            corrected_html = tmp / "index_corrected.html"
            corrections_path = tmp / "corrections.json"
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
                print(f"❌ FASE 6 falló: {res.stderr}")
                return 1
            print(f"✅ FASE 6 completada: {corrected_html}")
            print(f"   {res.stdout.strip()}")

            # Re-validate after correction
            verify_diagnostic = tmp / "verify-diagnostic.json"
            res = run_cmd([
                sys.executable,
                "tools/critics/design_critic.py",
                str(corrected_html),
                "--run-id", f"{run_id}-verify",
                "--tokens", "design-system/tokens",
                "--output", str(verify_diagnostic)
            ])
            if res.returncode != 0:
                print(f"❌ Re-validación falló: {res.stderr}")
                return 1

            verify = json.loads(verify_diagnostic.read_text())
            if verify.get("diagnostics"):
                print(f"❌ Re-validación falló: quedan {len(verify['diagnostics'])} issues")
                return 1
            print("✅ Re-validación: 0 issues (corrección exitosa)")

            final_html = corrected_html
            final_diagnostic = verify_diagnostic
        else:
            print(f"\n{'='*70}")
            print("PASO 6: FASE 6 — Sin issues, saltando corrección")
            print(f"{'='*70}")
            final_html = html_path
            final_diagnostic = diagnostic_path

        # ──────────────────────────────────────────────────────────────
        # PASO 7: FASE 7 — Approval Script
        # ──────────────────────────────────────────────────────────────
        print(f"\n{'='*70}")
        print("PASO 7: FASE 7 — Approval Script")
        print(f"{'='*70}")

        approval_path = tmp / "approval-record.json"
        res = run_cmd([
            sys.executable,
            "tools/builders/approval.py",
            str(final_diagnostic),
            "--run-id", f"{run_id}-approval",
            "--html", str(final_html),
            "--output", str(approval_path)
        ])
        if res.returncode not in (0, 2):
            print(f"❌ FASE 7 falló: {res.stderr}")
            return 1
        print(f"✅ FASE 7 completada: {approval_path}")
        print(f"   {res.stdout.strip()}")

        # ──────────────────────────────────────────────────────────────
        # RESULTADO FINAL
        # ──────────────────────────────────────────────────────────────
        approval = json.loads(approval_path.read_text())
        print(f"\n{'='*70}")
        print("RESULTADO E2E")
        print(f"{'='*70}")
        print(f"Run ID: {run_id}")
        print(f"Decisión final: {approval['decision'].upper()}")
        print(f"Riesgo: {approval['risk_assessment']['level'].upper()}")
        print(f"Razón: {approval['decision_reason']}")

        if approval['decision'] == 'approve':
            print("\n🎉 CIRCUITO E2E PASÓ COMPLETAMENTE")
            return 0
        else:
            print(f"\n⚠️ CIRCUITO E2E NO APROBADO: {approval['decision']}")
            return 1


if __name__ == "__main__":
    sys.exit(main())