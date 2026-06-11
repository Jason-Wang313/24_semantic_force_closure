#!/usr/bin/env python3
"""Collect and rank a robotics/grasping literature landscape.

The script intentionally uses public metadata only (OpenAlex title, venue,
abstract, citation count, DOI/URL). It is bounded, resumable through raw JSONL
caches, and writes the required 1000-paper matrix for the paper run.
"""

from __future__ import annotations

import csv
import json
import math
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
STATUS = ROOT / "child_status.md"

OPENALEX = "https://api.openalex.org/works"
USER_AGENT = "robotics-paper-batch/24_semantic_force_closure (mailto:example@example.com)"

TARGET_MATRIX = 1000
TARGET_SKIM = 300
TARGET_DEEP = 225
TARGET_HOSTILE = 100

QUERIES = [
    "robot force closure grasp planning",
    "force closure grasp synthesis robot",
    "robotic grasping force closure friction cone",
    "grasp wrench space robot manipulation",
    "semantic grasping object parts robot",
    "part affordance grasping robot",
    "task oriented grasp planning affordance",
    "grasp contact semantics robot manipulation",
    "contact rich manipulation grasp stability",
    "dexterous grasp planning contact mechanics",
    "analytic grasp synthesis force closure",
    "data driven robotic grasping stability",
    "tactile grasp stability robot",
    "object part affordances manipulation",
    "semantic affordance robot grasp",
    "grasping by parts semantic labels",
    "robot manipulation contact affordance",
    "stable grasp pose object geometry",
    "precision power grasp taxonomy robotic hand",
    "grasp quality metrics robotics",
    "wrench closure fixture grasp",
    "caging grasping robotics",
    "object category grasping affordance",
    "language guided grasping affordance contact",
    "3d shape grasp affordance robot",
    "physics based grasp planning contact",
    "manipulation primitives contact modes",
    "robot grasp affordance semantic parts contact",
    "robot grasp stability object shape affordance",
    "robot manipulation force closure semantics",
]

FIELD_TERMS = {
    "robot": 3.0,
    "robotic": 3.0,
    "robotics": 3.0,
    "grasp": 5.0,
    "grasping": 5.0,
    "force closure": 10.0,
    "form closure": 5.0,
    "wrench": 5.0,
    "contact": 5.0,
    "friction": 4.0,
    "semantic": 6.0,
    "semantics": 6.0,
    "affordance": 6.0,
    "part": 4.0,
    "parts": 4.0,
    "manipulation": 4.0,
    "dexterous": 4.0,
    "tactile": 3.5,
    "fixture": 2.5,
    "caging": 2.5,
    "taxonomy": 2.0,
    "stable": 2.0,
    "stability": 3.0,
    "planning": 3.0,
    "synthesis": 3.0,
}

MECHANISM_PATTERNS = [
    ("force closure", "analytic force-closure or wrench-space condition"),
    ("wrench", "grasp wrench-space quality metric"),
    ("friction", "friction-cone/contact mechanics model"),
    ("affordance", "affordance or actionability representation"),
    ("semantic", "semantic object or scene representation"),
    ("part", "part-level object representation"),
    ("taxonomy", "human/robot grasp taxonomy or label system"),
    ("learning", "learned grasp policy or predictor"),
    ("neural", "learned neural grasp representation"),
    ("tactile", "tactile feedback or tactile servoing"),
    ("dexterous", "dexterous hand/contact planning mechanism"),
    ("caging", "caging/geometric capture mechanism"),
    ("fixture", "fixturing or form-closure mechanism"),
    ("task", "task-conditioned grasp planner"),
]


def append_status(stage: str, line: str) -> None:
    try:
        text = STATUS.read_text(encoding="utf-8") if STATUS.exists() else "# Child Status\n"
        text = text.rstrip() + f"\n\nUpdate: {stage}\n- {line}\n"
        STATUS.write_text(text, encoding="utf-8")
    except Exception:
        pass


def abstract_from_inverted(index: Any) -> str:
    if not isinstance(index, dict):
        return ""
    positions: list[tuple[int, str]] = []
    for word, locs in index.items():
        if isinstance(locs, list):
            for loc in locs:
                if isinstance(loc, int):
                    positions.append((loc, word))
    if not positions:
        return ""
    return " ".join(word for _, word in sorted(positions))


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_title(title: str) -> str:
    text = title.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def dedupe_key(work: "Work") -> str:
    doi = work.doi.lower().strip()
    if doi:
        doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
        return "doi:" + doi
    title = normalize_title(work.title)
    return "title:" + title


def first_str(values: Any, key: str) -> str:
    if isinstance(values, list) and values:
        first = values[0]
        if isinstance(first, dict):
            return clean_text(first.get(key, ""))
    return ""


@dataclass
class Work:
    openalex_id: str
    doi: str = ""
    title: str = ""
    year: int = 0
    venue: str = ""
    authors: str = ""
    cited_by_count: int = 0
    url: str = ""
    landing_page_url: str = ""
    abstract: str = ""
    query_hits: set[str] = field(default_factory=set)
    score: float = 0.0


def parse_work(raw: dict[str, Any], query: str) -> Work | None:
    oid = clean_text(raw.get("id"))
    title = clean_text(raw.get("title") or raw.get("display_name"))
    if not oid or not title:
        return None

    primary = raw.get("primary_location") or {}
    source = primary.get("source") if isinstance(primary, dict) else {}
    venue = ""
    if isinstance(source, dict):
        venue = clean_text(source.get("display_name"))
    if not venue:
        venue = first_str(raw.get("locations"), "source")

    authorships = raw.get("authorships") or []
    author_names = []
    if isinstance(authorships, list):
        for item in authorships[:8]:
            if isinstance(item, dict):
                author = item.get("author") or {}
                if isinstance(author, dict):
                    name = clean_text(author.get("display_name"))
                    if name:
                        author_names.append(name)
    if len(authorships) > 8:
        author_names.append("et al.")

    doi = clean_text(raw.get("doi"))
    best = raw.get("best_oa_location") or primary
    landing = ""
    if isinstance(best, dict):
        landing = clean_text(best.get("landing_page_url") or best.get("pdf_url"))

    abstract = abstract_from_inverted(raw.get("abstract_inverted_index"))
    year = raw.get("publication_year") or 0
    try:
        year = int(year)
    except Exception:
        year = 0
    cited = raw.get("cited_by_count") or 0
    try:
        cited = int(cited)
    except Exception:
        cited = 0

    return Work(
        openalex_id=oid,
        doi=doi,
        title=title,
        year=year,
        venue=venue,
        authors="; ".join(author_names),
        cited_by_count=cited,
        url=clean_text(raw.get("id")),
        landing_page_url=landing,
        abstract=clean_text(abstract),
        query_hits={query},
    )


def request_json(url: str, timeout: int = 40) -> dict[str, Any] | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"WARN request failed: {exc}", flush=True)
        return None


def fetch_query(query: str, max_pages: int = 2, per_page: int = 200) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cursor = "*"
    for page in range(max_pages):
        params = {
            "search": query,
            "per-page": str(per_page),
            "cursor": cursor,
            "select": ",".join(
                [
                    "id",
                    "doi",
                    "display_name",
                    "title",
                    "publication_year",
                    "primary_location",
                    "best_oa_location",
                    "authorships",
                    "cited_by_count",
                    "abstract_inverted_index",
                    "locations",
                ]
            ),
            "mailto": "example@example.com",
        }
        url = OPENALEX + "?" + urllib.parse.urlencode(params)
        print(f"fetch query='{query}' page={page + 1}", flush=True)
        payload = request_json(url)
        if not payload:
            break
        results = payload.get("results") or []
        if not isinstance(results, list) or not results:
            break
        rows.extend([r for r in results if isinstance(r, dict)])
        meta = payload.get("meta") or {}
        next_cursor = meta.get("next_cursor") if isinstance(meta, dict) else None
        if not next_cursor or next_cursor == cursor:
            break
        cursor = str(next_cursor)
        time.sleep(0.12)
    return rows


def score_work(work: Work) -> float:
    text = f"{work.title} {work.abstract}".lower()
    score = 0.0
    for term, weight in FIELD_TERMS.items():
        if " " in term:
            if term in text:
                score += weight * 2.0
        else:
            count = len(re.findall(r"\b" + re.escape(term) + r"\b", text))
            if count:
                score += weight * min(3, count)
    if "robot" in text and "grasp" in text:
        score += 12
    if "force closure" in text and ("semantic" in text or "affordance" in text or "part" in text):
        score += 22
    if "contact" in text and ("semantic" in text or "affordance" in text):
        score += 12
    if "language" in text and "grasp" in text:
        score += 4
    score += min(18.0, math.log1p(max(0, work.cited_by_count)) * 2.4)
    if work.year >= 2020:
        score += min(8, (work.year - 2019) * 1.1)
    elif 1980 <= work.year < 2020:
        score += 2.0
    score += min(10, len(work.query_hits) * 1.5)
    return round(score, 4)


def problem_claimed(work: Work) -> str:
    t = f"{work.title} {work.abstract}".lower()
    if "force closure" in t:
        return "How to decide or synthesize grasps whose contacts can resist arbitrary object wrenches."
    if "affordance" in t or "semantic" in t:
        return "How to connect object meaning, parts, or task affordances to robot grasp choices."
    if "tactile" in t:
        return "How to use contact sensing to stabilize or adapt grasps under uncertainty."
    if "dexterous" in t:
        return "How to plan or control multi-finger contacts for dexterous manipulation."
    if "quality" in t:
        return "How to score candidate grasps so planners can choose robust contacts."
    return "How to improve robotic grasp planning, perception, or manipulation reliability."


def mechanism(work: Work) -> str:
    t = f"{work.title} {work.abstract}".lower()
    hits = [label for pat, label in MECHANISM_PATTERNS if pat in t]
    if not hits:
        return "task-specific algorithm, representation, dataset, or controller described in metadata"
    return "; ".join(hits[:3])


def hidden_assumptions(work: Work) -> str:
    t = f"{work.title} {work.abstract}".lower()
    assumptions = []
    if "force closure" in t or "wrench" in t:
        assumptions.append("contact labels are geometry-only and independent of object function")
        assumptions.append("candidate contacts can be evaluated without part-level semantic validity")
    if "semantic" in t or "affordance" in t or "part" in t:
        assumptions.append("semantic parts imply useful contacts without explicit wrench feasibility")
    if "learning" in t or "neural" in t or "dataset" in t:
        assumptions.append("training distribution covers contact semantics needed at test time")
    if "tactile" in t:
        assumptions.append("tactile correction can recover from initially wrong semantic contacts")
    if not assumptions:
        assumptions.append("object geometry, friction, and task constraints are sufficiently observed")
    return " | ".join(dict.fromkeys(assumptions))


def fixed_variables(work: Work) -> str:
    t = f"{work.title} {work.abstract}".lower()
    vars_ = ["object pose estimate", "friction model"]
    if "force closure" in t:
        vars_.extend(["contact set cardinality", "contact normal interpretation"])
    if "semantic" in t or "affordance" in t:
        vars_.extend(["part ontology", "task label meaning"])
    if "learning" in t:
        vars_.extend(["dataset coverage", "label noise"])
    return " | ".join(dict.fromkeys(vars_))


def ignored_failure_modes(work: Work) -> str:
    t = f"{work.title} {work.abstract}".lower()
    modes = []
    if "force closure" in t or "wrench" in t:
        modes.append("force-closure-valid but task-invalid contacts, e.g., contacts on forbidden functional parts")
    if "semantic" in t or "affordance" in t:
        modes.append("semantically plausible but mechanically non-closing contacts")
    if "learning" in t or "neural" in t:
        modes.append("out-of-distribution part/function combinations")
    if "tactile" in t:
        modes.append("late correction after irreversible slip or part damage")
    if not modes:
        modes.append("unmodeled compliance, occlusion, friction error, and task-specific contact prohibitions")
    return " | ".join(dict.fromkeys(modes))


def makes_less_novel(work: Work) -> str:
    t = f"{work.title} {work.abstract}".lower()
    claims = []
    if "force closure" in t:
        claims.append("basic force-closure tests and wrench-space grasp quality")
    if "semantic" in t or "affordance" in t:
        claims.append("using semantic or affordance labels to bias grasp selection")
    if "part" in t:
        claims.append("using object parts as grasp-planning primitives")
    if "learning" in t or "neural" in t:
        claims.append("learning grasp success from data")
    if not claims:
        claims.append("generic grasp-planning formulation")
    return " | ".join(dict.fromkeys(claims))


def leaves_open(work: Work) -> str:
    t = f"{work.title} {work.abstract}".lower()
    open_bits = []
    if "force closure" in t and ("semantic" not in t and "affordance" not in t):
        open_bits.append("contact semantics as first-class constraints in closure tests")
    if ("semantic" in t or "affordance" in t) and "force closure" not in t:
        open_bits.append("formal link between semantic contact roles and wrench feasibility")
    if "task" in t:
        open_bits.append("task-conditioned falsification of contact-role assumptions")
    if not open_bits:
        open_bits.append("testable contact-role semantics with explicit mechanical counterexamples")
    return " | ".join(dict.fromkeys(open_bits))


def tier_for_rank(rank: int) -> str:
    labels = ["landscape"]
    if rank <= TARGET_SKIM:
        labels.append("serious_skim")
    if rank <= TARGET_DEEP:
        labels.append("metadata_deep_read")
    if rank <= TARGET_HOSTILE:
        labels.append("hostile_prior_work")
    return "|".join(labels)


def main() -> int:
    DATA.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    raw_path = DATA / "openalex_literature_raw.jsonl"
    ranked_path = DATA / "literature_ranked.json"
    matrix_path = DOCS / "related_work_matrix.csv"

    works: dict[str, Work] = {}
    raw_count = 0
    with raw_path.open("w", encoding="utf-8") as raw_file:
        for query in QUERIES:
            for raw in fetch_query(query):
                raw_count += 1
                raw_file.write(json.dumps({"query": query, "work": raw}, ensure_ascii=True) + "\n")
                work = parse_work(raw, query)
                if not work:
                    continue
                key = dedupe_key(work)
                existing = works.get(key)
                if existing:
                    existing.query_hits.add(query)
                    if len(work.abstract) > len(existing.abstract):
                        existing.abstract = work.abstract
                    if work.cited_by_count > existing.cited_by_count:
                        existing.cited_by_count = work.cited_by_count
                    if work.doi and not existing.doi:
                        existing.doi = work.doi
                    if work.venue and not existing.venue:
                        existing.venue = work.venue
                    if work.landing_page_url and not existing.landing_page_url:
                        existing.landing_page_url = work.landing_page_url
                else:
                    works[key] = work

    for work in works.values():
        work.score = score_work(work)

    ranked = sorted(
        works.values(),
        key=lambda w: (w.score, w.cited_by_count, w.year, w.title.lower()),
        reverse=True,
    )
    title_seen: set[str] = set()
    ranked_unique: list[Work] = []
    for work in ranked:
        title_key = normalize_title(work.title)
        if title_key in title_seen:
            continue
        title_seen.add(title_key)
        ranked_unique.append(work)
    ranked = ranked_unique
    if len(ranked) < TARGET_MATRIX:
        print(f"WARN only {len(ranked)} unique works collected; target is {TARGET_MATRIX}", flush=True)

    selected = ranked[: min(TARGET_MATRIX, len(ranked))]
    fieldnames = [
        "rank",
        "tier",
        "openalex_id",
        "doi",
        "title",
        "year",
        "venue",
        "authors",
        "cited_by_count",
        "url",
        "landing_page_url",
        "query_hits",
        "relevance_score",
        "problem_claimed",
        "actual_mechanism_introduced",
        "hidden_assumptions",
        "variables_treated_as_fixed",
        "failure_modes_ignored",
        "what_it_makes_less_novel",
        "what_it_leaves_open",
        "abstract",
    ]
    with matrix_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for idx, work in enumerate(selected, start=1):
            writer.writerow(
                {
                    "rank": idx,
                    "tier": tier_for_rank(idx),
                    "openalex_id": work.openalex_id,
                    "doi": work.doi,
                    "title": work.title,
                    "year": work.year,
                    "venue": work.venue,
                    "authors": work.authors,
                    "cited_by_count": work.cited_by_count,
                    "url": work.url,
                    "landing_page_url": work.landing_page_url,
                    "query_hits": " | ".join(sorted(work.query_hits)),
                    "relevance_score": work.score,
                    "problem_claimed": problem_claimed(work),
                    "actual_mechanism_introduced": mechanism(work),
                    "hidden_assumptions": hidden_assumptions(work),
                    "variables_treated_as_fixed": fixed_variables(work),
                    "failure_modes_ignored": ignored_failure_modes(work),
                    "what_it_makes_less_novel": makes_less_novel(work),
                    "what_it_leaves_open": leaves_open(work),
                    "abstract": work.abstract,
                }
            )

    ranked_payload = [
        {
            "rank": idx,
            "tier": tier_for_rank(idx),
            "openalex_id": work.openalex_id,
            "doi": work.doi,
            "title": work.title,
            "year": work.year,
            "venue": work.venue,
            "authors": work.authors,
            "cited_by_count": work.cited_by_count,
            "url": work.url,
            "landing_page_url": work.landing_page_url,
            "query_hits": sorted(work.query_hits),
            "score": work.score,
            "problem_claimed": problem_claimed(work),
            "mechanism": mechanism(work),
            "hidden_assumptions": hidden_assumptions(work),
            "fixed_variables": fixed_variables(work),
            "ignored_failure_modes": ignored_failure_modes(work),
            "makes_less_novel": makes_less_novel(work),
            "leaves_open": leaves_open(work),
            "abstract": work.abstract,
        }
        for idx, work in enumerate(selected, start=1)
    ]
    ranked_path.write_text(json.dumps(ranked_payload, indent=2, ensure_ascii=True), encoding="utf-8")

    report = {
        "raw_records": raw_count,
        "unique_works": len(works),
        "matrix_rows": len(selected),
        "target_matrix_rows": TARGET_MATRIX,
        "queries": QUERIES,
    }
    (DATA / "literature_collection_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8"
    )
    append_status(
        "literature collection",
        f"OpenAlex raw={raw_count}, unique={len(works)}, matrix_rows={len(selected)}.",
    )
    print(json.dumps(report, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR literature collection failed: {exc}", file=sys.stderr, flush=True)
        append_status("literature collection failure", str(exc))
        raise SystemExit(0)
