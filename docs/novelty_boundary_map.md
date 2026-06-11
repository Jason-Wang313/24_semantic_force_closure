# Novelty Boundary Map

## What Is Claimed

- A contact set is task-legal force closed only if the origin is in the convex hull of wrench generators whose contact roles are allowed by the task.
- Post-hoc semantic filtering is not equivalent to SFC because the best geometric witness may use forbidden contacts while another allowed-only witness may or may not exist.
- Semantic-only acceptance is weaker than SFC because having enough allowed contacts does not prove wrench balance.

## What Is Not Claimed

- No new perception model, language model, tactile sensor, contact estimator, or real-robot system is claimed.
- Classical force closure, convex hull feasibility, friction cones, and semantic grasping are treated as prior work.
- The paper does not claim that SFC alone solves trajectory optimization or object uncertainty.

## Closest Attacks

1. Classical force-closure and grasp-quality metrics: closest on mechanics, but not task-role deletion.
2. Semantic grasping and affordance grounding: closest on task meaning, but usually not a post-deletion certificate.
3. Contact semantic maps and dexterous grasp datasets: closest on representation, but they rank or label contacts rather than certify surviving wrench generators.
4. LMI and convex grasp analysis: closest mathematical tools, reused here rather than claimed as new.
