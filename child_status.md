# Child Status

Stage: manual recovery complete or in final publication steps

Current facts:
- Attempt 2 failed because the original simulator used an expensive nested force-closure enumeration and timed out before producing a PDF.
- Recovered without deleting the valid OpenAlex cache or related-work matrix.
- `docs/related_work_matrix.csv` has 1000 data rows.
- LP-based SFC simulator completed 720 trials with adversarial check passed: True.
- Downloads PDF exists: True.
- Desktop PDF status: pending orchestrator copy.
- GitHub URL/status: pending GitHub push.

Recovery steps:
- Stopped the orphaned long-running Python simulator.
- Replaced the certificate search with a bounded linear-program feasibility certificate using SciPy HiGHS.
- Regenerated results, synthesis docs, paper source, final audit, and build script.
