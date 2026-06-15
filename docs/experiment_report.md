# V3 Full-Scale Experiment Report

## Execution

- Runner: `experiments/full_scale_semantic_force_closure.py`.
- Seed: 24024.
- Rows: 75,520 policy/certificate rows.
- Cases: 12,032 contact cases.
- Plot failures: 0.
- Output root: `results/full_scale/`.
- Figure root: `figures/full_scale/`.
- Table root: `results/full_scale/tex/`.

The suite was run sequentially and streamed family rows to disk. It keeps only summary counters and a small counterexample library in memory.

## Main Interpretation

The v3 result is a certificate-legality result, not a permissiveness result. In Family A, geometric FC accepts every contact cloud, but its active witness is task-legal in 0.000 under the trap-heavy protocol. Oracle SFC certifies 0.463. That 0.463 is the fraction of cases where a legal allowed-role witness exists. The remaining cases should be rejected or replanned.

Semantic-only acceptance and soft semantic penalties are unsafe foils. Semantic-only accepts 1.000 but is unsafe in 0.537. Soft-penalty FC accepts 1.000 and is true-legal in 0.000. These results support the hard-deletion certificate ordering.

## Uncertainty Interpretation

Observed SFC is unsafe under role-label noise. At 10% calibrated role-label error, observed SFC has unsafe rate 0.283. Risk-aware SFC records 0.000 unsafe certificates in that calibrated threshold-0.70 slice, but this is a calibrated-confidence result, not a universal safety theorem.

## Witness Ordering

Single-witness posthoc filtering fails in the main stress protocol because the selected geometric witness uses forbidden roles. Top-k posthoc improves with search budget and reaches 0.375 at k=16 in Family C. This shows posthoc filtering can approximate SFC only when it starts searching the semantic-deleted witness space.

## Final Artifact

The final PDF exported to `C:/Users/wangz/Downloads/24.pdf` is 25 pages, 369,669 bytes, SHA256 `97A560CC4A30E210346B035BE8FCFFF705544D1510B2DACE5B08C71D641E544A`.
