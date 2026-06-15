# Experiment Rigor Checklist

- [x] Deterministic seed recorded: 24024.
- [x] V3 runner streams rows family-by-family.
- [x] Full-scale suite clears 50,000-row target: 75,520 rows.
- [x] Contact case count recorded: 12,032.
- [x] Plot generation recorded zero failures.
- [x] Main family tests task geometry, contact density, trap strength, and friction band.
- [x] Semantic-noise family tests label error, confidence mode, and risk threshold.
- [x] Witness-ordering family tests top-k posthoc budgets.
- [x] Friction/model family tests friction bands and cone facets.
- [x] Ablations separate SFC, semantic-only, posthoc, soft penalty, noisy deletion, and auditless geometric declarations.
- [x] Negative controls include all allowed, none allowed, random roles, no forbidden advantage, and geometrically infeasible clouds.
- [x] Counterexample library records concrete hostile cases.
- [x] Final PDF text was checked for v3 marker and headline values.
- [ ] No real robot validation.
- [ ] No learned perception model.
- [ ] No tactile verification.
- [ ] No 3D hand kinematics, dynamics, compliance, or trajectory optimization.

Decision: rigorous enough for a final synthetic certificate-ordering paper under scoped claims; not enough for hardware or general grasp-success claims.
