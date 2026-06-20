# Paper 24 Full-Scale Execution Plan

## 2026-06-20 Visual-Hardening Addendum

The final v3 manuscript was rebuilt with the explicit VLA role-model hyperref
policy for boxed links. The Downloads artifact remains 25 pages and is now:

- Path: `C:/Users/wangz/Downloads/24.pdf`
- Size: 369,669 bytes
- SHA256: `A96EB09B4F6204ED53597C519B982F941D8BA87DD200F98028042BB7E3B68097`
- Link-box inventory: green = 25, red = 9, cyan = 0, with one-point borders on
  all 34 link annotations.

## Current Claim

The current v2 paper argues that task semantics should enter the force-closure certificate itself. Semantic Force Closure (SFC) deletes task-forbidden contact-role wrench generators before checking convex-hull feasibility. This breaks the assumption that semantic grasping can rank or filter contacts outside the mechanical certificate.

The current evidence is useful but too small for the requested final standard:

- Main deterministic suite: 720 planar trials over six task families.
- Main result: geometric force closure succeeds in 100.0% of trials, while SFC succeeds in 65.4%, exposing a 34.6% geometric optimism gap.
- V2 role-label stress: at 10% role-label error, unsafe false certificates reach 30.7%; at 30% error, they reach 67.2%.
- Current manuscript is far below the 20+ page target and frames the result as workshop-only / strong-revise.

The v3 goal is to make this a final 25+ page synthetic mechanism paper with broad evidence, sharper certificate logic, stronger baselines, explicit uncertainty and negative controls, and a verified final PDF in Downloads.

## Main Gaps To Close

1. **Scale gap:** 720 main trials is too small. The v3 suite should reach at least 50,000 policy/certificate rows while staying RAM-light.
2. **Regime gap:** The current suite varies task family but not contact density, forbidden-contact geometry, friction, wrench-cone resolution, allowed-contact sparsity, object role topology, or semantic ambiguity.
3. **Baseline gap:** Current comparisons are geometric FC, SFC, semantic-only acceptance, and post-hoc filtering. V3 should add soft semantic penalties, top-k posthoc witnesses, risk-aware SFC, abstaining SFC, oracle true-role SFC, noisy-observed SFC, and all-allowed/all-forbidden controls.
4. **Uncertainty gap:** V2 shows label noise can create unsafe false certificates, but it does not test confidence thresholds, abstention, ambiguous roles, correlated errors, adversarial mislabels, or role-calibration curves.
5. **Ablation gap:** The mechanism mixes role deletion, pre-certificate ordering, witness legality, and convex-hull feasibility. These need to be separated.
6. **Negative-control gap:** The paper must show when SFC adds nothing: all contacts allowed, no forbidden roles, no force-closure geometry, random labels unrelated to contact mechanics, and tasks where every feasible witness is already legal.
7. **Writing gap:** The final manuscript needs formal definitions, proof sketches, algorithm boxes, certificate examples, family-by-family results, uncertainty analysis, limitations, deployment guardrails, reproducibility details, and a final audit.

## V3 Method Upgrade

Keep ordinary SFC as the central certificate, but add scoped variants:

- **Geometric FC:** ordinary force closure over all role generators.
- **Oracle SFC:** true task-role deletion before the certificate.
- **Observed SFC:** deletion using noisy observed role labels.
- **Risk-aware SFC:** deletion using role posterior probabilities; ambiguous contacts are removed unless confidence exceeds a threshold.
- **Abstaining SFC:** returns no certificate when role uncertainty is too high.
- **Soft-penalty FC:** allows forbidden-role generators but penalizes them in the witness objective.
- **Top-k posthoc FC:** searches multiple geometric witnesses and accepts if any witness is legal.
- **Semantic-only acceptance:** counts allowed contacts/roles without checking wrench balance.
- **Witness-oracle:** best legal witness under true labels and known contacts, used as an upper diagnostic reference.

The paper should not claim perception, tactile estimation, or dexterous planning novelty. It should claim certificate ordering and witness legality under task semantics.

## Experiment Families

### Family A: Full-Scale Task And Geometry Sweep

Purpose: scale the original result across object/task templates, contact density, allowed-contact sparsity, friction, and trap strength.

Variables:

- Object/task templates: knife pass, mug serve, phone pickup, spray use, apple pick, scissors pass, syringe handoff, pan carry, tablet pickup, flower cut.
- Contact density: sparse, medium, dense.
- Allowed-contact sparsity: low, medium, high.
- Trap strength: none, mild, strong, adversarial forbidden-contact spread.
- Friction coefficient band and cone facet count.

Expected honest outcome:

- Geometric FC should overestimate task-legal stability when forbidden contacts are mechanically attractive.
- SFC gains should shrink when all useful contacts are allowed or when allowed contacts are already well distributed.

### Family B: Semantic Noise, Ambiguity, And Calibration

Purpose: expand the v2 label-noise result into a calibrated uncertainty study.

Variables:

- Independent label error: 0%, 2%, 5%, 10%, 20%, 30%, 40%.
- Correlated object-part confusions: blade/handle, rim/body, screen/edge, nozzle/body.
- Role posterior confidence: calibrated, overconfident, underconfident, adversarial.
- Risk thresholds for risk-aware and abstaining SFC.

Metrics:

- Observed certificate rate.
- True-legal certificate rate.
- Unsafe false certificate rate.
- Abstention rate.
- Missed true SFC rate.

Expected honest outcome:

- Observed SFC can become unsafe as labels degrade.
- Risk-aware SFC should reduce unsafe false certificates at the cost of abstention and missed certificates.

### Family C: Witness Ordering And Post-Hoc Filtering

Purpose: test the core noncommutativity claim.

Variables:

- Number of geometric witnesses considered by post-hoc filtering.
- Soft penalty weight on forbidden roles.
- Legal witness rank among geometric candidates.
- Cases with legal alternative witnesses versus cases with no legal witness.

Expected honest outcome:

- Single-witness post-hoc filtering should miss many legal SFC witnesses.
- Top-k posthoc improves but can still fail or become expensive.
- SFC is the direct certificate because it removes illegal generators before feasibility.

### Family D: Friction, Cone Resolution, And Model Perturbation

Purpose: ensure the result is not an artifact of one friction setting or two cone rays.

Variables:

- Friction bands from low to high.
- Cone facets: 2, 4, 8.
- Contact position perturbation.
- Role-dependent friction shifts.
- Small wrench noise and torque scaling.

Expected honest outcome:

- Absolute rates vary with friction and discretization.
- The SFC-implies-geometric monotonicity check should remain exact when the same generator set is used.

### Family E: Ablations

Purpose: isolate the mechanism.

Ablations:

- Delete semantics before certificate (SFC).
- Filter the chosen geometric witness after certificate.
- Count semantics only.
- Penalize forbidden roles softly.
- Use all roles but report illegal witness.
- Remove task role taxonomy.
- Remove witness legality auditing.

Expected honest outcome:

- Semantic-only acceptance can be optimistic.
- Soft penalties depend on arbitrary weights.
- Witness audit is necessary because a geometric certificate can be feasible for the wrong reason.

### Family F: Negative Controls

Purpose: prevent overclaiming.

Controls:

- All roles allowed.
- No roles allowed.
- Random role labels independent of task.
- Symmetric role layouts where every geometric witness is legal.
- Geometrically infeasible contact clouds.
- Perfectly separated legal contacts with no forbidden-contact advantage.

Expected honest outcome:

- SFC advantage disappears when there is no semantic exclusion or no geometric feasibility.
- No roles allowed should not produce SFC certificates.
- All roles allowed should make SFC equal geometric FC.

### Family G: Counterexample Library And Certificate Audits

Purpose: produce concrete cases for the manuscript and reviewer response.

Outputs:

- Geometric FC but not SFC examples.
- Semantic-only accepted but not SFC examples.
- Post-hoc rejected but SFC legal-alternative examples.
- No legal witness examples.
- Unsafe observed-SFC examples under label noise.
- Exact monotonicity audit: SFC can never succeed if geometric FC fails under identical generator sets.

## RAM-Light Execution Strategy

- Run one family at a time.
- Stream row dictionaries directly to CSV files.
- Keep only aggregate counters and small example libraries in memory.
- Save `results/full_scale/progress.json` after every family.
- Use deterministic seeds and family-specific offsets.
- Prefer SciPy HiGHS LP feasibility and compact contact sets.
- Avoid multiprocessing unless needed; sequential execution is acceptable.
- Generate figures from summaries after all rows are written.

## Required Figures And Tables

Figures:

- Main SFC/geometric gap by task and trap strength.
- Unsafe false certificate versus label error and risk threshold.
- Top-k posthoc recovery curve.
- Friction/cone-resolution sensitivity.
- Negative-control outcomes.

Tables:

- Main full-scale benchmark.
- Semantic noise and risk-aware SFC table.
- Witness ordering/posthoc table.
- Friction/model perturbation table.
- Ablation table.
- Negative-control table.
- Claim-to-evidence map.

## Manuscript Expansion Strategy

The final manuscript must reach at least 25 pages from real content:

- Core paper: abstract, introduction, related work, problem setup, formal certificate definitions, algorithms, proof sketches, simulator, baselines, full-scale results, discussion, limitations.
- Appendices: LP details, contact-role templates, witness examples, noise calibration, top-k posthoc analysis, friction/cone sensitivity, ablations, negative controls, counterexamples, deployment guardrails, reproducibility, artifact manifest, and final audit.

No padding. Length should come from definitions, experiments, result ledgers, examples, and limitation analysis.

## Final Acceptance Checklist

Before moving to Paper 25:

- `docs/full_scale_execution_plan.md` exists and was written before v3 substantive edits.
- Full-scale experiment suite completes with deterministic metadata.
- Results include at least 50,000 policy/certificate rows.
- Manuscript builds locally to at least 25 pages.
- PDF text contains `v3 final full-scale`, row/case counts, headline metrics, role-noise failure, and no-real-robot limitation.
- Final PDF is copied to `C:/Users/wangz/Downloads/24.pdf`.
- Local `paper/main.pdf` is removed after export.
- Final PDF page count, byte count, and SHA256 are recorded in docs.
- README, child status, claims, evidence summary, experiment report, rigor checklist, final audit, hostile response, reproducibility checklist, reviewer attacks, attack log, readiness decision, version log, and validation report are updated.
- Repo is committed, pushed, clean, and `HEAD == @{u}` before Paper 25 begins.
