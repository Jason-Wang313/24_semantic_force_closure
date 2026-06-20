# Paper24 VLA Highlight Hardening Plan

Date: 2026-06-20

## Objective

Make `C:/Users/wangz/Downloads/24.pdf` explicitly match the visible VLA-v4
role model's boxed-link behavior while preserving the final 25-page semantic
force-closure paper:

- citation links use green one-point boxes;
- internal figure/table/section links use red one-point boxes;
- no cyan URL boxes appear;
- the final PDF is rebuilt, copied only to Downloads, visually checked, and
  leaves no local `paper/main.pdf`.

## Plan-Start Evidence

Baseline artifact:

- Canonical PDF: `C:/Users/wangz/Downloads/24.pdf`
- Pages: 25
- Size: 369,669 bytes
- SHA256: `97A560CC4A30E210346B035BE8FCFFF705544D1510B2DACE5B08C71D641E544A`
- Local `paper/main.pdf`: absent
- Repository state: clean against `origin/master`

Baseline link inventory from the current Downloads PDF:

- Link pages: `[(1, 7), (2, 18), (5, 1), (6, 2), (7, 3), (8, 3)]`
- Annotation colors: green = 25, red = 9, cyan = 0
- Border widths: `(0, 0, 1)` for all 34 link annotations

Source finding:

- `paper/main.tex` is the active manuscript source.
- The preamble currently loads plain `hyperref` but has no explicit VLA-style
  `\hypersetup`.
- The current PDF already has the desired green/red boxed-link behavior, but
  the source should make that behavior explicit and stable.
- `scripts/build_paper.ps1` copies the final PDF to Downloads; if it leaves
  `paper/main.pdf`, remove that local PDF after verification.

## Role-Model Target

Install the same explicit hyperref policy as the visible VLA-v4 role model:

```tex
\usepackage{hyperref}
\hypersetup{
  colorlinks=false,
  pdfborder={0 0 1},
  citebordercolor={0 1 0},
  linkbordercolor={1 0 0},
  urlbordercolor={0 1 0}
}
```

## Execution Plan

1. Add the VLA `\hypersetup` block immediately after `\usepackage{hyperref}`
   in `paper/main.tex`.
2. Rebuild with `scripts/build_paper.ps1`, including BibTeX, so the final PDF
   is copied to Downloads.
3. Remove local `paper/main.pdf` after export if the build script leaves it.
4. If the first rebuild asks for another LaTeX pass, rerun the canonical build
   and use only the final artifact metadata.
5. Recompute page count, SHA256, annotation colors, border widths, and link
   pages from the rebuilt PDF.
6. Render all affected link pages from the rebuilt Downloads PDF into
   `tmp/pdfs/paper24_after`.
7. Visually inspect the rendered affected pages:
   - green citation boxes are crisp and aligned;
   - red internal-reference boxes are crisp and aligned;
   - no cyan boxes appear;
   - layout, figures, tables, headers, and page count remain stable.
8. Update README/status/audit/version/validation metadata with the new hash and
   visual-hardening result.
9. Scan LaTeX logs and build outputs for fatal errors, undefined
   citations/references, rerun warnings, and overfull boxes.
10. Remove Paper24 temp renders, leaving only the shared role-model render
    directory.
11. Stage only Paper24 source and metadata files, commit, push, and verify a
    clean repository.

## Non-Goals

- Do not alter experiment results, claims, figures, tables, bibliography
  content, or page count.
- Do not add or remove citations merely to change link counts.
- Do not leave intermediate PDFs or render folders behind.

## Completion Evidence

- Rebuilt Downloads artifact: `C:/Users/wangz/Downloads/24.pdf`
- Pages: 25
- Size: 369,669 bytes
- SHA256: `A96EB09B4F6204ED53597C519B982F941D8BA87DD200F98028042BB7E3B68097`
- Local `paper/main.pdf`: absent after export
- Link pages after rebuild: `[(1, 7), (2, 18), (5, 1), (6, 2), (7, 3), (8, 3)]`
- Annotation colors after rebuild: green = 25, red = 9, cyan = 0
- Border widths after rebuild: `(0, 0, 1)` for all 34 link annotations
- Rendered affected pages inspected from `tmp/pdfs/paper24_after`; green
  citation boxes and red internal-reference boxes are crisp and aligned, and
  no cyan boxes are present.
