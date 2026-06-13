# Semantic Force Closure

Anonymous ICLR-style paper artifact for paper 24 in the robotics/embodied-intelligence batch.

## Thesis

Task semantics should enter the force-closure certificate by deleting task-forbidden contact-role wrench generators before convex-hull feasibility is checked.

## Reproduce

```powershell
python scripts/run_semantic_force_closure.py
python scripts/write_recovery_artifacts.py
powershell -ExecutionPolicy Bypass -File scripts/build_paper.ps1
```

The final PDF target is `C:\Users\wangz\Downloads\24.pdf`.

## Main Artifacts

- `docs/related_work_matrix.csv`: 1000-paper literature matrix.
- `docs/literature_map.md`: landscape and assumption analysis.
- `docs/hostile_prior_work.md`: 100-paper hostile prior-work set.
- `results/semantic_force_closure_trials.csv`: deterministic trial rows.
- `results/summary.json`: aggregate evidence.
- `results/role_noise_stress_summary.json`: v2 role-label noise stress.
- `paper/main.tex`: anonymous ICLR-style manuscript.
- `docs/final_audit.md`: required final audit.
