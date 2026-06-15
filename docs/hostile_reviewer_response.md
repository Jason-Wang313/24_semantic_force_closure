# Hostile Reviewer Response

## Main Concern

The strongest objection is that SFC assumes reliable task-role labels. If a blade is mislabeled as a handle, observed SFC can certify an unsafe witness.

## V3 Response

The v3 paper foregrounds this failure. Family B corrupts role labels and shows that at 10% calibrated label error, observed SFC has unsafe rate 0.283. Risk-aware SFC records 0.000 unsafe certificates in the threshold-0.70 calibrated slice, but the paper does not claim universal safety under uncalibrated or adversarial confidence.

## Positive Evidence

Family A shows the certificate-ordering gap: geometric FC accepts 1.000 of contact clouds but its active witness is true-legal in 0.000, while oracle SFC finds legal witnesses in 0.463. Semantic-only and soft-penalty baselines accept unsafe witnesses, which supports hard semantic deletion before certificate search.

## Remaining Weakness

No real robot, no learned perception, no tactile witness verification, no 3D hand kinematics, and no trajectory optimization. The final claim is synthetic and certificate-level.
