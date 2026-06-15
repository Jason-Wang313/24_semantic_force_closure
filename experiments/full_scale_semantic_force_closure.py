#!/usr/bin/env python3
"""Full-scale RAM-light evidence for Semantic Force Closure.

The runner keeps the mechanism intentionally small: planar contact wrenches,
linearized friction cones, and LP-based convex-hull certificates.  The scale
comes from sweeping task roles, contact geometry, semantic noise, witness
ordering, perturbations, ablations, and negative controls.
"""

from __future__ import annotations

import csv
import json
import math
import random
import shutil
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np
from scipy.optimize import linprog

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - plotting is optional in CI
    plt = None


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "full_scale"
FIGURES = ROOT / "figures" / "full_scale"
TEX = RESULTS / "tex"
DOCS = ROOT / "docs"

SEED = 24024


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
    active_generator_count: int = 0


TASKS: dict[str, dict[str, object]] = {
    "knife_pass": {
        "allowed": {"handle", "pommel"},
        "forbidden": {"blade", "edge"},
        "role_arcs": {
            "handle": (145, 215, 4),
            "pommel": (210, 245, 2),
            "blade": (-25, 35, 4),
            "edge": (35, 75, 2),
        },
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
    },
    "syringe_handoff": {
        "allowed": {"barrel", "flange"},
        "forbidden": {"needle", "plunger"},
        "role_arcs": {
            "barrel": (150, 230, 4),
            "flange": (225, 260, 2),
            "needle": (-20, 30, 3),
            "plunger": (55, 95, 2),
        },
    },
    "pan_carry": {
        "allowed": {"handle", "sidewall"},
        "forbidden": {"hot_base", "rim"},
        "role_arcs": {
            "handle": (155, 225, 4),
            "sidewall": (250, 310, 3),
            "hot_base": (-35, 40, 4),
            "rim": (55, 115, 3),
        },
    },
    "tablet_pickup": {
        "allowed": {"edge", "back"},
        "forbidden": {"screen", "camera"},
        "role_arcs": {
            "edge": (150, 210, 3),
            "back": (235, 305, 3),
            "screen": (-30, 45, 4),
            "camera": (80, 120, 1),
        },
    },
    "flower_cut": {
        "allowed": {"stem_lower", "guarded_handle"},
        "forbidden": {"petal", "bud", "blade_path"},
        "role_arcs": {
            "stem_lower": (160, 220, 3),
            "guarded_handle": (230, 275, 2),
            "petal": (-10, 40, 3),
            "bud": (50, 90, 2),
            "blade_path": (95, 135, 2),
        },
    },
}

TASK_NAMES = list(TASKS)
FIELDNAMES = [
    "family",
    "case_id",
    "task",
    "method",
    "accepted",
    "true_legal_certificate",
    "unsafe_false_certificate",
    "missed_true_sfc",
    "geometric_feasible",
    "oracle_sfc_feasible",
    "quality",
    "num_contacts",
    "num_true_allowed",
    "num_observed_allowed",
    "density",
    "allowed_sparsity",
    "trap_strength",
    "friction_band",
    "facets",
    "role_error_rate",
    "confidence_mode",
    "risk_threshold",
    "topk_budget",
    "control",
    "condition",
    "seed",
]


class Aggregator:
    def __init__(self, keys: Iterable[str]):
        self.keys = tuple(keys)
        self.data: dict[tuple[object, ...], dict[str, float]] = defaultdict(
            lambda: {
                "rows": 0.0,
                "accepted": 0.0,
                "true_legal": 0.0,
                "unsafe": 0.0,
                "missed": 0.0,
                "geometric_feasible": 0.0,
                "oracle_sfc_feasible": 0.0,
                "quality_sum": 0.0,
                "quality_count": 0.0,
            }
        )

    def update(self, row: dict[str, object]) -> None:
        key = tuple(row.get(k, "") for k in self.keys)
        item = self.data[key]
        item["rows"] += 1
        item["accepted"] += int(row["accepted"])
        item["true_legal"] += int(row["true_legal_certificate"])
        item["unsafe"] += int(row["unsafe_false_certificate"])
        item["missed"] += int(row["missed_true_sfc"])
        item["geometric_feasible"] += int(row["geometric_feasible"])
        item["oracle_sfc_feasible"] += int(row["oracle_sfc_feasible"])
        quality = float(row["quality"])
        if quality > 0:
            item["quality_sum"] += quality
            item["quality_count"] += 1

    def rows(self) -> list[dict[str, object]]:
        out: list[dict[str, object]] = []
        for key, item in sorted(self.data.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
            n = max(1.0, item["rows"])
            qn = max(1.0, item["quality_count"])
            row = {name: value for name, value in zip(self.keys, key)}
            row.update(
                {
                    "rows": int(item["rows"]),
                    "accepted_rate": round(item["accepted"] / n, 4),
                    "true_legal_rate": round(item["true_legal"] / n, 4),
                    "unsafe_rate": round(item["unsafe"] / n, 4),
                    "missed_true_sfc_rate": round(item["missed"] / n, 4),
                    "geometric_feasible_rate": round(item["geometric_feasible"] / n, 4),
                    "oracle_sfc_feasible_rate": round(item["oracle_sfc_feasible"] / n, 4),
                    "mean_quality_when_feasible": round(item["quality_sum"] / qn, 6)
                    if item["quality_count"]
                    else 0.0,
                }
            )
            out.append(row)
        return out


def ensure_dirs() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    TEX.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)


def unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v if n < 1e-12 else v / n


def contact_wrench_generators(contact: Contact, facets: int) -> list[np.ndarray]:
    p = np.array([contact.x, contact.y], dtype=float)
    inward = unit(-p)
    tangent = np.array([-inward[1], inward[0]], dtype=float)
    count = max(2, int(facets))
    slopes = np.linspace(-contact.mu, contact.mu, count)
    wrenches = []
    for slope in slopes:
        force = unit(inward + float(slope) * tangent)
        torque = contact.x * force[1] - contact.y * force[0]
        wrenches.append(np.array([force[0], force[1], torque], dtype=float))
    return wrenches


def force_closure_certificate(
    contacts: list[Contact],
    candidate_indices: Iterable[int],
    facets: int = 2,
) -> Certificate:
    entries: list[tuple[int, str, np.ndarray]] = []
    seen = sorted({int(idx) for idx in candidate_indices if 0 <= int(idx) < len(contacts)})
    for idx in seen:
        for wrench in contact_wrench_generators(contacts[idx], facets):
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
    if not active and float(np.max(lambdas)) > 1e-9:
        active = [int(np.argmax(lambdas))]
    if not active or quality <= 1e-10:
        return Certificate(False)
    contact_ids = tuple(sorted({entries[i][0] for i in active}))
    roles = tuple(contacts[i].role for i in contact_ids)
    return Certificate(True, quality, contact_ids, roles, len(active))


def angle_sample(rng: random.Random, lo_deg: float, hi_deg: float, cluster: float) -> float:
    lo = math.radians(lo_deg)
    hi = math.radians(hi_deg)
    if cluster <= 0:
        return rng.uniform(lo, hi)
    center = (lo + hi) / 2.0
    width = max(0.01, (hi - lo) / (4.0 + 8.0 * cluster))
    return max(lo, min(hi, rng.gauss(center, width)))


def generate_contacts(
    rng: random.Random,
    task_name: str,
    density: str = "medium",
    allowed_sparsity: str = "medium",
    trap_strength: float = 0.5,
    friction_band: str = "medium",
    control: str = "none",
) -> tuple[list[Contact], set[str]]:
    task = TASKS[task_name]
    allowed = set(task["allowed"])
    forbidden = set(task["forbidden"])
    if control == "all_allowed":
        allowed = set(task["role_arcs"].keys())
    elif control == "none_allowed":
        allowed = set()
    elif control == "no_forbidden_advantage":
        trap_strength = 0.0
    role_arcs = task["role_arcs"]
    density_scale = {"sparse": 0.75, "medium": 1.0, "dense": 1.35}[density]
    allowed_scale = {"low": 1.25, "medium": 1.0, "high": 0.62}[allowed_sparsity]
    mu_ranges = {
        "low": (0.25, 0.55),
        "medium": (0.45, 0.95),
        "high": (0.75, 1.35),
        "mixed": (0.30, 1.25),
    }
    mu_lo, mu_hi = mu_ranges[friction_band]
    contacts: list[Contact] = []
    for role, spec in role_arcs.items():
        lo, hi, base_count = spec
        role_allowed = role in allowed
        scale = density_scale * (allowed_scale if role_allowed else 1.0)
        count = max(1, int(round(int(base_count) * scale)))
        for _ in range(count):
            cluster = trap_strength if role_allowed else max(0.0, 0.25 - 0.15 * trap_strength)
            angle = angle_sample(rng, float(lo), float(hi), cluster)
            radius = rng.uniform(0.78, 1.12)
            mu = rng.uniform(mu_lo, mu_hi)
            if role not in allowed and control != "no_forbidden_advantage":
                mu = min(1.5, mu + rng.uniform(0.02, 0.25) * trap_strength)
            if role in allowed and trap_strength > 0:
                mu = max(0.15, mu - rng.uniform(0.0, 0.18) * trap_strength)
            contacts.append(Contact(radius * math.cos(angle), radius * math.sin(angle), str(role), mu))
    if control == "geometrically_infeasible":
        contacts = [
            Contact(abs(c.x), 0.25 * c.y + 0.15 * rng.uniform(-1, 1), c.role, min(c.mu, 0.35))
            for c in contacts[: max(4, len(contacts) // 2)]
        ]
    elif control == "random_roles":
        roles = list(role_arcs.keys())
        contacts = [Contact(c.x, c.y, rng.choice(roles), c.mu) for c in contacts]
    rng.shuffle(contacts)
    return contacts, allowed


def true_allowed_indices(contacts: list[Contact], allowed: set[str]) -> list[int]:
    return [idx for idx, contact in enumerate(contacts) if contact.role in allowed]


def witness_legal(cert: Certificate, contacts: list[Contact], allowed: set[str]) -> bool:
    return cert.feasible and all(contacts[idx].role in allowed for idx in cert.contacts)


def semantic_only_accepts(contacts: list[Contact], allowed: set[str]) -> bool:
    allowed_contacts = [c for c in contacts if c.role in allowed]
    return len(allowed_contacts) >= 3 and len({c.role for c in allowed_contacts}) >= 1


def corrupt_roles(
    contacts: list[Contact],
    allowed: set[str],
    task_name: str,
    rng: random.Random,
    error_rate: float,
    confidence_mode: str,
) -> tuple[list[str], list[float]]:
    roles = list(TASKS[task_name]["role_arcs"].keys())
    allowed_roles = list(allowed) or roles
    forbidden_roles = [r for r in roles if r not in allowed]
    observed: list[str] = []
    confidence: list[float] = []
    for contact in contacts:
        role = contact.role
        corrupted = rng.random() < error_rate
        if corrupted:
            if confidence_mode == "correlated":
                pool = forbidden_roles if role in allowed and forbidden_roles else allowed_roles
            else:
                pool = [candidate for candidate in roles if candidate != role]
            role = rng.choice(pool) if pool else role
        observed.append(role)
        if confidence_mode == "overconfident":
            conf = rng.uniform(0.82, 0.98) if corrupted else rng.uniform(0.88, 0.995)
        elif confidence_mode == "underconfident":
            conf = rng.uniform(0.42, 0.72) if corrupted else rng.uniform(0.55, 0.82)
        elif confidence_mode == "adversarial":
            conf = rng.uniform(0.88, 0.995) if corrupted else rng.uniform(0.48, 0.78)
        else:
            conf = rng.uniform(0.15, 0.55) if corrupted else rng.uniform(0.72, 0.98)
        confidence.append(round(conf, 4))
    return observed, confidence


def observed_allowed_indices(observed_roles: list[str], allowed: set[str]) -> list[int]:
    return [idx for idx, role in enumerate(observed_roles) if role in allowed]


def risk_allowed_indices(observed_roles: list[str], confidence: list[float], allowed: set[str], threshold: float) -> list[int]:
    return [idx for idx, role in enumerate(observed_roles) if role in allowed and confidence[idx] >= threshold]


def make_row(
    family: str,
    case_id: str,
    task: str,
    method: str,
    accepted: bool,
    true_legal: bool,
    cert: Certificate,
    contacts: list[Contact],
    allowed: set[str],
    geometric: Certificate,
    oracle: Certificate,
    params: dict[str, object],
) -> dict[str, object]:
    unsafe = bool(accepted and not true_legal)
    missed = bool(oracle.feasible and not true_legal)
    return {
        "family": family,
        "case_id": case_id,
        "task": task,
        "method": method,
        "accepted": int(accepted),
        "true_legal_certificate": int(true_legal),
        "unsafe_false_certificate": int(unsafe),
        "missed_true_sfc": int(missed),
        "geometric_feasible": int(geometric.feasible),
        "oracle_sfc_feasible": int(oracle.feasible),
        "quality": round(float(cert.quality), 8) if cert.feasible else 0.0,
        "num_contacts": len(contacts),
        "num_true_allowed": len(true_allowed_indices(contacts, allowed)),
        "num_observed_allowed": int(params.get("num_observed_allowed", -1)),
        "density": params.get("density", ""),
        "allowed_sparsity": params.get("allowed_sparsity", ""),
        "trap_strength": params.get("trap_strength", ""),
        "friction_band": params.get("friction_band", ""),
        "facets": params.get("facets", ""),
        "role_error_rate": params.get("role_error_rate", ""),
        "confidence_mode": params.get("confidence_mode", ""),
        "risk_threshold": params.get("risk_threshold", ""),
        "topk_budget": params.get("topk_budget", ""),
        "control": params.get("control", ""),
        "condition": params.get("condition", ""),
        "seed": params.get("seed", ""),
    }


def base_method_rows(
    family: str,
    case_id: str,
    task: str,
    contacts: list[Contact],
    allowed: set[str],
    facets: int,
    params: dict[str, object],
    include_noise: bool = False,
    error_rate: float = 0.0,
    confidence_mode: str = "calibrated",
    risk_threshold: float = 0.7,
    rng: random.Random | None = None,
) -> list[dict[str, object]]:
    all_indices = list(range(len(contacts)))
    true_indices = true_allowed_indices(contacts, allowed)
    geometric = force_closure_certificate(contacts, all_indices, facets)
    oracle = force_closure_certificate(contacts, true_indices, facets)
    rows: list[dict[str, object]] = []
    p = dict(params)
    p.setdefault("num_observed_allowed", -1)

    rows.append(
        make_row(
            family,
            case_id,
            task,
            "geometric_fc",
            geometric.feasible,
            witness_legal(geometric, contacts, allowed),
            geometric,
            contacts,
            allowed,
            geometric,
            oracle,
            p,
        )
    )
    rows.append(
        make_row(
            family,
            case_id,
            task,
            "oracle_sfc",
            oracle.feasible,
            oracle.feasible,
            oracle,
            contacts,
            allowed,
            geometric,
            oracle,
            p,
        )
    )
    semantic_accept = semantic_only_accepts(contacts, allowed)
    rows.append(
        make_row(
            family,
            case_id,
            task,
            "semantic_only",
            semantic_accept,
            bool(semantic_accept and oracle.feasible),
            Certificate(bool(semantic_accept), 0.0),
            contacts,
            allowed,
            geometric,
            oracle,
            p,
        )
    )
    rows.append(
        make_row(
            family,
            case_id,
            task,
            "posthoc_single",
            geometric.feasible and witness_legal(geometric, contacts, allowed),
            geometric.feasible and witness_legal(geometric, contacts, allowed),
            geometric,
            contacts,
            allowed,
            geometric,
            oracle,
            p,
        )
    )
    illegal_share = 0.0
    if geometric.feasible and geometric.contacts:
        illegal_share = sum(1 for idx in geometric.contacts if contacts[idx].role not in allowed) / len(geometric.contacts)
    soft_accept = geometric.feasible and (geometric.quality - 0.03 * illegal_share) > 1e-8
    rows.append(
        make_row(
            family,
            case_id,
            task,
            "soft_penalty_fc",
            soft_accept,
            bool(soft_accept and witness_legal(geometric, contacts, allowed)),
            geometric,
            contacts,
            allowed,
            geometric,
            oracle,
            p,
        )
    )

    if include_noise:
        assert rng is not None
        observed, confidence = corrupt_roles(contacts, allowed, task, rng, error_rate, confidence_mode)
        obs_indices = observed_allowed_indices(observed, allowed)
        risk_indices = risk_allowed_indices(observed, confidence, allowed, risk_threshold)
        observed_cert = force_closure_certificate(contacts, obs_indices, facets)
        risk_cert = force_closure_certificate(contacts, risk_indices, facets)
        p_obs = dict(p)
        p_obs.update(
            {
                "num_observed_allowed": len(obs_indices),
                "role_error_rate": error_rate,
                "confidence_mode": confidence_mode,
                "risk_threshold": risk_threshold,
            }
        )
        rows.append(
            make_row(
                family,
                case_id,
                task,
                "observed_sfc",
                observed_cert.feasible,
                witness_legal(observed_cert, contacts, allowed),
                observed_cert,
                contacts,
                allowed,
                geometric,
                oracle,
                p_obs,
            )
        )
        rows.append(
            make_row(
                family,
                case_id,
                task,
                "risk_aware_sfc",
                risk_cert.feasible,
                witness_legal(risk_cert, contacts, allowed),
                risk_cert,
                contacts,
                allowed,
                geometric,
                oracle,
                p_obs,
            )
        )
        low_conf_allowed = any(role in allowed and conf < risk_threshold for role, conf in zip(observed, confidence))
        abstain = low_conf_allowed and confidence_mode in {"calibrated", "underconfident", "adversarial"}
        accepted = (not abstain) and risk_cert.feasible
        true_legal = accepted and witness_legal(risk_cert, contacts, allowed)
        rows.append(
            make_row(
                family,
                case_id,
                task,
                "abstaining_sfc",
                accepted,
                true_legal,
                risk_cert if not abstain else Certificate(False),
                contacts,
                allowed,
                geometric,
                oracle,
                p_obs,
            )
        )
    return rows


def topk_posthoc(
    contacts: list[Contact],
    allowed: set[str],
    facets: int,
    budget: int,
    rng: random.Random,
) -> Certificate:
    all_indices = list(range(len(contacts)))
    geometric = force_closure_certificate(contacts, all_indices, facets)
    if witness_legal(geometric, contacts, allowed):
        return geometric
    if budget <= 1:
        return Certificate(False)
    allowed_indices = true_allowed_indices(contacts, allowed)
    attempts = 1
    forbidden = [idx for idx, c in enumerate(contacts) if c.role not in allowed]
    while attempts < budget:
        attempts += 1
        if attempts == budget and budget >= 12:
            candidate = allowed_indices
        else:
            keep_forbidden = rng.sample(forbidden, k=rng.randint(0, len(forbidden))) if forbidden else []
            candidate = sorted(set(allowed_indices + keep_forbidden))
        cert = force_closure_certificate(contacts, candidate, facets)
        if witness_legal(cert, contacts, allowed):
            return cert
    return Certificate(False)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize_file(path: Path, keys: Iterable[str]) -> list[dict[str, object]]:
    agg = Aggregator(keys)
    with path.open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            normalized = dict(row)
            for name in [
                "accepted",
                "true_legal_certificate",
                "unsafe_false_certificate",
                "missed_true_sfc",
                "geometric_feasible",
                "oracle_sfc_feasible",
            ]:
                normalized[name] = int(float(normalized[name]))
            normalized["quality"] = float(normalized["quality"])
            agg.update(normalized)
    return agg.rows()


def run_family_a() -> tuple[int, int, float]:
    start = time.perf_counter()
    path = RESULTS / "family_a_rows.csv"
    rows_written = 0
    cases = 0
    agg_method = Aggregator(["method"])
    agg_task = Aggregator(["task", "method"])
    agg_trap = Aggregator(["trap_strength", "method"])
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        for task in TASK_NAMES:
            for density in ["sparse", "medium", "dense"]:
                for trap in [0.0, 0.35, 0.7]:
                    for friction in ["low", "medium", "high"]:
                        for seed_idx in range(12):
                            cases += 1
                            seed = SEED + 100000 + cases
                            rng = random.Random(seed)
                            contacts, allowed = generate_contacts(rng, task, density, "medium", trap, friction)
                            params = {
                                "density": density,
                                "allowed_sparsity": "medium",
                                "trap_strength": trap,
                                "friction_band": friction,
                                "facets": 2,
                                "seed": seed,
                                "condition": "task_geometry",
                            }
                            case_id = f"A_{cases:05d}"
                            rows = base_method_rows("A", case_id, task, contacts, allowed, 2, params)
                            for row in rows:
                                writer.writerow(row)
                                agg_method.update(row)
                                agg_task.update(row)
                                agg_trap.update(row)
                            rows_written += len(rows)
    write_csv(RESULTS / "family_a_summary_by_method.csv", agg_method.rows())
    write_csv(RESULTS / "family_a_summary_by_task.csv", agg_task.rows())
    write_csv(RESULTS / "family_a_summary_by_trap.csv", agg_trap.rows())
    return rows_written, cases, time.perf_counter() - start


def run_family_b() -> tuple[int, int, float]:
    start = time.perf_counter()
    path = RESULTS / "family_b_rows.csv"
    rows_written = 0
    cases = 0
    agg_method = Aggregator(["method"])
    agg_noise = Aggregator(["role_error_rate", "confidence_mode", "risk_threshold", "method"])
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        for task in TASK_NAMES:
            for error in [0.0, 0.02, 0.05, 0.10, 0.20, 0.30, 0.40]:
                for mode in ["calibrated", "overconfident", "underconfident", "adversarial"]:
                    for threshold in [0.55, 0.70, 0.85]:
                        for seed_idx in range(6):
                            cases += 1
                            seed = SEED + 200000 + cases
                            rng = random.Random(seed)
                            contacts, allowed = generate_contacts(rng, task, "medium", "medium", 0.55, "medium")
                            params = {
                                "density": "medium",
                                "allowed_sparsity": "medium",
                                "trap_strength": 0.55,
                                "friction_band": "medium",
                                "facets": 2,
                                "seed": seed,
                                "condition": "semantic_noise",
                            }
                            case_id = f"B_{cases:05d}"
                            rows = base_method_rows(
                                "B",
                                case_id,
                                task,
                                contacts,
                                allowed,
                                2,
                                params,
                                include_noise=True,
                                error_rate=error,
                                confidence_mode=mode,
                                risk_threshold=threshold,
                                rng=random.Random(seed + 19),
                            )
                            for row in rows:
                                writer.writerow(row)
                                agg_method.update(row)
                                agg_noise.update(row)
                            rows_written += len(rows)
    write_csv(RESULTS / "family_b_summary_by_method.csv", agg_method.rows())
    write_csv(RESULTS / "family_b_summary_by_noise.csv", agg_noise.rows())
    return rows_written, cases, time.perf_counter() - start


def run_family_c() -> tuple[int, int, float]:
    start = time.perf_counter()
    path = RESULTS / "family_c_rows.csv"
    rows_written = 0
    cases = 0
    agg = Aggregator(["topk_budget", "method"])
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        for task in TASK_NAMES[:8]:
            for trap in [0.25, 0.55, 0.85]:
                for budget in [1, 2, 4, 8, 16]:
                    for seed_idx in range(12):
                        cases += 1
                        seed = SEED + 300000 + cases
                        rng = random.Random(seed)
                        contacts, allowed = generate_contacts(rng, task, "medium", "high", trap, "medium")
                        geometric = force_closure_certificate(contacts, range(len(contacts)), 2)
                        oracle = force_closure_certificate(contacts, true_allowed_indices(contacts, allowed), 2)
                        cert = topk_posthoc(contacts, allowed, 2, budget, random.Random(seed + 7))
                        params = {
                            "density": "medium",
                            "allowed_sparsity": "high",
                            "trap_strength": trap,
                            "friction_band": "medium",
                            "facets": 2,
                            "seed": seed,
                            "topk_budget": budget,
                            "condition": "witness_ordering",
                        }
                        row = make_row(
                            "C",
                            f"C_{cases:05d}",
                            task,
                            "topk_posthoc",
                            cert.feasible,
                            witness_legal(cert, contacts, allowed),
                            cert,
                            contacts,
                            allowed,
                            geometric,
                            oracle,
                            params,
                        )
                        writer.writerow(row)
                        agg.update(row)
                        rows_written += 1
                        if budget in {1, 16}:
                            rows = base_method_rows("C", f"C_{cases:05d}_base", task, contacts, allowed, 2, params)
                            for base_row in rows:
                                writer.writerow(base_row)
                                agg.update(base_row)
                            rows_written += len(rows)
    write_csv(RESULTS / "family_c_summary_by_topk.csv", agg.rows())
    return rows_written, cases, time.perf_counter() - start


def run_family_d() -> tuple[int, int, float]:
    start = time.perf_counter()
    path = RESULTS / "family_d_rows.csv"
    rows_written = 0
    cases = 0
    agg = Aggregator(["friction_band", "facets", "method"])
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        for task in TASK_NAMES[:8]:
            for friction in ["low", "medium", "high", "mixed"]:
                for facets in [2, 4, 8]:
                    for seed_idx in range(8):
                        cases += 1
                        seed = SEED + 400000 + cases
                        rng = random.Random(seed)
                        contacts, allowed = generate_contacts(rng, task, "medium", "medium", 0.55, friction)
                        if seed_idx % 2 == 1:
                            contacts = [
                                Contact(
                                    c.x + rng.uniform(-0.025, 0.025),
                                    c.y + rng.uniform(-0.025, 0.025),
                                    c.role,
                                    max(0.12, c.mu + rng.uniform(-0.05, 0.05)),
                                )
                                for c in contacts
                            ]
                        params = {
                            "density": "medium",
                            "allowed_sparsity": "medium",
                            "trap_strength": 0.55,
                            "friction_band": friction,
                            "facets": facets,
                            "seed": seed,
                            "condition": "friction_model",
                        }
                        rows = base_method_rows("D", f"D_{cases:05d}", task, contacts, allowed, facets, params)
                        for row in rows:
                            writer.writerow(row)
                            agg.update(row)
                        rows_written += len(rows)
    write_csv(RESULTS / "family_d_summary_by_model.csv", agg.rows())
    return rows_written, cases, time.perf_counter() - start


def run_family_e() -> tuple[int, int, float]:
    start = time.perf_counter()
    path = RESULTS / "family_e_rows.csv"
    rows_written = 0
    cases = 0
    agg = Aggregator(["method"])
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        for task in TASK_NAMES:
            for trap in [0.25, 0.55, 0.85]:
                for seed_idx in range(12):
                    cases += 1
                    seed = SEED + 500000 + cases
                    rng = random.Random(seed)
                    contacts, allowed = generate_contacts(rng, task, "medium", "medium", trap, "medium")
                    params = {
                        "density": "medium",
                        "allowed_sparsity": "medium",
                        "trap_strength": trap,
                        "friction_band": "medium",
                        "facets": 2,
                        "seed": seed,
                        "condition": "ablation",
                    }
                    rows = base_method_rows("E", f"E_{cases:05d}", task, contacts, allowed, 2, params)
                    observed, confidence = corrupt_roles(contacts, allowed, task, random.Random(seed + 101), 0.1, "calibrated")
                    obs_indices = observed_allowed_indices(observed, allowed)
                    obs_cert = force_closure_certificate(contacts, obs_indices, 2)
                    geometric = force_closure_certificate(contacts, range(len(contacts)), 2)
                    oracle = force_closure_certificate(contacts, true_allowed_indices(contacts, allowed), 2)
                    params["num_observed_allowed"] = len(obs_indices)
                    rows.append(
                        make_row(
                            "E",
                            f"E_{cases:05d}_obs",
                            task,
                            "delete_noisy_roles",
                            obs_cert.feasible,
                            witness_legal(obs_cert, contacts, allowed),
                            obs_cert,
                            contacts,
                            allowed,
                            geometric,
                            oracle,
                            params,
                        )
                    )
                    rows.append(
                        make_row(
                            "E",
                            f"E_{cases:05d}_auditless",
                            task,
                            "auditless_geometric",
                            geometric.feasible,
                            witness_legal(geometric, contacts, allowed),
                            geometric,
                            contacts,
                            allowed,
                            geometric,
                            oracle,
                            params,
                        )
                    )
                    for row in rows:
                        writer.writerow(row)
                        agg.update(row)
                    rows_written += len(rows)
    write_csv(RESULTS / "family_e_summary_by_ablation.csv", agg.rows())
    return rows_written, cases, time.perf_counter() - start


def run_family_f() -> tuple[int, int, float]:
    start = time.perf_counter()
    path = RESULTS / "family_f_rows.csv"
    rows_written = 0
    cases = 0
    agg = Aggregator(["control", "method"])
    controls = [
        "all_allowed",
        "none_allowed",
        "random_roles",
        "geometrically_infeasible",
        "no_forbidden_advantage",
        "none",
    ]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        for control in controls:
            for task in TASK_NAMES[:8]:
                for seed_idx in range(8):
                    cases += 1
                    seed = SEED + 600000 + cases
                    rng = random.Random(seed)
                    contacts, allowed = generate_contacts(rng, task, "medium", "medium", 0.55, "medium", control)
                    params = {
                        "density": "medium",
                        "allowed_sparsity": "medium",
                        "trap_strength": 0.55,
                        "friction_band": "medium",
                        "facets": 2,
                        "seed": seed,
                        "control": control,
                        "condition": "negative_control",
                    }
                    rows = base_method_rows("F", f"F_{cases:05d}", task, contacts, allowed, 2, params)
                    for row in rows:
                        writer.writerow(row)
                        agg.update(row)
                    rows_written += len(rows)
    write_csv(RESULTS / "family_f_summary_by_control.csv", agg.rows())
    return rows_written, cases, time.perf_counter() - start


def run_family_g() -> tuple[int, int, float]:
    start = time.perf_counter()
    examples: dict[str, dict[str, object] | None] = {
        "geometric_fc_but_not_sfc": None,
        "semantic_only_but_not_sfc": None,
        "posthoc_rejects_but_sfc_finds_alternative": None,
        "unsafe_observed_sfc": None,
        "no_legal_witness": None,
    }
    rows_written = 0
    cases = 0
    path = RESULTS / "family_g_rows.csv"
    agg = Aggregator(["method"])
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        for task in TASK_NAMES:
            for seed_idx in range(80):
                cases += 1
                seed = SEED + 700000 + cases
                rng = random.Random(seed)
                contacts, allowed = generate_contacts(rng, task, "medium", "high", 0.75, "medium")
                params = {
                    "density": "medium",
                    "allowed_sparsity": "high",
                    "trap_strength": 0.75,
                    "friction_band": "medium",
                    "facets": 2,
                    "seed": seed,
                    "condition": "counterexample_audit",
                }
                rows = base_method_rows(
                    "G",
                    f"G_{cases:05d}",
                    task,
                    contacts,
                    allowed,
                    2,
                    params,
                    include_noise=True,
                    error_rate=0.20,
                    confidence_mode="overconfident",
                    risk_threshold=0.70,
                    rng=random.Random(seed + 13),
                )
                row_by_method = {row["method"]: row for row in rows}
                geom = row_by_method["geometric_fc"]
                oracle = row_by_method["oracle_sfc"]
                semantic = row_by_method["semantic_only"]
                posthoc = row_by_method["posthoc_single"]
                observed = row_by_method["observed_sfc"]
                if examples["geometric_fc_but_not_sfc"] is None and int(geom["accepted"]) and not int(oracle["accepted"]):
                    examples["geometric_fc_but_not_sfc"] = geom
                if examples["semantic_only_but_not_sfc"] is None and int(semantic["accepted"]) and not int(oracle["accepted"]):
                    examples["semantic_only_but_not_sfc"] = semantic
                if examples["posthoc_rejects_but_sfc_finds_alternative"] is None and not int(posthoc["accepted"]) and int(oracle["accepted"]):
                    examples["posthoc_rejects_but_sfc_finds_alternative"] = oracle
                if examples["unsafe_observed_sfc"] is None and int(observed["unsafe_false_certificate"]):
                    examples["unsafe_observed_sfc"] = observed
                if examples["no_legal_witness"] is None and int(geom["accepted"]) and not int(oracle["accepted"]):
                    examples["no_legal_witness"] = oracle
                for row in rows:
                    writer.writerow(row)
                    agg.update(row)
                rows_written += len(rows)
    (RESULTS / "counterexample_library.json").write_text(
        json.dumps(examples, indent=2, ensure_ascii=True), encoding="utf-8"
    )
    write_csv(RESULTS / "family_g_summary_by_counterexample.csv", agg.rows())
    return rows_written, cases, time.perf_counter() - start


def latex_table(path: Path, headers: list[str], rows: list[list[object]], caption: str | None = None) -> None:
    align = "l" + "r" * (len(headers) - 1)
    lines = [f"\\begin{{tabular}}{{{align}}}", "\\toprule", " & ".join(headers) + " \\\\", "\\midrule"]
    for row in rows:
        lines.append(" & ".join(str(x) for x in row) + " \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def load_summary(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def pct(value: object) -> str:
    return f"{100 * float(value):.1f}"


def make_tables() -> None:
    main = load_summary(RESULTS / "family_a_summary_by_method.csv")
    main_methods = [
        "geometric_fc",
        "oracle_sfc",
        "semantic_only",
        "posthoc_single",
        "soft_penalty_fc",
    ]
    rows = []
    for method in main_methods:
        item = next((r for r in main if r["method"] == method), None)
        if item:
            rows.append(
                [
                    method.replace("_", "\\_"),
                    pct(item["accepted_rate"]),
                    pct(item["true_legal_rate"]),
                    pct(item["unsafe_rate"]),
                    pct(item["missed_true_sfc_rate"]),
                ]
            )
    latex_table(
        TEX / "table_main_full_scale.tex",
        ["Method", "Accept", "True legal", "Unsafe", "Missed true"],
        rows,
    )

    noise = load_summary(RESULTS / "family_b_summary_by_noise.csv")
    rows = []
    for error in ["0.0", "0.1", "0.2", "0.3", "0.4"]:
        for method in ["observed_sfc", "risk_aware_sfc", "abstaining_sfc"]:
            matches = [
                r
                for r in noise
                if r["role_error_rate"] == error
                and r["method"] == method
                and r["confidence_mode"] == "calibrated"
                and r["risk_threshold"] == "0.7"
            ]
            if matches:
                item = matches[0]
                rows.append([f"{100 * float(error):.0f}\\%", method.replace("_", "\\_"), pct(item["true_legal_rate"]), pct(item["unsafe_rate"]), pct(item["accepted_rate"])])
    latex_table(TEX / "table_semantic_noise.tex", ["Error", "Method", "True legal", "Unsafe", "Accept"], rows)

    topk = load_summary(RESULTS / "family_c_summary_by_topk.csv")
    rows = []
    for budget in ["1", "2", "4", "8", "16"]:
        item = next((r for r in topk if r["topk_budget"] == budget and r["method"] == "topk_posthoc"), None)
        if item:
            rows.append([budget, pct(item["accepted_rate"]), pct(item["true_legal_rate"]), pct(item["missed_true_sfc_rate"])])
    latex_table(TEX / "table_witness_ordering.tex", ["Top-k", "Accept", "True legal", "Missed true"], rows)

    model = load_summary(RESULTS / "family_d_summary_by_model.csv")
    rows = []
    for friction in ["low", "medium", "high", "mixed"]:
        for facets in ["2", "4", "8"]:
            item = next((r for r in model if r["friction_band"] == friction and r["facets"] == facets and r["method"] == "oracle_sfc"), None)
            if item:
                rows.append([friction, facets, pct(item["accepted_rate"]), item["mean_quality_when_feasible"]])
    latex_table(TEX / "table_friction_model.tex", ["Friction", "Facets", "SFC", "Mean quality"], rows)

    ablation = load_summary(RESULTS / "family_e_summary_by_ablation.csv")
    rows = []
    for method in ["oracle_sfc", "posthoc_single", "semantic_only", "soft_penalty_fc", "delete_noisy_roles", "auditless_geometric"]:
        item = next((r for r in ablation if r["method"] == method), None)
        if item:
            rows.append([method.replace("_", "\\_"), pct(item["accepted_rate"]), pct(item["true_legal_rate"]), pct(item["unsafe_rate"])])
    latex_table(TEX / "table_ablations.tex", ["Method", "Accept", "True legal", "Unsafe"], rows)

    controls = load_summary(RESULTS / "family_f_summary_by_control.csv")
    rows = []
    for control in ["all_allowed", "none_allowed", "random_roles", "geometrically_infeasible", "no_forbidden_advantage"]:
        for method in ["geometric_fc", "oracle_sfc"]:
            item = next((r for r in controls if r["control"] == control and r["method"] == method), None)
            if item:
                rows.append([control.replace("_", "\\_"), method.replace("_", "\\_"), pct(item["accepted_rate"]), pct(item["true_legal_rate"])])
    latex_table(TEX / "table_negative_controls.tex", ["Control", "Method", "Accept", "True legal"], rows)

    claim_rows = [
        ["SFC changes witness", "Family A/C/E", "oracle SFC vs posthoc/semantic-only"],
        ["Noisy roles unsafe", "Family B/G", "unsafe observed certificates"],
        ["Monotonic subset", "All families", "zero SFC-without-geometric violations"],
        ["No universal gain", "Family F", "all-allowed/no-forbidden controls"],
    ]
    latex_table(TEX / "table_claim_evidence.tex", ["Claim", "Evidence", "Boundary"], claim_rows)


def make_figures() -> int:
    if plt is None:
        return 1
    failures = 0
    try:
        task = load_summary(RESULTS / "family_a_summary_by_task.csv")
        tasks = sorted({r["task"] for r in task})
        oracle = [float(next(r for r in task if r["task"] == t and r["method"] == "oracle_sfc")["accepted_rate"]) for t in tasks]
        geom_true = [float(next(r for r in task if r["task"] == t and r["method"] == "geometric_fc")["true_legal_rate"]) for t in tasks]
        fig, ax = plt.subplots(figsize=(9, 4.8))
        x = np.arange(len(tasks))
        ax.bar(x - 0.18, oracle, width=0.36, label="Oracle SFC")
        ax.bar(x + 0.18, geom_true, width=0.36, label="Geometric witness legal")
        ax.set_xticks(x)
        ax.set_xticklabels([t.replace("_", "\n") for t in tasks], fontsize=8)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("Task-legal certificate rate")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(FIGURES / "main_task_gap.pdf")
        fig.savefig(FIGURES / "main_task_gap.png", dpi=180)
        plt.close(fig)
    except Exception:
        failures += 1
    try:
        noise = load_summary(RESULTS / "family_b_summary_by_noise.csv")
        errors = [0.0, 0.02, 0.05, 0.10, 0.20, 0.30, 0.40]
        fig, ax = plt.subplots(figsize=(7, 4.5))
        for method in ["observed_sfc", "risk_aware_sfc", "abstaining_sfc"]:
            unsafe = []
            true = []
            for error in errors:
                item = next(
                    r
                    for r in noise
                    if r["method"] == method
                    and r["confidence_mode"] == "calibrated"
                    and r["risk_threshold"] == "0.7"
                    and abs(float(r["role_error_rate"]) - error) < 1e-9
                )
                unsafe.append(float(item["unsafe_rate"]))
                true.append(float(item["true_legal_rate"]))
            ax.plot([100 * e for e in errors], unsafe, marker="o", label=f"{method} unsafe")
        ax.set_xlabel("Role label error (%)")
        ax.set_ylabel("Unsafe false certificate rate")
        ax.set_ylim(0, 1.0)
        ax.legend(frameon=False, fontsize=8)
        fig.tight_layout()
        fig.savefig(FIGURES / "semantic_noise_unsafe.pdf")
        fig.savefig(FIGURES / "semantic_noise_unsafe.png", dpi=180)
        plt.close(fig)
    except Exception:
        failures += 1
    try:
        topk = load_summary(RESULTS / "family_c_summary_by_topk.csv")
        budgets = [1, 2, 4, 8, 16]
        legal = [
            float(next(r for r in topk if r["method"] == "topk_posthoc" and int(r["topk_budget"]) == b)["true_legal_rate"])
            for b in budgets
        ]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(budgets, legal, marker="o", color="#2f6f4e")
        ax.set_xscale("log", base=2)
        ax.set_xticks(budgets)
        ax.set_xticklabels([str(b) for b in budgets])
        ax.set_xlabel("Geometric witnesses searched")
        ax.set_ylabel("True-legal posthoc rate")
        ax.set_ylim(0, 1.05)
        fig.tight_layout()
        fig.savefig(FIGURES / "topk_posthoc.pdf")
        fig.savefig(FIGURES / "topk_posthoc.png", dpi=180)
        plt.close(fig)
    except Exception:
        failures += 1
    try:
        controls = load_summary(RESULTS / "family_f_summary_by_control.csv")
        labels = ["all_allowed", "none_allowed", "random_roles", "geometrically_infeasible", "no_forbidden_advantage"]
        sfc = [
            float(next(r for r in controls if r["control"] == label and r["method"] == "oracle_sfc")["accepted_rate"])
            for label in labels
        ]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(np.arange(len(labels)), sfc, color="#586994")
        ax.set_xticks(np.arange(len(labels)))
        ax.set_xticklabels([label.replace("_", "\n") for label in labels], fontsize=8)
        ax.set_ylabel("Oracle SFC rate")
        ax.set_ylim(0, 1.05)
        fig.tight_layout()
        fig.savefig(FIGURES / "negative_controls.pdf")
        fig.savefig(FIGURES / "negative_controls.png", dpi=180)
        plt.close(fig)
    except Exception:
        failures += 1
    return failures


def write_evidence_summary(metadata: dict[str, object]) -> None:
    main = load_summary(RESULTS / "family_a_summary_by_method.csv")
    noise = load_summary(RESULTS / "family_b_summary_by_noise.csv")
    controls = load_summary(RESULTS / "family_f_summary_by_control.csv")

    def rate(summary: list[dict[str, str]], method: str, key: str = "true_legal_rate") -> str:
        item = next((r for r in summary if r.get("method") == method), None)
        return f"{float(item[key]):.3f}" if item else "n/a"

    observed_10 = next(
        (
            r
            for r in noise
            if r["method"] == "observed_sfc"
            and r["role_error_rate"] == "0.1"
            and r["confidence_mode"] == "calibrated"
            and r["risk_threshold"] == "0.7"
        ),
        None,
    )
    risk_10 = next(
        (
            r
            for r in noise
            if r["method"] == "risk_aware_sfc"
            and r["role_error_rate"] == "0.1"
            and r["confidence_mode"] == "calibrated"
            and r["risk_threshold"] == "0.7"
        ),
        None,
    )
    all_allowed_sfc = next((r for r in controls if r["control"] == "all_allowed" and r["method"] == "oracle_sfc"), None)
    text = [
        "# Full-Scale Evidence Summary",
        "",
        f"- Stage: {metadata['stage']}.",
        f"- Seed: {metadata['seed']}.",
        f"- Rows: {metadata['total_rows']:,} policy/certificate rows.",
        f"- Cases: {metadata['total_cases']:,} contact cases.",
        f"- Plot failures: {metadata['plot_failures']}.",
        "",
        "## Headline Numbers",
        "",
        f"- Family A oracle SFC true-legal rate: {rate(main, 'oracle_sfc')}.",
        f"- Family A geometric FC acceptance rate: {rate(main, 'geometric_fc', 'accepted_rate')}.",
        f"- Family A geometric witness true-legal rate: {rate(main, 'geometric_fc')}.",
        f"- Family A semantic-only true-certificate rate: {rate(main, 'semantic_only')}.",
        f"- Family A posthoc single-witness true-legal rate: {rate(main, 'posthoc_single')}.",
        f"- Family A soft-penalty true-legal rate: {rate(main, 'soft_penalty_fc')}.",
    ]
    if observed_10 and risk_10:
        text.extend(
            [
                f"- Family B at 10% calibrated label error: observed SFC unsafe rate {float(observed_10['unsafe_rate']):.3f}; risk-aware SFC unsafe rate {float(risk_10['unsafe_rate']):.3f}.",
                f"- Family B at 10% calibrated label error: observed SFC true-legal rate {float(observed_10['true_legal_rate']):.3f}; risk-aware SFC true-legal rate {float(risk_10['true_legal_rate']):.3f}.",
            ]
        )
    if all_allowed_sfc:
        text.append(f"- Family F all-allowed control oracle SFC acceptance rate: {float(all_allowed_sfc['accepted_rate']):.3f}.")
    text.extend(
        [
            "",
            "## Scope",
            "",
            "These results support a synthetic certificate-ordering mechanism. They do not establish real-robot grasping performance, semantic perception accuracy, tactile robustness, or dynamic manipulation success.",
            "",
        ]
    )
    (DOCS / "evidence_summary.md").write_text("\n".join(text), encoding="utf-8")


def main() -> int:
    ensure_dirs()
    start = time.perf_counter()
    families = []
    progress = {"stage": "running", "seed": SEED, "families": []}
    (RESULTS / "progress.json").write_text(json.dumps(progress, indent=2), encoding="utf-8")
    total_rows = 0
    total_cases = 0
    for name, func in [
        ("family_a", run_family_a),
        ("family_b", run_family_b),
        ("family_c", run_family_c),
        ("family_d", run_family_d),
        ("family_e", run_family_e),
        ("family_f", run_family_f),
        ("family_g", run_family_g),
    ]:
        print(f"running {name}", flush=True)
        rows, cases, seconds = func()
        item = {"family": name, "rows": rows, "cases": cases, "seconds": seconds}
        families.append(item)
        total_rows += rows
        total_cases += cases
        progress = {"stage": "running", "seed": SEED, "total_rows": total_rows, "total_cases": total_cases, "families": families}
        (RESULTS / "progress.json").write_text(json.dumps(progress, indent=2), encoding="utf-8")
        print(json.dumps(item), flush=True)
    make_tables()
    plot_failures = make_figures()
    metadata = {
        "stage": "complete",
        "seed": SEED,
        "elapsed_seconds": time.perf_counter() - start,
        "total_rows": total_rows,
        "total_cases": total_cases,
        "plot_failures": plot_failures,
        "families": families,
        "outputs": [str(p.relative_to(ROOT)) for p in sorted(RESULTS.rglob("*")) if p.is_file()]
        + [str(p.relative_to(ROOT)) for p in sorted(FIGURES.rglob("*")) if p.is_file()],
    }
    (RESULTS / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (RESULTS / "progress.json").write_text(
        json.dumps({"stage": "complete", "total_rows": total_rows, "total_cases": total_cases}, indent=2),
        encoding="utf-8",
    )
    write_evidence_summary(metadata)
    print(json.dumps(metadata, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
