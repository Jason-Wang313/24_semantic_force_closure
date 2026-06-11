# Plan

## Objective
Create a complete, runnable robotics/embodied-intelligence paper project for paper 24, starting from the seed "Semantic Force Closure" but replacing the thesis if the literature survey shows a stronger direction.

## Non-Interactive Safety
- Use explicit timeouts for experiments, retrieval, and LaTeX builds.
- Avoid brittle inline PowerShell/Python for loops, CSV filtering, plotting, or bibliography work; create checked-in helper scripts instead.
- Treat all tool availability checks as fallible and document failures in `child_status.md`.
- Preserve useful existing artifacts if this retry folder already contains them.
- Keep `child_status.md` compact and rewrite it from current facts after major stages.

## Stages
1. Initialize status and inspect existing repository artifacts without deleting anything.
2. Build the literature pipeline:
   - retrieve at least 1000 candidate papers in grasp planning, force closure, semantic parts, contact affordances, tactile/contact reasoning, and manipulation;
   - score and save `docs/related_work_matrix.csv`;
   - produce a 300-paper serious skim, 200-250-paper deep read subset, and 100-paper hostile prior-work set.
3. Extract prior-work fields for important papers:
   - problem claimed;
   - mechanism introduced;
   - hidden assumptions;
   - fixed variables;
   - ignored failure modes;
   - what becomes less novel;
   - what remains open.
4. Define the field box, enumerate at least 20 false-able assumptions, propose assumption-breaking directions, and choose the strongest thesis.
5. Implement runnable evidence for the selected thesis with deterministic scripts, cached outputs, plots, and tests where appropriate.
6. Write the required documents:
   - `docs/literature_map.md`
   - `docs/hostile_prior_work.md`
   - `docs/novelty_boundary_map.md`
   - `docs/novelty_decision.md`
   - `docs/claims.md`
   - `docs/reviewer_attacks.md`
   - `docs/final_audit.md`
7. Fetch or recreate the latest official ICLR LaTeX template available at runtime, sanitize bibliography/text for pdfLaTeX, write the anonymous paper, and compile with direct `pdflatex`/`bibtex` passes.
8. Save the final PDF only to `C:/Users/wangz/Downloads/24.pdf`.
9. Create/push public GitHub repo `24_semantic_force_closure`; if blocked by credentials or network, document exact failure and recovery.
10. Final audit and final response.

## Expected Project Shape
- `scripts/` for retrieval, analysis, experiment, plotting, and build helpers.
- `data/` for cached literature and experiment outputs.
- `docs/` for survey and audit artifacts.
- `paper/` for LaTeX source, figures, and bibliography.
- `README.md` with runnable reproduction instructions.
