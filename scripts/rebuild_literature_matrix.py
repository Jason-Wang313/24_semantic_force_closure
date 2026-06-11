#!/usr/bin/env python3
"""Rebuild ranked literature artifacts from the raw OpenAlex JSONL cache."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from fetch_literature import (
    DATA,
    DOCS,
    TARGET_MATRIX,
    Work,
    append_status,
    fixed_variables,
    hidden_assumptions,
    ignored_failure_modes,
    leaves_open,
    makes_less_novel,
    mechanism,
    normalize_title,
    parse_work,
    problem_claimed,
    score_work,
    tier_for_rank,
)


def merge(existing: Work, new: Work, query: str) -> None:
    existing.query_hits.add(query)
    if len(new.abstract) > len(existing.abstract):
        existing.abstract = new.abstract
    if new.cited_by_count > existing.cited_by_count:
        existing.cited_by_count = new.cited_by_count
    if new.doi and not existing.doi:
        existing.doi = new.doi
    if new.venue and not existing.venue:
        existing.venue = new.venue
    if new.landing_page_url and not existing.landing_page_url:
        existing.landing_page_url = new.landing_page_url
    if new.year > existing.year:
        existing.year = new.year


def row_for(idx: int, work: Work) -> dict[str, object]:
    return {
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


def main() -> int:
    raw_path = DATA / "openalex_literature_raw.jsonl"
    matrix_path = DOCS / "related_work_matrix.csv"
    ranked_path = DATA / "literature_ranked.json"
    by_title: dict[str, Work] = {}
    raw_count = 0
    if not raw_path.exists():
        print(f"missing raw cache: {raw_path}")
        append_status("literature rebuild failure", f"missing raw cache {raw_path}")
        return 0

    with raw_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            raw_count += 1
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            query = str(payload.get("query", "cache"))
            work_raw = payload.get("work")
            if not isinstance(work_raw, dict):
                continue
            work = parse_work(work_raw, query)
            if not work:
                continue
            key = normalize_title(work.title)
            if not key:
                continue
            if key in by_title:
                merge(by_title[key], work, query)
            else:
                by_title[key] = work

    for work in by_title.values():
        work.score = score_work(work)
    ranked = sorted(
        by_title.values(),
        key=lambda w: (w.score, w.cited_by_count, w.year, w.title.lower()),
        reverse=True,
    )
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
            writer.writerow(row_for(idx, work))

    ranked_payload = []
    for idx, work in enumerate(selected, start=1):
        item = row_for(idx, work)
        item["query_hits"] = sorted(work.query_hits)
        ranked_payload.append(item)
    ranked_path.write_text(json.dumps(ranked_payload, indent=2, ensure_ascii=True), encoding="utf-8")

    report = {
        "raw_records": raw_count,
        "unique_normalized_titles": len(by_title),
        "matrix_rows": len(selected),
        "source": str(raw_path),
    }
    (DATA / "literature_rebuild_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8"
    )
    append_status(
        "literature rebuild",
        f"raw={raw_count}, unique_titles={len(by_title)}, matrix_rows={len(selected)}.",
    )
    print(json.dumps(report, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

