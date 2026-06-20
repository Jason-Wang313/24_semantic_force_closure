# Full-Scale Evidence Summary

- Stage: v3 final full-scale complete.
- Seed: 24024.
- Rows: 75,520 policy/certificate rows.
- Cases: 12,032 contact cases.
- Plot failures: 0.
- Runner: `experiments/full_scale_semantic_force_closure.py`.
- Final PDF: `C:/Users/wangz/Downloads/24.pdf`.
- Final PDF verification: 25 pages, 369,669 bytes, SHA256 `A96EB09B4F6204ED53597C519B982F941D8BA87DD200F98028042BB7E3B68097`.
- Final PDF link boxes: green citations = 25, red internal references = 9,
  cyan = 0, with one-point borders on all 34 link annotations.

## Headline Numbers

- Family A oracle SFC true-legal rate: 0.463.
- Family A geometric FC acceptance rate: 1.000.
- Family A geometric witness true-legal rate: 0.000.
- Family A semantic-only true-certificate rate: 0.463.
- Family A semantic-only unsafe rate: 0.537.
- Family A posthoc single-witness true-legal rate: 0.000.
- Family A soft-penalty true-legal rate: 0.000.
- Family B at 10% calibrated label error: observed SFC unsafe rate 0.283; risk-aware SFC unsafe rate 0.000.
- Family B at 10% calibrated label error: observed SFC true-legal rate 0.333; risk-aware SFC true-legal rate 0.433.
- Family C top-k posthoc true-legal rate: 0.000 at k=1, 0.076 at k=2, 0.215 at k=4, 0.281 at k=8, 0.375 at k=16.
- Family F all-allowed control oracle SFC acceptance rate: 1.000.

## Family Counts

- Family A task/geometry sweep: 16,200 rows over 3,240 cases.
- Family B semantic noise and uncertainty: 40,320 rows over 5,040 cases.
- Family C witness ordering: 4,320 rows over 1,440 cases.
- Family D friction/model perturbation: 3,840 rows over 768 cases.
- Family E ablations: 2,520 rows over 360 cases.
- Family F negative controls: 1,920 rows over 384 cases.
- Family G counterexample library: 6,400 rows over 800 cases.

## Scope

These results support a synthetic certificate-ordering mechanism. They do not establish real-robot grasping performance, semantic perception accuracy, tactile robustness, dynamic manipulation success, or trajectory-planner integration.
