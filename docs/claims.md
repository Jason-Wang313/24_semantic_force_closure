# Claims

## Supported

- The local simulator ran 720 deterministic trials with zero SFC-implies-geometric-FC violations.
- Overall geometric FC rate is 100.0%, while SFC rate is 65.4%.
- The geometric optimism gap is 34.6% across the deterministic trial set.
- The evidence includes counterexample records and an adversarial monotonicity check.

## V2 Role-Noise Stress

- At 10% role-label error, true-legal observed SFC falls to 44.9% and unsafe false certificates rise to 30.7%.
- At 30% role-label error, unsafe false certificates rise to 67.2%.

## Plausible But Not Fully Proven

- SFC can be inserted into larger dexterous grasp planners as a certificate layer.
- Contact-role witnesses may improve debugging of task-oriented grasp proposals.

## Unsupported

- No hardware generalization, learned perception accuracy, or real-time whole-body planning claim is supported.
- No robustness to noisy semantic role labels is claimed without uncertainty-aware certification.
