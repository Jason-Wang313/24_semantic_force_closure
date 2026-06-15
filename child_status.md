# Child Status

Stage: v3 final full-scale complete

Current facts:
- V3 plan was written first in `docs/full_scale_execution_plan.md`.
- V3 runner `experiments/full_scale_semantic_force_closure.py` completed with seed 24024.
- Full-scale suite produced 75,520 policy/certificate rows over 12,032 contact cases with zero plot failures.
- Family coverage: task/geometry sweep, semantic noise and uncertainty, witness ordering, friction/model perturbation, ablations, negative controls, and counterexample library.
- Final manuscript source is `paper/main.tex` and contains the marker `v3 final full-scale`.
- Final LaTeX build completed with pdflatex, bibtex, pdflatex, pdflatex all exiting 0.
- Final PDF was exported to `C:/Users/wangz/Downloads/24.pdf`.
- Verified final PDF: 25 pages, 369,669 bytes, SHA256 `97A560CC4A30E210346B035BE8FCFFF705544D1510B2DACE5B08C71D641E544A`.
- Final PDF text check found the v3 marker, 75,520 rows, 12,032 cases, 46.3 oracle SFC result, 28.3 observed-SFC unsafe result, risk-aware boundary, no-real-robot limitation, and final audit marker.
- Local `paper/main.pdf` was removed after export.
- GitHub URL/status: `https://github.com/Jason-Wang313/24_semantic_force_closure`.

Key v3 results:
- Family A: geometric FC acceptance 1.000, geometric witness true-legal rate 0.000, oracle SFC true-legal rate 0.463.
- Family A: semantic-only acceptance 1.000 but unsafe rate 0.537; soft-penalty FC acceptance 1.000 but unsafe rate 1.000.
- Family B calibrated 10% role-label error: observed SFC unsafe 0.283; risk-aware SFC unsafe 0.000 in the threshold-0.70 slice.
- Family C: top-k posthoc improves from 0.000 true-legal at k=1 to 0.375 at k=16.
- Family F: all-allowed control makes oracle SFC equal geometric FC at 1.000, while no-roles and geometrically infeasible controls correctly reject.

Remaining limitations:
- Synthetic planar proxy only.
- No real robot, tactile loop, learned perception model, 3D hand kinematics, dynamics, or trajectory optimization.
- SFC depends on correct or calibrated role labels.
- The result is a certificate-ordering result, not a claim that SFC increases grasp success rate.
