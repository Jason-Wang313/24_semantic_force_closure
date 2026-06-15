# Claims

## Supported By Formal Argument

1. In the same wrench-generator model, SFC implies ordinary geometric force closure because the SFC generator set is a subset of the geometric generator set.
2. The converse does not hold: a geometric certificate can require task-forbidden contact roles.
3. Post-hoc filtering of a selected geometric witness is not equivalent to deleting forbidden generators before certificate search.

## Supported By Runnable V3 Evidence

1. The full-scale suite produced 75,520 policy/certificate rows over 12,032 contact cases with zero plot failures.
2. In Family A, geometric FC accepts 1.000 of contact clouds but its active witness is true-legal in 0.000; oracle SFC finds a true-legal witness in 0.463.
3. Semantic-only acceptance is unsafe in Family A: it accepts 1.000 but has unsafe rate 0.537.
4. Soft-penalty and auditless geometric ablations can accept unsafe witnesses in the hostile protocol.
5. In the calibrated 10% label-error slice, observed SFC unsafe rate is 0.283 while risk-aware SFC unsafe rate is 0.000.
6. Top-k posthoc improves with search budget, rising from 0.000 true-legal at k=1 to 0.375 at k=16 in Family C.
7. Negative controls behave as expected: all roles allowed makes SFC equal geometric FC, no roles allowed returns no SFC certificate, and geometrically infeasible controls reject.

## Plausible But Not Fully Proven

1. SFC can serve as a certificate layer inside learned or model-based grasp planners.
2. Tactile witness verification should make SFC more deployable.
3. Robust or probabilistic SFC could certify under role/contact/friction uncertainty.

## Unsupported And Therefore Not Claimed

1. No claim of real-robot validation.
2. No claim of semantic perception accuracy.
3. No claim that SFC increases ordinary grasp success rate.
4. No claim of dynamic manipulation, compliance, rolling-contact, or trajectory-planning guarantees.
5. No claim of safety under uncalibrated or adversarial role labels.
