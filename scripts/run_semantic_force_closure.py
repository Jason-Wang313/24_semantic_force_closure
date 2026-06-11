#!/usr/bin/env python3
"""Run deterministic evidence for Semantic Force Closure (SFC).

The simulator is deliberately modest: planar rigid-body contacts with
linearized friction cones. That makes the central question testable without
hiding behind large learned models: does a grasp remain force-closed after the
task's semantic contact-role constraints delete forbidden wrench generators?
"""

from __future__ import annotations

import csv
import itertools
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.optimize import linprog


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"
STATUS = ROOT / "child_status.md"

SEED = 24024
TRIALS_PER_SCENARIO = 120


@dataclass(frozen=True)
class Contact:
    x: float
    y: float
    role: str
    mu: float


@dataclass
class Certificate:
    feasible: bool
    quality: float = 0.0
    contacts: tuple[int, ...] = ()
    roles: tuple[str, ...] = ()
    lambdas: tuple[float, ...] = ()


SCENARIOS = {
    "knife_pass": {
        "allowed": {"handle", "pommel"},
        "forbidden": {"blade", "edge"},
        "role_arcs": {
            "handle": (145, 215, 4),
            "pommel": (210, 245, 2),
            "blade": (-25, 35, 4),
            "edge": (35, 75, 2),
        },
        "trap_probability": 0.50,
    },
    "mug_serve": {
        "allowed": {"handle", "body", "base"},
        "forbidden": {"rim", "interior"},
        "role_arcs": {
            "handle": (135, 225, 3),
            "body": (-45, 45, 3),
            "base": (235, 305, 2),
            "rim": (60, 120, 3),
            "interior": (85, 140, 1),
        },
        "trap_probability": 0.35,
    },
    "phone_pick": {
        "allowed": {"left_edge", "right_edge", "back_edge"},
        "forbidden": {"screen", "camera"},
        "role_arcs": {
            "left_edge": (160, 200, 2),
            "right_edge": (-20, 20, 2),
            "back_edge": (245, 295, 2),
            "screen": (60, 120, 4),
            "camera": (120, 150, 1),
        },
        "trap_probability": 0.25,
    },
    "spray_bottle_use": {
        "allowed": {"body", "neck"},
        "forbidden": {"trigger", "nozzle"},
        "role_arcs": {
            "body": (195, 345, 5),
            "neck": (130, 170, 2),
            "trigger": (35, 75, 2),
            "nozzle": (-15, 25, 3),
        },
        "trap_probability": 0.40,
    },
    "apple_pick": {
        "allowed": {"body", "equator"},
        "forbidden": {"stem", "bruise"},
        "role_arcs": {
            "body": (190, 340, 4),
            "equator": (-20, 40, 2),
            "stem": (70, 110, 3),
            "bruise": (115, 150, 1),
        },
        "trap_probability": 0.35,
    },
    "scissors_pass": {
        "allowed": {"handle_loop", "pivot"},
        "forbidden": {"blade", "tip"},
        "role_arcs": {
            "handle_loop": (145, 225, 4),
            "pivot": (105, 135, 1),
            "blade": (-30, 45, 4),
            "tip": (45, 70, 1),
        },
        "trap_probability": 0.45,
    },
}


def append_status(stage: str, line: str) -> None:
    try:
        text = STATUS.read_text(encoding="utf-8") if STATUS.exists() else "# Child Status\n"
        STATUS.write_text(text.rstrip() + f"\n\nUpdate: {stage}\n- {line}\n", encoding="utf-8")
    except Exception:
        pass


def unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n < 1e-12:
        return v
    return v / n


def contact_wrench_generators(contact: Contact) -> np.ndarray:
    p = np.array([contact.x, contact.y], dtype=float)
    inward = unit(-p)
    tangent = np.array([-inward[1], inward[0]], dtype=float)
    forces = [unit(inward + contact.mu * tangent), unit(inward - contact.mu * tangent)]
    wrenches = []
    for force in forces:
        torque = contact.x * force[1] - contact.y * force[0]
        wrenches.append([force[0], force[1], torque])
    return np.array(wrenches, dtype=float)


def origin_in_hull(wrenches: np.ndarray, tol: float = 1e-7) -> tuple[bool, float, tuple[float, ...]]:
    if wrenches.shape[0] < 4:
        return False, 0.0, ()
    if np.linalg.matrix_rank(wrenches.T, tol=1e-8) < 3:
        return False, 0.0, ()
    matrix = np.vstack([wrenches.T, np.ones((1, wrenches.shape[0]))])
    target = np.array([0.0, 0.0, 0.0, 1.0])
    best_quality = 0.0
    best_lambda: tuple[float, ...] = ()
    for combo in itertools.combinations(range(wrenches.shape[0]), 4):
        sub = matrix[:, combo]
        try:
            lambdas = np.linalg.solve(sub, target)
        except np.linalg.LinAlgError:
            continue
        residual = float(np.linalg.norm(sub @ lambdas - target))
        if residual <= tol and np.all(lambdas >= -tol):
            min_lambda = max(0.0, float(np.min(lambdas)))
            singular = float(np.linalg.svd(wrenches[list(combo)].T, compute_uv=False)[-1])
            quality = min_lambda * singular
            if quality > best_quality:
                best_quality = quality
                best_lambda = tuple(float(x) for x in lambdas)
    return best_quality > 1e-10, best_quality, best_lambda


def force_closure_certificate(contacts: list[Contact], candidate_indices: Iterable[int]) -> Certificate:
    entries: list[tuple[int, str, np.ndarray]] = []
    for idx in candidate_indices:
        for wrench in contact_wrench_generators(contacts[idx]):
            entries.append((idx, contacts[idx].role, wrench))

    if len(entries) < 4:
        return Certificate(False)

    wrenches = np.array([entry[2] for entry in entries], dtype=float)
    if np.linalg.matrix_rank(wrenches.T, tol=1e-8) < 3:
        return Certificate(False)

    n = wrenches.shape[0]
    c = np.zeros(n + 1)
    c[-1] = -1.0
    a_eq = np.zeros((4, n + 1))
    a_eq[:3, :n] = wrenches.T
    a_eq[3, :n] = 1.0
    b_eq = np.array([0.0, 0.0, 0.0, 1.0])
    a_ub = np.zeros((n, n + 1))
    for row in range(n):
        a_ub[row, row] = -1.0
        a_ub[row, -1] = 1.0

    result = linprog(
        c,
        A_ub=a_ub,
        b_ub=np.zeros(n),
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=[(0.0, None)] * n + [(0.0, None)],
        method="highs",
    )
    if not result.success or result.x is None:
        return Certificate(False)

    lambdas = np.asarray(result.x[:n], dtype=float)
    quality = max(0.0, float(result.x[-1]))
    active = [i for i, value in enumerate(lambdas) if value > max(1e-7, quality * 0.05)]
    if not active:
        active = [int(np.argmax(lambdas))]
    contact_ids = tuple(sorted({entries[i][0] for i in active}))
    roles = tuple(contacts[i].role for i in contact_ids)
    return Certificate(
        feasible=True,
        quality=quality,
        contacts=contact_ids,
        roles=roles,
        lambdas=tuple(float(lambdas[i]) for i in active),
    )


def sample_angle(rng: random.Random, lo_deg: float, hi_deg: float, trap_bias: bool) -> float:
    lo = math.radians(lo_deg)
    hi = math.radians(hi_deg)
    if trap_bias:
        center = (lo + hi) / 2.0
        width = max(0.01, (hi - lo) / 7.0)
        return max(lo, min(hi, rng.gauss(center, width)))
    return rng.uniform(lo, hi)


def generate_contacts(rng: random.Random, scenario: dict[str, object]) -> list[Contact]:
    role_arcs = scenario["role_arcs"]
    trap = rng.random() < float(scenario["trap_probability"])
    contacts: list[Contact] = []
    for role, spec in role_arcs.items():
        lo, hi, count = spec
        for _ in range(int(count)):
            role_allowed = role in scenario["allowed"]
            # In trap cases, allowed contacts become more clustered while
            # forbidden contacts stay well spread and mechanically attractive.
            angle = sample_angle(rng, float(lo), float(hi), trap and role_allowed)
            radius = rng.uniform(0.78, 1.10)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            base_mu = rng.uniform(0.45, 0.95)
            if trap and not role_allowed:
                base_mu += rng.uniform(0.15, 0.35)
            contacts.append(Contact(x=x, y=y, role=str(role), mu=min(1.35, base_mu)))
    rng.shuffle(contacts)
    return contacts


def semantic_only_accepts(contacts: list[Contact], allowed: set[str]) -> bool:
    allowed_contacts = [c for c in contacts if c.role in allowed]
    if len(allowed_contacts) < 2:
        return False
    roles = {c.role for c in allowed_contacts}
    return len(roles) >= 1


def run_trial(rng: random.Random, scenario_name: str, trial_id: int) -> dict[str, object]:
    scenario = SCENARIOS[scenario_name]
    allowed = set(scenario["allowed"])
    contacts = generate_contacts(rng, scenario)
    all_indices = list(range(len(contacts)))
    allowed_indices = [idx for idx, c in enumerate(contacts) if c.role in allowed]

    geometric = force_closure_certificate(contacts, all_indices)
    sfc = force_closure_certificate(contacts, allowed_indices)
    semantic_only = semantic_only_accepts(contacts, allowed)
    posthoc = geometric.feasible and all(role in allowed for role in geometric.roles)

    return {
        "scenario": scenario_name,
        "trial_id": trial_id,
        "num_contacts": len(contacts),
        "num_allowed_contacts": len(allowed_indices),
        "geometric_fc": int(geometric.feasible),
        "semantic_force_closure": int(sfc.feasible),
        "semantic_only_accepts": int(semantic_only),
        "posthoc_best_geometric_accepts": int(posthoc),
        "geometric_quality": round(geometric.quality, 8),
        "sfc_quality": round(sfc.quality, 8),
        "geometric_roles": "|".join(geometric.roles),
        "sfc_roles": "|".join(sfc.roles),
        "geometric_optimism_gap": int(geometric.feasible and not sfc.feasible),
        "semantic_optimism_gap": int(semantic_only and not sfc.feasible),
        "posthoc_miss": int(sfc.feasible and not posthoc),
        "monotonicity_violation": int(sfc.feasible and not geometric.feasible),
    }


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    summary: dict[str, object] = {
        "seed": SEED,
        "trials_per_scenario": TRIALS_PER_SCENARIO,
        "total_trials": len(rows),
        "scenarios": {},
    }
    metrics = [
        "geometric_fc",
        "semantic_force_closure",
        "semantic_only_accepts",
        "posthoc_best_geometric_accepts",
        "geometric_optimism_gap",
        "semantic_optimism_gap",
        "posthoc_miss",
        "monotonicity_violation",
    ]
    for scenario in SCENARIOS:
        subset = [r for r in rows if r["scenario"] == scenario]
        item = {"n": len(subset)}
        for metric in metrics:
            count = int(sum(int(r[metric]) for r in subset))
            item[metric + "_count"] = count
            item[metric + "_rate"] = round(count / max(1, len(subset)), 4)
        sfc_qualities = [float(r["sfc_quality"]) for r in subset if int(r["semantic_force_closure"])]
        item["mean_sfc_quality_when_feasible"] = round(float(np.mean(sfc_qualities)), 6) if sfc_qualities else 0.0
        summary["scenarios"][scenario] = item
    for metric in metrics:
        count = int(sum(int(r[metric]) for r in rows))
        summary[metric + "_count"] = count
        summary[metric + "_rate"] = round(count / max(1, len(rows)), 4)
    return summary


def write_latex_table(summary: dict[str, object]) -> None:
    path = PAPER / "results_table.tex"
    PAPER.mkdir(exist_ok=True)
    lines = [
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Scenario & FC any & SFC & FC-not-SFC & Posthoc miss \\\\",
        "\\midrule",
    ]
    for scenario, item in summary["scenarios"].items():
        label = scenario.replace("_", "\\_")
        lines.append(
            f"{label} & "
            f"{100 * item['geometric_fc_rate']:.1f} & "
            f"{100 * item['semantic_force_closure_rate']:.1f} & "
            f"{100 * item['geometric_optimism_gap_rate']:.1f} & "
            f"{100 * item['posthoc_miss_rate']:.1f} \\\\"
        )
    lines.extend(
        [
            "\\midrule",
            f"All & {100 * summary['geometric_fc_rate']:.1f} & "
            f"{100 * summary['semantic_force_closure_rate']:.1f} & "
            f"{100 * summary['geometric_optimism_gap_rate']:.1f} & "
            f"{100 * summary['posthoc_miss_rate']:.1f} \\\\",
            "\\bottomrule",
            "\\end{tabular}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_counterexamples(rows: list[dict[str, object]]) -> None:
    examples = {
        "geometric_force_closed_but_not_sfc": None,
        "semantic_only_accepts_but_not_sfc": None,
        "posthoc_rejects_but_sfc_finds_alternative": None,
    }
    for row in rows:
        if examples["geometric_force_closed_but_not_sfc"] is None and int(row["geometric_optimism_gap"]):
            examples["geometric_force_closed_but_not_sfc"] = row
        if examples["semantic_only_accepts_but_not_sfc"] is None and int(row["semantic_optimism_gap"]):
            examples["semantic_only_accepts_but_not_sfc"] = row
        if examples["posthoc_rejects_but_sfc_finds_alternative"] is None and int(row["posthoc_miss"]):
            examples["posthoc_rejects_but_sfc_finds_alternative"] = row
    (RESULTS / "counterexamples.json").write_text(
        json.dumps(examples, indent=2, ensure_ascii=True), encoding="utf-8"
    )


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    rng = random.Random(SEED)
    rows: list[dict[str, object]] = []
    for scenario in SCENARIOS:
        print(f"scenario={scenario}", flush=True)
        for trial in range(TRIALS_PER_SCENARIO):
            rows.append(run_trial(rng, scenario, trial))

    trials_path = RESULTS / "semantic_force_closure_trials.csv"
    with trials_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = summarize(rows)
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
    checks = {
        "sfc_implies_geometric_fc_violations": summary["monotonicity_violation_count"],
        "all_trials": len(rows),
        "passed": summary["monotonicity_violation_count"] == 0,
    }
    (RESULTS / "adversarial_checks.json").write_text(
        json.dumps(checks, indent=2, ensure_ascii=True), encoding="utf-8"
    )
    write_counterexamples(rows)
    write_latex_table(summary)
    append_status(
        "experiments",
        "Ran deterministic SFC simulator; wrote trials CSV, summary, counterexamples, adversarial checks, LaTeX table.",
    )
    print(json.dumps(summary, indent=2), flush=True)
    print(json.dumps(checks, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
