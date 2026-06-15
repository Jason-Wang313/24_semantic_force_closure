# Semantic Force Closure

Anonymous ICLR-style paper artifact for paper 24 in the robotics/embodied-intelligence batch.

## Thesis

Task semantics should enter the force-closure certificate by deleting task-forbidden contact-role wrench generators before convex-hull feasibility is checked.

## V3 Full-Scale Status

- Stage: v3 final full-scale complete.
- Final PDF: `C:/Users/wangz/Downloads/24.pdf`.
- Final PDF verification: 25 pages, 369,669 bytes, SHA256 `97A560CC4A30E210346B035BE8FCFFF705544D1510B2DACE5B08C71D641E544A`.
- Full-scale runner: `experiments/full_scale_semantic_force_closure.py`.
- Full-scale suite: 75,520 policy/certificate rows over 12,032 contact cases, seed 24024, zero plot failures.
- Local build PDF policy: `paper/main.pdf` is removed after the canonical copy is exported to Downloads.

## Reproduce

```powershell
python .\experiments\full_scale_semantic_force_closure.py
cd .\paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The legacy v1/v2 recovery pipeline remains available:

```powershell
python scripts/run_semantic_force_closure.py
python scripts/write_recovery_artifacts.py
powershell -ExecutionPolicy Bypass -File scripts/build_paper.ps1
```

## Main Artifacts

- `docs/full_scale_execution_plan.md`: paper-specific v3 plan written before substantive edits.
- `experiments/full_scale_semantic_force_closure.py`: v3 RAM-light full-scale experiment runner.
- `results/full_scale/`: full-scale rows, summaries, metadata, progress, and generated TeX tables.
- `figures/full_scale/`: full-scale PDF/PNG figures used by the manuscript.
- `docs/evidence_summary.md`: final evidence ledger.
- `docs/experiment_report.md`: v3 result interpretation.
- `docs/final_audit.md`: required final audit with Downloads artifact verification.
- `paper/main.tex`: anonymous v3 final full-scale manuscript source.

## Headline Result

In Family A, geometric force closure accepts 100.0% of contact clouds, but its active witness is task-legal in 0.0% under the trap-heavy witness protocol. Oracle SFC finds a legal witness in 46.3%. At 10% calibrated role-label error, observed SFC has 28.3% unsafe certificates, while risk-aware SFC records 0.0% unsafe certificates in that slice. The paper is a synthetic certificate-ordering study, not a real-robot grasping claim.
