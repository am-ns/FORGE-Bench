# FORGE-Bench paper draft

Repository-wide release and scoring progress is tracked in
[`PROJECT_STATUS.md`](../../PROJECT_STATUS.md).

This directory contains the Chinese manuscript and a portable English LaTeX draft. The LaTeX entry point uses the standard `article` class and does not require template logos or custom class files.

Compile with:

```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

Incomplete aggregate results are shown as dashes and are never replaced with partial-sample estimates.

The manuscript is aligned to the September 11, 2026 public release: ten matched
500-video collections (5,000 videos) at
`https://huggingface.co/datasets/aaaabcd/FORGE-Bench`. A 451-video refresh
invalidated earlier cached aggregates, so the current table intentionally shows
dashes until complete post-refresh scoring is available.

The original VisionXLab template remains unchanged under `VisionXLab_LaTeX_Template/`.
