# Literature Map

Matrix rows: 1000. Serious skim tier: 300. Deep-read tier: 240. Hostile prior-work tier: 100.

## Top Ranked Works

1. 2023 | cites 85 | DexGraspNet: A Large-Scale Robotic Dexterous Grasp Dataset for General Objects Based on Simulation | arXiv (Cornell University)
2. 2026 | cites 0 | FSAG: Enhancing Human-to-Dexterous-Hand Finger-Specific Affordance Grounding via Diffusion Models | ArXiv.org
3. 2025 | cites 12 | Learning 6-DoF Fine-Grained Grasp Detection Based on Part Affordance Grounding | IEEE Transactions on Automation Science and Engineering
4. 2025 | cites 0 | ZeroDexGrasp: Zero-Shot Task-Oriented Dexterous Grasp Synthesis with Prompt-Based Multi-Stage Semantic Reasoning | ArXiv.org
5. 2009 | cites 7 | Grasp planning methodology for 3d arbitrary shaped objects | Dialnet (Universidad de la Rioja)
6. 2016 | cites 40 | Active vision for dexterous grasping of novel objects | venue unavailable
7. 2004 | cites 77 | On Quality Functions for Grasp Synthesis, Fixture Planning, and Coordinated Manipulation | IEEE Transactions on Automation Science and Engineering
8. 2024 | cites 32 | Robo-ABC: Affordance Generalization Beyond Categories via Semantic Correspondence for Robot Manipulation | Lecture notes in computer science
9. 1992 | cites 104 | Grasp Synthesis of Polygonal Objects Using a Three-Fingered Robot Hand | The International Journal of Robotics Research
10. 2026 | cites 0 | Visual-Tactile Grasp Dataset and Grasp Margin Matrix Analysis for Stability Evaluation | IEEE Transactions on Robotics
11. 2012 | cites 89 | Semantic grasping: Planning robotic grasps functionally suitable for an object manipulation task | venue unavailable
12. 2011 | cites 13 | Affordance based Part Recognition for Grasping and Manipulation | venue unavailable
13. 2026 | cites 0 | GenHand: generalised human grasp kinematic retargeting | npj Robotics
14. 2026 | cites 0 | AffordSim: A Scalable Data Generator and Benchmark for Affordance-Aware Robotic Manipulation | arXiv (Cornell University)
15. 2003 | cites 240 | Grasp analysis as linear matrix inequality problems | IEEE Transactions on Robotics and Automation
16. 2024 | cites 32 | Optimizing Contact Force on an Apple Picking Robot End-Effector | Agriculture
17. 2019 | cites 1 | Non-Planar Frictional Surface Contacts: Modeling and Application to Grasping. | arXiv (Cornell University)
18. 2024 | cites 2 | ContactDexNet: Multi-fingered Robotic Hand Grasping in Cluttered Environments through Hand-object Contact Semantic Mapping | arXiv (Cornell University)
19. 2018 | cites 2 | Dynamic Grasp Adaptation | venue unavailable
20. 2015 | cites 52 | Optimal grasp planning of multi-fingered robotic hands: a review | venue unavailable
21. 2012 | cites 25 | Estimating part tolerance bounds based on adaptive Cloud-based grasp planning with slip | venue unavailable
22. 2010 | cites 7 | Learning grasp stability based on haptic data | Chalmers Research (Chalmers University of Technology)
23. 2014 | cites 32 | Cloud-Based Grasp Analysis and Planning for Toleranced Parts Using Parallelized Monte Carlo Sampling | IEEE Transactions on Automation Science and Engineering
24. 2024 | cites 4 | TARS: Tactile Affordance in Robot Synesthesia for Dexterous Manipulation | IEEE Robotics and Automation Letters
25. 2011 | cites 50 | Part-based robot grasp planning from human demonstration | venue unavailable
26. 2023 | cites 8 | Harnessing the physical properties of objects for robotic grasping and manipulation | Aaltodoc (Aalto University)
27. 2021 | cites 11 | On-Orbit Robotic Grasping of a Spent Rocket Stage: Grasp Stability Analysis and Experimental Results | Frontiers in Robotics and AI
28. 2015 | cites 2 | A data-driven grasp planning method based on Gaussian Process Classifier | venue unavailable
29. 2020 | cites 10 | Grasp Planning Pipeline for Robust Manipulation of 3D Deformable Objects with Industrial Robotic Hand + Arm Systems | Applied Sciences
30. 2025 | cites 1 | Enhancing task-oriented robotic grasping via 3D affordance grounding from vision-language models | Complex & Intelligent Systems

## Hidden Assumptions Tested

- A force-closed grasp remains usable after task semantics remove illegal contacts.
- Post-hoc semantic filtering of a geometric grasp is equivalent to planning with semantic constraints.
- Part labels are only perception outputs, not variables inside the contact certificate.
- Forbidden contacts can be treated as high cost instead of deleted wrench generators.
- A grasp quality score is meaningful even when its best basis touches unsafe object regions.
- Functional grasping and force closure can be evaluated in separate modules.
- Learning a better grasp proposal distribution removes the need for a task-legal certificate.
- Semantic affordances are binary labels rather than role-conditioned wrench cones.
- Robustness to friction uncertainty covers robustness to forbidden contact roles.
- Task success is dominated by object geometry, not by which part is legally touched.
- A single best geometric basis is an adequate witness for downstream manipulation.
- Tactile checks after closure can repair an illegal contact choice without replanning.
- Dexterous grasp datasets encode task legality strongly enough for certificate-level reasoning.
- Foundation models can rank grasps but need not expose their contact-role witnesses.
- Object part recognition is only a preprocessing step.
- All contacts on a rigid object share the same semantic status for a task.
- A handle, blade, rim, screen, nozzle, stem, or tip can be represented only as a mask.
- SFC failure is rare when geometric FC succeeds.
- The grasp planner can ignore which wrench generators survive semantic deletion.
- Formal force-closure checks are too slow to use after semantic filtering.
- Counterexamples to post-hoc filtering are corner cases rather than design signals.

## Landscape Synthesis

The landscape joins classical grasp quality, linear-matrix inequality grasp analysis, semantic grasping, affordance-based part recognition, dexterous grasp datasets, contact semantic maps, and recent foundation-model task-oriented grasping. The common gap is that semantics usually rank or mask grasp candidates before or after a geometric force-closure calculation. This paper moves semantics into the certificate itself: delete illegal role-conditioned wrench generators first, then ask whether the origin remains in their convex hull.

## Selected Direction

Semantic Force Closure (SFC) is the chosen mechanism. It is not a new perception model or a new dataset; it is a task-conditioned contact certificate. The evidence is deliberately small and exact enough to expose failure modes: post-hoc filtering and semantic-only acceptance both certify some grasps that are not task-legal force-closed grasps.
