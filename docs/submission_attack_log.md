# Submission Attack Log

Updated: 2026-06-13 03:41:00 +01:00

## V2 Attack Rounds

1. **"SFC assumes perfect semantic role labels."** Added a role-label noise stress before semantic deletion.
2. **"Noisy labels may create unsafe certificates."** Confirmed. At 10% role-label error, unsafe false certificates reach 30.7%; at 30%, they reach 67.2%.
3. **"Observed SFC can become overconfident."** Confirmed. Observed SFC rate rises under noise while true-legal SFC falls.
4. **"The method needs uncertainty-aware semantics."** Still unresolved; added as required next work.
5. **"The simulator is planar and diagnostic."** Still unresolved; decision remains workshop-only / strong-revise.

## Terminal Assessment

The recoverable overclaim was addressed by adding role-noise stress and narrowing the claim to reliable labels or uncertainty-aware certification. Remaining weaknesses require perception uncertainty, hardware validation, and stronger learned-grasp comparisons.
