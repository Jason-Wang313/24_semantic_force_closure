# Reproducibility Checklist

- [x] Dependencies are listed in `requirements.txt`.
- [x] Legacy runner is `scripts/run_semantic_force_closure.py`.
- [x] V3 full-scale runner is `experiments/full_scale_semantic_force_closure.py`.
- [x] V3 outputs are under `results/full_scale/`.
- [x] V3 figures are under `figures/full_scale/`.
- [x] Generated V3 TeX tables are under `results/full_scale/tex/`.
- [x] Paper source is `paper/main.tex`.
- [x] Canonical batch PDF path is `C:/Users/wangz/Downloads/24.pdf`.
- [x] Canonical PDF is verified at 25 pages, 369,669 bytes, SHA256 `A96EB09B4F6204ED53597C519B982F941D8BA87DD200F98028042BB7E3B68097`.
- [x] Local `paper/main.pdf` is deleted after copying the canonical PDF to Downloads.
- [x] The full-scale runner compiles with `python -m py_compile`.
- [x] VLA-style link boxes verified with pypdf inventory and rendered-page
  visual inspection.

Recommended verification commands:

```powershell
python .\experiments\full_scale_semantic_force_closure.py
python -m py_compile .\experiments\full_scale_semantic_force_closure.py
cd .\paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdfinfo .\main.pdf
pdftotext .\main.pdf - | Select-String -Pattern 'v3 final full-scale|75,520|12,032|46.3|28.3|risk-aware|no real robot|Final Audit'
```
