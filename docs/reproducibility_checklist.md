# Reproducibility Checklist

- [x] Dependencies are listed in `requirements.txt`.
- [x] Main simulator source is `scripts/run_semantic_force_closure.py`.
- [x] Paper/docs generator is `scripts/write_recovery_artifacts.py`.
- [x] Main outputs are `results/semantic_force_closure_trials.csv`, `results/summary.json`, and `paper/results_table.tex`.
- [x] V2 outputs are `results/role_noise_stress.csv`, `results/role_noise_stress_summary.json`, and `results/role_noise_stress_table.tex`.
- [x] Paper source is `paper/main.tex`.
- [x] Canonical batch PDF path is `C:/Users/wangz/Downloads/24.pdf`.
- [x] Local `paper/main.pdf` was deleted after copying the canonical PDF to Downloads.

Recommended verification commands:

```powershell
python scripts\run_semantic_force_closure.py
python scripts\write_recovery_artifacts.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```
